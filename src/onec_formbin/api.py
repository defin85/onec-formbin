from __future__ import annotations

from pathlib import Path

from . import __version__
from .container import ContainerError, decode_text_body, parse_file, render_header, sha256_bytes
from .descriptor_json import parse_descriptor_body
from .models import Manifest, ManifestRecord, PackedRecord, RecordKind, manifest_path
from .workspace import (
    read_manifest,
    write_text_exact,
)
from .workspace import (
    read_record_body as read_record_body_exact,
)


def inspect_file(path: Path) -> dict:
    container = parse_file(path)
    return {
        "path": str(path),
        "prefix_sha256": sha256_bytes(container.prefix),
        "record_count": len(container.records),
        "records": [
            inspect_record(record)
            for record in container.records
        ],
    }


def inspect_record(record) -> dict:
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
    }
    if record.kind is RecordKind.DESCRIPTOR:
        info["descriptor_json"] = parse_descriptor_body(record.body, label=record.label)
    return info


def unpack_file(source: Path, output_dir: Path) -> Manifest:
    container = parse_file(source)
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

    manifest = Manifest(
        tool_version=__version__,
        source_file=str(source),
        prefix_sha256=sha256_bytes(container.prefix),
        record_count=len(manifest_records),
        records=manifest_records,
    )
    write_text_exact(manifest_path(output_dir), manifest.model_dump_json(indent=2) + "\n")
    return manifest


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
