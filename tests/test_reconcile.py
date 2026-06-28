"""Reconciliation / shadow-register tests — deterministic core + fake LLM matcher."""
from __future__ import annotations

from pathlib import Path

from theodora.agent.reconcile import Provider, reconcile, register_providers
from theodora.generate.builder import build_tables, package_name
from theodora.io.writer import write_package


def test_matches_by_code_and_normalised_name() -> None:
    register = [Provider(code="LEI1", name="Amazon Web Services EMEA SARL"), Provider(name="Microsoft Ireland")]
    actual = [Provider(code="LEI1", name="AWS"), Provider(name="Microsoft Ireland GmbH")]
    res = reconcile(register, actual)
    assert len(res.matched) == 2  # LEI1 by code; Microsoft by suffix-normalised name
    assert not res.shadow and not res.stale


def test_flags_shadow_and_stale() -> None:
    res = reconcile([Provider(name="Provider A")], [Provider(name="Provider B")])
    assert [p.name for p in res.shadow] == ["Provider B"]  # used, not registered
    assert [p.name for p in res.stale] == ["Provider A"]   # registered, not used


def test_llm_resolves_fuzzy_leftover() -> None:
    register = [Provider(name="Initech")]
    actual = [Provider(name="Initech Worldwide Holdings")]  # not an exact normalised match
    res = reconcile(register, actual, lambda _p: "[[0, 0]]")  # fake LLM proposes the pair
    assert res.llm_proposed and not res.shadow and not res.stale


def test_reads_providers_from_b0501(tmp_path: Path) -> None:
    lei, date = "DUMMYLEI123456789012", "2024-12-31"
    pkg = write_package(tmp_path, package_name(lei, date), build_tables(lei, date, None), lei, date)
    providers = register_providers(pkg)
    assert providers and (providers[0].code or providers[0].name)
