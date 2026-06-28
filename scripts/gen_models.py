"""Generate Pydantic domain models for the 15 DORA RoI templates.

Source of truth: spec/_extracted/template_fields.json (produced by extract_layout.py
from the EBA Annotated Table Layout). Output: src/theodora/domain/templates.py.

DO NOT hand-edit the generated file — change the spec or this generator and re-run:
    uv run python scripts/gen_models.py
"""
from __future__ import annotations

import json
import keyword
import pathlib
import re

SRC = pathlib.Path("spec/_extracted/template_fields.json")
OUT = pathlib.Path("src/theodora/domain/templates.py")

# Field whose presence marks a foreign key into B_02.01 (the central contractual-arrangement key).
FK_LABEL = "contractual arrangement reference number"


def snake(label: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", label.strip().lower()).strip("_")
    s = re.sub(r"_+", "_", s)
    if not s:
        s = "field"
    if s[0].isdigit():
        s = "f_" + s
    if keyword.iskeyword(s):
        s = s + "_"
    return s


def py_type(label: str) -> str:
    low = label.lower()
    if "date" in low:
        return "datetime.date"
    if any(k in low for k in ("annual expense", "estimated cost", "total annual", "value of total assets")):
        return "Decimal"
    return "str"


def class_name(tid: str) -> str:
    return tid.replace(".", "_")


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    L: list[str] = [
        '"""DORA RoI template models — GENERATED from spec/_extracted/template_fields.json.',
        "",
        "Do NOT hand-edit. Regenerate: uv run python scripts/gen_models.py",
        "",
        "- Field name  = snake_case(EBA label); alias = xBRL column code (the header in xBRL-CSV).",
        "- All fields Optional for now; mandatory-ness + enums come from the validation rules and",
        "  the 'list of possible values' (spec/) — bound in a later pass (no fabrication here).",
        "- Central key: B_02.01.contractual_arrangement_reference_number; the same field in",
        "  B_02.02/02.03/03.01/03.02/03.03/04.01/05.02/07.01 is a foreign key into it.",
        '"""',
        "from __future__ import annotations",
        "",
        "import datetime",
        "from decimal import Decimal",
        "from typing import ClassVar, Optional",
        "",
        "from pydantic import BaseModel, ConfigDict, Field",
        "",
        "",
        "class RoiTemplate(BaseModel):",
        '    """Base for all RoI template rows. Accepts both field name and xBRL alias."""',
        "    model_config = ConfigDict(populate_by_name=True)",
        "",
        "",
    ]
    registry: list[tuple[str, str]] = []
    for tid, d in data.items():
        cls = class_name(tid)
        registry.append((tid, cls))
        title = " ".join(str(d["title"]).split()).replace('"', "'")
        L.append(f"class {cls}(RoiTemplate):")
        L.append(f'    """{title}"""')
        L.append(f'    TEMPLATE_ID: ClassVar[str] = "{tid}"')
        seen: dict[str, bool] = {}
        for fld in d["fields"]:
            code = fld["code"]
            base = snake(fld["label"])
            name = base if base not in seen else f"{base}_{code}"
            seen[name] = True
            typ = py_type(fld["label"])
            desc = " ".join(str(fld["label"]).split()).replace('"', "'")
            L.append(f'    {name}: Optional[{typ}] = Field(None, alias="{code}", description="{desc}")')
        if not d["fields"]:
            L.append("    pass")
        L.append("")
        L.append("")
    reg = ", ".join(f'"{tid}": {cls}' for tid, cls in registry)
    L.append(f"TEMPLATES: dict[str, type[RoiTemplate]] = {{{reg}}}")
    L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"[written] {OUT} — {len(registry)} models, "
          f"{sum(len(d['fields']) for d in data.values())} fields total")


if __name__ == "__main__":
    main()
