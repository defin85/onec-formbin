from __future__ import annotations

import json
from pathlib import Path

from .api import inspect_file
from .container import ContainerError, decode_text_body, parse_file
from .descriptor_json import parse_descriptor_body
from .form_ast import AstNode, parse_form_source, serialize_form_text
from .models import (
    ManifestRecord,
    Record,
    RecordKind,
    SEMANTIC_SLICE_NAMES,
    container_inspect_path,
    semantic_slice_path,
)
from .workspace import read_manifest, read_text_exact, write_text_exact

SEMANTIC_VERSION = 1
SAMPLE_LIMIT = 12
PREVIEW_LIMIT = 80
FORM_META_SCHEMA = "onec-formbin.form-meta.v1"
FORM_META_VERSION = 1
EVENTS_SCHEMA = "onec-formbin.events.v1"
EVENTS_VERSION = 1
COMMANDS_SCHEMA = "onec-formbin.commands.v1"
COMMANDS_VERSION = 1
ATTRIBUTES_SCHEMA = "onec-formbin.attributes.v1"
ATTRIBUTES_VERSION = 1
CONTROLS_TREE_SCHEMA = "onec-formbin.controls-tree.v1"
CONTROLS_TREE_VERSION = 1
LAYOUT_SCHEMA = "onec-formbin.layout.v1"
LAYOUT_VERSION = 1
STRINGS_SCHEMA = "onec-formbin.strings.v1"
STRINGS_VERSION = 1
BUNDLE_CONTRACT_ID = "ordinary-form-bundle.v1"
CAPABILITIES_SCHEMA = "onec-formbin.bundle-capabilities.v1"
CAPABILITIES_VERSION = 1
PROVENANCE_SCHEMA = "onec-formbin.bundle-provenance.v1"
PROVENANCE_VERSION = 1
UNCERTAINTY_SCHEMA = "onec-formbin.bundle-uncertainty.v1"
UNCERTAINTY_VERSION = 1
INTEGRATION_SCHEMA = "onec-formbin.bundle-integration.v1"
INTEGRATION_VERSION = 1
FORM_ROOT_ID = "form-root"
FORM_OWNER_KIND = "form"
EVENT_OWNER_KIND = "event"
COMMAND_OWNER_KIND = "command"
CONTROL_OWNER_KIND = "control"
FORM_SCOPE = "form"
CONTROL_SCOPE = "control"
COMMAND_SOURCE_AST_ROOT_TITLE_MATCH = "ast-root-title-match"
FORM_TITLE_ROLE = "form_title"
EVENT_HANDLER_ROLE = "event_handler"
COMMAND_NAME_ROLE = "command_name"
COMMAND_TITLE_ROLE = "command_title"
CONTROL_NAME_ROLE = "control_name"
AST_STRING_ROLE = "ast_string"
CONTROL_KIND = "control"
CONTROL_PATTERN_ROLE = "control_pattern_binding_candidate"
WRITABLE_STRING_ROLES = {
    FORM_TITLE_ROLE,
    EVENT_HANDLER_ROLE,
    COMMAND_NAME_ROLE,
    COMMAND_TITLE_ROLE,
    CONTROL_NAME_ROLE,
}
LOCALIZED_TITLE_MAX_DEPTH = 2
TOP_LEVEL_FORM_EVENTS_INDEX = 4
CONTROL_SECTION_PATH = (1, 2, 2)
CONTROL_DATA_INDEX = 2
CONTROL_NAME_INDEX = 4
CONTROL_CHILDREN_INDEX = 5


def build_workspace_bundle_artifacts(path: Path) -> dict:
    node = parse_form_source(path)
    container_summary = summarize_container(path)
    workspace_bundle = summarize_workspace_bundle(path, node, container_summary=container_summary)
    return {
        "container": container_summary,
        "form_model": summarize_ast(node),
        "semantic": workspace_bundle["semantic"],
        "support": workspace_bundle["support"],
    }


def build_semantic_model(path: Path) -> dict:
    workspace_bundle = build_workspace_bundle_artifacts(path)
    return {
        "semantic_version": SEMANTIC_VERSION,
        "source": {
            "path": str(path),
            "kind": detect_source_kind(path),
        },
        "container": workspace_bundle["container"],
        "form_model": workspace_bundle["form_model"],
        "semantic": workspace_bundle["semantic"],
    }


def write_semantic_json(path: Path, model: dict) -> None:
    write_text_exact(path, json.dumps(model, ensure_ascii=False, indent=2) + "\n")


def build_semantic_file(source_path: Path, output_path: Path) -> None:
    write_semantic_json(output_path, build_semantic_model(source_path))


def detect_source_kind(path: Path) -> str:
    if path.is_dir():
        return "unpack_dir"
    if path.suffix.lower() == ".bin":
        return "form_bin"
    return "raw_file"


def summarize_container(path: Path) -> dict:
    inspect_backbone = load_inspect_backbone(path)

    if path.is_dir():
        manifest = read_manifest(path)
        records = manifest.records
        summary = {
            "available": True,
            "record_count": len(records),
            "descriptor_records": [
                summarize_descriptor_record(path, record) for record in records if record.kind is RecordKind.DESCRIPTOR
            ],
            "form_record": summarize_form_record(next_record(records, RecordKind.FORM)),
            "module_record": summarize_module_record(path, next_record(records, RecordKind.MODULE)),
        }
        if inspect_backbone is not None:
            summary["inspect_backbone"] = inspect_backbone
        return summary

    if path.suffix.lower() == ".bin":
        container = parse_file(path)
        records = container.records
        summary = {
            "available": True,
            "record_count": len(records),
            "descriptor_records": [
                summarize_descriptor_record(path, record) for record in records if record.kind is RecordKind.DESCRIPTOR
            ],
            "form_record": summarize_form_record(next_record(records, RecordKind.FORM)),
            "module_record": summarize_module_record(path, next_record(records, RecordKind.MODULE)),
        }
        if inspect_backbone is not None:
            summary["inspect_backbone"] = inspect_backbone
        return summary

    return {"available": False}


def load_inspect_backbone(path: Path) -> dict | None:
    if path.is_dir():
        inspect_path = container_inspect_path(path)
        if not inspect_path.exists():
            return None
        info = json.loads(read_text_exact(inspect_path))
    else:
        info = inspect_file(path)

    return {
        "descriptor_links": info["descriptor_links"],
        "continuation_chains": info["continuation_chains"],
        "pointer_links": info["pointer_links"],
        "record_layout": info["record_layout"],
    }


def summarize_semantic_slices(path: Path, node: AstNode, *, container_summary: dict) -> dict:
    form_meta = build_form_meta_slice(path, node, container_summary=container_summary)
    form_title_ref = extract_form_title_ref(node)
    form_events = collect_form_event_details(node, root_item_id=form_meta["root_item_id"])
    commands = collect_command_details(node, root_item_id=form_meta["root_item_id"])
    controls = collect_control_bundle(
        path,
        node,
        form_meta=form_meta,
        command_details=commands,
    )
    return {
        "form.meta.json": form_meta,
        "events.json": build_events_slice(form_events),
        "commands.json": build_commands_slice(commands),
        "attributes.json": controls["attributes"],
        "controls.tree.json": controls["controls_tree"],
        "layout.json": controls["layout"],
        "strings.json": build_strings_slice(
            node,
            root_item_id=form_meta["root_item_id"],
            form_title_ref=form_title_ref,
            form_events=form_events,
            commands=commands,
            control_name_paths=controls["control_name_paths"],
        ),
    }


