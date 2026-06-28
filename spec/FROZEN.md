# FROZEN — exact source versions for this corpus

Record the precise version/date of every artifact frozen into `spec/`. Theodora's
validation is only reproducible against a pinned snapshot. Bump deliberately.

| Component | Frozen version / date | File(s) | Notes |
|---|---|---|---|
| ITS (templates) | (EU) 2024/2956 | `its/` | OJ-published; check for amendments |
| Taxonomy architecture | v2.0 | `taxonomy/` | updated 21 Mar 2025 |
| Reporting framework | 4.0 | — | verify DORA RoI unchanged in 4.2 / 4.3 |
| DPM dictionary | v4.0 | `dpm/dpm2_4_0_glossary_*.xlsx` | updated 21 Mar 2025 |
| Annotated table layout | DORA 4.0 (`20241217`) | `dpm/` | — |
| Possible values | 3 Mar 2025 | `dpm/` | enums |
| Validation rules | 2025-03-20 | `validation/` | search DORA under Frameworks |
| Technical/business checks | 28 Apr 2025 | `validation/` | — |
| Filing Rules | v5.5 (2025-01-14) | `filing-rules/` | — |
| Sample instance | 2024-12-31 dummy | `samples/` | golden reference |

**Status:** all MUST + USEFUL artifacts downloaded into `spec/` on 2026-06-28 (gitignored — local only, not committed/redistributed). Golden xBRL-CSV instance unpacked under `samples/dora_golden_instance/` (templates b_01.01–b_99.01 + FilingIndicators/parameters/report.json).
**Open:** verify DORA RoI is unchanged across framework 4.0 → 4.2 / 4.3-draft before declaring final.
**corpus_version:** 0.1.0-draft
**frozen_on:** 2026-06-28 (provisional)
