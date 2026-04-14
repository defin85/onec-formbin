from __future__ import annotations

import difflib
import json
from dataclasses import dataclass
from pathlib import Path

from .container import ContainerError, decode_text_body, parse_file, sha256_bytes
from .form_ast import (
    FormAstError,
    append_form_continuation_text,
    ast_to_pretty_json,
    parse_form_text,
)
from .models import (
    FormRenderMode,
    ManifestRecord,
    RecordKind,
    SEMANTIC_SLICE_NAMES,
    SizePolicy,
    semantic_slice_path,
)
from .semantic_form import build_semantic_model
from .workspace import read_manifest, read_record_body, read_text_exact


@dataclass(slots=True)
class SourceRecord:
    index: int
    kind: RecordKind
    label: str
    field1: int
    field2: int
    field3: int
    size_policy: SizePolicy
    pointer_record_index: int | None
    relative_path: str
    body: bytes
    text_override: str | None = None

    @property
    def body_sha256(self) -> str:
        return sha256_bytes(self.body)

    @property
    def is_text(self) -> bool:
        return self.kind in {RecordKind.FORM, RecordKind.MODULE, RecordKind.TEXT}

    @property
    def text(self) -> str:
        if self.text_override is not None:
            return self.text_override
        if not self.is_text:
            raise ContainerError(f"Record {self.index} is not a text payload.")
        return decode_text_body(self.body)


@dataclass(slots=True)
class SourceView:
    path: Path
    prefix_sha256: str
    records: list[SourceRecord]


def diff_paths(
    left: Path,
    right: Path,
    *,
    form_mode: FormRenderMode = FormRenderMode.RAW,
    context: int = 3,
) -> dict:
    left_view = load_source(left)
    right_view = load_source(right)

    changed_records = []
    added_records = []
    removed_records = []

    max_len = max(len(left_view.records), len(right_view.records))
    for index in range(max_len):
        left_record = left_view.records[index] if index < len(left_view.records) else None
        right_record = right_view.records[index] if index < len(right_view.records) else None
        if left_record is None:
            added_records.append(record_summary(right_record))
            continue
        if right_record is None:
            removed_records.append(record_summary(left_record))
            continue

        metadata_changed = []
        for field in ("kind", "label", "field1", "field2", "field3", "pointer_record_index"):
            if getattr(left_record, field) != getattr(right_record, field):
                metadata_changed.append(field)

        body_changed = left_record.body_sha256 != right_record.body_sha256
        if not metadata_changed and not body_changed:
            continue

        body_diff = ""
        notes: list[str] = []
        render_mode = None
        if left_record.is_text and right_record.is_text:
            render_mode = form_mode.value if left_record.kind is RecordKind.FORM else "raw"
            if not (left_record.kind is RecordKind.FORM and form_mode is FormRenderMode.SEMANTIC):
                left_render, right_render, notes = render_payloads_for_diff(
                    left_record,
                    right_record,
                    left_source_path=left_view.path,
                    right_source_path=right_view.path,
                    form_mode=form_mode,
                )
                body_diff = unified_text_diff(
                    left_render,
                    right_render,
                    fromfile=f"{left}:{left_record.relative_path}",
                    tofile=f"{right}:{right_record.relative_path}",
                    context=context,
                )

        changed_records.append(
            {
                "index": index,
                "left": record_summary(left_record),
                "right": record_summary(right_record),
                "metadata_changed": metadata_changed,
                "body_changed": body_changed,
                "render_mode": render_mode,
                "notes": notes,
                "body_diff": body_diff,
            }
        )

    semantic_diff_text = ""
    semantic_notes: list[str] = []
    if form_mode is FormRenderMode.SEMANTIC:
        form_change = next(
            (
                record
                for record in changed_records
                if record["left"] is not None
                and record["right"] is not None
                and record["left"]["label"] == "form"
                and record["right"]["label"] == "form"
            ),
            None,
        )
        try:
            semantic_diff_text, semantic_notes = render_semantic_slice_diffs(
                left_view.path,
                right_view.path,
                context=context,
                prefer_workspace=(
                    form_change is None
                    or (not form_change["body_changed"] and not form_change["metadata_changed"])
                ),
            )
        except FormAstError as exc:
            semantic_notes = [f"form semantic build failed, semantic diff unavailable: {exc}"]

        if form_change is not None:
            form_change["render_mode"] = "semantic"
            form_change["body_diff"] = semantic_diff_text
            form_change["notes"] = semantic_notes
        elif semantic_diff_text:
            left_form = next((record for record in left_view.records if record.kind is RecordKind.FORM), None)
            right_form = next((record for record in right_view.records if record.kind is RecordKind.FORM), None)
            changed_records.append(
                {
                    "index": left_form.index if left_form is not None else right_form.index,
                    "left": record_summary(left_form),
                    "right": record_summary(right_form),
                    "metadata_changed": [],
                    "body_changed": False,
                    "render_mode": "semantic",
                    "notes": ["semantic workspace slices changed without raw form payload changes"],
                    "body_diff": semantic_diff_text,
                }
            )

    identical = (
        left_view.prefix_sha256 == right_view.prefix_sha256
        and not changed_records
        and not added_records
        and not removed_records
    )
    return {
        "left": str(left),
        "right": str(right),
        "identical": identical,
        "prefix_changed": left_view.prefix_sha256 != right_view.prefix_sha256,
        "left_record_count": len(left_view.records),
        "right_record_count": len(right_view.records),
        "added_records": added_records,
        "removed_records": removed_records,
        "changed_records": changed_records,
    }


