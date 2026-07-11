"""
Multi-zone storage layer for the FinMark data pipeline.

Storage zones:
- Clean zone
- Curated zone
- Quarantine zone
- Output metadata
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import (
    CLEAN_DIR,
    CURATED_DIR,
    QUARANTINE_DIR,
    create_project_directories,
)
from logger_config import get_logger


logger = get_logger()


def save_dataframe(
    dataframe: pd.DataFrame,
    file_path: Path,
) -> dict:
    """
    Save one DataFrame and return storage metadata.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        file_path,
        index=False,
    )

    metadata = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "row_count": len(dataframe),
        "column_count": len(
            dataframe.columns
        ),
        "file_size_bytes": (
            file_path.stat().st_size
        ),
        "status": "SAVED",
    }

    logger.info(
        "Dataset saved: %s | Rows: %d | "
        "Columns: %d | Size: %d bytes",
        file_path,
        metadata["row_count"],
        metadata["column_count"],
        metadata["file_size_bytes"],
    )

    return metadata


def save_clean_zone(
    datasets: dict[str, pd.DataFrame],
) -> list[dict]:
    """
    Save transformed operational datasets.
    """

    metadata_records = []

    for dataset_name, dataframe in (
        datasets.items()
    ):
        path = (
            CLEAN_DIR
            / f"{dataset_name}_clean.csv"
        )

        record = save_dataframe(
            dataframe,
            path,
        )

        record["storage_zone"] = "CLEAN"
        record["dataset"] = dataset_name

        metadata_records.append(record)

    return metadata_records


def save_curated_zone(
    curated_datasets: dict[
        str,
        pd.DataFrame,
    ],
) -> list[dict]:
    """
    Save analytics-ready datasets.
    """

    metadata_records = []

    for dataset_name, dataframe in (
        curated_datasets.items()
    ):
        path = (
            CURATED_DIR
            / f"{dataset_name}.csv"
        )

        record = save_dataframe(
            dataframe,
            path,
        )

        record["storage_zone"] = "CURATED"
        record["dataset"] = dataset_name

        metadata_records.append(record)

    return metadata_records


def save_quarantine_zone(
    quarantined_datasets: dict[
        str,
        pd.DataFrame,
    ],
) -> list[dict]:
    """
    Save rejected or suspicious records.
    """

    metadata_records = []

    for dataset_name, dataframe in (
        quarantined_datasets.items()
    ):

        if dataframe.empty:
            logger.info(
                "No quarantined rows for %s.",
                dataset_name,
            )
            continue

        path = (
            QUARANTINE_DIR
            / f"{dataset_name}_quarantine.csv"
        )

        record = save_dataframe(
            dataframe,
            path,
        )

        record["storage_zone"] = (
            "QUARANTINE"
        )

        record["dataset"] = dataset_name

        metadata_records.append(record)

    return metadata_records


def save_all_zones(
    transformed_datasets: dict[
        str,
        pd.DataFrame,
    ],
    curated_datasets: dict[
        str,
        pd.DataFrame,
    ],
    quarantined_datasets: dict[
        str,
        pd.DataFrame,
    ],
) -> pd.DataFrame:
    """
    Save all pipeline storage zones.
    """

    create_project_directories()

    metadata_records = []

    metadata_records.extend(
        save_clean_zone(
            transformed_datasets
        )
    )

    metadata_records.extend(
        save_curated_zone(
            curated_datasets
        )
    )

    metadata_records.extend(
        save_quarantine_zone(
            quarantined_datasets
        )
    )

    metadata_report = pd.DataFrame(
        metadata_records
    )

    metadata_path = (
        CURATED_DIR
        / "storage_metadata.csv"
    )

    metadata_report.to_csv(
        metadata_path,
        index=False,
    )

    print("\nSTORAGE SUMMARY")
    print("-" * 105)

    if metadata_report.empty:
        print("No datasets were saved.")

    else:
        display_columns = [
            "storage_zone",
            "dataset",
            "row_count",
            "column_count",
            "file_size_bytes",
            "status",
        ]

        print(
            metadata_report[
                display_columns
            ].to_string(
                index=False
            )
        )

    print("-" * 105)

    logger.info(
        "Storage metadata saved to: %s",
        metadata_path,
    )

    return metadata_report