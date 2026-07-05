"""
Warehouse package init.

Exposes builders for dimensions and facts, surrogate key assignments, and schema validation.
"""

from __future__ import annotations

from .dimension_builder import build_dimensions
from .surrogate_keys import assign_surrogate_keys
from .fact_builder import build_fact_tables
from .star_schema import validate_star_schema

__all__ = [
    "build_dimensions",
    "assign_surrogate_keys",
    "build_fact_tables",
    "validate_star_schema",
]
