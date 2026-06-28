"""Contract → Register extraction — the LLM proposes field values from a contract; Theodora's
validation decides. Pure logic: the proposer is injected (real LLM or a fake for tests).
"""
from __future__ import annotations

import json

from theodora.agent.llm import Proposer
from theodora.domain._field_dims import FIELD_DIMS
from theodora.domain.enums import DIMENSIONS
from theodora.validation.engine import _alias_labels


def _field_brief(tid: str) -> str:
    dims = FIELD_DIMS.get(tid, {})
    lines = []
    for alias, label in _alias_labels(tid).items():
        dim = dims.get(alias)
        hint = ""
        if dim and dim in DIMENSIONS:
            hint = f"  [coded value from {dim}, e.g. {sorted(DIMENSIONS[dim])[:3]}]"
        lines.append(f"  {alias}: {label}{hint}")
    return "\n".join(lines)


def extraction_prompt(tid: str, contract_text: str) -> str:
    return (
        f"DORA RoI template {tid}. Extract the following fields from the contract text.\n"
        f"Fields (key: meaning):\n{_field_brief(tid)}\n\n"
        f"Return ONLY a JSON object mapping field keys (cXXXX) to values. Omit fields that are "
        f"not present in the contract. Use the coded value where a dimension is given.\n\n"
        f"CONTRACT:\n{contract_text}"
    )


def extract_row(contract_text: str, tid: str, proposer: Proposer) -> dict[str, str]:
    """Ask the proposer to extract a row for `tid`; return only valid template columns."""
    raw = proposer(extraction_prompt(tid, contract_text))
    try:
        data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        return {}
    valid = set(_alias_labels(tid))
    return {k: str(v).strip() for k, v in data.items() if k in valid and v not in (None, "")}
