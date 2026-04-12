from __future__ import annotations

from pathlib import Path

from onec_formbin.api import unpack_file
from onec_formbin.semantic_form import build_semantic_model


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def test_build_semantic_model_reports_common_indicator_summary() -> None:
    model = build_semantic_model(fixture_path("common-indicator.Form.bin"))

    assert model["semantic_version"] == 1
    assert model["source"]["kind"] == "form_bin"
    assert model["container"]["record_count"] == 5
    assert model["container"]["form_record"]["index"] == 4
    assert model["container"]["form_record"]["split_form"] is False
    assert model["container"]["module_record"]["index"] == 3
    assert model["form_model"]["root_kind"] == "list"
    assert model["form_model"]["top_level_item_count"] == 18
    assert model["form_model"]["node_counts"]["string"] == 18
    assert "Индикатор" in model["form_model"]["string_samples"]


def test_build_semantic_model_reports_common_print_form_samples() -> None:
    model = build_semantic_model(fixture_path("common-print-form.Form.bin"))

    assert model["container"]["form_record"]["size_policy"] == "mirror"
    assert model["container"]["module_record"]["line_count"] > 10
    assert model["form_model"]["top_level_item_count"] == 20
    assert model["form_model"]["node_counts"]["string"] == 151
    assert "Печать" in model["form_model"]["string_samples"]
    assert model["form_model"]["top_level_items"][1]["kind"] == "list"


def test_build_semantic_model_matches_between_bin_and_unpacked_dir(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    from_bin = build_semantic_model(source)
    from_dir = build_semantic_model(unpack_dir)

    assert from_bin["container"]["form_record"]["split_form"] is True
    assert from_bin["container"]["form_record"]["pointer_record_index"] == 5
    assert from_dir["source"]["kind"] == "unpack_dir"
    assert from_bin["container"] == from_dir["container"]
    assert from_bin["form_model"] == from_dir["form_model"]