def summarize_workspace_bundle(path: Path, node: AstNode, *, container_summary: dict) -> dict:
    form_meta = build_form_meta_slice(path, node, container_summary=container_summary)
    form_title_ref = extract_form_title_ref(node)
    form_events = collect_form_event_details(node, root_item_id=form_meta["root_item_id"])
    commands = collect_command_details(node, root_item_id=form_meta["root_item_id"])
    controls = collect_control_bundle(
        path,
        node,
        form_meta=form_meta,
        command_details=commands,
    )
    semantic = {
        "form.meta.json": form_meta,
        "events.json": build_events_slice(form_events),
        "commands.json": build_commands_slice(commands),
        "attributes.json": controls["attributes"],
        "controls.tree.json": controls["controls_tree"],
        "layout.json": controls["layout"],
        "strings.json": build_strings_slice(
            node,
            root_item_id=form_meta["root_item_id"],
            form_title_ref=form_title_ref,
            form_events=form_events,
            commands=commands,
            control_name_paths=controls["control_name_paths"],
        ),
    }
    support = build_support_artifacts(
        path,
        container_summary=container_summary,
        semantic=semantic,
        form_title_ref=form_title_ref,
        form_events=form_events,
        commands=commands,
        controls=controls,
    )
    return {
        "semantic": semantic,
        "support": support,
    }


def build_support_artifacts(
    path: Path,
    *,
    container_summary: dict,
    semantic: dict,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    form_events: list[dict],
    commands: list[dict],
    controls: dict,
) -> dict:
    return {
        "capabilities.json": build_capabilities_artifact(
            path,
            container_summary=container_summary,
            semantic=semantic,
            form_title_ref=form_title_ref,
            form_events=form_events,
            commands=commands,
            controls=controls,
        ),
        "provenance.json": build_provenance_artifact(
            container_summary=container_summary,
            semantic=semantic,
            form_title_ref=form_title_ref,
            form_events=form_events,
            commands=commands,
            controls=controls,
        ),
        "uncertainty.json": build_uncertainty_artifact(container_summary=container_summary),
        "integration.json": build_integration_artifact(
            path,
            container_summary=container_summary,
            semantic=semantic,
        ),
    }


def build_capabilities_artifact(
    path: Path,
    *,
    container_summary: dict,
    semantic: dict,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    form_events: list[dict],
    commands: list[dict],
    controls: dict,
) -> dict:
    split_form = is_split_form_workspace(container_summary)
    control_ids = set(controls["control_name_paths"].values())
    editable_items: list[dict] = []

    if not split_form:
        if form_title_ref is not None:
            editable_items.append(
                {
                    "semantic_file": "semantic/form.meta.json",
                    "semantic_id": FORM_ROOT_ID,
                    "fields": ["form_title"],
                }
            )
        editable_items.extend(
            {
                "semantic_file": "semantic/events.json",
                "semantic_id": item["id"],
                "fields": ["handler"],
            }
            for item in form_events
        )
        editable_items.extend(
            {
                "semantic_file": "semantic/commands.json",
                "semantic_id": item["id"],
                "fields": ["name", "title"],
            }
            for item in commands
        )
        editable_items.extend(
            {
                "semantic_file": "semantic/controls.tree.json",
                "semantic_id": item["id"],
                "fields": ["name", "title"],
                "field_sync_groups": [["name", "title"]],
            }
            for item in semantic["controls.tree.json"]["items"]
            if item["id"] != FORM_ROOT_ID and item["id"] in control_ids
        )
        editable_items.extend(
            {
                "semantic_file": "semantic/attributes.json",
                "semantic_id": item["id"],
                "fields": ["name", "data_path"],
                "field_sync_groups": [["name", "data_path"]],
            }
            for item in semantic["attributes.json"]["items"]
        )
        editable_items.extend(
            {
                "semantic_file": "semantic/strings.json",
                "semantic_id": item["id"],
                "fields": ["value"],
                "role": item["role"],
                "alias_of": build_string_alias_target(item),
            }
            for item in semantic["strings.json"]["items"]
            if item["role"] in WRITABLE_STRING_ROLES
        )

    editable_items.sort(key=editable_item_sort_key)

    read_only_rules = [
        "semantic/layout.json remains read-only.",
        "semantic/form.meta.json fields outside editable_items stay read-only.",
        "semantic/events.json fields outside editable_items stay read-only.",
        "semantic/commands.json fields outside editable_items stay read-only.",
        "semantic/controls.tree.json structural fields stay read-only.",
        "semantic/attributes.json fields outside editable_items stay read-only.",
        "semantic/strings.json is writable only for alias roles listed in editable_items.",
    ]
    if split_form:
        read_only_rules.insert(0, "Split-form workspaces are read-only for apply-semantic.")

    return {
        "schema": CAPABILITIES_SCHEMA,
        "version": CAPABILITIES_VERSION,
        "bundle_contract": BUNDLE_CONTRACT_ID,
        "workspace_mode": "raw-first",
        "source_kind": detect_source_kind(path),
        "split_form": split_form,
        "apply_semantic_supported": not split_form,
        "editable_items": editable_items,
        "read_only_files": ["semantic/layout.json"],
        "write_constraints": [
            "controls.tree.json editable items require name and title to stay in sync.",
            "attributes.json editable items require name and data_path to stay in sync.",
            "strings.json editable items are aliases for already-supported owner write paths.",
        ],
        "read_only_rules": read_only_rules,
    }


def build_provenance_artifact(
    *,
    container_summary: dict,
    semantic: dict,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    form_events: list[dict],
    commands: list[dict],
    controls: dict,
) -> dict:
    split_form = is_split_form_workspace(container_summary)
    write_support = "unsupported_split_form" if split_form else "supported"
    alias_write_support = "unsupported_split_form" if split_form else "alias_supported"
    anchor = current_form_record_anchor(container_summary)
    control_paths = control_paths_by_id(controls["control_name_paths"])
    items: list[dict] = []

    if form_title_ref is not None:
        items.append(
            make_provenance_item(
                semantic_file="semantic/form.meta.json",
                semantic_id=FORM_ROOT_ID,
                owner_kind=FORM_OWNER_KIND,
                owner_id=FORM_ROOT_ID,
                anchor=anchor,
                fields={
                    "form_title": build_field_provenance(
                        [form_title_ref[1]],
                        write_support=write_support,
                    )
                },
            )
        )

    items.extend(
        make_provenance_item(
            semantic_file="semantic/events.json",
            semantic_id=item["id"],
            owner_kind=EVENT_OWNER_KIND,
            owner_id=item["owner_id"],
            anchor=anchor,
            fields={
                "handler": build_field_provenance(
                    [item["handler_path"]],
                    write_support=write_support,
                )
            },
        )
        for item in form_events
    )

    items.extend(
        make_provenance_item(
            semantic_file="semantic/commands.json",
            semantic_id=item["id"],
            owner_kind=COMMAND_OWNER_KIND,
            owner_id=item["owner_id"],
            anchor=anchor,
            fields={
                "name": build_field_provenance(
                    [item["name_path"]],
                    write_support=write_support,
                ),
                "title": build_field_provenance(
                    item["title_paths"],
                    write_support=write_support,
                ),
            },
        )
        for item in commands
    )

    items.extend(
        make_provenance_item(
            semantic_file="semantic/controls.tree.json",
            semantic_id=item["id"],
            owner_kind=CONTROL_OWNER_KIND,
            owner_id=item["id"],
            anchor=anchor,
            fields={
                "name": build_field_provenance(
                    control_paths[item["id"]],
                    write_support=write_support,
                    coupled_with=["title"],
                ),
                "title": build_field_provenance(
                    control_paths[item["id"]],
                    write_support=write_support,
                    coupled_with=["name"],
                ),
            },
        )
        for item in semantic["controls.tree.json"]["items"]
        if item["id"] != FORM_ROOT_ID and item["id"] in control_paths
    )

    items.extend(
        make_provenance_item(
            semantic_file="semantic/attributes.json",
            semantic_id=item["id"],
            owner_kind="attribute",
            owner_id=item["owner_id"],
            anchor=anchor,
            fields={
                "name": build_field_provenance(
                    control_paths[item["owner_id"]],
                    write_support=write_support,
                    coupled_with=["data_path"],
                ),
                "data_path": build_field_provenance(
                    control_paths[item["owner_id"]],
                    write_support=write_support,
                    coupled_with=["name"],
                ),
            },
        )
        for item in semantic["attributes.json"]["items"]
        if item["owner_id"] in control_paths
    )

    items.extend(
        make_provenance_item(
            semantic_file="semantic/strings.json",
            semantic_id=item["id"],
            owner_kind=item["owner_kind"],
            owner_id=item["owner_id"],
            anchor=anchor,
            fields={
                "value": build_field_provenance(
                    [parse_item_path(item["id"], prefix="string")],
                    write_support=alias_write_support,
                    alias_of=build_string_alias_target(item),
                    role=item["role"],
                )
            },
        )
        for item in semantic["strings.json"]["items"]
        if item["role"] in WRITABLE_STRING_ROLES
    )

    items.sort(key=provenance_item_sort_key)
    return {
        "schema": PROVENANCE_SCHEMA,
        "version": PROVENANCE_VERSION,
        "bundle_contract": BUNDLE_CONTRACT_ID,
        "items": items,
    }


