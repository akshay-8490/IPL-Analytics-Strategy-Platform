"""
Shared dataclasses for the Export & Validation pipeline.

These models define the public contracts returned by the
NB8 release pipeline.
"""

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ReleasePipelineResult",
]

@dataclass(frozen=True)
class ReleasePipelineResult:
    """
    Final result returned by the Export & Validation pipeline.

    Attributes
    ----------
    status : str
        Pipeline execution status.

    execution_time : float
        Total execution time in seconds.

    validation_summary : dict[str, Any]
        Summary of all validation checks.

    export_summary : dict[str, Any]
        Summary of exported project artifacts.

    project_statistics : dict[str, Any]
        Overall project statistics and metadata.
    """

    status: str

    execution_time: float

    validation_summary: dict[str, Any]

    export_summary: dict[str, Any]

    project_statistics: dict[str, Any]