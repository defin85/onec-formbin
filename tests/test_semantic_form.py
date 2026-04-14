from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from onec_formbin.api import pack_directory, unpack_file
from onec_formbin.container import ContainerError
from onec_formbin.models import support_artifact_path
from onec_formbin.semantic_form import (
    apply_semantic_workspace,
    build_semantic_model,
    build_workspace_bundle_artifacts,
)


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def string_items(model: dict, *, value: str | None = None, role: str | None = None) -> list[dict]:
    items = model["semantic"]["strings.json"]["items"]
    return [
        item
        for item in items
        if (value is None or item["value"] == value) and (role is None or item["role"] == role)
    ]


def event_items(model: dict) -> list[dict]:
    return model["semantic"]["events.json"]["items"]


def command_items(model: dict) -> list[dict]:
    return model["semantic"]["commands.json"]["items"]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    write_json(path, payload)


def test_build_semantic_model_reports_common_indicator_summary() -> None:
    model = build_semantic_model(fixture_path("common-indicator.Form.bin"))

    assert model["semantic_version"] == 1
    assert model["source"]["kind"] == "form_bin"
    assert model["container"]["record_count"] == 5
    assert model["container"]["form_record"]["index"] == 4
    assert model["container"]["form_record"]["split_form"] is False
    assert model["container"]["module_record"]["index"] == 3
    assert model["container"]["inspect_backbone"]["descriptor_links"] == [
        {"label": "module", "descriptor_index": 2, "payload_index": 3},
        {"label": "form", "descriptor_index": 1, "payload_index": 4},
    ]
    assert model["container"]["inspect_backbone"]["record_layout"]["total_size"] == 3657
    assert model["semantic"]["form.meta.json"] == {
        "schema": "onec-formbin.form-meta.v1",
        "version": 1,
        "form_name": "common-indicator",
        "form_title": "",
        "form_kind": "ordinary",
        "root_item_id": "form-root",
        "flags": {
            "has_explicit_title": False,
            "has_module_record": True,
        },
    }
    assert model["form_model"]["root_kind"] == "list"
    assert model["form_model"]["top_level_item_count"] == 18
    assert model["form_model"]["node_counts"]["string"] == 18
    assert "Индикатор" in model["form_model"]["string_samples"]
    assert model["semantic"]["strings.json"]["schema"] == "onec-formbin.strings.v1"
    assert model["semantic"]["strings.json"]["version"] == 1
    assert len(model["semantic"]["strings.json"]["items"]) == 18
    assert string_items(model, value="Индикатор", role="control_name") == [
        {
            "id": "string-1-2-2-1-4-1",
            "value": "Индикатор",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-1",
            "role": "control_name",
        }
    ]
    assert not string_items(model, role="form_title")
    assert model["semantic"]["events.json"] == {
        "schema": "onec-formbin.events.v1",
        "version": 1,
        "items": [],
    }
    assert model["semantic"]["commands.json"] == {
        "schema": "onec-formbin.commands.v1",
        "version": 1,
        "items": [],
    }
    assert model["semantic"]["controls.tree.json"]["items"][0] == {
        "id": "form-root",
        "kind": "form",
        "name": "common-indicator",
        "title": "",
        "parent_id": None,
        "child_ids": ["control-1-2-2-1", "control-1-2-2-2"],
        "command_ids": [],
        "event_bindings": [],
    }


