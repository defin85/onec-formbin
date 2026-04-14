from __future__ import annotations

import json
from pathlib import Path

from onec_formbin.api import inspect_file, unpack_file
from onec_formbin.models import container_inspect_path


def fixture_path(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / name


def test_inspect_file_reports_workspace_backbone_links_on_common_indicator() -> None:
    info = inspect_file(fixture_path("common-indicator.Form.bin"))

    assert info["descriptor_links"] == [
        {"label": "module", "descriptor_index": 2, "payload_index": 3},
        {"label": "form", "descriptor_index": 1, "payload_index": 4},
    ]
    assert info["continuation_chains"] == []
    assert info["pointer_links"] == []
    assert info["record_layout"] == {
        "prefix_size": 16,
        "total_size": 3657,
        "record_spans": [
            {"index": 0, "header_start": 16, "header_end": 47, "body_start": 47, "body_end": 559},
            {"index": 1, "header_start": 559, "header_end": 590, "body_start": 590, "body_end": 622},
            {"index": 2, "header_start": 622, "header_end": 653, "body_start": 653, "body_end": 689},
            {"index": 3, "header_start": 689, "header_end": 720, "body_start": 720, "body_end": 1232},
            {"index": 4, "header_start": 1232, "header_end": 1263, "body_start": 1263, "body_end": 3657},
        ],
    }

    opaque = info["records"][0]
    form_descriptor = info["records"][1]
    module = info["records"][3]
    form = info["records"][4]

    assert opaque["codec"] == "binary"
    assert opaque["record_role"] == "opaque_payload"
    assert opaque["workspace_relative_path"] == "records/000-opaque.bin"
    assert opaque["linked_descriptor_index"] is None
    assert opaque["continuation_chain"] is None

    assert form_descriptor["record_role"] == "form_descriptor"
    assert form_descriptor["workspace_relative_path"] == "records/001-form.descriptor.bin"
    assert form_descriptor["linked_descriptor_index"] is None

    assert module["codec"] == "utf-8-sig"
    assert module["record_role"] == "module_payload"
    assert module["workspace_relative_path"] == "records/003-module.bsl"
    assert module["linked_descriptor_index"] == 2
    assert module["continuation_chain"] is None

    assert form["codec"] == "utf-8-sig"
    assert form["record_role"] == "form_payload"
    assert form["workspace_relative_path"] == "records/004-form.raw"
    assert form["linked_descriptor_index"] == 1
    assert form["continuation_chain"] is None


def test_inspect_file_reports_split_form_continuation_metadata() -> None:
    info = inspect_file(fixture_path("i584-load-form.Form.bin"))

    assert info["descriptor_links"] == [
        {"label": "form", "descriptor_index": 1, "payload_index": 2},
        {"label": "module", "descriptor_index": 3, "payload_index": 4},
    ]
    assert info["continuation_chains"] == [
        {
            "kind": "form",
            "label": "form",
            "head_record_index": 2,
            "record_indices": [2, 5],
        }
    ]
    assert info["pointer_links"] == [
        {
            "source_record_index": 2,
            "target_record_index": 5,
            "target_header_start": 89120,
            "source_label": "form",
            "target_label": "opaque",
        }
    ]
    assert info["record_layout"] == {
        "prefix_size": 16,
        "total_size": 129805,
        "record_spans": [
            {"index": 0, "header_start": 16, "header_end": 47, "body_start": 47, "body_end": 559},
            {"index": 1, "header_start": 559, "header_end": 590, "body_start": 590, "body_end": 622},
            {"index": 2, "header_start": 622, "header_end": 653, "body_start": 653, "body_end": 66191},
            {"index": 3, "header_start": 66191, "header_end": 66222, "body_start": 66222, "body_end": 66258},
            {"index": 4, "header_start": 66258, "header_end": 66289, "body_start": 66289, "body_end": 89120},
            {"index": 5, "header_start": 89120, "header_end": 89151, "body_start": 89151, "body_end": 129805},
        ],
    }

    form = info["records"][2]
    module = info["records"][4]
    tail = info["records"][5]

    assert form["record_role"] == "form_payload"
    assert form["linked_descriptor_index"] == 1
    assert form["continuation_chain"] == [2, 5]

    assert module["record_role"] == "module_payload"
    assert module["linked_descriptor_index"] == 3
    assert module["continuation_chain"] is None

    assert tail["codec"] == "binary"
    assert tail["record_role"] == "form_continuation"
    assert tail["workspace_relative_path"] == "records/005-opaque.bin"
    assert tail["linked_descriptor_index"] is None
    assert tail["continuation_chain"] == [2, 5]


def test_unpack_writes_container_inspect_json_backbone(tmp_path: Path) -> None:
    source = fixture_path("common-indicator.Form.bin")
    unpack_dir = tmp_path / "unpack"

    unpack_file(source, unpack_dir)

    exported = json.loads(container_inspect_path(unpack_dir).read_text(encoding="utf-8"))
    assert exported == inspect_file(source)


def test_inspect_file_reads_container_inspect_json_from_unpacked_dir(tmp_path: Path) -> None:
    source = fixture_path("common-indicator.Form.bin")
    unpack_dir = tmp_path / "unpack"

    unpack_file(source, unpack_dir)

    assert inspect_file(unpack_dir) == inspect_file(source)
