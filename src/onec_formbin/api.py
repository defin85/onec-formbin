from __future__ import annotations

import json
from pathlib import Path

from . import __version__
from .container import ContainerError, decode_text_body, parse_file, render_header, sha256_bytes
from .descriptor_json import parse_descriptor_body
from .models import (
    Manifest,
    ManifestRecord,
    PackedRecord,
    RecordKind,
    SEMANTIC_SLICE_NAMES,
    container_inspect_path,
    descriptor_json_path,
    manifest_path,
    semantic_slice_path,
    support_artifact_path,
)
from .workspace import (
    read_manifest,
    write_text_exact,
)
from .workspace import (
    read_record_body as read_record_body_exact,
)


def inspect_file(path: Path) -> dict:
    if not path.exists():
        raise ContainerError(f"Path does not exist: {path}.")
    if path.is_dir():
        return read_workspace_inspect(path)
    container = parse_file(path)
    return inspect_container(container, path=path)


def inspect_container(container, *, path: Path) -> dict:
    descriptor_links, descriptor_index_by_payload = build_descriptor_links(container.records)
    continuation_chains, continuation_chain_by_record, continuation_target_label_by_record = (
        build_continuation_metadata(container.records)
    )
    pointer_links = build_pointer_links(container.records)
    record_layout = build_record_layout(container)
    return {
        "path": str(path),
        "prefix_sha256": sha256_bytes(container.prefix),
        "record_count": len(container.records),
        "records": [
            inspect_record(
                record,
                descriptor_index_by_payload=descriptor_index_by_payload,
                continuation_chain_by_record=continuation_chain_by_record,
                continuation_target_label_by_record=continuation_target_label_by_record,
            )
            for record in container.records
        ],
        "descriptor_links": descriptor_links,
        "continuation_chains": continuation_chains,
        "pointer_links": pointer_links,
        "record_layout": record_layout,
    }


def write_inspect_json(path: Path, info: dict) -> None:
    write_text_exact(path, json.dumps(info, ensure_ascii=False, indent=2) + "\n")


def write_workspace_descriptor_json(path: Path, info: dict) -> None:
    write_text_exact(path, json.dumps(info, ensure_ascii=False, indent=2) + "\n")


