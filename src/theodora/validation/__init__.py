"""Validation layer — the 4-layer rule engine.

L1 syntactic (types/enums/required) · L2 referential integrity across templates ·
L3 business logic (cascading criticality, BIA consistency) · L4 Filing-Rule v5.5 conformance.
Each finding carries a stable rule-ID.
"""

from theodora.validation.engine import Finding, validate_package

__all__ = ["Finding", "validate_package"]
