from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from onec_formbin.api import unpack_file


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "onec_formbin.cli", *args],
        cwd=repo_root(),
        text=True,
        capture_output=True,
        check=False,
    )


def mutate_workspace_json(unpack_dir: Path, name: str, mutate) -> None:
    path = unpack_dir / "semantic" / name
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_inspect_missing_input_emits_controlled_error_without_traceback() -> None:
    result = run_cli("inspect", "/does/not/exist.Form.bin")

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Path does not exist: /does/not/exist.Form.bin.\n"


def test_apply_semantic_requires_unpack_directory_without_traceback() -> None:
    result = run_cli("apply-semantic", str(fixture_path("common-print-form.Form.bin")))

    assert result.returncode == 2
    assert result.stdout == ""
    assert (
        result.stderr
        == f"error: Expected an unpack directory, got file: {fixture_path('common-print-form.Form.bin')}.\n"
    )


def test_apply_semantic_reports_missing_workspace_slice_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    (unpack_dir / "semantic" / "form.meta.json").unlink()

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic workspace is missing semantic/form.meta.json.\n"


def test_pack_reports_missing_manifest_without_traceback(tmp_path: Path) -> None:
    result = run_cli("pack", str(tmp_path), "-o", str(tmp_path / "out.Form.bin"))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Unpack directory is missing manifest.json; run unpack first.\n"


def test_apply_semantic_reports_controls_tree_event_binding_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "controls.tree.json",
        lambda payload: next(
            item for item in payload["items"] if item["id"] == "control-1-2-2-3-5-3"
        )["event_bindings"][0].__setitem__("name", "Дерево печати Х"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits currently support only controls.tree.json[].name/title.\n"


def test_apply_semantic_reports_layout_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "layout.json",
        lambda payload: payload["items"][0].__setitem__("order", 99),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits are not supported for semantic/layout.json.\n"


def test_apply_semantic_reports_attribute_owner_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "attributes.json",
        lambda payload: payload["items"][0].__setitem__("owner_id", "form-root"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits currently support only attributes.json[].name/data_path.\n"


def test_apply_semantic_reports_event_name_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "events.json",
        lambda payload: payload["items"][0].__setitem__("name", "Перед открытием Х"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits currently support only events.json[].handler.\n"


def test_apply_semantic_reports_command_name_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "commands.json",
        lambda payload: payload["items"][0].__setitem__("name", "ПечататьВсеХ"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits currently support only commands.json[].title.\n"


def test_apply_semantic_reports_unsupported_strings_role_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "strings.json",
        lambda payload: next(item for item in payload["items"] if item["role"] == "ast_string").__setitem__(
            "value",
            "unsupported",
        ),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits are not supported for strings.json role 'ast_string'.\n"


def test_apply_semantic_reports_form_meta_flags_edit_without_traceback(tmp_path: Path) -> None:
    unpack_dir = tmp_path / "unpack"
    unpack_file(fixture_path("common-print-form.Form.bin"), unpack_dir)
    mutate_workspace_json(
        unpack_dir,
        "form.meta.json",
        lambda payload: payload["flags"].__setitem__("has_explicit_title", False),
    )

    result = run_cli("apply-semantic", str(unpack_dir))

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: Semantic edits currently support only form.meta.json.form_title.\n"