def build_uncertainty_artifact(*, container_summary: dict) -> dict:
    items = [
        {
            "scope": "semantic/events.json",
            "effect": "partial_semantics",
            "reason": "form_scope_and_current_control_binding_bridge_only",
        },
        {
            "scope": "semantic/commands.json",
            "effect": "partial_semantics",
            "reason": "root_command_title_match_bridge_only",
        },
        {
            "scope": "semantic/attributes.json",
            "effect": "partial_semantics",
            "reason": "control_pattern_binding_candidates_only",
        },
        {
            "scope": "semantic/controls.tree.json",
            "effect": "partial_semantics",
            "reason": "explicit_control_wrappers_only",
        },
        {
            "scope": "semantic/layout.json",
            "effect": "read_only",
            "reason": "coarse_layout_visibility_bridge_only",
        },
        {
            "scope": "semantic/strings.json",
            "effect": "partial_semantics",
            "reason": "alias_roles_are_fixture_backed_subset_only",
        },
    ]
    if is_split_form_workspace(container_summary):
        items.insert(
            0,
            {
                "scope": "workspace",
                "effect": "write_unsupported",
                "reason": "split_form_writeback_unavailable",
            },
        )
    return {
        "schema": UNCERTAINTY_SCHEMA,
        "version": UNCERTAINTY_VERSION,
        "items": items,
    }


def build_integration_artifact(path: Path, *, container_summary: dict, semantic: dict) -> dict:
    return {
        "schema": INTEGRATION_SCHEMA,
        "version": INTEGRATION_VERSION,
        "bundle_contract": BUNDLE_CONTRACT_ID,
        "source_kind": detect_source_kind(path),
        "preferred_entrypoint": "support/integration.json",
        "preferred_ingest_files": [
            "support/integration.json",
            "support/uncertainty.json",
            "semantic/form.meta.json",
            "semantic/events.json",
            "semantic/commands.json",
            "semantic/attributes.json",
            "semantic/controls.tree.json",
            "semantic/layout.json",
            "semantic/strings.json",
        ],
        "container": {
            "record_count": container_summary.get("record_count", 0),
            "split_form": is_split_form_workspace(container_summary),
            "has_module_record": container_summary.get("module_record") is not None,
        },
        "form": {
            "form_name": semantic["form.meta.json"]["form_name"],
            "form_title": semantic["form.meta.json"]["form_title"],
            "form_kind": semantic["form.meta.json"]["form_kind"],
            "root_item_id": semantic["form.meta.json"]["root_item_id"],
        },
        "counts": {
            "events": len(semantic["events.json"]["items"]),
            "commands": len(semantic["commands.json"]["items"]),
            "attributes": len(semantic["attributes.json"]["items"]),
            "control_nodes": len(semantic["controls.tree.json"]["items"]),
            "layout_items": len(semantic["layout.json"]["items"]),
            "strings": len(semantic["strings.json"]["items"]),
        },
        "semantic_files": {
            name: {
                "path": f"semantic/{name}",
                "schema": semantic[name]["schema"],
                "version": semantic[name]["version"],
            }
            for name in SEMANTIC_SLICE_NAMES
        },
        "support_files": {
            "capabilities.json": {
                "path": "support/capabilities.json",
                "schema": CAPABILITIES_SCHEMA,
                "version": CAPABILITIES_VERSION,
            },
            "provenance.json": {
                "path": "support/provenance.json",
                "schema": PROVENANCE_SCHEMA,
                "version": PROVENANCE_VERSION,
            },
            "uncertainty.json": {
                "path": "support/uncertainty.json",
                "schema": UNCERTAINTY_SCHEMA,
                "version": UNCERTAINTY_VERSION,
            },
            "integration.json": {
                "path": "support/integration.json",
                "schema": INTEGRATION_SCHEMA,
                "version": INTEGRATION_VERSION,
            },
        },
    }


def is_split_form_workspace(container_summary: dict) -> bool:
    form_record = container_summary.get("form_record") or {}
    return bool(form_record.get("split_form"))


def current_form_record_anchor(container_summary: dict) -> dict:
    form_record = container_summary.get("form_record") or {}
    anchor: dict[str, int | str] = {}
    if "index" in form_record:
        anchor["record_index"] = form_record["index"]
    if "relative_path" in form_record:
        anchor["workspace_relative_path"] = form_record["relative_path"]
    return anchor


def editable_item_sort_key(item: dict) -> tuple:
    return (
        item["semantic_file"],
        item["semantic_id"],
        tuple(item["fields"]),
        item.get("role", ""),
    )


def provenance_item_sort_key(item: dict) -> tuple:
    return (item["semantic_file"], item["semantic_id"])


def control_paths_by_id(control_name_paths: dict[tuple[int, ...], str]) -> dict[str, list[tuple[int, ...]]]:
    grouped: dict[str, list[tuple[int, ...]]] = {}
    for path, control_id in control_name_paths.items():
        grouped.setdefault(control_id, []).append(path)
    for paths in grouped.values():
        paths.sort()
    return grouped


def make_provenance_item(
    *,
    semantic_file: str,
    semantic_id: str,
    owner_kind: str,
    owner_id: str,
    anchor: dict,
    fields: dict,
) -> dict:
    item = {
        "semantic_file": semantic_file,
        "semantic_id": semantic_id,
        "owner_kind": owner_kind,
        "owner_id": owner_id,
        "fields": fields,
    }
    item.update(anchor)
    return item


def build_field_provenance(
    paths: list[tuple[int, ...]],
    *,
    write_support: str,
    alias_of: str | None = None,
    coupled_with: list[str] | None = None,
    role: str | None = None,
) -> dict:
    payload = {
        "ast_string_paths": [list(path) for path in paths],
        "write_support": write_support,
    }
    if alias_of is not None:
        payload["alias_of"] = alias_of
    if coupled_with is not None:
        payload["coupled_with"] = coupled_with
    if role is not None:
        payload["role"] = role
    return payload


def build_string_alias_target(item: dict) -> str:
    role = item["role"]
    owner_id = item["owner_id"]
    if role == FORM_TITLE_ROLE:
        return "form_title"
    if role == EVENT_HANDLER_ROLE:
        return f"event:{owner_id}:handler"
    if role == COMMAND_NAME_ROLE:
        return f"command:{owner_id}:name"
    if role == COMMAND_TITLE_ROLE:
        return f"command:{owner_id}:title"
    if role == CONTROL_NAME_ROLE:
        return f"control:{owner_id}:name"
    raise ValueError(f"Unsupported writable string role: {role!r}")


def parse_item_path(item_id: str, *, prefix: str) -> tuple[int, ...]:
    expected_prefix = f"{prefix}-"
    if item_id == f"{prefix}-root":
        return ()
    if not item_id.startswith(expected_prefix):
        raise ValueError(f"Unexpected {prefix} item id: {item_id!r}")
    suffix = item_id[len(expected_prefix) :]
    return tuple(int(part) for part in suffix.split("-"))


