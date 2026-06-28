"""Reconciliation / shadow-register detection — compare the ICT providers *reported* in the
register (B_05.01) against the providers *actually used* (an external inventory). Providers used
but not registered are **shadow providers** — a DORA completeness gap.

Deterministic core (exact code match + suffix-normalised name match) works without an LLM; an
optional proposer resolves fuzzy name variants (LLM proposes the match, the report flags it for
review — Theodora/​the human decides).
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from theodora.agent.llm import Proposer
from theodora.validation.engine import _alias_labels

_TPP = "B_05.01"
_CODE_LABEL = "identification code of ict third-party service provider"
_NAME_LABEL = "legal name of ict third-party service provider"
_SUFFIXES = {
    "gmbh", "ag", "sarl", "sa", "ltd", "limited", "inc", "llc", "plc", "bv", "nv",
    "se", "kg", "ohg", "srl", "spa", "oy", "ab", "as", "corp", "corporation", "co",
}


@dataclass
class Provider:
    code: str = ""
    name: str = ""

    def label(self) -> str:
        return self.name or self.code or "?"


@dataclass
class ReconResult:
    matched: list[tuple[Provider, Provider]] = field(default_factory=list)
    shadow: list[Provider] = field(default_factory=list)   # used but NOT registered — the DORA gap
    stale: list[Provider] = field(default_factory=list)    # registered but not in the actual list
    llm_proposed: list[tuple[Provider, Provider]] = field(default_factory=list)  # advisory, review


def _norm(s: str) -> str:
    toks = [t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t and t not in _SUFFIXES]
    return " ".join(toks)


def _col(tid: str, target: str) -> str | None:
    for alias, label in _alias_labels(tid).items():
        if " ".join(label.lower().split()) == target:
            return alias
    return None


def _reports(pkg: Path) -> Path:
    return pkg / "reports" if (pkg / "reports").is_dir() else pkg


def register_providers(pkg: Path) -> list[Provider]:
    """Read the ICT providers reported in B_05.01 of a package."""
    code_col, name_col = _col(_TPP, _CODE_LABEL), _col(_TPP, _NAME_LABEL)
    csv_path = _reports(Path(pkg)) / f"{_TPP.lower()}.csv"
    if not csv_path.is_file():
        return []
    out: list[Provider] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = (row.get(code_col or "", "") or "").strip()
            name = (row.get(name_col or "", "") or "").strip()
            if code or name:
                out.append(Provider(code=code, name=name))
    return out


def _same(a: Provider, b: Provider) -> bool:
    if a.code and b.code and a.code.strip().lower() == b.code.strip().lower():
        return True
    na = _norm(a.name)
    return bool(na) and na == _norm(b.name)


def _llm_pairs(register: list[Provider], actual: list[Provider], proposer: Proposer) -> list[tuple[int, int]]:
    reg = "\n".join(f"{i}: {p.label()}" for i, p in enumerate(register))
    act = "\n".join(f"{i}: {p.label()}" for i, p in enumerate(actual))
    prompt = (
        "Match ICT providers across two lists that refer to the SAME company (ignore legal-form "
        f"suffixes, abbreviations and language).\nREGISTER:\n{reg}\n\nACTUAL:\n{act}\n\n"
        "Return ONLY a JSON array of [register_index, actual_index] pairs for confident matches."
    )
    raw = proposer(prompt)
    try:
        data = json.loads(raw[raw.index("["): raw.rindex("]") + 1])
    except (ValueError, json.JSONDecodeError):
        return []
    return [(int(p[0]), int(p[1])) for p in data if isinstance(p, (list, tuple)) and len(p) == 2]


def reconcile(
    register: list[Provider], actual: list[Provider], proposer: Proposer | None = None
) -> ReconResult:
    res = ReconResult()
    used: set[int] = set()
    rem_reg: list[Provider] = []
    for r in register:
        hit = next((i for i, a in enumerate(actual) if i not in used and _same(r, a)), None)
        if hit is None:
            rem_reg.append(r)
        else:
            res.matched.append((r, actual[hit]))
            used.add(hit)
    rem_act = [a for i, a in enumerate(actual) if i not in used]

    if proposer and rem_reg and rem_act:
        mr: set[int] = set()
        ma: set[int] = set()
        for ri, ai in _llm_pairs(rem_reg, rem_act, proposer):
            if 0 <= ri < len(rem_reg) and 0 <= ai < len(rem_act) and ri not in mr and ai not in ma:
                res.llm_proposed.append((rem_reg[ri], rem_act[ai]))
                mr.add(ri)
                ma.add(ai)
        rem_reg = [r for i, r in enumerate(rem_reg) if i not in mr]
        rem_act = [a for i, a in enumerate(rem_act) if i not in ma]

    res.stale = rem_reg
    res.shadow = rem_act
    return res
