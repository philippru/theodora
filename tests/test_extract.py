"""Contract-extraction tests — fake proposer (no LLM, no PDF)."""
from __future__ import annotations

from theodora.agent.extract import extract_row


def test_extracts_only_valid_columns() -> None:
    # B_02.01 has c0010 (arrangement ref) and c0020 (type). c9999 is not a column -> dropped.
    fake = lambda _p: '{"c0010": "CA-1", "c0020": "eba_CO:x1", "c9999": "junk"}'  # noqa: E731
    row = extract_row("…contract…", "B_02.01", fake)
    assert row == {"c0010": "CA-1", "c0020": "eba_CO:x1"}


def test_handles_non_json_gracefully() -> None:
    assert extract_row("…", "B_02.01", lambda _p: "sorry, no idea") == {}


def test_tolerates_prose_around_json() -> None:
    fake = lambda _p: 'Here you go:\n{"c0010": "CA-2"}\nHope that helps.'  # noqa: E731
    assert extract_row("…", "B_02.01", fake) == {"c0010": "CA-2"}
