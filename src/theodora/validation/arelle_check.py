"""Independent cross-check against the official EBA taxonomy via Arelle (optional extra).

This is a *second opinion* beyond Theodora's own L1–L4: it loads the generated package and the
real EBA DORA taxonomy in Arelle and reports XBRL-level findings. Requires the `arelle` extra
(`uv sync --extra arelle`) and, on first run, internet access to fetch+cache the eurofiling base
schemas the EBA taxonomy references. By default it runs the **full official EBA rule set**
(the e23…/v8… formula assertions); `structural_only=True` skips them for a fast offline check.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# Instance-level error codes worth surfacing (excludes the taxonomy's own xbrlgene warnings).
_INSTANCE_ERR = re.compile(r"\[(xbrlce|xbrldie|enumte|oime|xmlSchema\w*|xbrl\.\w+):[^\]]+\]")
_NOISE = ("xbrlgene", "dora-pre.xml", ".xsd ")


def arelle_available() -> bool:
    try:
        import arelle  # noqa: F401
        return True
    except ImportError:
        return False


def _resolve_packages(taxonomy: Path, tmp: Path) -> list[Path]:
    if taxonomy.is_dir():
        return sorted(taxonomy.glob("*.zip"))
    if taxonomy.suffix.lower() == ".zip":
        with zipfile.ZipFile(taxonomy) as z:
            inner = [n for n in z.namelist() if n.lower().endswith(".zip")]
            if inner:
                return [Path(z.extract(n, tmp)) for n in inner]
    return [taxonomy]


def crosscheck(
    package_dir: Path, taxonomy: Path, *, offline: bool = False, structural_only: bool = False
) -> tuple[int, list[str]]:
    """Return (exit_code, findings). 0 = Arelle validated with no findings.

    Default runs the full official EBA rule set (formula assertions); structural_only=True
    skips them (faster, works offline once the base schemas are cached).
    """
    report_json = Path(package_dir) / "reports" / "report.json"
    if not report_json.is_file():
        return 2, [f"report.json not found under {package_dir}"]
    with tempfile.TemporaryDirectory() as td:
        packages = _resolve_packages(Path(taxonomy), Path(td))
        cmd = [
            sys.executable, "-m", "arelle.CntlrCmdLine",
            "--file", str(report_json),
            "--packages", "|".join(str(p) for p in packages),
            "--validate",
        ]
        if structural_only:
            cmd += ["--formula", "none"]
        if offline:
            cmd += ["--internetConnectivity", "offline"]
        proc = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    log = proc.stdout + proc.stderr
    findings = [
        ln.strip() for ln in log.splitlines()
        if (_INSTANCE_ERR.search(ln) or "[message:" in ln) and not any(n in ln for n in _NOISE)
    ]
    validated = "validated in" in log
    if not validated:
        findings.insert(0, "Arelle did not complete validation (first run needs internet for base schemas).")
    return (0 if (validated and not findings) else 1), findings
