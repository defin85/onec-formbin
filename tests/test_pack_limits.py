from __future__ import annotations

from pathlib import Path

import pytest

from onec_formbin.api import pack_directory, unpack_file
from onec_formbin.container import ContainerError


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def test_non_mirror_record_rejects_size_change(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    form_path = unpack_dir / "records" / "002-form.raw"
    form_path.write_text(form_path.read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="")

    with pytest.raises(ContainerError):
        pack_directory(unpack_dir, tmp_path / "broken.Form.bin")

