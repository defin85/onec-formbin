from __future__ import annotations

import hashlib

OPAQUE_PREVIEW_BYTES = 24
KNOWN_DESCRIPTOR_FORMAT = "u64-pair-utf16le-v1"


def parse_descriptor_body(body: bytes, *, label: str | None = None) -> dict:
    parsed = parse_known_descriptor_body(body)
    if parsed is None:
        return {
            "format": "opaque",
            "body_size": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "hex_preview": body[:OPAQUE_PREVIEW_BYTES].hex(),
        }

    field_a, field_b, leading_nuls, name_utf16le, trailing_nuls = parsed
    summary = {
        "format": KNOWN_DESCRIPTOR_FORMAT,
        "body_size": len(body),
        "field_a_u64_le": field_a,
        "field_b_u64_le": field_b,
        "u64_values_match": field_a == field_b,
        "leading_nul_u16_count": leading_nuls,
        "name_utf16le": name_utf16le,
        "trailing_nul_u16_count": trailing_nuls,
    }
    if label is not None:
        summary["name_matches_record_label"] = name_utf16le == label
    return summary


def parse_known_descriptor_body(body: bytes) -> tuple[int, int, int, str, int] | None:
    if len(body) < 20 or len(body) % 2 != 0:
        return None

    tail = body[16:]
    code_units = [int.from_bytes(tail[index : index + 2], "little") for index in range(0, len(tail), 2)]
    leading_nuls = count_leading_nuls(code_units)
    trailing_nuls = count_trailing_nuls(code_units)
    name_units = code_units[leading_nuls : len(code_units) - trailing_nuls]
    if not name_units or any(unit == 0 for unit in name_units):
        return None

    name_start = leading_nuls * 2
    name_end = len(tail) - trailing_nuls * 2
    try:
        name_utf16le = tail[name_start:name_end].decode("utf-16le")
    except UnicodeDecodeError:
        return None

    return (
        int.from_bytes(body[0:8], "little"),
        int.from_bytes(body[8:16], "little"),
        leading_nuls,
        name_utf16le,
        trailing_nuls,
    )


def count_leading_nuls(code_units: list[int]) -> int:
    count = 0
    for unit in code_units:
        if unit != 0:
            break
        count += 1
    return count


def count_trailing_nuls(code_units: list[int]) -> int:
    count = 0
    for unit in reversed(code_units):
        if unit != 0:
            break
        count += 1
    return count
