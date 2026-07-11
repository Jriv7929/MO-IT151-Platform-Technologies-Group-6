"""
Data profiling and quality assessment.

This module calculates:
- Row and column counts
- Missing-value counts and percentages
- Duplicate records
- Unique values
- Completeness scores
- Column usability
- Dataset health status
"""

from __future__ import annotations

import pandas as pd

from config import (
    COLUMN_DROP_THRESHOLD,
    CRITICAL_COLUMNS,
    DATA_QUALITY_FILE,
    QUALITY_STATUS_GOOD,
    QUALITY_STATUS_WARNING,
)
from logger_config import get_logger


logger = get_logger()


def classify_quality_status(
    completeness_score: float,
) -> str:
    """
    Assign a quality status using dataset completeness.
    """

    if completeness_score >= QUALITY_STATUS_GOOD:
        return "GOOD"

    if completeness_score >= QUALITY_STATUS_WARNING:
        return "WARNING"

    return "CRITICAL"


def profile_column(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column_name: str,
) -> dict:
    """
    Create a quality profile for one column.
    """

    total_rows = len(dataframe)

    missing_count = int(
        dataframe[column_name].isna().sum()
    )

    non_missing_count = (
        total_rows - missing_count
    )

    missing_percentage = (
        missing_count / total_rows * 100
        if total_rows > 0
        else 0.0
    )

    completeness_ratio = (
        non_missing_count / total_rows
        if total_rows > 0
        else 0.0
    )

    unique_count = int(
        dataframe[column_name].nunique(
            dropna=True
        )
    )

    is_critical = (
        column_name
        in CRITICAL_COLUMNS.get(dataset_name, [])
    )

    recommended_action = "RETAIN"

    if (
        completeness_ratio < COLUMN_DROP_THRESHOLD
        and not is_critical
    ):
        recommended_action = (
            "REVIEW_FOR_DROP_OR_BUSINESS_RULE"
        )

    if (
        completeness_ratio < COLUMN_DROP_THRESHOLD
        and is_critical
    ):
        recommended_action = (
            "CRITICAL_REVIEW_REQUIRED"
        )

    return {
        "record_type": "COLUMN",
        "dataset": dataset_name,
        "column": column_name,
        "row_count": total_rows,
        "column_count": len(dataframe.columns),
        "missing_count": missing_count,
        "non_missing_count": non_missing_count,
        "missing_percentage": round(
            missing_percentage,
            2,
        ),
        "completeness_score": round(
            completeness_ratio * 100,
            2,
        ),
        "unique_count": unique_count,
        "duplicate_rows": "",
        "duplicate_percentage": "",
        "is_critical": is_critical,
        "quality_status": classify_quality_status(
            completeness_ratio
        ),
        "recommended_action": recommended_action,
    }


def profile_dataset(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> tuple[dict, list[dict]]:
    """
    Create dataset-level and column-level profiles.
    """

    total_rows = len(dataframe)
    total_columns = len(dataframe.columns)

    total_cells = (
        total_rows * total_columns
    )

    total_missing = int(
        dataframe.isna().sum().sum()
    )

    complete_cells = (
        total_cells - total_missing
    )

    completeness_ratio = (
        complete_cells / total_cells
        if total_cells > 0
        else 0.0
    )

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    duplicate_percentage = (
        duplicate_rows / total_rows * 100
        if total_rows > 0
        else 0.0
    )

    dataset_record = {
        "record_type": "DATASET",
        "dataset": dataset_name,
        "column": "",
        "row_count": total_rows,
        "column_count": total_columns,
        "missing_count": total_missing,
        "non_missing_count": complete_cells,
        "missing_percentage": round(
            (
                total_missing / total_cells * 100
                if total_cells > 0
                else 0.0
            ),
            2,
        ),
        "completeness_score": round(
            completeness_ratio * 100,
            2,
        ),
        "unique_count": "",
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round(
            duplicate_percentage,
            2,
        ),
        "is_critical": "",
        "quality_status": classify_quality_status(
            completeness_ratio
        ),
        "recommended_action": (
            "CONTINUE"
            if completeness_ratio
            >= QUALITY_STATUS_WARNING
            else "REVIEW_DATASET"
        ),
    }

    column_records = [
        profile_column(
            dataframe,
            dataset_name,
            column,
        )
        for column in dataframe.columns
    ]

    logger.info(
        "Profiling completed for %s | "
        "Rows: %d | Columns: %d | "
        "Completeness: %.2f%% | Duplicates: %d",
        dataset_name,
        total_rows,
        total_columns,
        completeness_ratio * 100,
        duplicate_rows,
    )

    return dataset_record, column_records


def profile_datasets(
    datasets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Profile all FinMark datasets and save the result.
    """

    all_records = []

    for dataset_name, dataframe in datasets.items():

        dataset_record, column_records = (
            profile_dataset(
                dataframe=dataframe,
                dataset_name=dataset_name,
            )
        )

        all_records.append(dataset_record)
        all_records.extend(column_records)

    report = pd.DataFrame(all_records)

    report.to_csv(
        DATA_QUALITY_FILE,
        index=False,
    )

    logger.info(
        "Data-quality report saved to: %s",
        DATA_QUALITY_FILE,
    )

    print("\nDATA QUALITY SUMMARY")
    print("-" * 95)

    dataset_summary = report[
        report["record_type"] == "DATASET"
    ][
        [
            "dataset",
            "row_count",
            "column_count",
            "missing_count",
            "completeness_score",
            "duplicate_rows",
            "quality_status",
        ]
    ]

    print(
        dataset_summary.to_string(
            index=False
        )
    )

    print("-" * 95)

    return report