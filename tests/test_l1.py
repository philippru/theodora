"""L1 validation-engine tests. Self-contained fixtures (no dependency on the gitignored spec)."""
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


def test_valid_minimal_has_no_l1_findings(tmp_path: Path) -> None:
    # Bare reports/ dir (no report.json/META-INF) -> L4 will flag package structure;
    # this test asserts the *L1* layer is clean on valid rows.
    pkg = _pkg(tmp_path, {
        "B_01.01": (
            ["c0010", "c0020", "c0030", "c0040", "c0050", "c0060"],
            [["LEI123", "Acme", "eba_GA:AL", "eba_CT:x12", "auth", "2024-12-31"]],
        ),
    })
    assert not [f for f in validate_package(pkg) if f.rule_id.startswith("THEO-L1")]


def test_bad_date_and_bad_enum_are_caught(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_01.01": (["c0010", "c0060"], [["LEI123", "not-a-date"]]),
        "B_02.01": (["c0010", "c0040"], [["ref-1", "eba_CU:ZZZ"]]),
    })
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L1-TYPE-001" in ids
    assert "THEO-L1-ENUM-001" in ids


def test_unknown_column_is_caught(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {"B_01.01": (["c9999"], [["x"]])})
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L1-COL-001" in ids


def test_missing_template_csv_is_caught(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    with (reports / "FilingIndicators.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["templateID", "reported"])
        w.writerow(["B_06.01", "true"])  # declared, but no b_06.01.csv written
    ids = {f.rule_id for f in validate_package(tmp_path)}
    assert "THEO-L1-STRUCT-001" in ids


def test_per_field_wrong_dimension_is_caught(tmp_path: Path) -> None:
    # B_01.01 c0030 expects a country (eba_GA); a currency value is wrong-dimension.
    pkg = _pkg(tmp_path, {"B_01.01": (["c0010", "c0030"], [["LEI", "eba_CU:ALL"]])})
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L1-ENUM-002" in ids


def test_missing_primary_key_is_caught(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {"B_02.01": (["c0010", "c0020"], [["", "eba_CO:x1"]])})
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L1-REQ-001" in ids
