from __future__ import annotations

from pathlib import Path

import pytest

from onec_formbin.api import pack_directory, roundtrip_check, unpack_file
from onec_formbin.container import decode_text_body, parse_file
from onec_formbin.models import RecordKind

FIXTURES = {
    "common-indicator": "common-indicator.Form.bin",
    "common-print-form": "common-print-form.Form.bin",
    "i584-load-form": "i584-load-form.Form.bin",
}


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / FIXTURES[name]


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_roundtrip_is_byte_identical(name: str) -> None:
    assert roundtrip_check(fixture_path(name))


def test_module_edit_is_repacked_for_mirror_record(tmp_path: Path) -> None:
    source = fixture_path("common-print-form")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "repacked.Form.bin"

    unpack_file(source, unpack_dir)
    module_path = unpack_dir / "records" / "003-module.bsl"
    original = module_path.read_text(encoding="utf-8")
    module_path.write_text(original + "\n// added by test\n", encoding="utf-8", newline="")

    pack_directory(unpack_dir, repacked)
    container = parse_file(repacked)
    module_records = [
        record
        for record in container.records
        if record.label == "module" and record.kind is RecordKind.MODULE
    ]
    assert len(module_records) == 1
    assert b"// added by test" in module_records[0].body


def test_form_edit_is_repacked_for_mirror_record(tmp_path: Path) -> None:
    source = fixture_path("common-print-form")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "repacked.Form.bin"

    unpack_file(source, unpack_dir)
    form_path = unpack_dir / "records" / "004-form.raw"
    original = form_path.read_text(encoding="utf-8")
    form_path.write_text(
        original.replace('"Печать"', '"Печать расширенная"', 1),
        encoding="utf-8",
        newline="",
    )

    pack_directory(unpack_dir, repacked)
    container = parse_file(repacked)
    form_records = [
        record
        for record in container.records
        if record.label == "form" and record.kind is RecordKind.FORM
    ]
    assert len(form_records) == 1
    assert "Печать расширенная" in decode_text_body(form_records[0].body)