def build_form_meta_slice(path: Path, node: AstNode, *, container_summary: dict) -> dict:
    form_title = extract_form_title(node)
    return {
        "schema": FORM_META_SCHEMA,
        "version": FORM_META_VERSION,
        "form_name": derive_form_name(path),
        "form_title": form_title,
        "form_kind": "ordinary",
        "root_item_id": FORM_ROOT_ID,
        "flags": {
            "has_explicit_title": bool(form_title),
            "has_module_record": container_summary.get("module_record") is not None,
        },
    }


def build_strings_slice(
    node: AstNode,
    *,
    root_item_id: str,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    form_events: list[dict],
    commands: list[dict],
    control_name_paths: dict[tuple[int, ...], str],
) -> dict:
    role_overrides: dict[tuple[int, ...], tuple[str, str, str]] = {}
    if form_title_ref is not None:
        _, title_path = form_title_ref
        role_overrides[title_path] = (FORM_OWNER_KIND, root_item_id, FORM_TITLE_ROLE)
    for event in form_events:
        role_overrides[event["handler_path"]] = (EVENT_OWNER_KIND, event["id"], EVENT_HANDLER_ROLE)
    for command in commands:
        role_overrides[command["name_path"]] = (COMMAND_OWNER_KIND, command["id"], COMMAND_NAME_ROLE)
        for title_path in command["title_paths"]:
            role_overrides[title_path] = (COMMAND_OWNER_KIND, command["id"], COMMAND_TITLE_ROLE)
    for name_path, control_id in control_name_paths.items():
        role_overrides[name_path] = (CONTROL_OWNER_KIND, control_id, CONTROL_NAME_ROLE)

    items: list[dict] = []
    collect_string_items(
        node,
        path=(),
        root_item_id=root_item_id,
        role_overrides=role_overrides,
        items=items,
    )
    return {
        "schema": STRINGS_SCHEMA,
        "version": STRINGS_VERSION,
        "items": items,
    }


def build_events_slice(items: list[dict]) -> dict:
    return {
        "schema": EVENTS_SCHEMA,
        "version": EVENTS_VERSION,
        "items": [public_event_item(item) for item in items],
    }


def build_commands_slice(items: list[dict]) -> dict:
    return {
        "schema": COMMANDS_SCHEMA,
        "version": COMMANDS_VERSION,
        "items": [public_command_item(item) for item in items],
    }


def derive_form_name(path: Path) -> str:
    if path.is_dir():
        manifest = read_manifest(path)
        if manifest.source_file:
            return normalize_form_name(manifest.source_file)
        return normalize_form_name(path.name)
    return normalize_form_name(path.name)


def normalize_form_name(value: str) -> str:
    name = Path(value).name
    suffix = ".form.bin"
    if name.lower().endswith(suffix):
        return name[: -len(suffix)]
    stem = Path(name).stem
    return stem or name


def extract_form_title(node: AstNode) -> str:
    title_ref = extract_form_title_ref(node)
    if title_ref is None:
        return ""
    title, _ = title_ref
    return title


def extract_form_title_ref(node: AstNode) -> tuple[str, tuple[int, ...]] | None:
    if node.kind != "list":
        return None
    top_level_items = node.items or []
    if len(top_level_items) < 2:
        return None
    header_section = top_level_items[1]
    if header_section.kind != "list":
        return None
    header_items = header_section.items or []
    if len(header_items) < 2:
        return None
    return find_localized_title_ref(header_items[1], depth=0, path=(1, 1))


def collect_form_event_details(node: AstNode, *, root_item_id: str) -> list[dict]:
    if node.kind != "list":
        return []
    top_level_items = node.items or []
    if len(top_level_items) <= TOP_LEVEL_FORM_EVENTS_INDEX:
        return []
    form_events_section = top_level_items[TOP_LEVEL_FORM_EVENTS_INDEX]
    items: list[dict] = []
    walk_event_details(
        form_events_section,
        path=(TOP_LEVEL_FORM_EVENTS_INDEX,),
        owner_id=root_item_id,
        scope=FORM_SCOPE,
        items=items,
    )
    return items


def walk_event_details(
    node: AstNode,
    *,
    path: tuple[int, ...],
    owner_id: str,
    scope: str,
    items: list[dict],
) -> None:
    if node.kind != "list":
        return

    event_item = build_event_detail(node, path=path, owner_id=owner_id, scope=scope)
    if event_item is not None:
        items.append(event_item)

    for index, child in enumerate(node.items or []):
        walk_event_details(
            child,
            path=(*path, index),
            owner_id=owner_id,
            scope=scope,
            items=items,
        )


def build_event_detail(
    node: AstNode,
    *,
    path: tuple[int, ...],
    owner_id: str,
    scope: str,
) -> dict | None:
    if node.kind != "list":
        return None
    items = node.items or []
    if len(items) < 3:
        return None
    if items[0].kind != "atom" or items[0].text != "3":
        return None
    if items[1].kind != "string" or items[2].kind != "list":
        return None
    if command_section_prefix(path) is not None:
        return None

    handler = decode_string_token(items[1].text or "")
    if not handler:
        return None

    title = extract_named_record_title(items[2]) or handler
    return {
        "id": build_event_item_id(path),
        "name": title,
        "handler": handler,
        "scope": scope,
        "owner_id": owner_id,
        "handler_path": (*path, 1),
    }


def public_event_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "name": item["name"],
        "handler": item["handler"],
        "scope": item["scope"],
        "owner_id": item["owner_id"],
    }


def collect_command_details(node: AstNode, *, root_item_id: str) -> list[dict]:
    action_titles_by_section: dict[tuple[int, ...], dict[str, tuple[int, ...]]] = {}
    root_candidates: list[dict] = []
    walk_command_candidates(
        node,
        path=(),
        action_titles_by_section=action_titles_by_section,
        root_candidates=root_candidates,
    )

    items: list[dict] = []
    for candidate in root_candidates:
        path = candidate["path"]
        section_prefix = command_section_prefix(path)
        if section_prefix is None:
            continue
        action_title_paths = action_titles_by_section.get(section_prefix, {})
        if candidate["title"] not in action_title_paths:
            continue
        title_paths = [candidate["title_path"], action_title_paths[candidate["title"]]]
        deduped_title_paths: list[tuple[int, ...]] = []
        for title_path in title_paths:
            if title_path not in deduped_title_paths:
                deduped_title_paths.append(title_path)
        items.append(
            {
                "id": build_command_item_id(path),
                "name": candidate["name"],
                "title": candidate["title"],
                "owner_id": root_item_id,
                "source": COMMAND_SOURCE_AST_ROOT_TITLE_MATCH,
                "path": path,
                "name_path": (*path, 1),
                "title_paths": deduped_title_paths,
            }
        )
    return items


def walk_command_candidates(
    node: AstNode,
    *,
    path: tuple[int, ...],
    action_titles_by_section: dict[tuple[int, ...], dict[str, tuple[int, ...]]],
    root_candidates: list[dict],
) -> None:
    if node.kind != "list":
        return

    root_candidate = build_root_command_candidate(node, path=path)
    if root_candidate is not None:
        root_candidates.append(root_candidate)

    action_candidate = build_action_command_candidate(node, path=path)
    if action_candidate is not None:
        section_prefix, title, title_path = action_candidate
        action_titles_by_section.setdefault(section_prefix, {}).setdefault(title, title_path)

    for index, child in enumerate(node.items or []):
        walk_command_candidates(
            child,
            path=(*path, index),
            action_titles_by_section=action_titles_by_section,
            root_candidates=root_candidates,
        )