def read_workspace_inspect(directory: Path) -> dict:
    inspect_path = container_inspect_path(directory)
    if not inspect_path.exists():
        raise ContainerError(
            f"Unpack directory is missing {inspect_path.name}; run unpack first or inspect the source Form.bin."
        )

    try:
        payload = json.loads(inspect_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContainerError(f"Invalid inspect JSON at {inspect_path}.") from exc

    if not isinstance(payload, dict):
        raise ContainerError(f"Inspect JSON at {inspect_path} must be a top-level object.")

    required_keys = ("path", "record_count", "records")
    missing = [key for key in required_keys if key not in payload]
    if missing:
        missing_text = ", ".join(missing)
        raise ContainerError(f"Inspect JSON at {inspect_path} is missing required keys: {missing_text}.")

    if not isinstance(payload["records"], list):
        raise ContainerError(f"Inspect JSON at {inspect_path} must contain a records list.")

    return payload


def inspect_record(
    record,
    *,
    descriptor_index_by_payload: dict[int, int],
    continuation_chain_by_record: dict[int, list[int]],
    continuation_target_label_by_record: dict[int, str],
) -> dict:
    info = {
        "index": record.index,
        "header_start": record.header_start,
        "body_start": record.body_start,
        "body_end": record.body_end,
        "field1": record.field1,
        "field2": record.field2,
        "field3": record.field3,
        "kind": record.kind.value,
        "label": record.label,
        "size_policy": record.size_policy.value,
        "pointer_record_index": record.pointer_record_index,
        "body_sha256": sha256_bytes(record.body),
        "codec": record.codec,
        "record_role": classify_record_role(
            record,
            continuation_target_label_by_record=continuation_target_label_by_record,
        ),
        "workspace_relative_path": record.relative_path,
        "linked_descriptor_index": descriptor_index_by_payload.get(record.index),
        "continuation_chain": continuation_chain_by_record.get(record.index),
    }
    if record.kind is RecordKind.DESCRIPTOR:
        info["descriptor_json"] = parse_descriptor_body(record.body, label=record.label)
    return info


def build_descriptor_links(records: list) -> tuple[list[dict[str, int | str]], dict[int, int]]:
    descriptor_index_by_label = {
        record.label: record.index
        for record in records
        if record.kind is RecordKind.DESCRIPTOR
    }
    links: list[dict[str, int | str]] = []
    descriptor_index_by_payload: dict[int, int] = {}
    for record in records:
        if record.kind not in {RecordKind.FORM, RecordKind.MODULE}:
            continue
        descriptor_index = descriptor_index_by_label.get(record.label)
        if descriptor_index is None:
            continue
        links.append(
            {
                "label": record.label,
                "descriptor_index": descriptor_index,
                "payload_index": record.index,
            }
        )
        descriptor_index_by_payload[record.index] = descriptor_index
    return links, descriptor_index_by_payload


def build_continuation_metadata(
    records: list,
) -> tuple[list[dict[str, int | str | list[int]]], dict[int, list[int]], dict[int, str]]:
    record_by_index = {record.index: record for record in records}
    chains: list[dict[str, int | str | list[int]]] = []
    continuation_chain_by_record: dict[int, list[int]] = {}
    continuation_target_label_by_record: dict[int, str] = {}

    for record in records:
        if record.pointer_record_index is None:
            continue

        chain = [record.index]
        seen = {record.index}
        next_index = record.pointer_record_index
        while next_index is not None and next_index not in seen:
            target_record = record_by_index.get(next_index)
            if target_record is None:
                break
            chain.append(target_record.index)
            seen.add(target_record.index)
            next_index = target_record.pointer_record_index

        chains.append(
            {
                "kind": record.kind.value,
                "label": record.label,
                "head_record_index": record.index,
                "record_indices": chain,
            }
        )
        for index in chain:
            continuation_chain_by_record[index] = chain
        for index in chain[1:]:
            continuation_target_label_by_record[index] = record.label

    return chains, continuation_chain_by_record, continuation_target_label_by_record


def build_pointer_links(records: list) -> list[dict[str, int | str]]:
    record_by_index = {record.index: record for record in records}
    links: list[dict[str, int | str]] = []
    for record in records:
        target_index = record.pointer_record_index
        if target_index is None:
            continue
        target_record = record_by_index.get(target_index)
        if target_record is None:
            continue
        links.append(
            {
                "source_record_index": record.index,
                "target_record_index": target_record.index,
                "target_header_start": target_record.header_start,
                "source_label": record.label,
                "target_label": target_record.label,
            }
        )
    return links


def build_record_layout(container) -> dict:
    return {
        "prefix_size": len(container.prefix),
        "total_size": container.total_size,
        "record_spans": [
            {
                "index": record.index,
                "header_start": record.header_start,
                "header_end": record.header_end,
                "body_start": record.body_start,
                "body_end": record.body_end,
            }
            for record in container.records
        ],
    }


def classify_record_role(
    record,
    *,
    continuation_target_label_by_record: dict[int, str],
) -> str:
    continuation_label = continuation_target_label_by_record.get(record.index)
    if continuation_label is not None:
        return f"{continuation_label}_continuation"
    if record.kind is RecordKind.DESCRIPTOR:
        return f"{record.label}_descriptor"
    return f"{record.label}_payload"


def unpack_file(source: Path, output_dir: Path) -> Manifest:
    container = parse_file(source)
    inspect_info = inspect_container(container, path=source)
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "prefix.bin").write_bytes(container.prefix)

    manifest_records: list[ManifestRecord] = []
    for record in container.records:
        record_path = output_dir / record.relative_path
        record_path.parent.mkdir(parents=True, exist_ok=True)
        if record.kind in {RecordKind.FORM, RecordKind.MODULE, RecordKind.TEXT}:
            text = decode_text_body(record.body)
            write_text_exact(record_path, text)
        else:
            record_path.write_bytes(record.body)
        manifest_records.append(
            ManifestRecord(
                index=record.index,
                header_start=record.header_start,
                field1=record.field1,
                field2=record.field2,
                field3=record.field3,
                kind=record.kind,
                label=record.label,
                size_policy=record.size_policy,
                pointer_record_index=record.pointer_record_index,
                codec=record.codec,
                relative_path=record.relative_path,
                sha256=sha256_bytes(record.body),
            )
        )

    export_workspace_descriptor_json(output_dir, container.records)

    manifest = Manifest(
        tool_version=__version__,
        source_file=str(source),
        prefix_sha256=sha256_bytes(container.prefix),
        record_count=len(manifest_records),
        records=manifest_records,
    )
    write_inspect_json(container_inspect_path(output_dir), inspect_info)
    write_text_exact(manifest_path(output_dir), manifest.model_dump_json(indent=2) + "\n")
    export_workspace_semantic_json(output_dir, output_dir)
    return manifest


