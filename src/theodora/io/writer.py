"""xBRL-CSV report-package writer.

Serialises template rows into the EBA report-package layout (matching the golden
reference): META-INF/reportPackage.json + reports/{report.json, FilingIndicators.csv,
parameters.csv, <template>.csv}. Deterministic: same input -> byte-identical output.
"""
from __future__ import annotations

import csv
from pathlib import Path

from theodora.domain.templates import TEMPLATES

_REPORT_JSON = (
    '{\n'
    '    "documentInfo": {\n'
    '        "documentType": "https://xbrl.org/2021/xbrl-csv",\n'
    '        "extends": [\n'
    '            "http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/dora/4.0/mod/dora.json"\n'
    '        ]\n'
    '    }\n'
    '}\n'
)
_REPORT_PACKAGE_JSON = (
    '{\n'
    '    "documentInfo": {\n'
    '        "documentType": "https://xbrl.org/report-package/2023"\n'
    '    }\n'
    '}\n'
)


def write_package(
    out_root: Path,
    package_name: str,
    tables: dict[str, list[dict]],
    entity_lei: str,
    reference_date: str,
    *,
    skip_report_json: bool = False,
) -> Path:
    pkg = Path(out_root) / package_name
    reports = pkg / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (pkg / "META-INF").mkdir(exist_ok=True)
    (pkg / "META-INF" / "reportPackage.json").write_text(_REPORT_PACKAGE_JSON, encoding="utf-8")
    if not skip_report_json:
        (reports / "report.json").write_text(_REPORT_JSON, encoding="utf-8")

    with (reports / "FilingIndicators.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["templateID", "reported"])
        for tid in TEMPLATES:
            w.writerow([tid, "true"])

    (reports / "parameters.csv").write_text(
        "name,value\n"
        f"entityID,rs:{entity_lei}.CON\n"
        f"refPeriod,{reference_date}\n"
        "baseCurrency,iso4217:EUR\n"
        "decimalsInteger,0\n"
        "decimalsMonetary,-3\n",
        encoding="utf-8",
    )

    for tid, model in TEMPLATES.items():
        headers = [fi.alias for fi in model.model_fields.values() if fi.alias]
        with (reports / f"{tid.lower()}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(headers)
            for row in tables.get(tid, []):
                w.writerow([row.get(h, "") for h in headers])

    return pkg