def render_diff_report(report: dict) -> str:
    lines = [
        f"left: {report['left']}",
        f"right: {report['right']}",
        f"identical: {'yes' if report['identical'] else 'no'}",
    ]
    if report["prefix_changed"]:
        lines.append("prefix: changed")
    if report["added_records"]:
        lines.append(f"added: {len(report['added_records'])}")
    if report["removed_records"]:
        lines.append(f"removed: {len(report['removed_records'])}")
    if report["changed_records"]:
        lines.append(f"changed: {len(report['changed_records'])}")

    for record in report["changed_records"]:
        left = record["left"]
        right = record["right"]
        lines.append(
            "record "
            f"#{record['index']}: "
            f"{left['kind']}/{left['label']} -> {right['kind']}/{right['label']}"
        )
        if record["metadata_changed"]:
            lines.append("  metadata: " + ", ".join(record["metadata_changed"]))
        for note in record["notes"]:
            lines.append(f"  note: {note}")
        if record["body_diff"]:
            lines.append(record["body_diff"].rstrip("\n"))
    return "\n".join(lines) + "\n"


def load_source(path: Path) -> SourceView:
    if path.is_dir():
        manifest = read_manifest(path)
        prefix = (path / "prefix.bin").read_bytes()
        records = [
            source_record_from_manifest(path, record)
            for record in sorted(manifest.records, key=lambda item: item.index)
        ]
        attach_form_text_overrides(path, records)
        return SourceView(path=path, prefix_sha256=sha256_bytes(prefix), records=records)

    container = parse_file(path)
    records = [
        SourceRecord(
            index=record.index,
            kind=record.kind,
            label=record.label,
            field1=record.field1,
            field2=record.field2,
            field3=record.field3,
            size_policy=record.size_policy,
            pointer_record_index=record.pointer_record_index,
            relative_path=record.relative_path,
            body=record.body,
        )
        for record in container.records
    ]
    attach_form_text_overrides(path.parent, records)
    return SourceView(path=path, prefix_sha256=sha256_bytes(container.prefix), records=records)


def source_record_from_manifest(root: Path, record: ManifestRecord) -> SourceRecord:
    return SourceRecord(
        index=record.index,
        kind=record.kind,
        label=record.label,
        field1=record.field1,
        field2=record.field2,
        field3=record.field3,
        size_policy=record.size_policy,
        pointer_record_index=record.pointer_record_index,
        relative_path=record.relative_path,
        body=read_record_body(root, record),
    )


