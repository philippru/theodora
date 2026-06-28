"""Validation engine — L1 (syntactic) + L2 (referential integrity).

L1 = structure + types + enum membership. L2 = foreign keys across templates.
(L3 business logic, L4 filing-rule conformance come later.) Every finding carries a
stable rule-ID.

No fabrication: types from the generated Pydantic models (domain/templates.py), enum
members from the EBA possible-values list (domain/enums.py), and the L2 foreign keys from
the EBA field labels + the DORA data model (B_02.01 = contractual-arrangements master,
B_05.01 = ICT third-party provider master, B_06.01 = functions master). Binding each L2
check to the exact EBA rule code (e23…/v8…) is a later refinement.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from theodora.domain._field_dims import FIELD_DIMS
from theodora.domain.enums import DIMENSIONS, dimension_of
from theodora.domain.templates import TEMPLATES

# EBA cross-reference (category-level; exact per-rule binding lives in the taxonomy formula
# linkbase under val/, out of scope here):
#   L1 enum/required ↔ EBA "Existence" rules e23674_e…e23792_e + DPM dimensional validation
#   L2 referential   ↔ EBA "Existence" / cross-table rules
#   L3 business      ↔ EBA "User defined" business rules (v8…)


@dataclass
class Finding:
    rule_id: str
    severity: str  # BLOCKER | ERROR | WARNING
    template: str
    row: int | None
    field: str | None
    message: str


# L2 foreign keys: normalised field label -> (master template, rule-id).
# The master's primary key is the field carrying the SAME label.
FK_TARGETS: dict[str, tuple[str, str]] = {
    "contractual arrangement reference number": ("B_02.01", "THEO-L2-FK-ARRANGEMENT"),
    "identification code of ict third-party service provider": ("B_05.01", "THEO-L2-FK-TPP"),
    "function identifier": ("B_06.01", "THEO-L2-FK-FUNCTION"),
}

# L3: the "Yes" code for B_06.01 'Criticality or importance assessment' (dimension BT),
# per the EBA Possible Values sheet B0601 (DPM 4.0; see spec/FROZEN.md). A function row with
# this value is critical/important and triggers the conditional-mandatory cascade.
CRITICAL_ASSESSMENT = "eba_BT:x28"


def _norm(s: str) -> str:
    """Normalise a label for matching: lowercase, drop ' the ', collapse whitespace."""
    return " ".join((s or "").lower().replace(" the ", " ").split())


def _read_csv(p: Path) -> tuple[list[str], list[dict]]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return list(reader.fieldnames or []), rows  # type: ignore[return-value]


def _alias_labels(tid: str) -> dict[str, str]:
    """alias -> normalised label for a template's model fields."""
    model = TEMPLATES.get(tid)
    if not model:
        return {}
    return {fi.alias: _norm(fi.description or "") for fi in model.model_fields.values() if fi.alias}


def _check_l1(tid: str, cols: list[str], rows: list[dict], findings: list[Finding]) -> None:
    model = TEMPLATES.get(tid)
    if model is None:
        findings.append(Finding("THEO-L1-MODEL-001", "WARNING", tid, None, None, "no model for template id"))
        return
    aliases = {fi.alias for fi in model.model_fields.values() if fi.alias}
    bound = FIELD_DIMS.get(tid, {})  # column -> expected xBRL dimension
    has_key = "c0010" in aliases
    for c in cols:
        if c not in aliases:
            findings.append(Finding("THEO-L1-COL-001", "ERROR", tid, None, c, f"unknown column '{c}' for {tid}"))
    for i, row in enumerate(rows, start=1):
        clean = {k: v for k, v in row.items() if (v or "").strip() != ""}  # empty cell == absent
        if has_key and not (row.get("c0010") or "").strip():
            findings.append(Finding("THEO-L1-REQ-001", "ERROR", tid, i, "c0010", "primary key (c0010) is empty"))
        try:
            model.model_validate(clean)
        except ValidationError as exc:
            for err in exc.errors():
                loc = err.get("loc") or ("?",)
                findings.append(Finding("THEO-L1-TYPE-001", "ERROR", tid, i, str(loc[0]), err.get("msg", "type error")))
        for c, v in row.items():
            val = (v or "").strip()
            if not val:
                continue
            dim = dimension_of(val)
            expected = bound.get(c)
            if expected and dim and dim != expected:
                findings.append(Finding("THEO-L1-ENUM-002", "ERROR", tid, i, c,
                                        f"value '{val}' uses dimension {dim}, but column expects {expected}"))
                continue
            check_dim = expected or dim
            if check_dim:
                members = DIMENSIONS.get(check_dim)
                if members is not None and val not in members:
                    findings.append(Finding("THEO-L1-ENUM-001", "ERROR", tid, i, c,
                                            f"value '{val}' is not a valid {check_dim} member"))


