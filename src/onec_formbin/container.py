from __future__ import annotations

import hashlib
from pathlib import Path

from .models import (
    FORM_UTF16,
    HEADER_SIZE,
    MODULE_UTF16,
    PREFIX_SIZE,
    SENTINEL,
    UTF8_BOM,
    Container,
    Record,
    RecordKind,
    SizePolicy,
)


class ContainerError(ValueError):
    """Raised when a container cannot be parsed or rebuilt safely."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_container(data: bytes) -> Container:
    if len(data) < PREFIX_SIZE:
        raise ContainerError("File is shorter than the fixed Form.bin prefix.")

    prefix = data[:PREFIX_SIZE]
    records: list[Record] = []
    offset = PREFIX_SIZE
    while offset < len(data):
        field1, field2, field3 = parse_header(data, offset)
        header_end = offset + HEADER_SIZE
        body_start = header_end
        body_end = body_start + field2
        if body_end > len(data):
            raise ContainerError(
                f"Record {len(records)} exceeds file size: body_end={body_end}, size={len(data)}"
            )
        body = data[body_start:body_end]
        kind, label = classify_body(body)
        record = Record(
            index=len(records),
            header_start=offset,
            header_end=header_end,
            body_start=body_start,
            body_end=body_end,
            field1=field1,
            field2=field2,
            field3=field3,
            kind=kind,
            label=label,
            size_policy=SizePolicy.MIRROR if field1 == field2 else SizePolicy.PRESERVE,
            body=body,
        )
        records.append(record)
        offset = body_end

    start_to_index = {record.header_start: record.index for record in records}
    for record in records:
        if record.field3 != SENTINEL and record.field3 in start_to_index:
            record.pointer_record_index = start_to_index[record.field3]

    return Container(prefix=prefix, records=records)


def parse_file(path: Path) -> Container:
    return parse_container(path.read_bytes())


def parse_header(data: bytes, offset: int) -> tuple[int, int, int]:
    chunk = data[offset : offset + HEADER_SIZE]
    if len(chunk) != HEADER_SIZE:
        raise ContainerError(f"Truncated header at offset {offset}.")
    if chunk[:2] != b"\r\n" or chunk[-3:] != b" \r\n":
        raise ContainerError(f"Bad header framing at offset {offset}.")
    if chunk[10:11] != b" " or chunk[19:20] != b" ":
        raise ContainerError(f"Bad header separators at offset {offset}.")
    field1 = parse_hex(chunk[2:10], offset)
    field2 = parse_hex(chunk[11:19], offset)
    field3 = parse_hex(chunk[20:28], offset)
    return field1, field2, field3


def parse_hex(raw: bytes, offset: int) -> int:
    try:
        return int(raw.decode("ascii"), 16)
    except ValueError as exc:
        raise ContainerError(f"Invalid hex field at offset {offset}: {raw!r}") from exc


def render_header(field1: int, field2: int, field3: int) -> bytes:
    return f"\r\n{field1:08x} {field2:08x} {field3:08x} \r\n".encode("ascii")


def classify_body(body: bytes) -> tuple[RecordKind, str]:
    if FORM_UTF16 in body:
        return RecordKind.DESCRIPTOR, "form"
    if MODULE_UTF16 in body:
        return RecordKind.DESCRIPTOR, "module"
    if body.startswith(UTF8_BOM + b"{"):
        return RecordKind.FORM, "form"
    if body.startswith(UTF8_BOM):
        return RecordKind.MODULE, "module"
    return RecordKind.BINARY, "opaque"


def decode_text_body(body: bytes) -> str:
    if not body.startswith(UTF8_BOM):
        raise ContainerError("Expected UTF-8 BOM payload.")
    return body[len(UTF8_BOM) :].decode("utf-8")


def encode_text_body(text: str) -> bytes:
    return UTF8_BOM + text.encode("utf-8")

