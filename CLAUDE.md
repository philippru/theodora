# Theodora — Agent Instructions

This file is intentionally a **showcase**: it demonstrates how to instruct an AI agent
to build under architecture governance.

## Architektur-Invarianten (Definition of Done)

- **Core ist LLM-frei.** Hexagonale Architektur: `domain/` ← `validation/` ← `io/` ← `cli/`.
  Abhängigkeiten zeigen nach innen; die CLi enthält keine Geschäftslogik.
- **Regeln sind Daten** (`spec/`), nicht Code.
- **Determinismus:** `roi generate` muss über 3 Läufe byte-identische Ausgabe liefern.
- **Pro Validierungsregel-ID ein Testpaar** (valid + verletzt).
- **ruff + mypy müssen grün sein.** Englisch im Code.

## Spec-Quellen (eingefroren unter `spec/`)

- DORA ITS (EU) 2024/2956 — 15 Templates B_01..B_07
- EBA Filing Rules v5.5; DPM-Datenpunkte; relevante EBA-Q&As
- Cross-Check-Referenzen: Arelle, sowie öffentliche Validatoren als Qualitätslatte

## Standalone (kritisch)

- Dieses Repo muss für externe Contributors **eigenständig** funktionieren — keine externen
  Tools als Build- oder Laufzeit-Abhängigkeit.
- Lokale Pre-Commit-Hooks (falls genutzt) liegen in `.git/hooks/` und werden **nie** versioniert.