def _check_l2(reports_data: dict[str, tuple[list[str], list[dict]]], findings: list[Finding]) -> None:
    # Build master key sets: master template -> set of primary-key values.
    master_keys: dict[str, set[str]] = {}
    for canon, (master_tid, _rule) in FK_TARGETS.items():
        if master_tid not in reports_data:
            continue
        pk_alias = next((a for a, lbl in _alias_labels(master_tid).items() if lbl == canon), None)
        if not pk_alias:
            continue
        _, rows = reports_data[master_tid]
        master_keys[master_tid] = {(r.get(pk_alias) or "").strip() for r in rows if (r.get(pk_alias) or "").strip()}

    for tid, (_cols, rows) in reports_data.items():
        labels = _alias_labels(tid)
        for canon, (master_tid, rule_id) in FK_TARGETS.items():
            if tid == master_tid or master_tid not in master_keys:
                continue
            for alias, lbl in labels.items():
                if lbl != canon:
                    continue
                for i, row in enumerate(rows, start=1):
                    v = (row.get(alias) or "").strip()
                    if v and v not in master_keys[master_tid]:
                        findings.append(
                            Finding(rule_id, "ERROR", tid, i, alias,
                                    f"{alias}='{v}' not found in {master_tid} (referential integrity)")
                        )


def _check_l3(reports_data: dict[str, tuple[list[str], list[dict]]], findings: list[Finding]) -> None:
    """L3 business logic — cascading criticality (B_06.01).

    Derived from the field labels + the DORA criticality logic; binding to the exact EBA
    rule codes (v8…) is a later refinement.
    """
    b6 = reports_data.get("B_06.01")
    if not b6:
        return
    lbl6 = _alias_labels("B_06.01")
    crit_alias = next((a for a, lbl in lbl6.items() if lbl == "criticality or importance assessment"), None)
    fid_alias6 = next((a for a, lbl in lbl6.items() if lbl == "function identifier"), None)
    if not crit_alias:
        return
    by_label6 = {lbl: a for a, lbl in lbl6.items()}
    required_when_critical = [
        "reasons for criticality or importance",
        "date of last assessment of criticality or importance",
        "recovery time objective of function",
        "recovery point objective of function",
        "impact of discontinuing function",
    ]
    _, rows6 = b6
    critical_fids: set[str] = set()
    for i, row in enumerate(rows6, start=1):
        if (row.get(crit_alias) or "").strip() != CRITICAL_ASSESSMENT:
            continue
        if fid_alias6 and (row.get(fid_alias6) or "").strip():
            critical_fids.add((row.get(fid_alias6) or "").strip())
        for lab in required_when_critical:
            a = by_label6.get(lab)
            if a and not (row.get(a) or "").strip():
                findings.append(Finding("THEO-L3-CRIT-001", "ERROR", "B_06.01", i, a,
                                        f"function is critical/important but '{lab}' is empty"))

    b2 = reports_data.get("B_02.02")
    if not (b2 and critical_fids):
        return
    lbl2 = _alias_labels("B_02.02")
    fid_alias2 = next((a for a, lbl in lbl2.items() if lbl == "function identifier"), None)
    rel_alias = next((a for a, lbl in lbl2.items() if lbl.startswith("level of reliance")), None)
    if not (fid_alias2 and rel_alias):
        return
    _, rows2 = b2
    for i, row in enumerate(rows2, start=1):
        fid = (row.get(fid_alias2) or "").strip()
        if fid in critical_fids and not (row.get(rel_alias) or "").strip():
            findings.append(Finding("THEO-L3-CRIT-002", "ERROR", "B_02.02", i, rel_alias,
                                    f"arrangement supports critical function '{fid}' but '{rel_alias}' (level of reliance) is empty"))