def build_root_command_candidate(node: AstNode, *, path: tuple[int, ...]) -> dict | None:
    items = node.items or []
    if len(items) < 3:
        return None
    if items[0].kind != "atom" or items[0].text != "3":
        return None
    if items[1].kind != "string" or items[2].kind != "list":
        return None
    if command_section_prefix(path) is None:
        return None

    name = decode_string_token(items[1].text or "")
    if not name:
        return None
    title_ref = extract_named_record_title_ref(items[2])
    if title_ref is None:
        return None
    title, title_path = title_ref
    return {
        "path": path,
        "name": name,
        "title": title,
        "title_path": (*path, 2, *title_path),
    }


def build_action_command_candidate(
    node: AstNode,
    *,
    path: tuple[int, ...],
) -> tuple[tuple[int, ...], str, tuple[int, ...]] | None:
    items = node.items or []
    if len(items) < 5:
        return None
    if items[0].kind != "atom" or items[0].text != "8":
        return None
    if items[1].kind != "string" or items[4].kind != "list":
        return None

    section_prefix = command_section_prefix(path)
    if section_prefix is None:
        return None

    title_ref = find_localized_title_ref(items[4], depth=0, path=(4,))
    if title_ref is None:
        return None
    title, title_path = title_ref
    return section_prefix, title, (*path, *title_path)


def command_section_prefix(path: tuple[int, ...]) -> tuple[int, ...] | None:
    if 7 not in path:
        return None
    return path[: path.index(7) + 1]


def build_command_item_id(path: tuple[int, ...]) -> str:
    return "command-" + "-".join(str(part) for part in path)


def build_event_item_id(path: tuple[int, ...]) -> str:
    return "event-" + "-".join(str(part) for part in path)


def build_control_item_id(path: tuple[int, ...]) -> str:
    return "control-" + "-".join(str(part) for part in path)


def build_attribute_item_id(path: tuple[int, ...]) -> str:
    return "attribute-" + "-".join(str(part) for part in path)


def public_command_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "name": item["name"],
        "title": item["title"],
        "owner_id": item["owner_id"],
        "source": item["source"],
    }


def collect_control_bundle(path: Path, node: AstNode, *, form_meta: dict, command_details: list[dict]) -> dict:
    control_details: list[dict] = []
    layout_items: list[dict] = []
    attribute_items: list[dict] = []
    control_name_paths: dict[tuple[int, ...], str] = {}
    top_level_child_ids: list[str] = []

    control_section = get_node_by_path(node, CONTROL_SECTION_PATH)
    if control_section is not None and control_section.kind == "list":
        order = 0
        for index, child in enumerate(control_section.items or []):
            detail = build_control_detail(
                child,
                path=(*CONTROL_SECTION_PATH, index),
                parent_id=FORM_ROOT_ID,
                control_details=control_details,
                layout_items=layout_items,
                attribute_items=attribute_items,
                control_name_paths=control_name_paths,
            )
            if detail is None:
                continue
            top_level_child_ids.append(detail["id"])
            layout_items.append(
                {
                    "control_id": detail["id"],
                    "container_id": FORM_ROOT_ID,
                    "order": order,
                    "group_kind": "form-root-child-list",
                    "visibility": "unknown",
                }
            )
            order += 1

    assign_control_command_links(control_details, command_details)
    layout_items.sort(key=lambda item: item["group_kind"] != "form-root-child-list")

    root_item = {
        "id": FORM_ROOT_ID,
        "kind": "form",
        "name": form_meta["form_name"],
        "title": form_meta["form_title"],
        "parent_id": None,
        "child_ids": top_level_child_ids,
        "command_ids": [],
        "event_bindings": [],
    }
    return {
        "controls_tree": {
            "schema": CONTROLS_TREE_SCHEMA,
            "version": CONTROLS_TREE_VERSION,
            "root_id": FORM_ROOT_ID,
            "items": [root_item, *[public_control_item(item) for item in control_details]],
        },
        "layout": {
            "schema": LAYOUT_SCHEMA,
            "version": LAYOUT_VERSION,
            "items": layout_items,
        },
        "attributes": {
            "schema": ATTRIBUTES_SCHEMA,
            "version": ATTRIBUTES_VERSION,
            "items": attribute_items,
        },
        "control_name_paths": control_name_paths,
    }


def build_control_detail(
    node: AstNode,
    *,
    path: tuple[int, ...],
    parent_id: str,
    control_details: list[dict],
    layout_items: list[dict],
    attribute_items: list[dict],
    control_name_paths: dict[tuple[int, ...], str],
) -> dict | None:
    name_ref = extract_control_name_ref(node)
    if name_ref is None:
        return None
    name, name_path = name_ref
    control_id = build_control_item_id(path)
    detail = {
        "id": control_id,
        "kind": CONTROL_KIND,
        "name": name,
        "title": name,
        "parent_id": parent_id,
        "child_ids": [],
        "command_ids": [],
        "event_bindings": collect_control_event_bindings(node, path=path),
        "path": path,
    }
    control_details.append(detail)
    control_name_paths[(*path, *name_path)] = control_id

    pattern_marker = extract_control_pattern_marker(node)
    if pattern_marker:
        attribute_items.append(
            {
                "id": build_attribute_item_id(path),
                "name": name,
                "owner_id": control_id,
                "data_path": name,
                "type_hint": f"pattern:{pattern_marker}",
                "role": CONTROL_PATTERN_ROLE,
            }
        )

    children_container = extract_control_children_container(node)
    if children_container is None:
        return detail

    order = 0
    for index, child in enumerate(children_container.items or []):
        child_detail = build_control_detail(
            child,
            path=(*path, CONTROL_CHILDREN_INDEX, index),
            parent_id=control_id,
            control_details=control_details,
            layout_items=layout_items,
            attribute_items=attribute_items,
            control_name_paths=control_name_paths,
        )
        if child_detail is None:
            continue
        detail["child_ids"].append(child_detail["id"])
        layout_items.append(
            {
                "control_id": child_detail["id"],
                "container_id": control_id,
                "order": order,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            }
        )
        order += 1
    return detail


def public_control_item(item: dict) -> dict:
    return {
        "id": item["id"],
        "kind": item["kind"],
        "name": item["name"],
        "title": item["title"],
        "parent_id": item["parent_id"],
        "child_ids": item["child_ids"],
        "command_ids": item["command_ids"],
        "event_bindings": item["event_bindings"],
    }


def extract_control_name_ref(node: AstNode) -> tuple[str, tuple[int, ...]] | None:
    if node.kind != "list":
        return None
    items = node.items or []
    if len(items) <= CONTROL_NAME_INDEX:
        return None
    name_node = items[CONTROL_NAME_INDEX]
    if name_node.kind != "list":
        return None
    name_items = name_node.items or []
    if len(name_items) < 2 or name_items[1].kind != "string":
        return None
    name = decode_string_token(name_items[1].text or "")
    if not name:
        return None
    return name, (CONTROL_NAME_INDEX, 1)


def extract_control_children_container(node: AstNode) -> AstNode | None:
    if node.kind != "list":
        return None
    items = node.items or []
    if len(items) <= CONTROL_CHILDREN_INDEX:
        return None
    container = items[CONTROL_CHILDREN_INDEX]
    if container.kind != "list":
        return None
    return container


def extract_control_pattern_marker(node: AstNode) -> str | None:
    if node.kind != "list":
        return None
    items = node.items or []
    if len(items) <= CONTROL_DATA_INDEX:
        return None
    data_node = items[CONTROL_DATA_INDEX]
    if data_node.kind != "list":
        return None
    for item in data_node.items or []:
        if item.kind != "list":
            continue
        entry_items = item.items or []
        if len(entry_items) < 2:
            continue
        if entry_items[0].kind != "string" or decode_string_token(entry_items[0].text or "") != "Pattern":
            continue
        marker_node = entry_items[1]
        if marker_node.kind != "list":
            continue
        marker_items = marker_node.items or []
        if not marker_items or marker_items[0].kind != "string":
            continue
        marker = decode_string_token(marker_items[0].text or "")
        if marker:
            return marker
    return None


