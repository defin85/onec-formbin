from __future__ import annotations

import json
from pathlib import Path

import typer

from .api import inspect_file, pack_directory, roundtrip_check, unpack_file, write_inspect_json
from .container import ContainerError
from .diffing import diff_paths, render_diff_report
from .form_ast import build_form_file, parse_form_source, write_ast_json
from .models import FormRenderMode
from .semantic_form import apply_semantic_workspace, build_semantic_file

app = typer.Typer(help="Inspect, unpack, and repack 1C Form.bin containers.")


def format_os_error(exc: OSError) -> str:
    path = exc.filename or str(exc)
    if isinstance(exc, FileNotFoundError):
        return f"Path does not exist: {path}."
    if isinstance(exc, NotADirectoryError):
        return f"Expected an unpack directory, got file: {path}."
    if isinstance(exc, IsADirectoryError):
        return f"Expected a file path, got directory: {path}."
    if isinstance(exc, PermissionError):
        return f"Permission denied: {path}."
    return str(exc)


@app.command("inspect")
def inspect_command(
    path: Path,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON."),
    output: Path | None = typer.Option(None, "-o", "--output", help="Write JSON to a file."),
) -> None:
    """Inspect container records or an unpack workspace inspect snapshot."""
    info = inspect_file(path)
    if as_json:
        if output is not None:
            write_inspect_json(output, info)
            typer.echo(f"wrote inspect JSON to {output}")
            return
        typer.echo(json.dumps(info, ensure_ascii=False, indent=2))
        return
    if output is not None:
        raise typer.BadParameter("--output requires --json")

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
        help="Render form payloads as raw brace text, experimental AST JSON, or semantic slice JSON.",
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


@app.command("apply-semantic")
def apply_semantic_command(directory: Path) -> None:
    """Apply supported semantic workspace edits back to the unpacked form.raw."""
    apply_semantic_workspace(directory)
    typer.echo(f"applied semantic edits in {directory}")


def main() -> int:
    try:
        app()
        return 0
    except ContainerError as exc:
        typer.echo(f"error: {exc}", err=True)
        return 2
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError, PermissionError) as exc:
        typer.echo(f"error: {format_os_error(exc)}", err=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
