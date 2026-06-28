"""L4 filing-rule conformance tests — package structure."""
from __future__ import annotations

from pathlib import Path

from theodora.validation.engine import validate_package

_GOLDEN_NAME = "DUMMYLEI123456789012.CON_FR_DORA010100_DORA_2024-12-31_20241213174803429"
_REPORT_JSON = (
    '{"documentInfo":{"documentType":"https://xbrl.org/2021/xbrl-csv",'
    '"extends":["http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/dora/4.0/mod/dora.json"]}}'
)


def _full_pkg(tmp_path: Path, *, report_json: str = _REPORT_JSON, with_metainf: bool = True,
              extra_csv: str | None = None, name: str = _GOLDEN_NAME) -> Path:
    pkg = tmp_path / name
    reports = pkg / "reports"
    reports.mkdir(parents=True)
    if with_metainf:
        (pkg / "META-INF").mkdir()
        (pkg / "META-INF" / "reportPackage.json").write_text(
            '{"documentInfo":{"documentType":"https://xbrl.org/report-package/2023"}}', encoding="utf-8")
    (reports / "report.json").write_text(report_json, encoding="utf-8")
    (reports / "FilingIndicators.csv").write_text("templateID,reported\nB_01.01,true\n", encoding="utf-8")
    (reports / "b_01.01.csv").write_text("c0010\nLEI\n", encoding="utf-8")
    if extra_csv:
        (reports / extra_csv).write_text("x\n1\n", encoding="utf-8")
    return pkg


def test_valid_package_has_no_l4_findings(tmp_path: Path) -> None:
    ids = {f.rule_id for f in validate_package(_full_pkg(tmp_path))}
    assert not any(i.startswith("THEO-L4") for i in ids)


def test_missing_report_json_is_caught(tmp_path: Path) -> None:
    pkg = _full_pkg(tmp_path)
    (pkg / "reports" / "report.json").unlink()
    assert any(f.rule_id == "THEO-L4-PKG-001" for f in validate_package(pkg))


def test_wrong_document_type_is_caught(tmp_path: Path) -> None:
    pkg = _full_pkg(tmp_path, report_json='{"documentInfo":{"documentType":"wrong","extends":["dora.json"]}}')
    assert any(f.rule_id == "THEO-L4-PKG-002" for f in validate_package(pkg))


def test_missing_metainf_is_caught(tmp_path: Path) -> None:
    pkg = _full_pkg(tmp_path, with_metainf=False)
    assert any(f.rule_id == "THEO-L4-PKG-004" for f in validate_package(pkg))


def test_unexpected_csv_name_is_caught(tmp_path: Path) -> None:
    pkg = _full_pkg(tmp_path, extra_csv="b_77.77.csv")
    assert any(f.rule_id == "THEO-L4-NAME-001" for f in validate_package(pkg))
