"""Generate src/theodora/generate/_samples.py — one valid sample value per (template, column).

Source: the EBA golden xBRL-CSV instance under spec/samples/ (gitignored, local). The golden
is a fully-populated, taxonomy-valid sample, so its per-column values are guaranteed valid
(enum members, dates, etc.). The generator uses these to populate non-key fact cells so the
output is XBRL-dimensionally valid (no `xbrlce:unmappedCellValue`).

Regenerate: uv run python scripts/gen_samples.py
"""
from __future__ import annotations

import csv
import glob
import pathlib

from theodora.domain.templates import TEMPLATES

OUT = pathlib.Path("src/theodora/generate/_samples.py")


def main() -> None:
    reports = pathlib.Path(glob.glob("spec/samples/dora_golden_instance/*/reports")[0])
    samples: dict[str, dict[str, str]] = {}
    for tid in TEMPLATES:
        f = reports / f"{tid.lower()}.csv"
        if not f.is_file():
            continue
        colvals: dict[str, str] = {}
        with f.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                for k, v in row.items():
                    if k and v and str(v).strip() and k not in colvals:
                        colvals[k] = str(v).strip()
        if colvals:
            samples[tid] = colvals

    L = [
        '"""Valid per-column sample values — GENERATED from the EBA golden instance.',
        "",
        "Do NOT hand-edit. Regenerate: uv run python scripts/gen_samples.py",
        '"""',
        "from __future__ import annotations",
        "",
        "",
        "SAMPLES: dict[str, dict[str, str]] = {",
    ]
    for tid in sorted(samples):
        L.append(f"    {tid!r}: {{")
        for code in sorted(samples[tid]):
            L.append(f"        {code!r}: {samples[tid][code]!r},")
        L.append("    },")
    L.append("}")
    L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"[written] {OUT} — {len(samples)} templates, {sum(len(v) for v in samples.values())} sample values")


if __name__ == "__main__":
    main()
