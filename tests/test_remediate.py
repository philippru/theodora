"""Remediation-loop tests — uses a fake proposer (no LLM, no network)."""
from __future__ import annotations

from pathlib import Path

from theodora.agent.remediate import remediate
from theodora.generate.builder import build_tables, package_name
from theodora.io.writer import write_package
from theodora.validation.engine import validate_package

_LEI, _DATE = "DUMMYLEI123456789012", "2024-12-31"


def _pkg(tmp_path: Path, inject: str | None = None) -> Path:
    return write_package(tmp_path, package_name(_LEI, _DATE), build_tables(_LEI, _DATE, inject), _LEI, _DATE)


def test_valid_proposal_is_accepted(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, "THEO-L1-ENUM-001")  # criticality set to an invalid eba_BT member
    assert any(f.rule_id == "THEO-L1-ENUM-001" for f in validate_package(pkg))
    result = remediate(pkg, lambda _prompt: "eba_BT:x29")  # fake LLM proposes a valid value
    assert result.changes
    assert not any(f.rule_id == "THEO-L1-ENUM-001" for f in result.remaining)


def test_bad_proposal_is_rejected_by_revalidation(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, "THEO-L1-ENUM-001")
    # fake LLM proposes another invalid value -> finding must persist (Theodora decides).
    result = remediate(pkg, lambda _prompt: "eba_BT:xZZZ")
    assert any(f.rule_id == "THEO-L1-ENUM-001" for f in result.remaining)
