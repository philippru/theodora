# `spec/` — frozen EBA source artifacts

Theodora validates against a **frozen snapshot** of the EBA DORA RoI reporting
framework. Download the files below into the matching subfolders, then record the
exact versions in [`FROZEN.md`](FROZEN.md). Principle: **nothing fabricated** — every
rule in `theodora/validation/` traces to a file here.

- **Hub (almost everything):** https://www.eba.europa.eu/activities/direct-supervision-and-oversight/digital-operational-resilience-act/preparation-dora-application
- **Legal source (the 15 templates):** Commission Implementing Regulation (EU) 2024/2956 — https://eur-lex.europa.eu/eli/reg_impl/2024/2956/oj
- **Cross-check tool:** Arelle (open-source XBRL processor) — https://arelle.org
- **Freeze target:** Taxonomy architecture **v2.0** · Reporting framework **4.0** · DPM **v4.0** · Filing Rules **v5.5**.
  ⚠ Verify whether DORA RoI changed in framework **4.2 / 4.3-draft** before freezing — report against *one* fixed version.

---

## ✅ MUST download — build Phase 0/1 on these

Exact names as they appear on the EBA hub page → target folder → which Theodora layer it feeds.

| EBA item | → folder | feeds |
|---|---|---|
| **ITS on the registers of information** (OJ) — *or* the EUR-Lex link above | `its/` | template structure B_01–B_07 |
| **Data Point Model table layout** → file `20241217 Annotated Table Layout DORADORA 4.0` | `dpm/` | **START HERE** — domain model (fields, templates) |
| **Data Point Model Dictionary** (updated 21 Mar 2025, `dpm2_4_0_glossary_…xlsx`) | `dpm/` | field names/types → domain model + L1 |
| **Data Model for DORA RoI** | `dpm/` | relationships → domain model + L2 |
| **List of possible values for all data fields with drop downs** (3 Mar 2025) | `dpm/` | **L1** (enums / allowed values) |
| **Validation rules** (download, search DORA under *Frameworks*) | `validation/` | **L2/L3** (referential + business) |
| **Overview of technical checks, validation rules and business checks** (28 Apr 2025) | `validation/` | **L2/L3/L4** — human-readable check catalogue |
| **EBA reporting filing rules v5.5** | `filing-rules/` | **L4** (filenames/encoding/structure) |
| **Taxonomy package under taxonomy architecture v2.0** (search DORA file) | `taxonomy/` | the XBRL taxonomy (writer + Arelle) |
| **Sample files for taxonomy v2.0** → `instances xBRL-CSV` → `DUMMYLEI123456789012.CON_FR_DORA010100_DORA_2024-12-31_…` | `samples/` | **golden reference** for the xBRL-CSV writer + cross-check |

## 🟡 USEFUL — clarifications & priorities (grab if convenient)

| EBA item | → folder | why |
|---|---|---|
| **FAQ on reporting of the registers of information** (28 Mar 2025) | `reference/` | the fragmented Q&A clarifications (painpoint #5) |
| **Observations from testing … key common issues** (16 May 2025) | `reference/` | tells you which validations fail most → prioritize |
| **ITS on RoI — Annex 2 list of licensed activities** (DPM v4.0) | `dpm/` | enum for the licensed-activity field (L1) |
| **Preparing plain csv reporting package for DORA** (slides) | `reference/` | explains the plain-CSV package layout (writer) |
| **Explanations of the data quality feedback** (slides) + **DORA Sample data quality responses** | `reference/` | shape of validation output / DQ semantics |

## ⚪ OPTIONAL — reference only (2024 dry-run era)

| EBA item | → folder | why |
|---|---|---|
| **DORA plain csv sample reporting package** `[zip]` | `samples/` | a second sample package |
| **XLS to CSV conversion tool** `[xlsm]` + **Instructions** `[pdf]` | `reference/` | EBA's own Excel→CSV converter — study as reference, don't depend on it |
| **Template for the register of information** `[xlsb]` | `reference/` | example Excel template for the future Excel-reader |
| **Reporting technical package** (framework 4.0 bulk) | — | alternative bulk download of taxonomy+DPM+validation if you'd rather grab one big package than the individual MUST items |

## ⛔ SKIP

- **ESAs Decision on reporting … for CTPP designation** — different reporting flow, not the RoI.
- All other **2024 Dry Run** material (summary report, workshop presentations/videos, factsheets, press releases, **draft** DPM / **draft** taxonomy, dry-run Annex 2, dry-run FAQ, dry-run DQ-check explanation) — superseded by the official 2025 artifacts above.

---

## Folder layout

```
spec/
  its/           # ITS (EU) 2024/2956 + OJ text
  dpm/           # annotated table layout, DPM dictionary, data model, possible values, Annex 2
  validation/    # EBA validation rules, overview of technical/business checks
  filing-rules/  # Filing Rules v5.5
  taxonomy/      # taxonomy package (architecture v2.0)
  samples/       # golden xBRL-CSV instance(s)
  reference/     # FAQ, common issues, slides, EBA conversion tool
  FROZEN.md      # exact versions/dates frozen for this corpus
```

Once the MUST files are in place, the `domain/` Pydantic models get modelled
**accurately against `dpm/`** — not from memory.
