"""
Transformation layer for the FinMark data pipeline.

Responsibilities:
- Convert datetime and numeric fields safely
- Create analytical date attributes
- Create event classifications
- Create transaction indicators
- Generate daily and monthly summaries
- Prepare curated datasets for analytics
"""

from __future__ import annotations

import pandas as pd

from config import (
    DAILY_ACTIVITY_FILE,
    DAILY_SALES_FILE,
    EVENT_CLASSIFICATION_FILE,
    EVENT_TYPE_SUMMARY_FILE,
    MONTHLY_SALES_FILE,
)
from logger_config import get_logger


logger = get_logger()


def transform_event_logs(
    event_logs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform the Event Logs dataset.
    """

    dataframe = event_logs.copy()

    dataframe["event_time"] = pd.to_datetime(
        dataframe["event_time"],
        errors="coerce",
    )

    dataframe["amount"] = pd.to_numeric(
        dataframe["amount"],
        errors="coerce",
    )

    dataframe["event_date"] = (
        dataframe["event_time"].dt.date
    )

    dataframe["event_hour"] = (
        dataframe["event_time"].dt.hour
    )

    dataframe["event_day_name"] = (
        dataframe["event_time"].dt.day_name()
    )

    dataframe["event_month"] = (
        dataframe["event_time"]
        .dt.to_period("M")
        .astype("string")
    )

    dataframe["event_week"] = (
        dataframe["event_time"]
        .dt.to_period("W")
        .astype("string")
    )

    dataframe["is_transaction"] = (
        dataframe["event_category"]
        .eq("transaction")
    )

    dataframe["is_behavioral"] = (
        dataframe["event_category"]
        .eq("behavioral")
    )

    dataframe["peak_hour_flag"] = (
        dataframe["event_hour"]
        .between(9, 21, inclusive="both")
    )

    logger.info(
        "Event Logs transformation completed | "
        "Rows: %d | Invalid dates: %d",
        len(dataframe),
        int(dataframe["event_time"].isna().sum()),
    )

    return dataframe


def transform_marketing_summary(
    marketing_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform the Marketing Summary dataset.
    """

    dataframe = marketing_summary.copy()

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    dataframe["report_generated"] = pd.to_datetime(
        dataframe["report_generated"],
        errors="coerce",
    )

    numeric_columns = [
        "users_active",
        "total_sales",
        "new_customers",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe["month"] = (
        dataframe["date"]
        .dt.to_period("M")
        .astype("string")
    )

    dataframe["week"] = (
        dataframe["date"]
        .dt.to_period("W")
        .astype("string")
    )

    dataframe["day_name"] = (
        dataframe["date"].dt.day_name()
    )

    dataframe["sales_per_active_user"] = (
        dataframe["total_sales"]
        .div(dataframe["users_active"])
        .where(dataframe["users_active"] > 0)
    )

    logger.info(
        "Marketing Summary transformation completed | "
        "Rows: %d | Invalid dates: %d",
        len(dataframe),
        int(dataframe["date"].isna().sum()),
    )

    return dataframe


def transform_trend_report(
    trend_report: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform ISO week values such as 2023-W21.
    """

    dataframe = trend_report.copy()

    dataframe["avg_users"] = pd.to_numeric(
        dataframe["avg_users"],
        errors="coerce",
    )

    dataframe["sales_growth_rate"] = pd.to_numeric(
        dataframe["sales_growth_rate"],
        errors="coerce",
    )

    dataframe["week_start_date"] = pd.to_datetime(
        dataframe["week"].astype(str) + "-1",
        format="%G-W%V-%u",
        errors="coerce",
    )

    dataframe["year"] = (
        dataframe["week_start_date"].dt.year
    )

    dataframe["month"] = (
        dataframe["week_start_date"]
        .dt.to_period("M")
        .astype("string")
    )

    logger.info(
        "Trend Report transformation completed | "
        "Rows: %d | Invalid weeks: %d",
        len(dataframe),
        int(
            dataframe["week_start_date"]
            .isna()
            .sum()
        ),
    )

    return dataframe


def create_event_classification_report(
    event_logs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize event categories and amount handling.
    """

    report = (
        event_logs
        .groupby(
            [
                "event_type",
                "event_category",
                "amount_status",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="record_count")
        .sort_values(
            by="record_count",
            ascending=False,
        )
    )

    report.to_csv(
        EVENT_CLASSIFICATION_FILE,
        index=False,
    )

    return report


def create_daily_activity_summary(
    event_logs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create daily user and event activity metrics.
    """

    valid_dates = event_logs.dropna(
        subset=["event_date"]
    ).copy()

    summary = (
        valid_dates
        .groupby("event_date")
        .agg(
            total_events=(
                "event_type",
                "size",
            ),
            unique_users=(
                "user_id",
                "nunique",
            ),
            transaction_events=(
                "is_transaction",
                "sum",
            ),
            behavioral_events=(
                "is_behavioral",
                "sum",
            ),
            peak_hour_events=(
                "peak_hour_flag",
                "sum",
            ),
        )
        .reset_index()
    )

    summary.to_csv(
        DAILY_ACTIVITY_FILE,
        index=False,
    )

    return summary


def create_event_type_summary(
    event_logs: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create event-type-level analytics.
    """

    summary = (
        event_logs
        .groupby(
            [
                "event_type",
                "event_category",
            ],
            dropna=False,
        )
        .agg(
            total_events=(
                "event_type",
                "size",
            ),
            unique_users=(
                "user_id",
                "nunique",
            ),
            valid_amount_count=(
                "amount",
                "count",
            ),
            total_amount=(
                "amount",
                "sum",
            ),
            average_amount=(
                "amount",
                "mean",
            ),
        )
        .reset_index()
    )

    summary.to_csv(
        EVENT_TYPE_SUMMARY_FILE,
        index=False,
    )

    return summary


def create_daily_sales_summary(
    marketing_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create daily sales metrics.
    """

    summary = (
        marketing_summary
        .dropna(subset=["date"])
        [
            [
                "date",
                "users_active",
                "total_sales",
                "new_customers",
                "sales_per_active_user",
            ]
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )

    summary.to_csv(
        DAILY_SALES_FILE,
        index=False,
    )

    return summary


def create_monthly_sales_summary(
    marketing_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create monthly sales metrics.
    """

    summary = (
        marketing_summary
        .dropna(subset=["month"])
        .groupby("month")
        .agg(
            total_sales=(
                "total_sales",
                "sum",
            ),
            average_daily_sales=(
                "total_sales",
                "mean",
            ),
            average_active_users=(
                "users_active",
                "mean",
            ),
            total_new_customers=(
                "new_customers",
                "sum",
            ),
            reporting_days=(
                "date",
                "count",
            ),
        )
        .reset_index()
        .sort_values("month")
    )

    summary.to_csv(
        MONTHLY_SALES_FILE,
        index=False,
    )

    return summary


def transform_datasets(
    datasets: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
]:
    """
    Transform all cleaned datasets and create curated tables.
    """

    transformed_datasets = {
        "event_logs": transform_event_logs(
            datasets["event_logs"]
        ),
        "marketing_summary": (
            transform_marketing_summary(
                datasets["marketing_summary"]
            )
        ),
        "trend_report": transform_trend_report(
            datasets["trend_report"]
        ),
    }

    event_logs = transformed_datasets[
        "event_logs"
    ]

    marketing_summary = transformed_datasets[
        "marketing_summary"
    ]

    curated_datasets = {
        "event_classification_report":
            create_event_classification_report(
                event_logs
            ),
        "daily_activity_summary":
            create_daily_activity_summary(
                event_logs
            ),
        "event_type_summary":
            create_event_type_summary(
                event_logs
            ),
        "daily_sales_summary":
            create_daily_sales_summary(
                marketing_summary
            ),
        "monthly_sales_summary":
            create_monthly_sales_summary(
                marketing_summary
            ),
    }

    print("\nTRANSFORMATION SUMMARY")
    print("-" * 80)

    for name, dataframe in (
        transformed_datasets.items()
    ):
        print(
            f"{name:<25}"
            f"{len(dataframe):>8} rows "
            f"{len(dataframe.columns):>8} columns"
        )

    print("\nCURATED DATASETS")
    print("-" * 80)

    for name, dataframe in (
        curated_datasets.items()
    ):
        print(
            f"{name:<35}"
            f"{len(dataframe):>8} rows"
        )

    print("-" * 80)

    return (
        transformed_datasets,
        curated_datasets,
    )