def collect_control_event_bindings(node: AstNode, *, path: tuple[int, ...]) -> list[dict]:
    if node.kind != "list":
        return []
    items = node.items or []
    if len(items) <= CONTROL_DATA_INDEX or items[CONTROL_DATA_INDEX].kind != "list":
        return []
    details: list[dict] = []
    walk_event_details(
        items[CONTROL_DATA_INDEX],
        path=(*path, CONTROL_DATA_INDEX),
        owner_id=build_control_item_id(path),
        scope=CONTROL_SCOPE,
        items=details,
    )
    return [public_event_item(item) for item in details]


def assign_control_command_links(control_details: list[dict], command_details: list[dict]) -> None:
    if not control_details:
        return
    path_candidates = [(item["path"], item) for item in control_details]
    for command in command_details:
        best_match = None
        for control_path, control_item in path_candidates:
            if command["path"][: len(control_path)] != control_path:
                continue
            if best_match is None or len(control_path) > len(best_match["path"]):
                best_match = {"path": control_path, "item": control_item}
        if best_match is None:
            continue
        best_match["item"]["command_ids"].append(command["id"])


def extract_named_record_title(node: AstNode) -> str | None:
    title_ref = extract_named_record_title_ref(node)
    if title_ref is None:
        return None
    return title_ref[0]


def extract_named_record_title_ref(node: AstNode) -> tuple[str, tuple[int, ...]] | None:
    if node.kind != "list":
        return None
    items = node.items or []
    for index in (2, 3, 4):
        if index >= len(items):
            continue
        title_ref = find_localized_title_ref(items[index], depth=0, path=(index,))
        if title_ref is not None:
            return title_ref
    return None


def extract_localized_title(node: AstNode) -> str | None:
    title_ref = find_localized_title_ref(node, depth=0, path=())
    if title_ref is None:
        return None
    return title_ref[0]


def find_localized_title_ref(
    node: AstNode,
    *,
    depth: int,
    path: tuple[int, ...],
) -> tuple[str, tuple[int, ...]] | None:
    if node.kind == "list":
        items = node.items or []
        if len(items) >= 3 and items[2].kind == "list":
            localized_items = items[2].items or []
            strings = [
                (index, decode_string_token(item.text or ""))
                for index, item in enumerate(localized_items)
                if item.kind == "string"
            ]
            if len(strings) >= 2 and is_locale_code(strings[0][1]) and strings[1][1]:
                return strings[1][1], (*path, 2, strings[1][0])
        if depth >= LOCALIZED_TITLE_MAX_DEPTH:
            return None
        for index, item in enumerate(items):
            title = find_localized_title_ref(item, depth=depth + 1, path=(*path, index))
            if title:
                return title
    return None


def is_locale_code(value: str) -> bool:
    return 1 < len(value) <= 5 and value.replace("-", "").isalpha()


def collect_string_items(
    node: AstNode,
    *,
    path: tuple[int, ...],
    root_item_id: str,
    role_overrides: dict[tuple[int, ...], tuple[str, str, str]],
    items: list[dict],
) -> None:
    if node.kind == "string":
        owner_kind = FORM_OWNER_KIND
        owner_id = root_item_id
        role = AST_STRING_ROLE
        override = role_overrides.get(path)
        if override is not None:
            owner_kind, owner_id, role = override
        items.append(
            {
                "id": build_string_item_id(path),
                "value": decode_string_token(node.text or ""),
                "owner_kind": owner_kind,
                "owner_id": owner_id,
                "role": role,
            }
        )
        return

    if node.kind != "list":
        return

    for index, item in enumerate(node.items or []):
        collect_string_items(
            item,
            path=(*path, index),
            root_item_id=root_item_id,
            role_overrides=role_overrides,
            items=items,
        )


def build_string_item_id(path: tuple[int, ...]) -> str:
    if not path:
        return "string-root"
    return "string-" + "-".join(str(part) for part in path)


def get_node_by_path(node: AstNode, path: tuple[int, ...]) -> AstNode | None:
    current = node
    for index in path:
        if current.kind != "list":
            return None
        items = current.items or []
        if index >= len(items):
            return None
        current = items[index]
    return current


def load_workspace_semantic_state(directory: Path) -> dict:
    desired: dict[str, dict] = {}
    for name in SEMANTIC_SLICE_NAMES:
        path = semantic_slice_path(directory, name)
        if not path.exists():
            raise ContainerError(f"Semantic workspace is missing {path.relative_to(directory)}.")
        try:
            payload = json.loads(read_text_exact(path))
        except json.JSONDecodeError as exc:
            raise ContainerError(f"Invalid semantic JSON at {path}.") from exc
        if not isinstance(payload, dict):
            raise ContainerError(f"Semantic JSON at {path} must be a top-level object.")
        desired[name] = payload
    return desired


def apply_semantic_workspace(directory: Path) -> None:
    manifest = read_manifest(directory)
    form_record = next_record(manifest.records, RecordKind.FORM)
    if form_record is None:
        raise ContainerError("Unpack directory does not contain a form record.")
    if form_record.pointer_record_index is not None:
        raise ContainerError("Semantic edits are not supported for split-form workspaces yet.")

    plan = collect_semantic_edit_plan(directory)
    apply_semantic_edit_plan(directory, plan)

    from .api import export_workspace_semantic_json

    export_workspace_semantic_json(directory, directory)


def collect_semantic_edit_plan(directory: Path) -> dict:
    model = build_semantic_model(directory)
    baseline = model["semantic"]
    desired = load_workspace_semantic_state(directory)
    node = parse_form_source(directory)
    form_meta = baseline["form.meta.json"]
    root_item_id = form_meta["root_item_id"]
    form_title_ref = extract_form_title_ref(node)
    event_details = collect_form_event_details(node, root_item_id=root_item_id)
    command_details = collect_command_details(node, root_item_id=root_item_id)
    controls = collect_control_bundle(
        directory,
        node,
        form_meta=form_meta,
        command_details=command_details,
    )

    plan = {
        "path_updates": {},
        "targets": {},
    }

    collect_form_meta_edits(
        baseline["form.meta.json"],
        desired["form.meta.json"],
        form_title_ref=form_title_ref,
        plan=plan,
    )
    collect_event_edits(
        baseline["events.json"],
        desired["events.json"],
        event_details=event_details,
        plan=plan,
    )
    collect_command_edits(
        baseline["commands.json"],
        desired["commands.json"],
        command_details=command_details,
        plan=plan,
    )
    collect_controls_tree_edits(
        baseline["controls.tree.json"],
        desired["controls.tree.json"],
        control_name_paths=controls["control_name_paths"],
        plan=plan,
    )
    collect_attribute_edits(
        baseline["attributes.json"],
        desired["attributes.json"],
        control_name_paths=controls["control_name_paths"],
        plan=plan,
    )
    collect_strings_edits(
        baseline["strings.json"],
        desired["strings.json"],
        form_title_ref=form_title_ref,
        event_details=event_details,
        command_details=command_details,
        control_name_paths=controls["control_name_paths"],
        plan=plan,
    )

    for name in ("layout.json",):
        if desired[name] != baseline[name]:
            raise ContainerError(f"Semantic edits are not supported for semantic/{name}.")

    return plan


def collect_form_meta_edits(
    baseline: dict,
    desired: dict,
    *,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    plan: dict,
) -> None:
    for key, value in desired.items():
        if key == "form_title":
            continue
        if baseline.get(key) != value:
            raise ContainerError("Semantic edits currently support only form.meta.json.form_title.")
    if desired["form_title"] == baseline["form_title"]:
        return
    if form_title_ref is None:
        raise ContainerError("Semantic form-title edits require an explicit title string in the current AST bridge.")
    register_semantic_edit(
        plan,
        target_key="form_title",
        value=desired["form_title"],
        paths=[form_title_ref[1]],
    )