def test_build_semantic_model_reports_common_print_form_samples() -> None:
    model = build_semantic_model(fixture_path("common-print-form.Form.bin"))

    assert model["container"]["form_record"]["size_policy"] == "mirror"
    assert model["container"]["module_record"]["line_count"] > 10
    assert model["form_model"]["top_level_item_count"] == 20
    assert model["form_model"]["node_counts"]["string"] == 151
    assert "Печать" in model["form_model"]["string_samples"]
    assert model["form_model"]["top_level_items"][1]["kind"] == "list"
    assert len(model["semantic"]["strings.json"]["items"]) == 151
    assert event_items(model) == [
        {
            "id": "event-4-1-2",
            "name": "Перед открытием",
            "handler": "ПередОткрытием",
            "scope": "form",
            "owner_id": "form-root",
        },
        {
            "id": "event-4-2-2",
            "name": "Перед закрытием",
            "handler": "ПередЗакрытием",
            "scope": "form",
            "owner_id": "form-root",
        },
    ]
    assert command_items(model) == [
        {
            "id": "command-1-2-2-2-2-1-7-5-4",
            "name": "ПечататьВсе",
            "title": "Печатать все",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        }
    ]
    assert string_items(model, value="Печать", role="form_title") == [
        {
            "id": "string-1-1-0-2-1",
            "value": "Печать",
            "owner_kind": "form",
            "owner_id": "form-root",
            "role": "form_title",
        }
    ]
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "event_handler"] == [
        {
            "id": "string-4-1-2-1",
            "value": "ПередОткрытием",
            "owner_kind": "event",
            "owner_id": "event-4-1-2",
            "role": "event_handler",
        },
        {
            "id": "string-4-2-2-1",
            "value": "ПередЗакрытием",
            "owner_kind": "event",
            "owner_id": "event-4-2-2",
            "role": "event_handler",
        },
    ]
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "command_name"] == [
        {
            "id": "string-1-2-2-2-2-1-7-5-4-1",
            "value": "ПечататьВсе",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_name",
        }
    ]
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "command_title"] == [
        {
            "id": "string-1-2-2-2-2-1-7-5-4-2-2-2-1",
            "value": "Печатать все",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_title",
        },
        {
            "id": "string-1-2-2-2-2-1-7-9-6-4-2-1",
            "value": "Печатать все",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_title",
        },
    ]
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "control_name"] == [
        {
            "id": "string-1-2-2-1-4-1",
            "value": "КоманднаяПанель1",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-1",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-2-4-1",
            "value": "ОсновныеДействияФормы",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-2",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-4-1",
            "value": "Панель1",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-1-4-1",
            "value": "Разделитель1",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-1",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-2-4-1",
            "value": "ТабДок",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-2",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-3-4-1",
            "value": "ДеревоПечати",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-3",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-4-4-1",
            "value": "КомандыДерева",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-4",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-5-4-1",
            "value": "ПоОриентировать",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-5",
            "role": "control_name",
        },
        {
            "id": "string-1-2-2-3-5-6-4-1",
            "value": "НеИспользоватьДеревоПечати",
            "owner_kind": "control",
            "owner_id": "control-1-2-2-3-5-6",
            "role": "control_name",
        },
    ]
    assert model["semantic"]["attributes.json"] == {
        "schema": "onec-formbin.attributes.v1",
        "version": 1,
        "items": [
            {
                "id": "attribute-1-2-2-3-5-3",
                "name": "ДеревоПечати",
                "owner_id": "control-1-2-2-3-5-3",
                "data_path": "ДеревоПечати",
                "type_hint": "pattern:#",
                "role": "control_pattern_binding_candidate",
            }
        ],
    }
    assert model["semantic"]["controls.tree.json"] == {
        "schema": "onec-formbin.controls-tree.v1",
        "version": 1,
        "root_id": "form-root",
        "items": [
            {
                "id": "form-root",
                "kind": "form",
                "name": "common-print-form",
                "title": "Печать",
                "parent_id": None,
                "child_ids": ["control-1-2-2-1", "control-1-2-2-2", "control-1-2-2-3"],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-1",
                "kind": "control",
                "name": "КоманднаяПанель1",
                "title": "КоманднаяПанель1",
                "parent_id": "form-root",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-2",
                "kind": "control",
                "name": "ОсновныеДействияФормы",
                "title": "ОсновныеДействияФормы",
                "parent_id": "form-root",
                "child_ids": [],
                "command_ids": ["command-1-2-2-2-2-1-7-5-4"],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3",
                "kind": "control",
                "name": "Панель1",
                "title": "Панель1",
                "parent_id": "form-root",
                "child_ids": [
                    "control-1-2-2-3-5-1",
                    "control-1-2-2-3-5-2",
                    "control-1-2-2-3-5-3",
                    "control-1-2-2-3-5-4",
                    "control-1-2-2-3-5-5",
                    "control-1-2-2-3-5-6",
                ],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3-5-1",
                "kind": "control",
                "name": "Разделитель1",
                "title": "Разделитель1",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3-5-2",
                "kind": "control",
                "name": "ТабДок",
                "title": "ТабДок",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3-5-3",
                "kind": "control",
                "name": "ДеревоПечати",
                "title": "ДеревоПечати",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [
                    {
                        "id": "event-1-2-2-3-5-3-2-4-1-2",
                        "name": "Дерево печати при активизации строки",
                        "handler": "ДеревоПечатиПриАктивизацииСтроки",
                        "scope": "control",
                        "owner_id": "control-1-2-2-3-5-3",
                    }
                ],
            },
            {
                "id": "control-1-2-2-3-5-4",
                "kind": "control",
                "name": "КомандыДерева",
                "title": "КомандыДерева",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3-5-5",
                "kind": "control",
                "name": "ПоОриентировать",
                "title": "ПоОриентировать",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [],
            },
            {
                "id": "control-1-2-2-3-5-6",
                "kind": "control",
                "name": "НеИспользоватьДеревоПечати",
                "title": "НеИспользоватьДеревоПечати",
                "parent_id": "control-1-2-2-3",
                "child_ids": [],
                "command_ids": [],
                "event_bindings": [
                    {
                        "id": "event-1-2-2-3-5-6-2-2-1-2",
                        "name": "Не использовать дерево печати при изменении",
                        "handler": "НеИспользоватьДеревоПечатиПриИзменении",
                        "scope": "control",
                        "owner_id": "control-1-2-2-3-5-6",
                    }
                ],
            },
        ],
    }
    assert model["semantic"]["layout.json"] == {
        "schema": "onec-formbin.layout.v1",
        "version": 1,
        "items": [
            {
                "control_id": "control-1-2-2-1",
                "container_id": "form-root",
                "order": 0,
                "group_kind": "form-root-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-2",
                "container_id": "form-root",
                "order": 1,
                "group_kind": "form-root-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3",
                "container_id": "form-root",
                "order": 2,
                "group_kind": "form-root-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-1",
                "container_id": "control-1-2-2-3",
                "order": 0,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-2",
                "container_id": "control-1-2-2-3",
                "order": 1,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-3",
                "container_id": "control-1-2-2-3",
                "order": 2,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-4",
                "container_id": "control-1-2-2-3",
                "order": 3,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-5",
                "container_id": "control-1-2-2-3",
                "order": 4,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
            {
                "control_id": "control-1-2-2-3-5-6",
                "container_id": "control-1-2-2-3",
                "order": 5,
                "group_kind": "control-child-list",
                "visibility": "unknown",
            },
        ],
    }


def test_build_semantic_model_includes_inspect_backbone_for_cli_source() -> None:
    model = build_semantic_model(fixture_path("common-print-form.Form.bin"))

    backbone = model["container"]["inspect_backbone"]
    assert backbone["descriptor_links"] == [
        {"label": "module", "descriptor_index": 2, "payload_index": 3},
        {"label": "form", "descriptor_index": 1, "payload_index": 4},
    ]
    assert backbone["continuation_chains"] == []
    assert backbone["pointer_links"] == []
    assert backbone["record_layout"]["prefix_size"] == 16
    assert backbone["record_layout"]["total_size"] == 23821
    assert model["semantic"]["form.meta.json"] == {
        "schema": "onec-formbin.form-meta.v1",
        "version": 1,
        "form_name": "common-print-form",
        "form_title": "Печать",
        "form_kind": "ordinary",
        "root_item_id": "form-root",
        "flags": {
            "has_explicit_title": True,
            "has_module_record": True,
        },
    }
    assert model["semantic"]["strings.json"]["items"][0] == {
        "id": "string-1-1-0-2-0",
        "value": "ru",
        "owner_kind": "form",
        "owner_id": "form-root",
        "role": "ast_string",
    }


def test_build_semantic_model_matches_between_bin_and_unpacked_dir(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    from_bin = build_semantic_model(source)
    from_dir = build_semantic_model(unpack_dir)

    assert from_bin["container"]["form_record"]["split_form"] is True
    assert from_bin["container"]["form_record"]["pointer_record_index"] == 5
    assert from_bin["container"]["inspect_backbone"]["pointer_links"] == [
        {
            "source_record_index": 2,
            "target_record_index": 5,
            "target_header_start": 89120,
            "source_label": "form",
            "target_label": "opaque",
        }
    ]
    assert from_bin["semantic"]["form.meta.json"] == {
        "schema": "onec-formbin.form-meta.v1",
        "version": 1,
        "form_name": "i584-load-form",
        "form_title": 'Обработка "I584 - Поступление агентских товаров и услуг"',
        "form_kind": "ordinary",
        "root_item_id": "form-root",
        "flags": {
            "has_explicit_title": True,
            "has_module_record": True,
        },
    }
    assert len(from_bin["semantic"]["strings.json"]["items"]) == 1329
    assert string_items(
        from_bin,
        value='Обработка "I584 - Поступление агентских товаров и услуг"',
        role="form_title",
    ) == [
        {
            "id": "string-1-1-0-2-1",
            "value": 'Обработка "I584 - Поступление агентских товаров и услуг"',
            "owner_kind": "form",
            "owner_id": "form-root",
            "role": "form_title",
        }
    ]
    assert event_items(from_bin) == [
        {
            "id": "event-4-1-2",
            "name": "Перед открытием",
            "handler": "ПередОткрытием",
            "scope": "form",
            "owner_id": "form-root",
        }
    ]
    assert command_items(from_bin) == [
        {
            "id": "command-1-2-2-3-2-1-7-5-4",
            "name": "ДействияФормыВосстановитьНастройки",
            "title": "Действия формы восстановить настройки",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-3-2-1-7-6-4",
            "name": "ДействияФормыСохранитьНастройки",
            "title": "Сохранить настройки",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-4-2-1-7-5-4",
            "name": "СоздатьКонтрагента",
            "title": "Создать контрагента",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-4-2-1-7-10-4",
            "name": "ОсновныеДействияФормыИмпортИзФайла",
            "title": "Импорт из файла",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-6-5-7-2-1-7-5-4",
            "name": "КоманднаяПанельСтекВыбратьВсе",
            "title": "Выбрать все",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-6-5-7-2-1-7-7-4",
            "name": "КоманднаяПанельСтекЗапуститьРегламент",
            "title": "Запустить регламент",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
        {
            "id": "command-1-2-2-6-5-7-2-1-7-8-4",
            "name": "КоманднаяПанельСтекСнятьВсе",
            "title": "Снять все",
            "owner_id": "form-root",
            "source": "ast-root-title-match",
        },
    ]
    assert len(from_bin["semantic"]["attributes.json"]["items"]) == 13
    assert from_bin["semantic"]["attributes.json"]["items"][0] == {
        "id": "attribute-1-2-2-2",
        "name": "ИмяФайла",
        "owner_id": "control-1-2-2-2",
        "data_path": "ИмяФайла",
        "type_hint": "pattern:S",
        "role": "control_pattern_binding_candidate",
    }
    assert from_bin["semantic"]["attributes.json"]["items"][-1] == {
        "id": "attribute-1-2-2-19",
        "name": "ИсточникДанных",
        "owner_id": "control-1-2-2-19",
        "data_path": "ИсточникДанных",
        "type_hint": "pattern:#",
        "role": "control_pattern_binding_candidate",
    }
    control_events = [
        binding
        for item in from_bin["semantic"]["controls.tree.json"]["items"]
        for binding in item["event_bindings"]
    ]
    assert all(binding["scope"] == "control" for binding in control_events)
    assert next(binding for binding in control_events if binding["owner_id"] == "control-1-2-2-2") == {
        "id": "event-1-2-2-2-2-4-1-2",
        "name": "Имя файла открытие",
        "handler": "ИмяФайлаОткрытие",
        "scope": "control",
        "owner_id": "control-1-2-2-2",
    }
    assert from_dir["source"]["kind"] == "unpack_dir"
    assert from_bin["container"] == from_dir["container"]
    assert from_bin["semantic"] == from_dir["semantic"]
    assert from_bin["form_model"] == from_dir["form_model"]


def test_unpack_writes_semantic_slice_artifacts(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    bundle = build_workspace_bundle_artifacts(unpack_dir)
    for name, payload in bundle["semantic"].items():
        artifact = unpack_dir / "semantic" / name
        assert artifact.exists()
        assert json.loads(artifact.read_text(encoding="utf-8")) == payload
    for name, payload in bundle["support"].items():
        artifact = support_artifact_path(unpack_dir, name)
        assert artifact.exists()
        assert json.loads(artifact.read_text(encoding="utf-8")) == payload

    capabilities = json.loads(support_artifact_path(unpack_dir, "capabilities.json").read_text(encoding="utf-8"))
    assert capabilities["bundle_contract"] == "ordinary-form-bundle.v1"
    assert capabilities["apply_semantic_supported"] is True
    assert {
        "semantic_file": "semantic/commands.json",
        "semantic_id": "command-1-2-2-2-2-1-7-5-4",
        "fields": ["name", "title"],
    } in capabilities["editable_items"]

    provenance = json.loads(support_artifact_path(unpack_dir, "provenance.json").read_text(encoding="utf-8"))
    command_entry = next(
        item
        for item in provenance["items"]
        if item["semantic_file"] == "semantic/commands.json"
        and item["semantic_id"] == "command-1-2-2-2-2-1-7-5-4"
    )
    assert command_entry["fields"]["name"] == {
        "ast_string_paths": [[1, 2, 2, 2, 2, 1, 7, 5, 4, 1]],
        "write_support": "supported",
    }
    assert command_entry["fields"]["title"] == {
        "ast_string_paths": [
            [1, 2, 2, 2, 2, 1, 7, 5, 4, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 1, 7, 9, 6, 4, 2, 1],
        ],
        "write_support": "supported",
    }


def test_unpack_materializes_control_event_binding_metadata(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    controls = json.loads((unpack_dir / "semantic" / "controls.tree.json").read_text(encoding="utf-8"))
    items = controls["items"]
    tree = next(item for item in items if item["id"] == "control-1-2-2-3-5-3")
    toggle = next(item for item in items if item["id"] == "control-1-2-2-3-5-6")
    assert tree["event_bindings"] == [
        {
            "id": "event-1-2-2-3-5-3-2-4-1-2",
            "name": "Дерево печати при активизации строки",
            "handler": "ДеревоПечатиПриАктивизацииСтроки",
            "scope": "control",
            "owner_id": "control-1-2-2-3-5-3",
        }
    ]
    assert toggle["event_bindings"] == [
        {
            "id": "event-1-2-2-3-5-6-2-2-1-2",
            "name": "Не использовать дерево печати при изменении",
            "handler": "НеИспользоватьДеревоПечатиПриИзменении",
            "scope": "control",
            "owner_id": "control-1-2-2-3-5-6",
        }
    ]


def test_unpack_materializes_command_bridge_alignment(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    commands = json.loads((unpack_dir / "semantic" / "commands.json").read_text(encoding="utf-8"))
    controls = json.loads((unpack_dir / "semantic" / "controls.tree.json").read_text(encoding="utf-8"))

    assert commands == {
        "schema": "onec-formbin.commands.v1",
        "version": 1,
        "items": [
            {
                "id": "command-1-2-2-2-2-1-7-5-4",
                "name": "ПечататьВсе",
                "title": "Печатать все",
                "owner_id": "form-root",
                "source": "ast-root-title-match",
            }
        ],
    }
    owner = next(item for item in controls["items"] if item["id"] == "control-1-2-2-2")
    assert owner["command_ids"] == ["command-1-2-2-2-2-1-7-5-4"]


def test_unpack_writes_semantic_slice_artifacts_on_split_form_holdout(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    bundle = build_workspace_bundle_artifacts(unpack_dir)
    for name, payload in bundle["semantic"].items():
        artifact = unpack_dir / "semantic" / name
        assert artifact.exists()
        assert json.loads(artifact.read_text(encoding="utf-8")) == payload
    for name, payload in bundle["support"].items():
        artifact = support_artifact_path(unpack_dir, name)
        assert artifact.exists()
        assert json.loads(artifact.read_text(encoding="utf-8")) == payload

    capabilities = json.loads(support_artifact_path(unpack_dir, "capabilities.json").read_text(encoding="utf-8"))
    assert capabilities["split_form"] is True
    assert capabilities["apply_semantic_supported"] is False
    assert capabilities["editable_items"] == []

    uncertainty = json.loads(support_artifact_path(unpack_dir, "uncertainty.json").read_text(encoding="utf-8"))
    assert uncertainty["items"][0] == {
        "scope": "workspace",
        "effect": "write_unsupported",
        "reason": "split_form_writeback_unavailable",
    }


def test_apply_semantic_updates_form_title_workspace_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    meta_path = unpack_dir / "semantic" / "form.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["form_title"] = "Печать2"
    write_json(meta_path, meta)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["form.meta.json"]["form_title"] == "Печать2"
    assert string_items(model, value="Печать2", role="form_title")


def test_apply_semantic_updates_command_title_workspace_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    commands_path = unpack_dir / "semantic" / "commands.json"
    commands = json.loads(commands_path.read_text(encoding="utf-8"))
    commands["items"][0]["title"] = "Печатать всё"
    write_json(commands_path, commands)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать всё"
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "command_title"] == [
        {
            "id": "string-1-2-2-2-2-1-7-5-4-2-2-2-1",
            "value": "Печатать всё",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_title",
        },
        {
            "id": "string-1-2-2-2-2-1-7-9-6-4-2-1",
            "value": "Печатать всё",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_title",
        },
    ]


def test_apply_semantic_updates_command_name_workspace_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    commands_path = unpack_dir / "semantic" / "commands.json"
    commands = json.loads(commands_path.read_text(encoding="utf-8"))
    commands["items"][0]["name"] = "ПечататьВсе2"
    write_json(commands_path, commands)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0] == {
        "id": "command-1-2-2-2-2-1-7-5-4",
        "name": "ПечататьВсе2",
        "title": "Печатать все",
        "owner_id": "form-root",
        "source": "ast-root-title-match",
    }


def test_apply_semantic_updates_command_name_string_alias_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    strings_path = unpack_dir / "semantic" / "strings.json"
    strings = json.loads(strings_path.read_text(encoding="utf-8"))
    target = next(
        item
        for item in strings["items"]
        if item["role"] == "command_name" and item["owner_id"] == "command-1-2-2-2-2-1-7-5-4"
    )
    target["value"] = "ПечататьВсе3"
    write_json(strings_path, strings)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0]["name"] == "ПечататьВсе3"
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать все"
    assert string_items(model, value="ПечататьВсе3", role="command_name") == [
        {
            "id": "string-1-2-2-2-2-1-7-5-4-1",
            "value": "ПечататьВсе3",
            "owner_kind": "command",
            "owner_id": "command-1-2-2-2-2-1-7-5-4",
            "role": "command_name",
        }
    ]


def test_apply_semantic_updates_event_handler_workspace_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    events_path = unpack_dir / "semantic" / "events.json"
    events = json.loads(events_path.read_text(encoding="utf-8"))
    events["items"][0]["handler"] = "ПередОткрытием2"
    write_json(events_path, events)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["events.json"]["items"][0]["handler"] == "ПередОткрытием2"
    assert [item for item in model["semantic"]["strings.json"]["items"] if item["role"] == "event_handler"][0] == {
        "id": "string-4-1-2-1",
        "value": "ПередОткрытием2",
        "owner_kind": "event",
        "owner_id": "event-4-1-2",
        "role": "event_handler",
    }


def test_apply_semantic_updates_supported_strings_aliases_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    strings_path = unpack_dir / "semantic" / "strings.json"
    strings = json.loads(strings_path.read_text(encoding="utf-8"))
    for item in strings["items"]:
        if item["role"] == "form_title":
            item["value"] = "Печать3"
        if item["role"] == "event_handler" and item["owner_id"] == "event-4-1-2":
            item["value"] = "ПередОткрытием3"
        if item["role"] == "command_title":
            item["value"] = "Печатать три"
    write_json(strings_path, strings)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["form.meta.json"]["form_title"] == "Печать3"
    assert model["semantic"]["events.json"]["items"][0]["handler"] == "ПередОткрытием3"
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать три"


def test_apply_semantic_updates_control_name_string_alias_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    strings_path = unpack_dir / "semantic" / "strings.json"
    strings = json.loads(strings_path.read_text(encoding="utf-8"))
    target = next(
        item
        for item in strings["items"]
        if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3"
    )
    target["value"] = "ДеревоПечати2"
    write_json(strings_path, strings)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    control = next(
        item for item in model["semantic"]["controls.tree.json"]["items"] if item["id"] == "control-1-2-2-3-5-3"
    )
    assert control["name"] == "ДеревоПечати2"
    assert control["title"] == "ДеревоПечати2"
    assert next(
        item
        for item in model["semantic"]["strings.json"]["items"]
        if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3"
    ) == {
        "id": "string-1-2-2-3-5-3-4-1",
        "value": "ДеревоПечати2",
        "owner_kind": "control",
        "owner_id": "control-1-2-2-3-5-3",
        "role": "control_name",
    }
    assert model["semantic"]["attributes.json"]["items"][0] == {
        "id": "attribute-1-2-2-3-5-3",
        "name": "ДеревоПечати2",
        "owner_id": "control-1-2-2-3-5-3",
        "data_path": "ДеревоПечати2",
        "type_hint": "pattern:#",
        "role": "control_pattern_binding_candidate",
    }


def test_apply_semantic_updates_controls_tree_name_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    controls_path = unpack_dir / "semantic" / "controls.tree.json"
    controls = json.loads(controls_path.read_text(encoding="utf-8"))
    target = next(item for item in controls["items"] if item["id"] == "control-1-2-2-3-5-3")
    target["name"] = "ДеревоПечати3"
    target["title"] = "ДеревоПечати3"
    write_json(controls_path, controls)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    control = next(
        item for item in model["semantic"]["controls.tree.json"]["items"] if item["id"] == "control-1-2-2-3-5-3"
    )
    assert control["name"] == "ДеревоПечати3"
    assert control["title"] == "ДеревоПечати3"
    assert next(
        item
        for item in model["semantic"]["strings.json"]["items"]
        if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3"
    ) == {
        "id": "string-1-2-2-3-5-3-4-1",
        "value": "ДеревоПечати3",
        "owner_kind": "control",
        "owner_id": "control-1-2-2-3-5-3",
        "role": "control_name",
    }
    assert model["semantic"]["attributes.json"]["items"][0] == {
        "id": "attribute-1-2-2-3-5-3",
        "name": "ДеревоПечати3",
        "owner_id": "control-1-2-2-3-5-3",
        "data_path": "ДеревоПечати3",
        "type_hint": "pattern:#",
        "role": "control_pattern_binding_candidate",
    }


def test_apply_semantic_updates_attributes_name_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    attributes_path = unpack_dir / "semantic" / "attributes.json"
    attributes = json.loads(attributes_path.read_text(encoding="utf-8"))
    attributes["items"][0]["name"] = "ДеревоПечати4"
    attributes["items"][0]["data_path"] = "ДеревоПечати4"
    write_json(attributes_path, attributes)

    apply_semantic_workspace(unpack_dir)
    pack_directory(unpack_dir, repacked)

    model = build_semantic_model(repacked)
    assert model["semantic"]["attributes.json"]["items"][0] == {
        "id": "attribute-1-2-2-3-5-3",
        "name": "ДеревоПечати4",
        "owner_id": "control-1-2-2-3-5-3",
        "data_path": "ДеревоПечати4",
        "type_hint": "pattern:#",
        "role": "control_pattern_binding_candidate",
    }
    control = next(
        item for item in model["semantic"]["controls.tree.json"]["items"] if item["id"] == "control-1-2-2-3-5-3"
    )
    assert control["name"] == "ДеревоПечати4"
    assert control["title"] == "ДеревоПечати4"
    assert next(
        item
        for item in model["semantic"]["strings.json"]["items"]
        if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3"
    ) == {
        "id": "string-1-2-2-3-5-3-4-1",
        "value": "ДеревоПечати4",
        "owner_kind": "control",
        "owner_id": "control-1-2-2-3-5-3",
        "role": "control_name",
    }


def test_apply_semantic_rejects_attributes_edits_with_diverging_data_path(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    attributes_path = unpack_dir / "semantic" / "attributes.json"
    attributes = json.loads(attributes_path.read_text(encoding="utf-8"))
    attributes["items"][0]["name"] = "ДеревоПечати5"
    write_json(attributes_path, attributes)

    with pytest.raises(ContainerError, match="name and data_path to stay in sync"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_unsupported_strings_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    strings_path = unpack_dir / "semantic" / "strings.json"
    strings = json.loads(strings_path.read_text(encoding="utf-8"))
    first_ast_string = next(item for item in strings["items"] if item["role"] == "ast_string")
    first_ast_string["value"] = "unsupported"
    write_json(strings_path, strings)

    with pytest.raises(ContainerError, match="strings.json role"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_split_form_workspace(tmp_path: Path) -> None:
    source = fixture_path("i584-load-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    with pytest.raises(ContainerError, match="split-form"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_form_meta_non_title_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "form.meta.json",
        lambda payload: payload["flags"].__setitem__("has_explicit_title", False),
    )

    with pytest.raises(ContainerError, match=r"form\.meta\.json\.form_title"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_layout_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "layout.json",
        lambda payload: payload["items"][0].__setitem__("order", 99),
    )

    with pytest.raises(ContainerError, match=r"semantic/layout\.json"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_event_non_handler_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "events.json",
        lambda payload: payload["items"][0].__setitem__("name", "Перед открытием Х"),
    )

    with pytest.raises(ContainerError, match=r"events\.json\[\]\.handler"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_command_source_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "commands.json",
        lambda payload: payload["items"][0].__setitem__("source", "other"),
    )

    with pytest.raises(ContainerError, match=r"commands\.json\[\]\.name/title"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_controls_tree_structural_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    def mutate(payload: dict) -> None:
        target = next(item for item in payload["items"] if item["id"] == "control-1-2-2-3-5-3")
        target["child_ids"].append("control-extra")

    mutate_workspace_json(unpack_dir, "controls.tree.json", mutate)

    with pytest.raises(ContainerError, match=r"controls\.tree\.json\[\]\.name/title"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_attribute_owner_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "attributes.json",
        lambda payload: payload["items"][0].__setitem__("owner_id", "form-root"),
    )

    with pytest.raises(ContainerError, match=r"attributes\.json\[\]\.name/data_path"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_rejects_controls_tree_event_binding_metadata_changes(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    unpack_file(source, unpack_dir)

    def mutate(payload: dict) -> None:
        target = next(item for item in payload["items"] if item["id"] == "control-1-2-2-3-5-3")
        target["event_bindings"][0]["name"] = "Дерево печати Х"

    mutate_workspace_json(unpack_dir, "controls.tree.json", mutate)

    with pytest.raises(ContainerError, match=r"controls\.tree\.json\[\]\.name/title"):
        apply_semantic_workspace(unpack_dir)


def test_apply_semantic_cli_updates_attributes_name_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "attributes.json",
        lambda payload: (
            payload["items"][0].__setitem__("name", "ДеревоПечатиCLI"),
            payload["items"][0].__setitem__("data_path", "ДеревоПечатиCLI"),
        ),
    )

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["attributes.json"]["items"][0] == {
        "id": "attribute-1-2-2-3-5-3",
        "name": "ДеревоПечатиCLI",
        "owner_id": "control-1-2-2-3-5-3",
        "data_path": "ДеревоПечатиCLI",
        "type_hint": "pattern:#",
        "role": "control_pattern_binding_candidate",
    }


def test_apply_semantic_cli_updates_control_name_string_alias_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    def mutate(payload: dict) -> None:
        target = next(
            item
            for item in payload["items"]
            if item["role"] == "control_name" and item["owner_id"] == "control-1-2-2-3-5-3"
        )
        target["value"] = "ДеревоПечатиCLI2"

    mutate_workspace_json(unpack_dir, "strings.json", mutate)

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    control = next(
        item for item in model["semantic"]["controls.tree.json"]["items"] if item["id"] == "control-1-2-2-3-5-3"
    )
    assert control["name"] == "ДеревоПечатиCLI2"
    assert control["title"] == "ДеревоПечатиCLI2"


def test_apply_semantic_cli_updates_command_title_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "commands.json",
        lambda payload: payload["items"][0].__setitem__("title", "Печатать CLI"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать CLI"


def test_apply_semantic_cli_updates_command_name_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "commands.json",
        lambda payload: payload["items"][0].__setitem__("name", "ПечататьВсеCLI"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0]["name"] == "ПечататьВсеCLI"
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать все"


def test_apply_semantic_cli_updates_command_name_string_alias_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    def mutate(payload: dict) -> None:
        target = next(
            item
            for item in payload["items"]
            if item["role"] == "command_name" and item["owner_id"] == "command-1-2-2-2-2-1-7-5-4"
        )
        target["value"] = "ПечататьВсеCLI2"

    mutate_workspace_json(unpack_dir, "strings.json", mutate)

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["commands.json"]["items"][0]["name"] == "ПечататьВсеCLI2"
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать все"


def test_apply_semantic_cli_updates_event_handler_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    mutate_workspace_json(
        unpack_dir,
        "events.json",
        lambda payload: payload["items"][0].__setitem__("handler", "ПередОткрытиемCLI"),
    )

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["events.json"]["items"][0]["handler"] == "ПередОткрытиемCLI"


def test_apply_semantic_cli_updates_supported_strings_aliases_and_repacked_form(tmp_path: Path) -> None:
    source = fixture_path("common-print-form.Form.bin")
    unpack_dir = tmp_path / "unpack"
    repacked = tmp_path / "edited.Form.bin"
    unpack_file(source, unpack_dir)

    def mutate(payload: dict) -> None:
        for item in payload["items"]:
            if item["role"] == "form_title":
                item["value"] = "ПечатьCLI"
            elif item["role"] == "event_handler" and item["owner_id"] == "event-4-1-2":
                item["value"] = "ПередОткрытиемCLI2"
            elif item["role"] == "command_title":
                item["value"] = "Печатать CLI2"

    mutate_workspace_json(unpack_dir, "strings.json", mutate)

    result = run_cli("apply-semantic", str(unpack_dir))
    assert result.returncode == 0
    assert result.stderr == ""
    result = run_cli("pack", str(unpack_dir), "-o", str(repacked))
    assert result.returncode == 0
    assert result.stderr == ""

    model = build_semantic_model(repacked)
    assert model["semantic"]["form.meta.json"]["form_title"] == "ПечатьCLI"
    assert model["semantic"]["events.json"]["items"][0]["handler"] == "ПередОткрытиемCLI2"
    assert model["semantic"]["commands.json"]["items"][0]["title"] == "Печатать CLI2"
