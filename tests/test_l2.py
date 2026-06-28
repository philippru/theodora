"""L2 referential-integrity tests (FK into the B_02.01 / B_05.01 / B_06.01 masters)."""
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


def test_consistent_arrangement_fk_is_clean(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_02.01": (["c0010"], [["CA-1"], ["CA-2"]]),
        "B_04.01": (["c0010"], [["CA-1"]]),  # references an existing arrangement
    })
    ids = {f.rule_id for f in validate_package(pkg)}
    assert "THEO-L2-FK-ARRANGEMENT" not in ids


def test_orphan_arrangement_fk_is_caught(tmp_path: Path) -> None:
    pkg = _pkg(tmp_path, {
        "B_02.01": (["c0010"], [["CA-1"]]),
        "B_04.01": (["c0010"], [["CA-999"]]),  # orphan reference
    })
    assert any(f.rule_id == "THEO-L2-FK-ARRANGEMENT" for f in validate_package(pkg))


def test_orphan_tpp_fk_is_caught(tmp_path: Path) -> None:
    # B_05.01 c0010 = ICT TPP id (master); B_03.02 c0020 = same label (FK).
    pkg = _pkg(tmp_path, {
        "B_05.01": (["c0010"], [["TPP-1"]]),
        "B_03.02": (["c0010", "c0020"], [["CA-1", "TPP-X"]]),  # orphan TPP
    })
    assert any(f.rule_id == "THEO-L2-FK-TPP" for f in validate_package(pkg))
