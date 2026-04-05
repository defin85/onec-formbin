from __future__ import annotations

from pathlib import Path

import pytest

from onec_formbin.form_ast import (
    ast_from_data,
    ast_to_data,
    build_form_file,
    parse_form_source,
    parse_form_text,
    read_ast_json,
    serialize_form_text,
    write_ast_json,
)

FIXTURES = [
    "common-indicator.Form.bin",
    "common-print-form.Form.bin",
    "i584-load-form.Form.bin",
]


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


@pytest.mark.parametrize("name", FIXTURES)
def test_parse_serialize_form_ast_is_structurally_stable(name: str) -> None:
    original = parse_form_source(fixture_path(name))
    rebuilt = parse_form_text(serialize_form_text(original))
    assert ast_to_data(rebuilt) == ast_to_data(original)


def test_parse_form_source_supports_split_form_payload(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"

    from onec_formbin.api import unpack_file

    unpack_file(source, unpack_dir)

    parsed_from_bin = parse_form_source(source)
    parsed_from_dir = parse_form_source(unpack_dir)

    assert ast_to_data(parsed_from_dir) == ast_to_data(parsed_from_bin)


def test_ast_json_roundtrip_and_build_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    ast_path = tmp_path / "form.ast.json"
    raw_path = tmp_path / "rebuilt-form.raw"

    node = parse_form_source(source)
    write_ast_json(ast_path, node)
    build_form_file(ast_path, raw_path)

    restored = read_ast_json(ast_path)
    reparsed = parse_form_text(raw_path.read_text(encoding="utf-8"))
    assert ast_to_data(restored) == ast_to_data(node)
    assert ast_to_data(reparsed) == ast_to_data(node)
    assert ast_to_data(ast_from_data(ast_to_data(node))) == ast_to_data(node)
