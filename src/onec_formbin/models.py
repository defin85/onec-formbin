from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

PREFIX_SIZE = 16
HEADER_SIZE = 31
SENTINEL = 0x7FFFFFFF
UTF8_BOM = b"\xef\xbb\xbf"
FORM_UTF16 = b"f\x00o\x00r\x00m\x00"
MODULE_UTF16 = b"m\x00o\x00d\x00u\x00l\x00e\x00"
SEMANTIC_SLICE_NAMES = (
    "form.meta.json",
    "events.json",
    "commands.json",
    "attributes.json",
    "controls.tree.json",
    "layout.json",
    "strings.json",
)


class RecordKind(StrEnum):
    BINARY = "binary"
    DESCRIPTOR = "descriptor"
    FORM = "form"
    MODULE = "module"
    TEXT = "text"


class SizePolicy(StrEnum):
    MIRROR = "mirror"
    PRESERVE = "preserve"


class FormRenderMode(StrEnum):
    RAW = "raw"
    AST = "ast"
    SEMANTIC = "semantic"


@dataclass(slots=True)
class Record:
    index: int
    header_start: int
    header_end: int
    body_start: int
    body_end: int
    field1: int
    field2: int
    field3: int
    kind: RecordKind
    label: str
    size_policy: SizePolicy
    body: bytes
    pointer_record_index: int | None = None

    @property
    def body_size(self) -> int:
        return len(self.body)

    @property
    def relative_path(self) -> str:
        stem = f"{self.index:03d}-{self.label}"
        if self.kind is RecordKind.DESCRIPTOR:
            return f"records/{stem}.descriptor.bin"
        if self.kind is RecordKind.FORM:
            return f"records/{stem}.raw"
        if self.kind is RecordKind.MODULE:
            return f"records/{stem}.bsl"
        if self.kind is RecordKind.TEXT:
            return f"records/{stem}.txt"
        return f"records/{stem}.bin"

    @property
    def codec(self) -> str:
        if self.kind in {RecordKind.FORM, RecordKind.MODULE, RecordKind.TEXT}:
            return "utf-8-sig"
        return "binary"


class ManifestRecord(BaseModel):
    index: int
    header_start: int
    field1: int
    field2: int
    field3: int
    kind: RecordKind
    label: str
    size_policy: SizePolicy
    pointer_record_index: int | None = None
    codec: str
    relative_path: str
    sha256: str


class Manifest(BaseModel):
    manifest_version: int = Field(default=1)
    tool_version: str
    source_file: str | None = None
    prefix_sha256: str
    record_count: int
    records: list[ManifestRecord]


@dataclass(slots=True)
class Container:
    prefix: bytes
    records: list[Record]

    @property
    def total_size(self) -> int:
        if not self.records:
            return len(self.prefix)
        return self.records[-1].body_end


@dataclass(slots=True)
class PackedRecord:
    record: ManifestRecord
    body: bytes
    field1: int
    field2: int
    field3: int


def manifest_path(directory: Path) -> Path:
    return directory / "manifest.json"


def container_inspect_path(directory: Path) -> Path:
    return directory / "container.inspect.json"


def descriptor_json_path(directory: Path, label: str) -> Path:
    return directory / "descriptors" / f"{label}.descriptor.json"


def semantic_dir_path(directory: Path) -> Path:
    return directory / "semantic"


def semantic_slice_path(directory: Path, name: str) -> Path:
    return semantic_dir_path(directory) / name
