from __future__ import annotations

import json
from pathlib import Path

import typer

from .api import inspect_file, pack_directory, roundtrip_check, unpack_file
from .container import ContainerError
from .diffing import diff_paths, render_diff_report
from .form_ast import build_form_file, parse_form_source, write_ast_json
from .models import FormRenderMode
from .semantic_form import build_semantic_file

app = typer.Typer(help="Inspect, unpack, and repack 1C Form.bin containers.")


@app.command("inspect")
def inspect_command(
    path: Path,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON."),
) -> None:
    """Inspect container records."""
    info = inspect_file(path)
    if as_json:
        typer.echo(json.dumps(info, ensure_ascii=False, indent=2))
        return

    typer.echo(f"path: {info['path']}")
    typer.echo(f"records: {info['record_count']}")
    for record in info["records"]:
        typer.echo(
            "  "
            f"#{record['index']} "
            f"off={record['header_start']} "
            f"size={record['field2']} "
            f"kind={record['kind']} "
            f"label={record['label']} "
            f"pointer={record['pointer_record_index']}"
        )


@app.command("unpack")
def unpack_command(path: Path, output: Path = typer.Option(..., "-o", "--output")) -> None:
    """Unpack a Form.bin container into a directory."""
    manifest = unpack_file(path, output)
    typer.echo(f"unpacked {manifest.record_count} records to {output}")


@app.command("pack")
def pack_command(directory: Path, output: Path = typer.Option(..., "-o", "--output")) -> None:
    """Pack an unpacked directory back into Form.bin."""
    pack_directory(directory, output)
    typer.echo(f"packed container to {output}")


@app.command("roundtrip-check")
def roundtrip_command(path: Path) -> None:
    """Verify byte-identical unpack/pack round-trip."""
    ok = roundtrip_check(path)
    if not ok:
        raise typer.Exit(code=1)
    typer.echo("roundtrip ok")


@app.command("diff")
def diff_command(
    left: Path,
    right: Path,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON."),
    form_mode: FormRenderMode = typer.Option(
        FormRenderMode.RAW,
        "--form-mode",
        help="Render form payloads as raw brace text or experimental AST JSON.",
    ),
    context: int = typer.Option(3, "--context", min=0, help="Unified diff context lines."),
) -> None:
    """Compare two Form.bin files or two unpack directories."""
    report = diff_paths(left, right, form_mode=form_mode, context=context)
    if as_json:
        typer.echo(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        typer.echo(render_diff_report(report), nl=False)
    if not report["identical"]:
        raise typer.Exit(code=1)


@app.command("parse-form")
def parse_form_command(path: Path, output: Path = typer.Option(..., "-o", "--output")) -> None:
    """Parse form.raw, an unpack dir, or Form.bin into experimental AST JSON."""
    node = parse_form_source(path)
    write_ast_json(output, node)
    typer.echo(f"wrote AST to {output}")


@app.command("build-form")
def build_form_command(path: Path, output: Path = typer.Option(..., "-o", "--output")) -> None:
    """Build form.raw text from experimental AST JSON."""
    build_form_file(path, output)
    typer.echo(f"wrote form.raw to {output}")


@app.command("semantic-form")
def semantic_form_command(path: Path, output: Path = typer.Option(..., "-o", "--output")) -> None:
    """Build experimental semantic JSON from form.raw, an unpack dir, or Form.bin."""
    build_semantic_file(path, output)
    typer.echo(f"wrote semantic model to {output}")


def main() -> None:
    try:
        app()
    except ContainerError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2) from exc


if __name__ == "__main__":
    main()
