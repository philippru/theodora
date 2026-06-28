"""Generate src/theodora/domain/_field_dims.py — per-(template, column) xBRL dimension.

Derived from the golden instance: for each column whose golden values are coded (eba_XX:..),
record the dimension XX. Enables per-field enum binding (a coded value in a bound column must
use that column's dimension, not merely *a* valid dimension).

Regenerate: uv run python scripts/gen_field_dims.py
"""
from __future__ import annotations

import csv
import glob
import pathlib
import re

from theodora.domain.templates import TEMPLATES

OUT = pathlib.Path("src/theodora/domain/_field_dims.py")
_CODED = re.compile(r"^(eba_[A-Za-z0-9]+):")


def main() -> None:
    reports = pathlib.Path(glob.glob("spec/samples/dora_golden_instance/*/reports")[0])
    field_dims: dict[str, dict[str, str]] = {}
    for tid in TEMPLATES:
        f = reports / f"{tid.lower()}.csv"
        if not f.is_file():
            continue
        dims: dict[str, str] = {}
        with f.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                for k, v in row.items():
                    if k and v and k not in dims:
                        m = _CODED.match(str(v).strip())
                        if m:
                            dims[k] = m.group(1)
        if dims:
            field_dims[tid] = dims

    L = [
        '"""Per-(template, column) xBRL dimension — GENERATED from the golden instance.',
        "",
        "Do NOT hand-edit. Regenerate: uv run python scripts/gen_field_dims.py",
        '"""',
        "from __future__ import annotations",
        "",
        "",
        "FIELD_DIMS: dict[str, dict[str, str]] = {",
    ]
    for tid in sorted(field_dims):
        L.append(f"    {tid!r}: {{")
        for code in sorted(field_dims[tid]):
            L.append(f"        {code!r}: {field_dims[tid][code]!r},")
        L.append("    },")
    L.append("}")
    L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"[written] {OUT} — {sum(len(v) for v in field_dims.values())} bound columns, {len(field_dims)} templates")


if __name__ == "__main__":
    main()