def _check_l4(pkg: Path, findings: list[Finding]) -> None:
    """L4 filing-rule conformance — package structure.

    Grounded in the EBA golden reference package + Filing Rules v5.5; binding to exact
    FR v5.5 rule numbers is a later refinement.
    """
    has_wrapper = (pkg / "reports").is_dir()
    reports = pkg / "reports" if has_wrapper else pkg

    rj = reports / "report.json"
    if not rj.is_file():
        findings.append(Finding("THEO-L4-PKG-001", "ERROR", "-", None, None, "reports/report.json missing"))
    else:
        try:
            di = json.loads(rj.read_text(encoding="utf-8")).get("documentInfo", {})
            if di.get("documentType") != "https://xbrl.org/2021/xbrl-csv":
                findings.append(Finding("THEO-L4-PKG-002", "ERROR", "-", None, "report.json",
                                        f"unexpected documentType {di.get('documentType')!r}"))
            if "dora" not in " ".join(di.get("extends", [])).lower():
                findings.append(Finding("THEO-L4-PKG-003", "ERROR", "-", None, "report.json",
                                        "report does not extend the DORA module"))
        except (ValueError, OSError) as exc:
            findings.append(Finding("THEO-L4-PKG-002", "ERROR", "-", None, "report.json", f"invalid JSON: {exc}"))

    if has_wrapper and not (pkg / "META-INF" / "reportPackage.json").is_file():
        findings.append(Finding("THEO-L4-PKG-004", "ERROR", "-", None, None, "META-INF/reportPackage.json missing"))

    if not (reports / "FilingIndicators.csv").is_file():
        findings.append(Finding("THEO-L4-PKG-005", "ERROR", "-", None, None, "reports/FilingIndicators.csv missing"))

    aux = {"filingindicators.csv", "parameters.csv"}
    valid_csv = {f"{tid.lower()}.csv" for tid in TEMPLATES}
    for f in sorted(reports.glob("*.csv")):
        name = f.name.lower()
        if name not in aux and name not in valid_csv:
            findings.append(Finding("THEO-L4-NAME-001", "WARNING", "-", None, f.name,
                                    f"unexpected CSV filename '{f.name}' (not a known template)"))
        try:
            f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(Finding("THEO-L4-ENC-001", "ERROR", "-", None, f.name,
                                    "file is not valid UTF-8 (Filing Rules require UTF-8)"))

    if has_wrapper and not re.match(r"^[A-Z0-9]{20}\..*DORA.*_\d{4}-\d{2}-\d{2}_", pkg.name):
        findings.append(Finding("THEO-L4-NAME-002", "WARNING", "-", None, pkg.name,
                                "package folder name does not match the EBA convention (LEI.…_DORA…_refdate_timestamp)"))


def validate_package(pkg: Path) -> list[Finding]:
    """Run L1 + L2 checks over a RoI report package directory."""
    findings: list[Finding] = []
    reports = pkg / "reports" if (pkg / "reports").is_dir() else pkg

    fi = reports / "FilingIndicators.csv"
    reported: dict[str, bool] = {}
    if fi.is_file():
        _, rows = _read_csv(fi)
        for row in rows:
            tid = (row.get("templateID") or "").strip()
            if tid:
                reported[tid] = (row.get("reported") or "").strip().lower() == "true"
    else:
        findings.append(Finding("THEO-L1-STRUCT-000", "ERROR", "-", None, None, "FilingIndicators.csv missing"))

    reports_data: dict[str, tuple[list[str], list[dict]]] = {}
    for tid, is_reported in reported.items():
        if not is_reported:
            continue
        f = reports / f"{tid.lower()}.csv"
        if not f.is_file():
            findings.append(Finding("THEO-L1-STRUCT-001", "ERROR", tid, None, None, f"template reported but {f.name} missing"))
            continue
        reports_data[tid] = _read_csv(f)

    for tid, (cols, rows) in reports_data.items():
        _check_l1(tid, cols, rows, findings)
    _check_l2(reports_data, findings)
    _check_l3(reports_data, findings)
    _check_l4(pkg, findings)
    return findings
