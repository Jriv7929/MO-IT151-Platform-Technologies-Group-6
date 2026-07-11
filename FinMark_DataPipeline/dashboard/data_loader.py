from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIRECTORY = PROJECT_ROOT / "data"
RAW_DIRECTORY = DATA_DIRECTORY / "raw"
CURATED_DIRECTORY = DATA_DIRECTORY / "curated"
OUTPUT_DIRECTORY = PROJECT_ROOT / "output"


def load_csv(
    file_path: Path,
    required: bool = False,
) -> pd.DataFrame:
    """
    Safely loads a CSV file.

    Missing optional files return an empty DataFrame.
    Required files raise a clear error.
    """

    if not file_path.exists():
        if required:
            raise FileNotFoundError(
                f"Required dashboard file not found: {file_path}"
            )

        return pd.DataFrame()

    try:
        return pd.read_csv(file_path)

    except Exception as error:
        if required:
            raise RuntimeError(
                f"Unable to read dashboard file: {file_path}"
            ) from error

        return pd.DataFrame()


def find_existing_file(
    directories: list[Path],
    filenames: list[str],
) -> Path | None:
    """
    Returns the first matching file found in the supplied directories.
    """

    for directory in directories:
        if not directory.exists():
            continue

        for filename in filenames:
            file_path = directory / filename

            if file_path.exists():
                return file_path

    return None


def load_first_available(
    directories: list[Path],
    filenames: list[str],
) -> pd.DataFrame:
    """
    Loads the first available matching CSV file.
    """

    file_path = find_existing_file(
        directories=directories,
        filenames=filenames,
    )

    if file_path is None:
        return pd.DataFrame()

    return load_csv(file_path)


def normalize_datetime_column(
    dataframe: pd.DataFrame,
    possible_columns: list[str],
) -> pd.DataFrame:
    """
    Converts the first matching date or datetime column.
    """

    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    for column in possible_columns:
        if column in result.columns:
            result[column] = pd.to_datetime(
                result[column],
                errors="coerce",
            )

            break

    return result


def normalize_numeric_column(
    dataframe: pd.DataFrame,
    possible_columns: list[str],
) -> pd.DataFrame:
    """
    Converts the first matching numeric column.

    Currency symbols and commas are removed where necessary.
    """

    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    for column in possible_columns:
        if column in result.columns:
            cleaned_values = (
                result[column]
                .astype(str)
                .str.replace("PHP", "", regex=False)
                .str.replace("₱", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )

            result[column] = pd.to_numeric(
                cleaned_values,
                errors="coerce",
            )

            break

    return result


def prepare_marketing_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepares the marketing dataset for dashboard charts.
    """

    if dataframe.empty:
        return dataframe

    result = normalize_datetime_column(
        dataframe,
        [
            "date",
            "marketing_date",
            "record_date",
        ],
    )

    result = normalize_numeric_column(
        result,
        [
            "total_sales",
            "sales",
            "revenue",
            "sales_amount",
        ],
    )

    result = normalize_numeric_column(
        result,
        [
            "users_active",
            "active_users",
            "daily_active_users",
        ],
    )

    result = normalize_numeric_column(
        result,
        [
            "new_customers",
            "customer_count",
        ],
    )

    return result


def prepare_event_logs(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepares event-log fields for analysis.
    """

    if dataframe.empty:
        return dataframe

    result = normalize_datetime_column(
        dataframe,
        [
            "event_time",
            "event_timestamp",
            "timestamp",
            "event_date",
        ],
    )

    result = normalize_numeric_column(
        result,
        [
            "amount",
            "transaction_amount",
            "sales_amount",
        ],
    )

    return result


def prepare_trend_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepares weekly trend data.
    """

    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    numeric_columns = [
        "avg_users",
        "average_users",
        "sales_growth_rate",
        "growth_rate",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

    return result


def load_dashboard_data() -> dict[str, Any]:
    """
    Loads all datasets required by the Stage 7 dashboard.
    """

    source_directories = [
        CURATED_DIRECTORY,
        DATA_DIRECTORY / "processed",
        DATA_DIRECTORY / "clean",
        DATA_DIRECTORY / "transformed",
        RAW_DIRECTORY,
    ]

    event_logs = load_first_available(
        directories=source_directories,
        filenames=[
            "event_logs_curated.csv",
            "event_logs_processed.csv",
            "event_logs_cleaned.csv",
            "event_logs_transformed.csv",
            "event_logs.csv",
        ],
    )

    marketing_summary = load_first_available(
        directories=source_directories,
        filenames=[
            "marketing_summary_curated.csv",
            "marketing_summary_processed.csv",
            "marketing_summary_cleaned.csv",
            "marketing_summary_transformed.csv",
            "marketing_summary.csv",
        ],
    )

    trend_report = load_first_available(
        directories=source_directories,
        filenames=[
            "trend_report_curated.csv",
            "trend_report_processed.csv",
            "trend_report_cleaned.csv",
            "trend_report_transformed.csv",
            "trend_report.csv",
        ],
    )

    data = {
        "event_logs": prepare_event_logs(event_logs),
        "marketing_summary": prepare_marketing_data(
            marketing_summary
        ),
        "trend_report": prepare_trend_data(trend_report),
        "business_kpis": load_csv(
            OUTPUT_DIRECTORY / "business_kpis.csv"
        ),
        "pipeline_health": load_csv(
            OUTPUT_DIRECTORY / "pipeline_health_metrics.csv"
        ),
        "executive_summary": load_csv(
            OUTPUT_DIRECTORY / "executive_summary.csv"
        ),
        "dashboard_alerts": load_csv(
            OUTPUT_DIRECTORY / "dashboard_alerts.csv"
        ),
        "dashboard_status": load_csv(
            OUTPUT_DIRECTORY / "dashboard_status.csv"
        ),
        "powerbi_dataset": load_csv(
            OUTPUT_DIRECTORY / "powerbi_dashboard_dataset.csv"
        ),
    }

    return data