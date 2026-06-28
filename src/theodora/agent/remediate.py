"""Remediation loop — LLM proposes a fix per validation finding; Theodora re-validates and
keeps only what passes. Pure logic: the proposer is injected (real LLM or a fake for tests).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from theodora.agent.llm import Proposer
from theodora.domain._field_dims import FIELD_DIMS
from theodora.domain.enums import DIMENSIONS
from theodora.validation.engine import Finding, validate_package

# Cell-level findings an LLM can plausibly fix by proposing a new value.
_FIXABLE = {"THEO-L1-ENUM-001", "THEO-L1-ENUM-002", "THEO-L1-TYPE-001", "THEO-L1-REQ-001"}


@dataclass
class FixResult:
    changes: list[tuple[str, int, str, str, str]] = field(default_factory=list)  # tid,row,alias,old,new
    remaining: list[Finding] = field(default_factory=list)


def _reports(pkg: Path) -> Path:
    return pkg / "reports" if (pkg / "reports").is_dir() else pkg


def _prompt(f: Finding, tid: str) -> str:
    dim = FIELD_DIMS.get(tid, {}).get(f.field or "")
    if dim and dim in DIMENSIONS:
        sample = sorted(DIMENSIONS[dim])[:8]
        hint = f"It must be a valid {dim} code, e.g. one of {sample}."
    elif f.rule_id == "THEO-L1-TYPE-001":
        hint = "It must match the field's type (e.g. a date as YYYY-MM-DD, or a number)."
    elif f.rule_id == "THEO-L1-REQ-001":
        hint = "It must be a non-empty identifier."
    else:
        hint = "Provide a valid value."
    return (f"DORA RoI template {tid}, column {f.field}. Validation error: {f.message}. {hint} "
            f"Return ONLY the corrected value.")


def remediate(pkg: Path, proposer: Proposer, *, max_rounds: int = 3) -> FixResult:
    pkg = Path(pkg)
    reports = _reports(pkg)
    result = FixResult()
    for _ in range(max_rounds):
        fixable = [
            f for f in validate_package(pkg)
            if f.rule_id in _FIXABLE and f.field and f.row
        ]
        if not fixable:
            break
        by_template: dict[str, list[Finding]] = {}
        for f in fixable:
            by_template.setdefault(f.template, []).append(f)
        changed = False
        for tid, findings in by_template.items():
            csv_path = reports / f"{tid.lower()}.csv"
            if not csv_path.is_file():
                continue
            with csv_path.open(encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                cols = reader.fieldnames or []
                rows = list(reader)
            for f in findings:
                idx = (f.row or 0) - 1
                if 0 <= idx < len(rows) and f.field in rows[idx]:
                    old = rows[idx].get(f.field) or ""
                    new = proposer(_prompt(f, tid)).strip()
                    if new and new != old:
                        rows[idx][f.field] = new
                        result.changes.append((tid, f.row or 0, f.field or "", old, new))
                        changed = True
            with csv_path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=cols)
                writer.writeheader()
                writer.writerows(rows)
        if not changed:
            break
    result.remaining = validate_package(pkg)
    return result
