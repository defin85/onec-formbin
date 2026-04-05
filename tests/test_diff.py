from __future__ import annotations

from pathlib import Path

from onec_formbin.api import unpack_file
from onec_formbin.diffing import diff_paths
from onec_formbin.models import FormRenderMode
from onec_formbin.workspace import read_text_exact, write_text_exact


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def test_diff_identical_file_reports_no_changes() -> None:
    source = fixture_path("common-print-form.Form.bin")
    report = diff_paths(source, source)
    assert report["identical"] is True
    assert report["changed_records"] == []


def test_diff_reports_module_change_between_unpacked_dirs(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    module_path = right_dir / "records" / "003-module.bsl"
    write_text_exact(
        module_path,
        read_text_exact(module_path) + "\n// changed in diff test\n",
    )

    report = diff_paths(left_dir, right_dir)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "module"
    assert "// changed in diff test" in changed["body_diff"]


def test_diff_can_render_form_payload_in_ast_mode(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    form_path = right_dir / "records" / "004-form.raw"
    content = read_text_exact(form_path)
    write_text_exact(form_path, content.replace('"Печать"', '"Печать2"', 1))

    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.AST)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "ast"
    assert "Печать2" in changed["body_diff"]
