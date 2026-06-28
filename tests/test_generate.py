"""`roi generate` tests — round-trip validity, determinism, and inject-violation fixtures."""
from __future__ import annotations

from pathlib import Path

from theodora.generate.builder import build_tables, package_name
from theodora.io.writer import write_package
from theodora.validation.engine import validate_package

_LEI = "DUMMYLEI123456789012"
_DATE = "2024-12-31"


def _gen(out_root: Path, inject: str | None = None, *, skip_report_json: bool = False) -> Path:
    tables = build_tables(_LEI, _DATE, inject)
    return write_package(out_root, package_name(_LEI, _DATE), tables, _LEI, _DATE,
                         skip_report_json=skip_report_json)


def test_roundtrip_generated_package_is_valid(tmp_path: Path) -> None:
    # The headline property: what we generate, we validate clean.
    assert validate_package(_gen(tmp_path)) == []


def test_generation_is_deterministic(tmp_path: Path) -> None:
    p1 = _gen(tmp_path / "a")
    p2 = _gen(tmp_path / "b")
    b1 = {p.relative_to(p1): p.read_bytes() for p in p1.rglob("*") if p.is_file()}
    b2 = {p.relative_to(p2): p.read_bytes() for p in p2.rglob("*") if p.is_file()}
    assert b1 == b2


def test_inject_arrangement_fk(tmp_path: Path) -> None:
    ids = {f.rule_id for f in validate_package(_gen(tmp_path, "THEO-L2-FK-ARRANGEMENT"))}
    assert "THEO-L2-FK-ARRANGEMENT" in ids


def test_inject_enum(tmp_path: Path) -> None:
    ids = {f.rule_id for f in validate_package(_gen(tmp_path, "THEO-L1-ENUM-001"))}
    assert "THEO-L1-ENUM-001" in ids


def test_inject_criticality(tmp_path: Path) -> None:
    ids = {f.rule_id for f in validate_package(_gen(tmp_path, "THEO-L3-CRIT-001"))}
    assert "THEO-L3-CRIT-001" in ids


def test_inject_filing_rule(tmp_path: Path) -> None:
    ids = {f.rule_id for f in validate_package(_gen(tmp_path, "THEO-L4-PKG-001", skip_report_json=True))}
    assert "THEO-L4-PKG-001" in ids
