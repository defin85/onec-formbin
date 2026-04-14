from __future__ import annotations

import json
from pathlib import Path

from onec_formbin.api import unpack_file
from onec_formbin.diffing import diff_paths
from onec_formbin.models import FormRenderMode
from onec_formbin.workspace import read_text_exact, write_text_exact


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def semantic_workspace_change(tmp_path: Path, mutator) -> dict:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)
    mutator(right_dir)
    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.SEMANTIC)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "semantic"
    assert changed["notes"] == ["semantic workspace slices changed without raw form payload changes"]
    return changed


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


def test_diff_can_render_form_payload_in_semantic_mode(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    form_path = right_dir / "records" / "004-form.raw"
    content = read_text_exact(form_path)
    write_text_exact(form_path, content.replace('"Печать"', '"Печать2"', 1))

    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.SEMANTIC)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "semantic"
    assert "### semantic/form.meta.json" in changed["body_diff"]
    assert "### semantic/strings.json" in changed["body_diff"]
    assert "Печать2" in changed["body_diff"]


def test_diff_can_render_workspace_semantic_slice_changes_before_apply(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    meta_path = right_dir / "semantic" / "form.meta.json"
    meta = json.loads(read_text_exact(meta_path))
    meta["form_title"] = "ПечатьW"
    write_text_exact(meta_path, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.SEMANTIC)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "semantic"
    assert changed["notes"] == ["semantic workspace slices changed without raw form payload changes"]
    assert "### semantic/form.meta.json" in changed["body_diff"]
    assert "ПечатьW" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]


def test_diff_can_render_workspace_controls_tree_changes_before_apply(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    controls_path = right_dir / "semantic" / "controls.tree.json"
    controls = json.loads(read_text_exact(controls_path))
    target = next(item for item in controls["items"] if item["id"] == "control-1-2-2-3-5-3")
    target["name"] = "ДеревоПечати4"
    target["title"] = "ДеревоПечати4"
    write_text_exact(controls_path, json.dumps(controls, ensure_ascii=False, indent=2) + "\n")

    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.SEMANTIC)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "semantic"
    assert changed["notes"] == ["semantic workspace slices changed without raw form payload changes"]
    assert "### semantic/controls.tree.json" in changed["body_diff"]
    assert "ДеревоПечати4" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]


def test_diff_can_render_workspace_attributes_changes_before_apply(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    unpack_file(source, left_dir)
    unpack_file(source, right_dir)

    attributes_path = right_dir / "semantic" / "attributes.json"
    attributes = json.loads(read_text_exact(attributes_path))
    attributes["items"][0]["name"] = "ДеревоПечати5"
    attributes["items"][0]["data_path"] = "ДеревоПечати5"
    write_text_exact(attributes_path, json.dumps(attributes, ensure_ascii=False, indent=2) + "\n")

    report = diff_paths(left_dir, right_dir, form_mode=FormRenderMode.SEMANTIC)
    assert report["identical"] is False
    assert len(report["changed_records"]) == 1
    changed = report["changed_records"][0]
    assert changed["right"]["label"] == "form"
    assert changed["render_mode"] == "semantic"
    assert changed["notes"] == ["semantic workspace slices changed without raw form payload changes"]
    assert "### semantic/attributes.json" in changed["body_diff"]
    assert "ДеревоПечати5" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]


