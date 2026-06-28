"""Theodora CLI — `roi` command.

Thin command layer only (hexagonal: the CLI holds no business logic).
Real logic lives in theodora.domain / .validation / .generate / .io.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="roi",
    help="Theodora — the open DORA Register of Information (RoI) toolkit.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def validate(
    package: str = typer.Argument(..., help="Path to a RoI package directory."),
) -> None:
    """Validate a RoI package (L1 structure/types/enums + L2 referential integrity)."""
    from pathlib import Path

    from theodora.validation.engine import validate_package

    findings = validate_package(Path(package))
    if not findings:
        typer.echo("OK — no findings.")
        raise typer.Exit(code=0)
    for f in findings:
        loc = f" row={f.row}" if f.row else ""
        fld = f" {f.field}" if f.field else ""
        typer.echo(f"[{f.severity}] {f.rule_id} {f.template}{loc}{fld}: {f.message}")
    blocking = sum(1 for f in findings if f.severity in ("BLOCKER", "ERROR"))
    typer.echo(f"\n{len(findings)} finding(s), {blocking} blocking.")
    raise typer.Exit(code=1 if blocking else 0)


@app.command()
def generate(
    entity: str = typer.Option(..., "--entity", "-e", help="20-char LEI of the reporting financial entity."),
    output: str = typer.Option("./roi-out", "--output", "-o", help="Output directory."),
    reference_date: str = typer.Option("2024-12-31", "--reference-date", help="Reporting reference date (YYYY-MM-DD)."),
    inject_violation: str | None = typer.Option(
        None, "--inject-violation", help="Rule-ID to deliberately violate (for fixtures)."
    ),
) -> None:
    """Generate a deterministic, valid RoI package in xBRL-CSV format."""
    from pathlib import Path

    from theodora.generate.builder import build_tables, package_name
    from theodora.io.writer import write_package

    tables = build_tables(entity, reference_date, inject_violation)
    pkg = write_package(
        Path(output), package_name(entity, reference_date), tables, entity, reference_date,
        skip_report_json=(inject_violation == "THEO-L4-PKG-001"),
    )
    typer.echo(f"wrote {pkg}")
    raise typer.Exit(code=0)


@app.command()
def template(
    output: str = typer.Option("roi-template.xlsx", "--output", "-o", help="Output .xlsx path."),
) -> None:
    """Write a blank Excel template (one sheet per RoI template) for an institution to fill in."""
    from pathlib import Path

    from theodora.io.excel import write_workbook

    write_workbook(Path(output), {})
    typer.echo(f"wrote {output}")
    raise typer.Exit(code=0)


@app.command()
def convert(
    input: str = typer.Option(..., "--input", "-i", help="Filled source Excel workbook (.xlsx)."),
    entity: str = typer.Option(..., "--entity", "-e", help="20-char LEI of the reporting entity."),
    output: str = typer.Option("./roi-out", "--output", "-o", help="Output directory."),
    reference_date: str = typer.Option("2024-12-31", "--reference-date", help="Reference date (YYYY-MM-DD)."),
    validate_after: bool = typer.Option(False, "--validate", help="Validate the generated package."),
) -> None:
    """Convert a filled Excel workbook into an xBRL-CSV package (Excel -> xBRL-CSV)."""
    from pathlib import Path

    from theodora.generate.builder import package_name
    from theodora.io.excel import read_workbook
    from theodora.io.writer import write_package

    tables = read_workbook(Path(input))
    pkg = write_package(Path(output), package_name(entity, reference_date), tables, entity, reference_date)
    typer.echo(f"wrote {pkg}")
    if validate_after:
        from theodora.validation.engine import validate_package

        findings = validate_package(pkg)
        if not findings:
            typer.echo("OK — no findings.")
        else:
            for f in findings:
                typer.echo(f"[{f.severity}] {f.rule_id} {f.template} row={f.row} {f.field}: {f.message}")
            typer.echo(f"\n{len(findings)} finding(s)")
            raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@app.command()
def crosscheck(
    package: str = typer.Option(..., "--package", "-p", help="Generated RoI package directory."),
    taxonomy: str = typer.Option(..., "--taxonomy", "-t", help="EBA taxonomy package zip (container or single) or a folder of package zips."),
    offline: bool = typer.Option(False, "--offline", help="Offline mode (needs eurofiling base schemas already cached)."),
    structural_only: bool = typer.Option(False, "--structural-only", help="Skip the official EBA formula rules (fast, offline once cached)."),
) -> None:
    """Validate a package against the OFFICIAL EBA taxonomy + rule set via Arelle (optional extra)."""
    from pathlib import Path

    from theodora.validation.arelle_check import arelle_available, crosscheck as run_crosscheck

    if not arelle_available():
        typer.echo("Arelle not installed. Install with:  uv sync --extra arelle")
        raise typer.Exit(code=2)
    code, findings = run_crosscheck(Path(package), Path(taxonomy), offline=offline, structural_only=structural_only)
    if code == 0:
        scope = "structure" if structural_only else "structure + the full official EBA rule set"
        typer.echo(f"OK — Arelle: conformant against the official EBA taxonomy ({scope}).")
    else:
        for f in findings[:50]:
            typer.echo(f)
        typer.echo(f"\n{len(findings)} Arelle finding(s).")
    raise typer.Exit(code=code)


@app.command()
def fix(
    package: str = typer.Option(..., "--package", "-p", help="RoI package directory to remediate."),
    output: str | None = typer.Option(None, "--output", "-o", help="Write the fixed copy here (default: in place)."),
    model: str | None = typer.Option(None, "--model", "-m", help="LiteLLM model id (e.g. anthropic/claude-sonnet-4-6, openai/gpt-4o-mini, gemini/…, bedrock/…, ollama/…). Default: $THEODORA_LLM_MODEL."),
) -> None:
    """LLM proposes fixes for validation findings — kept only if re-validation passes (Theodora decides)."""
    import shutil
    from pathlib import Path

    from theodora.agent.llm import available, litellm_proposer
    from theodora.agent.remediate import remediate

    if not available():
        typer.echo("LLM extra not installed. Install with:  uv sync --extra agent")
        raise typer.Exit(code=2)
    target = Path(package)
    if output:
        target = Path(output)
        shutil.copytree(Path(package), target, dirs_exist_ok=True)
    result = remediate(target, litellm_proposer(model))
    for tid, row, alias, old, new in result.changes:
        typer.echo(f"fixed {tid} row={row} {alias}: '{old}' -> '{new}'")
    typer.echo(f"\n{len(result.changes)} change(s) applied; {len(result.remaining)} finding(s) remaining.")
    raise typer.Exit(code=0 if not result.remaining else 1)


if __name__ == "__main__":
    app()
