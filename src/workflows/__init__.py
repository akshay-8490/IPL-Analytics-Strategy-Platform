"""
Workflows package init.

Exposes run_database_pipeline function.
"""

from __future__ import annotations

from .database_pipeline import (
    DatabasePipelineResult,
    run_database_pipeline,
)

__all__ = [
    "DatabasePipelineResult",
    "run_database_pipeline",
]
