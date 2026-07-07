"""
project_exporter.py

Export and package the final IPL Analytics & Strategy Platform release.

This module is responsible for collecting artifacts generated throughout the
project, organizing them into a release structure, generating metadata,
validation reports, and a release manifest.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from config.config import (
    ANALYTICS_DATA_DIR,
    MODELS_DIR,
    RELEASE_DIR,
    WAREHOUSE_DIR,
)

from src.models.release import ReleasePipelineResult
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

###############################################################################
# Release Directory Structure
###############################################################################

RELEASE_STRUCTURE = {
    "metadata": "metadata",
    "warehouse": "warehouse",
    "analytics": "analytics",
    "machine_learning": "machine_learning",
    "validation": "validation",
}

def _create_release_structure() -> dict[str, Path]:
    """
    Create the release directory structure.

    Returns
    -------
    dict[str, Path]
        Mapping of logical names to created directories.
    """

    logger.info("Creating release directory structure...")

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    directories = {}

    for key, folder in RELEASE_STRUCTURE.items():
        path = RELEASE_DIR / folder
        path.mkdir(parents=True, exist_ok=True)
        directories[key] = path

    return directories

def _copy_directory(
    source: Path,
    destination: Path,
) -> int:
    """
    Copy an entire directory recursively.

    Returns
    -------
    int
        Number of copied files.
    """

    if not source.exists():
        logger.warning("Source directory does not exist: %s", source)
        return 0

    copied = 0

    for item in source.rglob("*"):

        target = destination / item.relative_to(source)

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)

        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            copied += 1

    return copied

def _export_project_metadata(
    directory: Path,
    project_statistics: dict[str, Any],
) -> None:
    """
    Export project metadata.
    """

    metadata = {
        "project": "IPL Analytics & Strategy Platform",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        **project_statistics,
    }

    output = directory / "project_metadata.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

def _export_validation_report(
    directory: Path,
    validation_summary: dict[str, Any],
) -> None:
    """
    Export validation report.
    """

    output = directory / "validation_summary.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(validation_summary, file, indent=4)

def _export_release_manifest(
    files_exported: int,
    directories_created: int,
    status: str,
) -> None:
    """
    Export release manifest.
    """

    manifest = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "files_exported": files_exported,
        "directories_created": directories_created,
        "status": status,
    }

    output = RELEASE_DIR / "manifest.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

def export_project(
    pipeline_result: ReleasePipelineResult,
) -> dict[str, Any]:
    """
    Export the complete project release.

    Parameters
    ----------
    pipeline_result : ReleasePipelineResult
        Result produced by the export validation pipeline.

    Returns
    -------
    dict[str, Any]
        Export summary.
    """

    logger.info("Starting project export...")

    release_dirs = _create_release_structure()

    files_exported = 0

    files_exported += _copy_directory(
        WAREHOUSE_DIR,
        release_dirs["warehouse"],
    )

    files_exported += _copy_directory(
        ANALYTICS_DATA_DIR,
        release_dirs["analytics"],
    )

    files_exported += _copy_directory(
        MODELS_DIR,
        release_dirs["machine_learning"],
    )


    _export_project_metadata(
        release_dirs["metadata"],
        pipeline_result.project_statistics,
    )

    _export_validation_report(
        release_dirs["validation"],
        pipeline_result.validation_summary,
    )

    files_exported += 2

    _export_release_manifest(
        files_exported=files_exported,
        directories_created=len(RELEASE_STRUCTURE),
        status=pipeline_result.status,
    )

    files_exported += 1

    logger.info("Project export completed successfully.")

    return {
        "status": pipeline_result.status,
        "release_directory": str(RELEASE_DIR),
        "directories_created": len(RELEASE_STRUCTURE),
        "files_exported": files_exported,
    }

__all__ = [
    "export_project",
]