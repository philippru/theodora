"""L3 business-logic tests — cascading criticality (B_06.01)."""
from __future__ import annotations

import csv
from pathlib import Path

from theodora.validation.engine import validate_package


def _pkg(tmp_path: Path, tables: dict[str, tuple[list[str], list[list[str]]]]) -> Path:
    reports = tmp_path / "reports"
    reports.mkdir()
    with (reports / "FilingIndicators.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["templateID", "reported"])
        for tid in tables:
            w.writerow([tid, "true"])
    for tid, (header, rows) in tables.items():
        with (reports / f"{tid.lower()}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
    return tmp_path


# B_06.01: c0010 function id · c0050 criticality · c0060 reasons · c0070 date ·
# c0080 RTO · c0090 RPO · c0100 impact. eba_BT:x28 = "Yes" (critical).

def test_critical_function_missing_required_is_caught(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_06.01": (
            ["c0010", "c0050", "c0060", "c0070", "c0080", "c0090", "c0100"],
            [["F1", "eba_BT:x28", "", "", "", "", ""]],  # critical but everything empty
        ),
    })
    assert any(f.rule_id == "THEO-L3-CRIT-001" for f in validate_package(pkg))


def test_non_critical_function_has_no_l3(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_06.01": (["c0010", "c0050"], [["F1", "eba_BT:x29"]]),  # "No" -> not critical
    })
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L3-CRIT-001" not in ids


def test_critical_complete_function_is_clean(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_06.01": (
            ["c0010", "c0050", "c0060", "c0070", "c0080", "c0090", "c0100"],
            [["F1", "eba_BT:x28", "reason", "2024-01-01", "10", "5", "eba_ZZ:x791"]],
        ),
    })
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L3-CRIT-001" not in ids


def test_cascade_reliance_required_when_function_critical(tmp_path: Path) -> None:
    # B_02.02: c0050 function id (FK) · c0180 level of reliance.
    pkg = _pkg(tmp_path, {
        "B_06.01": (
            ["c0010", "c0050", "c0060", "c0070", "c0080", "c0090", "c0100"],
            [["F1", "eba_BT:x28", "reason", "2024-01-01", "10", "5", "eba_ZZ:x791"]],
        ),
        "B_02.02": (["c0050", "c0180"], [["F1", ""]]),  # supports critical F1, no reliance
    })
    assert any(f.rule_id == "THEO-L3-CRIT-002" for f in validate_package(pkg))