def collect_event_edits(baseline: dict, desired: dict, *, event_details: list[dict], plan: dict) -> None:
    baseline_items = baseline["items"]
    desired_items = desired["items"]
    if len(baseline_items) != len(desired_items):
        raise ContainerError("Semantic edits do not support adding or removing events.")
    detail_by_id = {item["id"]: item for item in event_details}
    for baseline_item, desired_item in zip(baseline_items, desired_items, strict=True):
        if baseline_item["id"] != desired_item.get("id"):
            raise ContainerError("Semantic edits require stable event item ordering and ids.")
        for key in ("id", "name", "scope", "owner_id"):
            if baseline_item[key] != desired_item.get(key):
                raise ContainerError("Semantic edits currently support only events.json[].handler.")
        if baseline_item["handler"] == desired_item["handler"]:
            continue
        detail = detail_by_id.get(baseline_item["id"])
        if detail is None:
            raise ContainerError(f"Cannot map semantic event {baseline_item['id']} back to the AST bridge.")
        register_semantic_edit(
            plan,
            target_key=f"event:{baseline_item['id']}:handler",
            value=desired_item["handler"],
            paths=[detail["handler_path"]],
        )


def collect_command_edits(baseline: dict, desired: dict, *, command_details: list[dict], plan: dict) -> None:
    baseline_items = baseline["items"]
    desired_items = desired["items"]
    if len(baseline_items) != len(desired_items):
        raise ContainerError("Semantic edits do not support adding or removing commands.")
    detail_by_id = {item["id"]: item for item in command_details}
    for baseline_item, desired_item in zip(baseline_items, desired_items, strict=True):
        if baseline_item["id"] != desired_item.get("id"):
            raise ContainerError("Semantic edits require stable command item ordering and ids.")
        for key in ("id", "owner_id", "source"):
            if baseline_item[key] != desired_item.get(key):
                raise ContainerError("Semantic edits currently support only commands.json[].name/title.")
        if baseline_item["name"] == desired_item["name"] and baseline_item["title"] == desired_item["title"]:
            continue
        detail = detail_by_id.get(baseline_item["id"])
        if detail is None:
            raise ContainerError(f"Cannot map semantic command {baseline_item['id']} back to the AST bridge.")
        if baseline_item["name"] != desired_item["name"]:
            register_semantic_edit(
                plan,
                target_key=f"command:{baseline_item['id']}:name",
                value=desired_item["name"],
                paths=[detail["name_path"]],
            )
        if baseline_item["title"] != desired_item["title"]:
            register_semantic_edit(
                plan,
                target_key=f"command:{baseline_item['id']}:title",
                value=desired_item["title"],
                paths=detail["title_paths"],
            )


def collect_controls_tree_edits(
    baseline: dict,
    desired: dict,
    *,
    control_name_paths: dict[tuple[int, ...], str],
    plan: dict,
) -> None:
    baseline_items = baseline["items"]
    desired_items = desired["items"]
    if len(baseline_items) != len(desired_items):
        raise ContainerError("Semantic edits do not support adding or removing controls.")

    control_paths = {
        control_id: [path]
        for path, control_id in control_name_paths.items()
    }

    for baseline_item, desired_item in zip(baseline_items, desired_items, strict=True):
        if baseline_item["id"] != desired_item.get("id"):
            raise ContainerError("Semantic edits require stable control item ordering and ids.")
        for key in ("id", "kind", "parent_id", "child_ids", "command_ids", "event_bindings"):
            if baseline_item[key] != desired_item.get(key):
                raise ContainerError("Semantic edits currently support only controls.tree.json[].name/title.")
        if baseline_item["name"] == desired_item["name"] and baseline_item["title"] == desired_item["title"]:
            continue
        if baseline_item["id"] == FORM_ROOT_ID:
            raise ContainerError("Semantic edits currently support only explicit control labels in controls.tree.json.")
        if desired_item["name"] != desired_item["title"]:
            raise ContainerError("Semantic edits require controls.tree.json[].name and title to stay in sync.")
        paths = control_paths.get(baseline_item["id"])
        if not paths:
            raise ContainerError(f"Cannot map semantic control {baseline_item['id']} back to the AST bridge.")
        register_semantic_edit(
            plan,
            target_key=f"control:{baseline_item['id']}:name",
            value=desired_item["name"],
            paths=paths,
        )


def collect_attribute_edits(
    baseline: dict,
    desired: dict,
    *,
    control_name_paths: dict[tuple[int, ...], str],
    plan: dict,
) -> None:
    baseline_items = baseline["items"]
    desired_items = desired["items"]
    if len(baseline_items) != len(desired_items):
        raise ContainerError("Semantic edits do not support adding or removing attributes.")

    attribute_paths = {
        f"attribute-{control_id.removeprefix('control-')}": [path]
        for path, control_id in control_name_paths.items()
    }

    for baseline_item, desired_item in zip(baseline_items, desired_items, strict=True):
        if baseline_item["id"] != desired_item.get("id"):
            raise ContainerError("Semantic edits require stable attribute item ordering and ids.")
        for key in ("id", "owner_id", "type_hint", "role"):
            if baseline_item[key] != desired_item.get(key):
                raise ContainerError("Semantic edits currently support only attributes.json[].name/data_path.")
        if baseline_item["name"] == desired_item["name"] and baseline_item["data_path"] == desired_item["data_path"]:
            continue
        if desired_item["name"] != desired_item["data_path"]:
            raise ContainerError("Semantic edits require attributes.json[].name and data_path to stay in sync.")
        paths = attribute_paths.get(baseline_item["id"])
        if not paths:
            raise ContainerError(f"Cannot map semantic attribute {baseline_item['id']} back to the AST bridge.")
        register_semantic_edit(
            plan,
            target_key=f"attribute:{baseline_item['id']}:name",
            value=desired_item["name"],
            paths=paths,
        )


def collect_strings_edits(
    baseline: dict,
    desired: dict,
    *,
    form_title_ref: tuple[str, tuple[int, ...]] | None,
    event_details: list[dict],
    command_details: list[dict],
    control_name_paths: dict[tuple[int, ...], str],
    plan: dict,
) -> None:
    baseline_items = baseline["items"]
    desired_items = desired["items"]
    if len(baseline_items) != len(desired_items):
        raise ContainerError("Semantic edits do not support adding or removing string items.")

    event_paths = {item["id"]: [item["handler_path"]] for item in event_details}
    command_name_paths = {item["id"]: [item["name_path"]] for item in command_details}
    command_title_paths = {item["id"]: item["title_paths"] for item in command_details}
    control_paths = {
        control_id: [path]
        for path, control_id in control_name_paths.items()
    }
    form_title_paths = [] if form_title_ref is None else [form_title_ref[1]]

    for baseline_item, desired_item in zip(baseline_items, desired_items, strict=True):
        for key in ("id", "owner_kind", "owner_id", "role"):
            if baseline_item[key] != desired_item.get(key):
                raise ContainerError("Semantic edits currently support only strings.json[].value on alias roles.")
        if baseline_item["value"] == desired_item["value"]:
            continue

        role = baseline_item["role"]
        owner_id = baseline_item["owner_id"]
        if role == FORM_TITLE_ROLE:
            if owner_id != FORM_ROOT_ID or not form_title_paths:
                raise ContainerError("Cannot map strings form_title alias back to the current AST bridge.")
            register_semantic_edit(
                plan,
                target_key="form_title",
                value=desired_item["value"],
                paths=form_title_paths,
            )
            continue
        if role == EVENT_HANDLER_ROLE:
            paths = event_paths.get(owner_id)
            if not paths:
                raise ContainerError(f"Cannot map strings event alias {owner_id} back to the AST bridge.")
            register_semantic_edit(
                plan,
                target_key=f"event:{owner_id}:handler",
                value=desired_item["value"],
                paths=paths,
            )
            continue
        if role == COMMAND_NAME_ROLE:
            paths = command_name_paths.get(owner_id)
            if not paths:
                raise ContainerError(f"Cannot map strings command alias {owner_id} back to the current AST bridge.")
            register_semantic_edit(
                plan,
                target_key=f"command:{owner_id}:name",
                value=desired_item["value"],
                paths=paths,
            )
            continue
        if role == COMMAND_TITLE_ROLE:
            paths = command_title_paths.get(owner_id)
            if not paths:
                raise ContainerError(f"Cannot map strings command alias {owner_id} back to the AST bridge.")
            register_semantic_edit(
                plan,
                target_key=f"command:{owner_id}:title",
                value=desired_item["value"],
                paths=paths,
            )
            continue
        if role == CONTROL_NAME_ROLE:
            paths = control_paths.get(owner_id)
            if not paths:
                raise ContainerError(f"Cannot map strings control alias {owner_id} back to the AST bridge.")
            register_semantic_edit(
                plan,
                target_key=f"control:{owner_id}:name",
                value=desired_item["value"],
                paths=paths,
            )
            continue
        raise ContainerError(f"Semantic edits are not supported for strings.json role {role!r}.")


