# Theodora

**The open DORA Register of Information (RoI) toolkit** — generate and validate the DORA
Register of Information in the EBA-mandated **xBRL-CSV** format, locally and reproducibly.

> *Recht in strukturierte, prüfbare Form gebracht.*

## Why

Every financial entity in scope of [DORA](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
must submit a Register of all its ICT third-party arrangements — 15 relationally-linked
templates (B_01.01–B_99.01) in a pedantic xBRL-CSV package. Dry-run failure rates have been
around **93.5%**.

Existing tools are either **partial + free** (browser converters, validators) or
**complete + paid + closed**. Theodora targets the empty quadrant: **open (Apache-2.0,
commercial use permitted), complete, local, automatable** — your ICT third-party register
never leaves your perimeter.

## Install

```bash
uv sync                    # core
uv sync --extra arelle     # + optional Arelle cross-check
```

## Usage

```bash
# 1. blank Excel template to fill in (one sheet per template)
uv run roi template -o roi-template.xlsx

# 2. convert a filled workbook into a submission package (and validate it)
uv run roi convert -i filled.xlsx -e <LEI> -o out/ --validate

# validate an existing package (L1–L4)
uv run roi validate out/<package-dir>

# generate a deterministic, valid sample package (--inject-violation for fixtures)
uv run roi generate -e <LEI> -o out/

# cross-check against the OFFICIAL EBA taxonomy AND run the full official rule set, via Arelle
uv run --extra arelle roi crosscheck -p out/<package-dir> -t <EBA-taxonomy-package.zip>
#   add --structural-only for a fast offline check (skips the e23/v8 formula rules)

# (optional [agent] extra) an LLM proposes fixes for findings — kept ONLY if re-validation passes
uv run --extra agent roi fix -p out/<package-dir> --model anthropic/claude-sonnet-4-6
#   provider-agnostic via LiteLLM: Claude · OpenAI · Gemini · Bedrock · Azure · local (Ollama)

# (optional [agent] extra) extract a template row from a contract PDF — shown for review, then validate
uv run --extra agent roi extract --pdf contract.pdf --template B_02.02 --model anthropic/claude-sonnet-4-6

# reconcile registered providers (B_05.01) vs an actually-used list — flags SHADOW providers (DORA gap)
uv run roi reconcile -p out/<package-dir> -a actual-providers.txt   # add --model … for fuzzy name matching
```

`roi convert` accepts columns identified by either the xBRL code (`c0010`) or the human
field label; sheet names are matched flexibly (`B_01.01` / `B0101` / `b_01.01`).

## Validation layers

| Layer | Checks | Rule-IDs |
|---|---|---|
| **L1** | structure, unknown columns, types, enum membership | `THEO-L1-STRUCT/COL/TYPE/ENUM` |
| **L2** | referential integrity (FK → B_02.01 / B_05.01 / B_06.01) | `THEO-L2-FK-*` |
| **L3** | business logic — cascading criticality (B_06.01 → B_02.02) | `THEO-L3-CRIT-*` |
| **L4** | filing-rule conformance — package structure, naming, UTF-8 | `THEO-L4-PKG/NAME/ENC-*` |

Every rule traces to the EBA spec (DPM, possible values, field labels, data model); nothing
is fabricated. Beyond Theodora's own L1–L4, `roi crosscheck` runs the **full official EBA rule
set** (the `e23…`/`v8…` formula assertions) via Arelle against the real EBA DORA 4.0 taxonomy —
and packages produced by `roi generate` pass it clean (structure + all official assertions).

## Spec

`spec/` holds a *frozen* snapshot of the EBA artifacts (gitignored — download locally). See
[`spec/README.md`](spec/README.md) for the exact files and links, and `spec/FROZEN.md` for
the pinned versions (Taxonomy v2.0 · Framework 4.0 · DPM 4.0 · Filing Rules v5.5).

## Status

Early but functional: `convert` / `validate` / `generate` / `crosscheck` all work; generated
packages are XBRL-conformant. An optional **agent layer** (`fix` / `extract` / `reconcile`) lets an
LLM propose fixes, extract from contracts, and detect shadow providers — every proposal must pass
validation (*LLM proposes, Theodora decides*). Not yet production-hardened.

## Maintainer

**Philipp Ruisinger**, Wien · <philipp@ruisinger.at> — full [Impressum](IMPRESSUM.md).

## License

[Apache-2.0](LICENSE) — commercial use explicitly permitted. © 2026 Philipp Ruisinger.