def attach_form_text_overrides(root: Path, records: list[SourceRecord]) -> None:
    for record in records:
        if record.kind is not RecordKind.FORM:
            continue
        try:
            record.text_override = append_form_continuation_text(
                root,
                records,
                record,
                decode_text_body(record.body),
            )
        except ContainerError:
            continue


def record_summary(record: SourceRecord | None) -> dict | None:
    if record is None:
        return None
    return {
        "index": record.index,
        "kind": record.kind.value,
        "label": record.label,
        "field1": record.field1,
        "field2": record.field2,
        "field3": record.field3,
        "pointer_record_index": record.pointer_record_index,
        "relative_path": record.relative_path,
        "body_sha256": record.body_sha256,
    }


def render_payloads_for_diff(
    left: SourceRecord,
    right: SourceRecord,
    *,
    left_source_path: Path,
    right_source_path: Path,
    form_mode: FormRenderMode,
) -> tuple[str, str, list[str]]:
    if (
        left.kind is RecordKind.FORM
        and right.kind is RecordKind.FORM
        and form_mode is FormRenderMode.AST
    ):
        try:
            left_ast = parse_form_text(left.text)
            right_ast = parse_form_text(right.text)
            return ast_to_pretty_json(left_ast), ast_to_pretty_json(right_ast), []
        except FormAstError as exc:
            note = f"form AST parse failed, raw diff shown: {exc}"
            return left.text, right.text, [note]
    return left.text, right.text, []


def render_semantic_slice_diffs(
    left_source_path: Path,
    right_source_path: Path,
    *,
    context: int,
    prefer_workspace: bool,
) -> tuple[str, list[str]]:
    left_semantic = load_semantic_slices_for_diff(left_source_path, prefer_workspace=prefer_workspace)
    right_semantic = load_semantic_slices_for_diff(right_source_path, prefer_workspace=prefer_workspace)

    parts: list[str] = []
    for key in sorted(set(left_semantic) | set(right_semantic)):
        left_text = render_semantic_slice(left_semantic.get(key))
        right_text = render_semantic_slice(right_semantic.get(key))
        diff = unified_text_diff(
            left_text,
            right_text,
            fromfile=f"semantic/{key}:left",
            tofile=f"semantic/{key}:right",
            context=context,
        )
        if not diff:
            continue
        if parts:
            parts.append("\n")
        parts.append(f"### semantic/{key}\n")
        parts.append(diff)

    notes: list[str] = []
    if not parts:
        notes.append("semantic slices identical; raw form text changed")
    return "".join(parts), notes


def render_semantic_slice(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def load_semantic_slices_for_diff(path: Path, *, prefer_workspace: bool) -> dict:
    if not path.is_dir() or not prefer_workspace:
        return build_semantic_model(path)["semantic"]

    workspace_slices: dict[str, object] = {}
    fallback_semantic: dict | None = None
    found_workspace_slice = False
    for name in SEMANTIC_SLICE_NAMES:
        slice_path = semantic_slice_path(path, name)
        if slice_path.exists():
            found_workspace_slice = True
            try:
                workspace_slices[name] = json.loads(read_text_exact(slice_path))
            except json.JSONDecodeError as exc:
                raise ContainerError(f"Invalid semantic JSON at {slice_path}.") from exc
            continue
        if fallback_semantic is None:
            fallback_semantic = build_semantic_model(path)["semantic"]
        workspace_slices[name] = fallback_semantic[name]

    if found_workspace_slice:
        return workspace_slices
    return build_semantic_model(path)["semantic"]


def unified_text_diff(
    left: str,
    right: str,
    *,
    fromfile: str,
    tofile: str,
    context: int,
) -> str:
    return "".join(
        difflib.unified_diff(
            left.splitlines(keepends=True),
            right.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
            n=context,
        )
    )
