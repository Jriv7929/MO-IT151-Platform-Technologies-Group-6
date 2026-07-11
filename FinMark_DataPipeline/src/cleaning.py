"""
Cleaning layer for the FinMark data pipeline.

Responsibilities:
- Remove exact duplicate records
- Standardize text values
- Retain documented business columns
- Preserve pipeline quality fields
- Avoid replacing valid null values with zero
- Produce a cleaning report
"""

from __future__ import annotations

import pandas as pd

from config import (
    CLEANING_REPORT_FILE,
    REQUIRED_COLUMNS,
)
from logger_config import get_logger


logger = get_logger()


# Additional columns created by the fallback layer
QUALITY_COLUMNS = {
    "event_logs": [
        "event_category",
        "amount_status",
    ],
    "marketing_summary": [],
    "trend_report": [],
}


def standardize_text_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove unnecessary leading and trailing spaces
    from text columns.

    Missing values remain missing.
    """

    dataframe = dataframe.copy()

    text_columns = dataframe.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        dataframe[column] = dataframe[column].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    return dataframe


def retain_documented_columns(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Keep only documented business fields and pipeline
    quality fields.

    Unexpected placeholder columns are removed here.
    """

    allowed_columns = (
        REQUIRED_COLUMNS.get(dataset_name, [])
        + QUALITY_COLUMNS.get(dataset_name, [])
    )

    existing_columns = [
        column
        for column in allowed_columns
        if column in dataframe.columns
    ]

    removed_columns = [
        column
        for column in dataframe.columns
        if column not in existing_columns
    ]

    if removed_columns:
        logger.info(
            "%s: Removing %d undocumented columns.",
            dataset_name,
            len(removed_columns),
        )

    return dataframe[existing_columns].copy()


def clean_dataset(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> tuple[pd.DataFrame, dict]:
    """
    Clean one dataset and generate cleaning statistics.

    Parameters
    ----------
    dataframe:
        Dataset to clean.

    dataset_name:
        Logical dataset name.

    Returns
    -------
    tuple
        cleaned_dataframe:
            Cleaned dataset.

        cleaning_record:
            Summary of cleaning actions.
    """

    dataframe = dataframe.copy()

    rows_before = len(dataframe)
    columns_before = len(dataframe.columns)

    duplicate_count = int(
        dataframe.duplicated().sum()
    )

    # Remove exact duplicate rows
    dataframe = (
        dataframe
        .drop_duplicates()
        .copy()
    )

    # Standardize text values
    dataframe = standardize_text_columns(
        dataframe
    )

    # Remove undocumented placeholder columns
    dataframe = retain_documented_columns(
        dataframe,
        dataset_name,
    )

    rows_after = len(dataframe)
    columns_after = len(dataframe.columns)

    cleaning_record = {
        "dataset": dataset_name,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "duplicates_removed": duplicate_count,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": (
            columns_before - columns_after
        ),
        "remaining_missing_values": int(
            dataframe.isna().sum().sum()
        ),
        "status": "CLEANED",
    }

    logger.info(
        "Cleaning completed for %s | "
        "Rows: %d -> %d | "
        "Columns: %d -> %d | "
        "Duplicates removed: %d | "
        "Remaining missing values: %d",
        dataset_name,
        rows_before,
        rows_after,
        columns_before,
        columns_after,
        duplicate_count,
        cleaning_record[
            "remaining_missing_values"
        ],
    )

    return dataframe, cleaning_record


def clean_datasets(
    datasets: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, pd.DataFrame],
    pd.DataFrame,
]:
    """
    Clean all FinMark datasets.

    Parameters
    ----------
    datasets:
        Dictionary containing all datasets.

    Returns
    -------
    tuple
        cleaned_datasets:
            Dictionary of cleaned datasets.

        cleaning_report:
            DataFrame containing cleaning statistics.
    """

    cleaned_datasets = {}
    cleaning_records = []

    for dataset_name, dataframe in datasets.items():

        cleaned_dataframe, cleaning_record = (
            clean_dataset(
                dataframe=dataframe,
                dataset_name=dataset_name,
            )
        )

        cleaned_datasets[dataset_name] = (
            cleaned_dataframe
        )

        cleaning_records.append(
            cleaning_record
        )

    cleaning_report = pd.DataFrame(
        cleaning_records
    )

    cleaning_report.to_csv(
        CLEANING_REPORT_FILE,
        index=False,
    )

    logger.info(
        "Cleaning report saved to: %s",
        CLEANING_REPORT_FILE,
    )

    print("\nCLEANING SUMMARY")
    print("-" * 100)

    display_columns = [
        "dataset",
        "rows_before",
        "rows_after",
        "duplicates_removed",
        "columns_before",
        "columns_after",
        "remaining_missing_values",
    ]

    print(
        cleaning_report[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("-" * 100)

    return cleaned_datasets, cleaning_report