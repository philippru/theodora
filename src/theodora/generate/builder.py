"""Deterministic synthetic RoI builder.

Produces a referentially-consistent, *valid* set of template rows (round-trips through
the validation engine to zero findings). `--inject-violation` deliberately breaks one rule
to produce a negative fixture. Deterministic: no randomness, no clock.
"""
from __future__ import annotations

from theodora.domain.templates import TEMPLATES
from theodora.generate._samples import SAMPLES
from theodora.validation.engine import _alias_labels

# Stable synthetic keys so all foreign keys resolve.
_CA = "CA-1"      # contractual arrangement
_TPP = "TPP-1"    # ICT third-party service provider
_FUNC = "FUNC-1"  # function

# Label -> forced value for keys/FKs/criticality (so foreign keys resolve and criticality
# stays "No"). All OTHER columns are filled from valid golden samples (see build_tables) so
# every row carries real facts — required for XBRL-dimensional validity (no unmappedCellValue).
_BY_LABEL = {
    "contractual arrangement reference number": _CA,
    "identification code of ict third-party service provider": _TPP,
    "function identifier": _FUNC,
    "criticality or importance assessment": "eba_BT:x29",  # "No" -> not critical
}


def package_name(entity_lei: str, reference_date: str) -> str:
    # EBA convention: {LEI}.CON_{cc}_{module}_{framework}_{refdate}_{timestamp}.
    # Timestamp is a fixed synthetic value for determinism.
    return f"{entity_lei}.CON_XX_DORA010100_DORA_{reference_date}_00000000000000000"


def _value(norm_label: str, entity_lei: str) -> str:
    if "lei" in norm_label.split():  # any LEI field -> a valid-format 20-char LEI
        return entity_lei
    return _BY_LABEL.get(norm_label, "")


def build_tables(entity_lei: str, reference_date: str, inject: str | None = None) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {tid: [] for tid in TEMPLATES}
    for tid in TEMPLATES:
        sample = SAMPLES.get(tid, {})
        row = {
            alias: (_value(lbl, entity_lei) or sample.get(alias, ""))
            for alias, lbl in _alias_labels(tid).items()
        }
        if any(row.values()):
            tables[tid] = [row]

    if inject == "THEO-L2-FK-ARRANGEMENT":
        _set(tables, "B_04.01", "contractual arrangement reference number", "CA-MISSING")
    elif inject == "THEO-L1-ENUM-001":
        _set(tables, "B_06.01", "criticality or importance assessment", "eba_BT:x999")  # invalid member
    elif inject == "THEO-L3-CRIT-001":
        _set(tables, "B_06.01", "criticality or importance assessment", "eba_BT:x28")  # critical
        for lbl in (  # ... but blank the now-required fields
            "reasons for criticality or importance",
            "date of last assessment of criticality or importance",
            "recovery time objective of function",
            "recovery point objective of function",
            "impact of discontinuing function",
        ):
            _set(tables, "B_06.01", lbl, "")
    return tables


def _set(tables: dict[str, list[dict]], tid: str, norm_label: str, value: str) -> None:
    for alias, lbl in _alias_labels(tid).items():
        if lbl == norm_label and tables.get(tid):
            tables[tid][0][alias] = value
