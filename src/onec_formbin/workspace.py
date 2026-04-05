from __future__ import annotations

from pathlib import Path

from .container import encode_text_body
from .models import Manifest, ManifestRecord, manifest_path


def read_manifest(directory: Path) -> Manifest:
    return Manifest.model_validate_json(manifest_path(directory).read_text(encoding="utf-8"))


def read_record_body(input_dir: Path, record: ManifestRecord) -> bytes:
    path = input_dir / record.relative_path
    if record.codec == "utf-8-sig":
        text = read_text_exact(path)
        return encode_text_body(text)
    return path.read_bytes()


def write_text_exact(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def read_text_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()

