from __future__ import annotations

import json
from pathlib import Path

from onec_formbin.api import inspect_file, unpack_file
from onec_formbin.models import descriptor_json_path
from onec_formbin.semantic_form import build_semantic_model


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def descriptor_record(info: dict, label: str) -> dict:
    return next(record for record in info["records"] if record["kind"] == "descriptor" and record["label"] == label)


def semantic_descriptor_record(model: dict, label: str) -> dict:
    return next(record for record in model["container"]["descriptor_records"] if record["label"] == label)


def test_inspect_file_includes_common_indicator_descriptor_json() -> None:
    info = inspect_file(fixture_path("common-indicator.Form.bin"))

    form_descriptor = descriptor_record(info, "form")["descriptor_json"]
    module_descriptor = descriptor_record(info, "module")["descriptor_json"]

    assert form_descriptor["format"] == "u64-pair-utf16le-v1"
    assert form_descriptor["field_a_u64_le"] == form_descriptor["field_b_u64_le"]
    assert form_descriptor["leading_nul_u16_count"] == 2
    assert form_descriptor["name_utf16le"] == "form"
    assert form_descriptor["name_matches_record_label"] is True
    assert form_descriptor["trailing_nul_u16_count"] == 2

    assert module_descriptor["body_size"] == 36
    assert module_descriptor["name_utf16le"] == "module"
    assert module_descriptor["name_matches_record_label"] is True


def test_semantic_model_includes_descriptor_json_for_common_print_form() -> None:
    model = build_semantic_model(fixture_path("common-print-form.Form.bin"))

    form_descriptor = semantic_descriptor_record(model, "form")["descriptor_json"]
    module_descriptor = semantic_descriptor_record(model, "module")["descriptor_json"]

    assert form_descriptor["format"] == "u64-pair-utf16le-v1"
    assert form_descriptor["name_utf16le"] == "form"
    assert module_descriptor["format"] == "u64-pair-utf16le-v1"
    assert module_descriptor["name_utf16le"] == "module"
    assert module_descriptor["u64_values_match"] is True


def test_inspect_file_includes_descriptor_json_on_split_form_holdout() -> None:
    info = inspect_file(fixture_path("i584-load-form.Form.bin"))

    form_descriptor = descriptor_record(info, "form")["descriptor_json"]
    module_descriptor = descriptor_record(info, "module")["descriptor_json"]

    assert form_descriptor["format"] == "u64-pair-utf16le-v1"
    assert form_descriptor["name_utf16le"] == "form"
    assert module_descriptor["format"] == "u64-pair-utf16le-v1"
    assert module_descriptor["name_utf16le"] == "module"
    assert form_descriptor["field_a_u64_le"] == module_descriptor["field_a_u64_le"]


def test_unpack_writes_descriptor_json_artifacts(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    info = inspect_file(source)
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    form_descriptor = json.loads(descriptor_json_path(unpack_dir, "form").read_text(encoding="utf-8"))
    module_descriptor = json.loads(descriptor_json_path(unpack_dir, "module").read_text(encoding="utf-8"))

    assert form_descriptor == descriptor_record(info, "form")["descriptor_json"]
    assert module_descriptor == descriptor_record(info, "module")["descriptor_json"]


def test_unpack_writes_descriptor_json_artifacts_on_split_form_holdout(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    info = inspect_file(source)
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    form_descriptor = json.loads(descriptor_json_path(unpack_dir, "form").read_text(encoding="utf-8"))
    module_descriptor = json.loads(descriptor_json_path(unpack_dir, "module").read_text(encoding="utf-8"))

    assert form_descriptor == descriptor_record(info, "form")["descriptor_json"]
    assert module_descriptor == descriptor_record(info, "module")["descriptor_json"]