def test_diff_can_render_workspace_layout_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        layout_path = right_dir / "semantic" / "layout.json"
        layout = json.loads(read_text_exact(layout_path))
        layout["items"][0]["order"] = 99
        write_text_exact(layout_path, json.dumps(layout, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/layout.json" in changed["body_diff"]
    assert '"order": 99' in changed["body_diff"]
    assert "### semantic/controls.tree.json" not in changed["body_diff"]


def test_diff_can_render_workspace_events_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        events_path = right_dir / "semantic" / "events.json"
        events = json.loads(read_text_exact(events_path))
        events["items"][0]["handler"] = "ПередОткрытиемХ"
        write_text_exact(events_path, json.dumps(events, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/events.json" in changed["body_diff"]
    assert "ПередОткрытиемХ" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]


def test_diff_can_render_workspace_commands_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        commands_path = right_dir / "semantic" / "commands.json"
        commands = json.loads(read_text_exact(commands_path))
        commands["items"][0]["title"] = "Печатать ХХ"
        write_text_exact(commands_path, json.dumps(commands, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/commands.json" in changed["body_diff"]
    assert "Печатать ХХ" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]
    assert "### semantic/controls.tree.json" not in changed["body_diff"]


def test_diff_can_render_workspace_commands_changes_without_controls_or_strings_leak_before_apply(
    tmp_path: Path,
) -> None:
    def mutate(right_dir: Path) -> None:
        commands_path = right_dir / "semantic" / "commands.json"
        commands = json.loads(read_text_exact(commands_path))
        commands["items"][0]["title"] = "Печатать YY"
        write_text_exact(commands_path, json.dumps(commands, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/commands.json" in changed["body_diff"]
    assert "Печатать YY" in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]
    assert "### semantic/controls.tree.json" not in changed["body_diff"]


def test_diff_can_render_workspace_strings_form_title_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        strings_path = right_dir / "semantic" / "strings.json"
        strings = json.loads(read_text_exact(strings_path))
        for item in strings["items"]:
            if item["role"] == "form_title":
                item["value"] = "ПечатьW"
                break
        write_text_exact(strings_path, json.dumps(strings, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/strings.json" in changed["body_diff"]
    assert "ПечатьW" in changed["body_diff"]
    assert "### semantic/form.meta.json" not in changed["body_diff"]


def test_diff_can_render_workspace_strings_control_name_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        strings_path = right_dir / "semantic" / "strings.json"
        strings = json.loads(read_text_exact(strings_path))
        for item in strings["items"]:
            if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3":
                item["value"] = "ДеревоПечатиZ"
                break
        write_text_exact(strings_path, json.dumps(strings, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/strings.json" in changed["body_diff"]
    assert "ДеревоПечатиZ" in changed["body_diff"]
    assert "### semantic/controls.tree.json" not in changed["body_diff"]
    assert "### semantic/attributes.json" not in changed["body_diff"]


def test_diff_can_render_workspace_controls_tree_event_binding_metadata_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        controls_path = right_dir / "semantic" / "controls.tree.json"
        controls = json.loads(read_text_exact(controls_path))
        target = next(item for item in controls["items"] if item["id"] == "control-1-2-2-3-5-3")
        target["event_bindings"][0]["name"] = "Дерево печати Х"
        write_text_exact(controls_path, json.dumps(controls, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/controls.tree.json" in changed["body_diff"]
    assert "Дерево печати Х" in changed["body_diff"]
    assert "### semantic/events.json" not in changed["body_diff"]


def test_diff_can_render_workspace_strings_alias_batch_changes_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        strings_path = right_dir / "semantic" / "strings.json"
        strings = json.loads(read_text_exact(strings_path))
        for item in strings["items"]:
            if item["role"] == "form_title":
                item["value"] = "ПечатьQ"
            elif item["role"] == "event_handler" and item["owner_id"] == "event-4-1-2":
                item["value"] = "ПередОткрытиемQ"
            elif item["role"] == "command_title":
                item["value"] = "Печатать Q"
        write_text_exact(strings_path, json.dumps(strings, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/strings.json" in changed["body_diff"]
    assert "ПечатьQ" in changed["body_diff"]
    assert "ПередОткрытиемQ" in changed["body_diff"]
    assert "Печатать Q" in changed["body_diff"]
    assert "### semantic/form.meta.json" not in changed["body_diff"]
    assert "### semantic/events.json" not in changed["body_diff"]
    assert "### semantic/commands.json" not in changed["body_diff"]


def test_diff_can_render_workspace_controls_tree_changes_without_attributes_leak_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        controls_path = right_dir / "semantic" / "controls.tree.json"
        controls = json.loads(read_text_exact(controls_path))
        target = next(item for item in controls["items"] if item["id"] == "control-1-2-2-3-5-3")
        target["name"] = "ДеревоПечати4"
        target["title"] = "ДеревоПечати4"
        write_text_exact(controls_path, json.dumps(controls, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/controls.tree.json" in changed["body_diff"]
    assert "ДеревоПечати4" in changed["body_diff"]
    assert "### semantic/attributes.json" not in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]


def test_diff_can_render_workspace_attributes_changes_without_controls_leak_before_apply(tmp_path: Path) -> None:
    def mutate(right_dir: Path) -> None:
        attributes_path = right_dir / "semantic" / "attributes.json"
        attributes = json.loads(read_text_exact(attributes_path))
        attributes["items"][0]["name"] = "ДеревоПечати6"
        attributes["items"][0]["data_path"] = "ДеревоПечати6"
        write_text_exact(attributes_path, json.dumps(attributes, ensure_ascii=False, indent=2) + "\n")

    changed = semantic_workspace_change(tmp_path, mutate)
    assert "### semantic/attributes.json" in changed["body_diff"]
    assert "ДеревоПечати6" in changed["body_diff"]
    assert "### semantic/controls.tree.json" not in changed["body_diff"]
    assert "### semantic/strings.json" not in changed["body_diff"]
