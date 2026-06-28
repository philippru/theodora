"""Domain layer — Pydantic models for the 15 DORA RoI templates (B_01.01–B_99.01).

Models are GENERATED in `templates.py` from the frozen EBA spec (see scripts/gen_models.py).
B_02.01.contractual_arrangement_reference_number is the central FK hub.
"""

from theodora.domain.templates import TEMPLATES, RoiTemplate

__all__ = ["TEMPLATES", "RoiTemplate"]
