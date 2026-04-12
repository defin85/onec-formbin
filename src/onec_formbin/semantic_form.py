from __future__ import annotations

import json
from pathlib import Path

from .container import decode_text_body, parse_file
from .descriptor_json import parse_descriptor_body
from .form_ast import AstNode, parse_form_source
from .models import ManifestRecord, Record, RecordKind
from .workspace import read_manifest, read_text_exact, write_text_exact

SEMANTIC_VERSION = 1
SAMPLE_LIMIT = 12
PREVIEW_LIMIT = 80


def build_semantic_model(path: Path) -> dict:
    node = parse_form_source(path)
    return {
        "semantic_version": SEMANTIC_VERSION,
        "source": {
            "path": str(path),
            "kind": detect_source_kind(path),
        },
        "container": summarize_container(path),
        "form_model": summarize_ast(node),
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
    if path.is_dir():
        manifest = read_manifest(path)
        records = manifest.records
        return {
            "available": True,
            "record_count": len(records),
            "descriptor_records": [
                summarize_descriptor_record(path, record) for record in records if record.kind is RecordKind.DESCRIPTOR
            ],
            "form_record": summarize_form_record(next_record(records, RecordKind.FORM)),
            "module_record": summarize_module_record(path, next_record(records, RecordKind.MODULE)),
        }

    if path.suffix.lower() == ".bin":
        container = parse_file(path)
        records = container.records
        return {
            "available": True,
            "record_count": len(records),
            "descriptor_records": [
                summarize_descriptor_record(path, record) for record in records if record.kind is RecordKind.DESCRIPTOR
            ],
            "form_record": summarize_form_record(next_record(records, RecordKind.FORM)),
            "module_record": summarize_module_record(path, next_record(records, RecordKind.MODULE)),
        }

    return {"available": False}


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
