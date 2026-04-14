from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from .container import ContainerError
from .container import encode_text_body
from .models import Manifest, ManifestRecord, manifest_path


def read_manifest(directory: Path) -> Manifest:
    if not directory.exists():
        raise ContainerError(f"Unpack directory does not exist: {directory}.")
    if not directory.is_dir():
        raise ContainerError(f"Expected an unpack directory, got file: {directory}.")

    path = manifest_path(directory)
    if not path.exists():
        raise ContainerError(f"Unpack directory is missing {path.name}; run unpack first.")

    try:
        return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        raise ContainerError(f"Invalid manifest JSON at {path}.") from exc


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
