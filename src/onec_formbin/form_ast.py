from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .container import decode_text_body, parse_file
from .models import RecordKind
from .workspace import read_manifest, read_text_exact, write_text_exact


class FormAstError(ValueError):
    """Raised when a brace-form payload cannot be parsed or serialized."""


@dataclass(slots=True)
class AstNode:
    kind: str
    text: str | None = None
    items: list["AstNode"] | None = None


def parse_form_source(path: Path) -> AstNode:
    return parse_form_text(load_form_text(path))


def parse_form_text(text: str) -> AstNode:
    parser = _BraceParser(text.lstrip("\ufeff"))
    node = parser.parse_value()
    parser.skip_ws()
    if not parser.at_end():
        raise FormAstError(f"Unexpected trailing data at offset {parser.pos}.")
    return node


def serialize_form_text(node: AstNode) -> str:
    if node.kind == "list":
        return "{" + ",".join(serialize_form_text(item) for item in node.items or []) + "}"
    if node.kind in {"atom", "literal", "string"} and node.text is not None:
        return node.text
    raise FormAstError(f"Unsupported AST node: {node!r}")


def write_ast_json(path: Path, node: AstNode) -> None:
    data = {"ast_version": 1, "root": ast_to_data(node)}
    write_text_exact(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_ast_json(path: Path) -> AstNode:
    data = json.loads(read_text_exact(path))
    if data.get("ast_version") != 1:
        raise FormAstError(f"Unsupported AST version: {data.get('ast_version')!r}")
    return ast_from_data(data["root"])


def build_form_file(ast_path: Path, output_path: Path) -> None:
    node = read_ast_json(ast_path)
    write_text_exact(output_path, serialize_form_text(node))


def load_form_text(path: Path) -> str:
    if path.is_dir():
        manifest = read_manifest(path)
        form_records = [record for record in manifest.records if record.kind is RecordKind.FORM]
        if len(form_records) != 1:
            raise FormAstError(f"Expected exactly one form record, got {len(form_records)}.")
        form_record = form_records[0]
        form_text = read_text_exact(path / form_record.relative_path)
        return append_form_continuation_text(path, manifest.records, form_record, form_text)

    if path.suffix.lower() == ".bin":
        container = parse_file(path)
        form_records = [record for record in container.records if record.kind is RecordKind.FORM]
        if len(form_records) != 1:
            raise FormAstError(f"Expected exactly one form payload, got {len(form_records)}.")
        form_record = form_records[0]
        form_text = decode_text_body(form_record.body)
        return append_form_continuation_text(path.parent, container.records, form_record, form_text)

    return read_text_exact(path)


def ast_to_data(node: AstNode) -> dict:
    if node.kind == "list":
        return {
            "kind": "list",
            "items": [ast_to_data(item) for item in node.items or []],
        }
    return {"kind": node.kind, "text": node.text}


def ast_from_data(data: dict) -> AstNode:
    kind = data["kind"]
    if kind == "list":
        return AstNode(kind="list", items=[ast_from_data(item) for item in data.get("items", [])])
    return AstNode(kind=kind, text=data["text"])


def ast_to_pretty_json(node: AstNode) -> str:
    return json.dumps(ast_to_data(node), ensure_ascii=False, indent=2) + "\n"


def append_form_continuation_text(
    root: Path,
    records: list,
    form_record,
    form_text: str,
) -> str:
    target_index = getattr(form_record, "pointer_record_index", None)
    if target_index is None:
        return form_text

    target_record = next((record for record in records if record.index == target_index), None)
    if target_record is None:
        return form_text

    if hasattr(target_record, "body"):
        tail_bytes = target_record.body
    else:
        tail_bytes = (root / target_record.relative_path).read_bytes()

    try:
        tail_text = tail_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return form_text
    return form_text + tail_text


class _BraceParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def at_end(self) -> bool:
        return self.pos >= len(self.text)

    def skip_ws(self) -> None:
        while not self.at_end() and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse_value(self) -> AstNode:
        self.skip_ws()
        if self.at_end():
            raise FormAstError("Unexpected end of input.")
        if self.text.startswith("{#", self.pos):
            return self.parse_literal_block()
        if self.text[self.pos] == "{":
            return self.parse_list()
        return self.parse_atom()

    def parse_list(self) -> AstNode:
        self.expect("{")
        items: list[AstNode] = []
        self.skip_ws()
        if self.peek("}"):
            self.pos += 1
            return AstNode(kind="list", items=items)
        while True:
            items.append(self.parse_value())
            self.skip_ws()
            if self.peek("}"):
                self.pos += 1
                return AstNode(kind="list", items=items)
            self.expect(",")

    def parse_atom(self) -> AstNode:
        if self.text[self.pos] == '"':
            return AstNode(kind="string", text=self.read_string_token())
        start = self.pos
        while not self.at_end() and self.text[self.pos] not in ",{} \t\r\n":
            self.pos += 1
        if start == self.pos:
            raise FormAstError(f"Expected atom at offset {self.pos}.")
        return AstNode(kind="atom", text=self.text[start:self.pos])

    def parse_literal_block(self) -> AstNode:
        start = self.pos
        end = self.text.find("}", self.pos)
        if end == -1:
            raise FormAstError(f"Unterminated literal block at offset {start}.")
        self.pos = end + 1
        return AstNode(kind="literal", text=self.text[start:self.pos])

    def read_string_token(self) -> str:
        start = self.pos
        self.pos += 1
        while not self.at_end():
            char = self.text[self.pos]
            if char == '"':
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '"':
                    self.pos += 2
                    continue
                self.pos += 1
                return self.text[start:self.pos]
            self.pos += 1
        raise FormAstError(f"Unterminated string at offset {start}.")

    def expect(self, value: str) -> None:
        self.skip_ws()
        if self.at_end() or self.text[self.pos] != value:
            raise FormAstError(f"Expected {value!r} at offset {self.pos}.")
        self.pos += 1

    def peek(self, value: str) -> bool:
        return not self.at_end() and self.text[self.pos] == value