def register_semantic_edit(plan: dict, *, target_key: str, value: str, paths: list[tuple[int, ...]]) -> None:
    existing_value = plan["targets"].get(target_key)
    if existing_value is not None and existing_value != value:
        raise ContainerError(f"Conflicting semantic edits target {target_key}.")
    plan["targets"][target_key] = value
    for path in paths:
        existing_path_value = plan["path_updates"].get(path)
        if existing_path_value is not None and existing_path_value != value:
            raise ContainerError(f"Conflicting semantic edits for AST string path {path}.")
        plan["path_updates"][path] = value


def apply_semantic_edit_plan(directory: Path, plan: dict) -> None:
    if not plan["path_updates"]:
        return

    node = parse_form_source(directory)
    for path, value in plan["path_updates"].items():
        apply_string_value_at_path(node, path, value)

    manifest = read_manifest(directory)
    form_record = next_record(manifest.records, RecordKind.FORM)
    if form_record is None:
        raise ContainerError("Unpack directory does not contain a form record.")
    write_text_exact(directory / form_record.relative_path, serialize_form_text(node))


def apply_string_value_at_path(node: AstNode, path: tuple[int, ...], value: str) -> None:
    target = get_node_by_path(node, path)
    if target is None or target.kind != "string":
        raise ContainerError(f"AST string path {path} is unavailable for semantic editing.")
    target.text = encode_string_token(value)


def encode_string_token(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def next_record(records: list[Record | ManifestRecord], kind: RecordKind) -> Record | ManifestRecord | None:
    return next((record for record in records if record.kind is kind), None)


def summarize_descriptor_record(path: Path, record: Record | ManifestRecord) -> dict:
    return {
        "index": record.index,
        "label": record.label,
        "kind": record.kind.value,
        "size_policy": record.size_policy.value,
        "relative_path": record.relative_path,
        "descriptor_json": parse_descriptor_body(load_descriptor_body(path, record), label=record.label),
    }


def summarize_form_record(record: Record | ManifestRecord | None) -> dict | None:
    if record is None:
        return None
    continuation_record_index = record.pointer_record_index
    return {
        "index": record.index,
        "label": record.label,
        "kind": record.kind.value,
        "size_policy": record.size_policy.value,
        "field1": record.field1,
        "field2": record.field2,
        "pointer_record_index": continuation_record_index,
        "split_form": continuation_record_index is not None,
        "relative_path": record.relative_path,
    }


def summarize_module_record(path: Path, record: Record | ManifestRecord | None) -> dict | None:
    if record is None:
        return None
    text = load_module_text(path, record)
    return {
        "index": record.index,
        "label": record.label,
        "kind": record.kind.value,
        "size_policy": record.size_policy.value,
        "field1": record.field1,
        "field2": record.field2,
        "relative_path": record.relative_path,
        "line_count": len(text.splitlines()),
        "char_count": len(text),
    }


def load_descriptor_body(path: Path, record: Record | ManifestRecord) -> bytes:
    if path.is_dir():
        return (path / record.relative_path).read_bytes()
    if isinstance(record, Record):
        return record.body
    raise TypeError(f"Unsupported record type for descriptor body: {type(record)!r}")


def load_module_text(path: Path, record: Record | ManifestRecord) -> str:
    if path.is_dir():
        return read_text_exact(path / record.relative_path)
    if isinstance(record, Record):
        return decode_text_body(record.body)
    raise TypeError(f"Unsupported record type for module text: {type(record)!r}")


def summarize_ast(node: AstNode) -> dict:
    counts = {
        "list": 0,
        "atom": 0,
        "string": 0,
        "literal": 0,
    }
    stats = {
        "max_depth": 0,
        "max_list_width": 0,
    }
    atom_samples: list[str] = []
    string_samples: list[str] = []
    seen_atoms: set[str] = set()
    seen_strings: set[str] = set()

    walk_ast(
        node,
        depth=0,
        counts=counts,
        stats=stats,
        atom_samples=atom_samples,
        string_samples=string_samples,
        seen_atoms=seen_atoms,
        seen_strings=seen_strings,
    )

    top_level_items = []
    if node.kind == "list":
        for index, item in enumerate(node.items or []):
            top_level_items.append(summarize_top_level_item(index, item))

    return {
        "root_kind": node.kind,
        "top_level_item_count": len(node.items or []) if node.kind == "list" else 0,
        "node_counts": counts,
        "max_depth": stats["max_depth"],
        "max_list_width": stats["max_list_width"],
        "atom_samples": atom_samples,
        "string_samples": string_samples,
        "top_level_items": top_level_items,
    }


def walk_ast(
    node: AstNode,
    *,
    depth: int,
    counts: dict[str, int],
    stats: dict[str, int],
    atom_samples: list[str],
    string_samples: list[str],
    seen_atoms: set[str],
    seen_strings: set[str],
) -> None:
    counts[node.kind] += 1
    stats["max_depth"] = max(stats["max_depth"], depth)

    if node.kind == "list":
        stats["max_list_width"] = max(stats["max_list_width"], len(node.items or []))
        for item in node.items or []:
            walk_ast(
                item,
                depth=depth + 1,
                counts=counts,
                stats=stats,
                atom_samples=atom_samples,
                string_samples=string_samples,
                seen_atoms=seen_atoms,
                seen_strings=seen_strings,
            )
        return

    if node.kind == "atom":
        token = node.text or ""
        if token and token not in seen_atoms and len(atom_samples) < SAMPLE_LIMIT:
            atom_samples.append(token)
            seen_atoms.add(token)
        return

    if node.kind == "string":
        value = decode_string_token(node.text or "")
        if value and value not in seen_strings and len(string_samples) < SAMPLE_LIMIT:
            string_samples.append(value)
            seen_strings.add(value)


def summarize_top_level_item(index: int, node: AstNode) -> dict:
    if node.kind == "list":
        return {
            "index": index,
            "kind": "list",
            "item_count": len(node.items or []),
            "child_kind_sample": [item.kind for item in (node.items or [])[:5]],
        }

    if node.kind == "string":
        value = decode_string_token(node.text or "")
        return {
            "index": index,
            "kind": "string",
            "value_preview": preview_text(value),
            "value_length": len(value),
        }

    if node.kind == "literal":
        text = node.text or ""
        return {
            "index": index,
            "kind": "literal",
            "text_preview": preview_text(text),
            "text_length": len(text),
        }

    text = node.text or ""
    return {
        "index": index,
        "kind": "atom",
        "text_preview": preview_text(text),
        "text_length": len(text),
    }


def decode_string_token(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1].replace('""', '"')
    return token


def preview_text(text: str) -> str:
    if len(text) <= PREVIEW_LIMIT:
        return text
    return text[:PREVIEW_LIMIT] + "..."