def export_workspace_descriptor_json(output_dir: Path, records: list) -> None:
    for record in records:
        if record.kind is not RecordKind.DESCRIPTOR:
            continue
        if record.label not in {"form", "module"}:
            continue
        artifact_path = descriptor_json_path(output_dir, record.label)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        write_workspace_descriptor_json(
            artifact_path,
            parse_descriptor_body(record.body, label=record.label),
        )


def export_workspace_semantic_json(source_path: Path, output_dir: Path) -> None:
    from .semantic_form import build_workspace_bundle_artifacts

    bundle = build_workspace_bundle_artifacts(source_path)
    semantic = bundle["semantic"]
    for name in SEMANTIC_SLICE_NAMES:
        artifact_path = semantic_slice_path(output_dir, name)
        write_workspace_descriptor_json(artifact_path, semantic[name])
    for name, payload in bundle["support"].items():
        artifact_path = support_artifact_path(output_dir, name)
        write_workspace_descriptor_json(artifact_path, payload)


def pack_directory(input_dir: Path, output_file: Path) -> None:
    manifest = read_manifest(input_dir)
    prefix = (input_dir / "prefix.bin").read_bytes()

    packed_records: list[PackedRecord] = []
    for record in manifest.records:
        body = read_record_body_exact(input_dir, record)
        if record.size_policy == "mirror":
            field1 = len(body)
        else:
            if len(body) != record.field2:
                raise ContainerError(
                    "Size-changing edit is not allowed for record "
                    f"{record.index} ({record.relative_path}); field1 is undocumented."
                )
            field1 = record.field1
        packed_records.append(
            PackedRecord(
                record=record,
                body=body,
                field1=field1,
                field2=len(body),
                field3=record.field3,
            )
        )

    header_starts = calculate_header_starts(prefix, packed_records)
    for packed in packed_records:
        target_index = packed.record.pointer_record_index
        if target_index is not None:
            packed.field3 = header_starts[target_index]

    output = bytearray(prefix)
    for packed in packed_records:
        output.extend(render_header(packed.field1, packed.field2, packed.field3))
        output.extend(packed.body)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(bytes(output))


def roundtrip_check(path: Path) -> bool:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="onec-formbin-") as tmp:
        tmpdir = Path(tmp)
        unpack_dir = tmpdir / "unpack"
        repacked = tmpdir / path.name
        unpack_file(path, unpack_dir)
        pack_directory(unpack_dir, repacked)
        return path.read_bytes() == repacked.read_bytes()


def calculate_header_starts(prefix: bytes, records: list[PackedRecord]) -> list[int]:
    starts: list[int] = []
    offset = len(prefix)
    for packed in records:
        starts.append(offset)
        offset += len(render_header(packed.field1, packed.field2, packed.field3))
        offset += len(packed.body)
    return starts
