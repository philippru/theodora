"""Arelle cross-check test — opt-in (slow, needs internet + the EBA taxonomy in spec/).

Run with:  THEODORA_ARELLE_TEST=1 uv run --extra arelle pytest tests/test_crosscheck.py
Skipped otherwise (so the normal suite stays fast and CI-portable).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from theodora.validation.arelle_check import arelle_available

_TAXO = Path("spec/taxonomy/taxo_package_4.0_errata5.zip")
_ENABLED = os.environ.get("THEODORA_ARELLE_TEST") == "1"

pytestmark = pytest.mark.skipif(
    not (_ENABLED and arelle_available() and _TAXO.exists()),
    reason="set THEODORA_ARELLE_TEST=1, install [arelle], and provide spec/ taxonomy",
)


def test_generated_package_is_xbrl_conformant(tmp_path: Path) -> None:
    from theodora.generate.builder import build_tables, package_name
    from theodora.io.writer import write_package
    from theodora.validation.arelle_check import crosscheck

    lei, date = "DUMMYLEI123456789012", "2024-12-31"
    pkg = write_package(tmp_path, package_name(lei, date), build_tables(lei, date), lei, date)
    code, findings = crosscheck(pkg, _TAXO)
    assert code == 0, findings
