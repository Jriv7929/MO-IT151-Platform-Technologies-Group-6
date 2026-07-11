"""
Business analytics layer for the FinMark data pipeline.

Responsibilities:
- Generate executive business KPIs
- Analyze customer and event activity
- Calculate data-quality metrics
- Calculate a prototype pipeline-health score
- Produce a Power BI-ready dataset
- Respect degraded-mode restrictions
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from config import (
    ANALYTICS_DETAIL_FILE,
    BUSINESS_KPI_FILE,
    EXECUTIVE_SUMMARY_FILE,
    PIPELINE_HEALTH_FILE,
    POWERBI_DATASET_FILE,
)
from logger_config import get_logger


logger = get_logger()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value into a safe numeric value.
    """

    if value is None or pd.isna(value):
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def add_kpi(
    records: list[dict],
    category: str,
    metric: str,
    value: Any,
    unit: str = "",
    source: str = "",
    status: str = "AVAILABLE",
    description: str = "",
) -> None:
    """
    Add one KPI to the business KPI report.
    """

    records.append(
        {
            "category": category,
            "metric": metric,
            "value": value,
            "unit": unit,
            "source": source,
            "status": status,
            "description": description,
        }
    )


# ============================================================
# BUSINESS KPI FUNCTIONS
# ============================================================

def calculate_sales_kpis(
    marketing_summary: pd.DataFrame,
    monthly_sales: pd.DataFrame,
) -> list[dict]:
    """
    Calculate financial KPIs using Marketing Summary.

    Marketing Summary remains an independent trusted source,
    even when Event Logs financial amounts are disabled.
    """

    records: list[dict] = []

    dataframe = marketing_summary.copy()

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    numeric_columns = [
        "total_sales",
        "users_active",
        "new_customers",
        "sales_per_active_user",
    ]

    for column in numeric_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

    total_sales = dataframe["total_sales"].sum(
        skipna=True
    )

    average_daily_sales = dataframe[
        "total_sales"
    ].mean()

    median_daily_sales = dataframe[
        "total_sales"
    ].median()

    maximum_daily_sales = dataframe[
        "total_sales"
    ].max()

    minimum_daily_sales = dataframe[
        "total_sales"
    ].min()

    average_active_users = dataframe[
        "users_active"
    ].mean()

    total_new_customers = dataframe[
        "new_customers"
    ].sum(skipna=True)

    average_sales_per_user = dataframe[
        "sales_per_active_user"
    ].mean()

    add_kpi(
        records,
        category="Financial",
        metric="Total Sales",
        value=round(total_sales, 2),
        unit="currency",
        source="marketing_summary",
        description=(
            "Total sales across all available reporting days."
        ),
    )

    add_kpi(
        records,
        category="Financial",
        metric="Average Daily Sales",
        value=round(average_daily_sales, 2),
        unit="currency",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Financial",
        metric="Median Daily Sales",
        value=round(median_daily_sales, 2),
        unit="currency",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Financial",
        metric="Highest Daily Sales",
        value=round(maximum_daily_sales, 2),
        unit="currency",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Financial",
        metric="Lowest Daily Sales",
        value=round(minimum_daily_sales, 2),
        unit="currency",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Customer",
        metric="Average Active Users",
        value=round(average_active_users, 2),
        unit="users",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Customer",
        metric="Total New Customers",
        value=round(total_new_customers, 0),
        unit="customers",
        source="marketing_summary",
    )

    add_kpi(
        records,
        category="Financial",
        metric="Average Sales per Active User",
        value=round(average_sales_per_user, 2),
        unit="currency per user",
        source="marketing_summary",
    )

    valid_sales_rows = dataframe.dropna(
        subset=["date", "total_sales"]
    )

    if not valid_sales_rows.empty:

        best_day_row = valid_sales_rows.loc[
            valid_sales_rows[
                "total_sales"
            ].idxmax()
        ]

        add_kpi(
            records,
            category="Financial",
            metric="Best Sales Date",
            value=best_day_row["date"].strftime(
                "%Y-%m-%d"
            ),
            unit="date",
            source="marketing_summary",
        )

    if not monthly_sales.empty:

        best_month_row = monthly_sales.loc[
            monthly_sales[
                "total_sales"
            ].idxmax()
        ]

        add_kpi(
            records,
            category="Financial",
            metric="Best Performing Month",
            value=best_month_row["month"],
            unit="month",
            source="monthly_sales_summary",
        )

        add_kpi(
            records,
            category="Financial",
            metric="Best Month Sales",
            value=round(
                best_month_row["total_sales"],
                2,
            ),
            unit="currency",
            source="monthly_sales_summary",
        )

    return records


def calculate_activity_kpis(
    event_logs: pd.DataFrame,
) -> list[dict]:
    """
    Calculate customer-behavior and event KPIs.
    """

    records: list[dict] = []

    dataframe = event_logs.copy()

    total_events = len(dataframe)

    unique_users = dataframe[
        "user_id"
    ].nunique(dropna=True)

    transaction_events = int(
        dataframe["is_transaction"].sum()
    )

    behavioral_events = int(
        dataframe["is_behavioral"].sum()
    )

    peak_hour_events = int(
        dataframe["peak_hour_flag"].sum()
    )

    peak_hour_percentage = (
        peak_hour_events / total_events * 100
        if total_events > 0
        else 0.0
    )

    event_counts = (
        dataframe["event_type"]
        .value_counts(dropna=True)
    )

    top_event_type = (
        event_counts.index[0]
        if not event_counts.empty
        else "Unavailable"
    )

    top_event_count = (
        int(event_counts.iloc[0])
        if not event_counts.empty
        else 0
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Processed Events",
        value=total_events,
        unit="events",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Unique Users",
        value=unique_users,
        unit="users",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Behavioral Events",
        value=behavioral_events,
        unit="events",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Valid Transaction Events",
        value=transaction_events,
        unit="events",
        source="event_logs_clean",
        description=(
            "Transaction events remaining after quarantine."
        ),
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Peak-Hour Events",
        value=peak_hour_events,
        unit="events",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Peak-Hour Event Percentage",
        value=round(peak_hour_percentage, 2),
        unit="percent",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Most Frequent Event Type",
        value=top_event_type,
        unit="event type",
        source="event_logs_clean",
    )

    add_kpi(
        records,
        category="Customer Activity",
        metric="Most Frequent Event Count",
        value=top_event_count,
        unit="events",
        source="event_logs_clean",
    )

    return records


# ============================================================
# DATA-QUALITY AND HEALTH FUNCTIONS
# ============================================================

def calculate_adjusted_completeness(
    datasets: dict[str, pd.DataFrame],
) -> float:
    """
    Calculate completeness while treating valid behavioral
    amount nulls as acceptable business values.

    This avoids unfairly penalizing events such as login,
    search, or page_view for having no transaction amount.
    """

    total_cells = 0
    invalid_missing_cells = 0

    for dataset_name, dataframe in (
        datasets.items()
    ):

        total_cells += (
            len(dataframe)
            * len(dataframe.columns)
        )

        missing_mask = dataframe.isna()

        if (
            dataset_name == "event_logs"
            and "amount_status"
            in dataframe.columns
            and "amount" in dataframe.columns
        ):
            valid_business_nulls = (
                dataframe["amount"].isna()
                & dataframe[
                    "amount_status"
                ].eq("not_applicable")
            )

            missing_count = int(
                missing_mask.sum().sum()
            )

            missing_count -= int(
                valid_business_nulls.sum()
            )

        else:
            missing_count = int(
                missing_mask.sum().sum()
            )

        invalid_missing_cells += missing_count

    if total_cells == 0:
        return 0.0

    completeness = (
        total_cells - invalid_missing_cells
    ) / total_cells * 100

    return round(completeness, 2)


def calculate_pipeline_health(
    transformed_datasets: dict[
        str,
        pd.DataFrame,
    ],
    validation_report: pd.DataFrame,
    cleaning_report: pd.DataFrame,
    storage_report: pd.DataFrame,
    fallback_result: Any,
    quarantined_rows: int,
    original_event_rows: int,
) -> tuple[pd.DataFrame, dict]:
    """
    Calculate factual health indicators and a transparent
    prototype pipeline-health score.

    Prototype formula:
    - 45% adjusted completeness
    - 25% row retention
    - 20% validation score
    - 10% storage success rate
    """

    adjusted_completeness = (
        calculate_adjusted_completeness(
            transformed_datasets
        )
    )

    processed_event_rows = len(
        transformed_datasets["event_logs"]
    )

    retention_rate = (
        processed_event_rows
        / original_event_rows
        * 100
        if original_event_rows > 0
        else 0.0
    )

    warning_count = int(
        validation_report[
            "warning_count"
        ].sum()
    )

    error_count = int(
        validation_report[
            "error_count"
        ].sum()
    )

    validation_score = max(
        0.0,
        100.0
        - warning_count * 5
        - error_count * 20,
    )

    if storage_report.empty:
        storage_success_rate = 0.0

    else:
        storage_success_rate = (
            storage_report["status"]
            .eq("SAVED")
            .mean()
            * 100
        )

    health_score = (
        adjusted_completeness * 0.45
        + retention_rate * 0.25
        + validation_score * 0.20
        + storage_success_rate * 0.10
    )

    health_score = round(
        health_score,
        2,
    )

    if health_score >= 90:
        health_status = "HEALTHY"

    elif health_score >= 75:
        health_status = "WARNING"

    else:
        health_status = "CRITICAL"

    metrics = [
        {
            "metric": "Adjusted Completeness",
            "value": adjusted_completeness,
            "unit": "percent",
        },
        {
            "metric": "Event Row Retention",
            "value": round(
                retention_rate,
                2,
            ),
            "unit": "percent",
        },
        {
            "metric": "Validation Score",
            "value": round(
                validation_score,
                2,
            ),
            "unit": "percent",
        },
        {
            "metric": "Storage Success Rate",
            "value": round(
                storage_success_rate,
                2,
            ),
            "unit": "percent",
        },
        {
            "metric": "Quarantined Rows",
            "value": quarantined_rows,
            "unit": "rows",
        },
        {
            "metric": "Validation Warnings",
            "value": warning_count,
            "unit": "warnings",
        },
        {
            "metric": "Validation Errors",
            "value": error_count,
            "unit": "errors",
        },
        {
            "metric": "Pipeline Health Score",
            "value": health_score,
            "unit": "score out of 100",
        },
    ]

    health_report = pd.DataFrame(
        metrics
    )

    summary = {
        "pipeline_health_score": (
            health_score
        ),
        "pipeline_health_status": (
            health_status
        ),
        "adjusted_completeness": (
            adjusted_completeness
        ),
        "retention_rate": round(
            retention_rate,
            2,
        ),
        "validation_score": round(
            validation_score,
            2,
        ),
        "storage_success_rate": round(
            storage_success_rate,
            2,
        ),
        "quarantined_rows": (
            quarantined_rows
        ),
        "pipeline_mode": (
            fallback_result.pipeline_mode
        ),
        "event_log_financial_kpis_enabled":
            fallback_result
            .financial_kpis_enabled,
    }

    return health_report, summary


# ============================================================
# POWER BI DATASET
# ============================================================

def create_powerbi_dataset(
    curated_datasets: dict[
        str,
        pd.DataFrame,
    ],
) -> pd.DataFrame:
    """
    Create one date-based dataset for Power BI.

    Daily sales data is joined with daily activity data.
    """

    daily_sales = curated_datasets[
        "daily_sales_summary"
    ].copy()

    daily_activity = curated_datasets[
        "daily_activity_summary"
    ].copy()

    daily_sales["date"] = pd.to_datetime(
        daily_sales["date"],
        errors="coerce",
    )

    daily_activity["event_date"] = (
        pd.to_datetime(
            daily_activity["event_date"],
            errors="coerce",
        )
    )

    powerbi_dataset = daily_sales.merge(
        daily_activity,
        left_on="date",
        right_on="event_date",
        how="left",
    )

    if "event_date" in powerbi_dataset:
        powerbi_dataset = (
            powerbi_dataset.drop(
                columns=["event_date"]
            )
        )

    activity_columns = [
        "total_events",
        "unique_users",
        "transaction_events",
        "behavioral_events",
        "peak_hour_events",
    ]

    for column in activity_columns:
        if column in powerbi_dataset.columns:
            powerbi_dataset[column] = (
                powerbi_dataset[column]
                .fillna(0)
                .astype(int)
            )

    powerbi_dataset["year"] = (
        powerbi_dataset["date"].dt.year
    )

    powerbi_dataset["month"] = (
        powerbi_dataset["date"]
        .dt.to_period("M")
        .astype("string")
    )

    powerbi_dataset["day_name"] = (
        powerbi_dataset["date"]
        .dt.day_name()
    )

    powerbi_dataset.to_csv(
        POWERBI_DATASET_FILE,
        index=False,
    )

    return powerbi_dataset


# ============================================================
# MAIN ANALYTICS FUNCTION
# ============================================================

def generate_business_analytics(
    transformed_datasets: dict[
        str,
        pd.DataFrame,
    ],
    curated_datasets: dict[
        str,
        pd.DataFrame,
    ],
    validation_report: pd.DataFrame,
    cleaning_report: pd.DataFrame,
    storage_report: pd.DataFrame,
    fallback_result: Any,
    quarantined_datasets: dict[
        str,
        pd.DataFrame,
    ],
    original_event_rows: int,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Run the complete Stage 5 analytics layer.

    Returns
    -------
    business_kpis
    health_report
    executive_summary
    powerbi_dataset
    """

    event_logs = transformed_datasets[
        "event_logs"
    ]

    marketing_summary = (
        transformed_datasets[
            "marketing_summary"
        ]
    )

    monthly_sales = curated_datasets[
        "monthly_sales_summary"
    ]

    kpi_records: list[dict] = []

    kpi_records.extend(
        calculate_sales_kpis(
            marketing_summary,
            monthly_sales,
        )
    )

    kpi_records.extend(
        calculate_activity_kpis(
            event_logs
        )
    )

    quarantined_rows = sum(
        len(dataframe)
        for dataframe
        in quarantined_datasets.values()
    )

    health_report, health_summary = (
        calculate_pipeline_health(
            transformed_datasets=
                transformed_datasets,
            validation_report=
                validation_report,
            cleaning_report=
                cleaning_report,
            storage_report=
                storage_report,
            fallback_result=
                fallback_result,
            quarantined_rows=
                quarantined_rows,
            original_event_rows=
                original_event_rows,
        )
    )

    add_kpi(
        kpi_records,
        category="Pipeline Health",
        metric="Pipeline Health Score",
        value=health_summary[
            "pipeline_health_score"
        ],
        unit="score out of 100",
        source="pipeline_health",
    )

    add_kpi(
        kpi_records,
        category="Data Quality",
        metric="Adjusted Completeness",
        value=health_summary[
            "adjusted_completeness"
        ],
        unit="percent",
        source="pipeline_health",
    )

    add_kpi(
        kpi_records,
        category="Data Quality",
        metric="Quarantined Records",
        value=quarantined_rows,
        unit="rows",
        source="quarantine_zone",
    )

    business_kpis = pd.DataFrame(
        kpi_records
    )

    business_kpis.to_csv(
        BUSINESS_KPI_FILE,
        index=False,
    )

    health_report.to_csv(
        PIPELINE_HEALTH_FILE,
        index=False,
    )

    powerbi_dataset = (
        create_powerbi_dataset(
            curated_datasets
        )
    )

    total_sales_row = business_kpis[
        business_kpis["metric"]
        == "Total Sales"
    ]

    total_sales = (
        total_sales_row.iloc[0]["value"]
        if not total_sales_row.empty
        else np.nan
    )

    executive_summary = pd.DataFrame(
        [
            {
                "pipeline_mode":
                    health_summary[
                        "pipeline_mode"
                    ],
                "pipeline_health_status":
                    health_summary[
                        "pipeline_health_status"
                    ],
                "pipeline_health_score":
                    health_summary[
                        "pipeline_health_score"
                    ],
                "adjusted_completeness":
                    health_summary[
                        "adjusted_completeness"
                    ],
                "event_row_retention_rate":
                    health_summary[
                        "retention_rate"
                    ],
                "records_processed":
                    len(event_logs),
                "records_quarantined":
                    quarantined_rows,
                "total_sales":
                    total_sales,
                "unique_users":
                    event_logs[
                        "user_id"
                    ].nunique(
                        dropna=True
                    ),
                "event_log_financial_kpis_enabled":
                    health_summary[
                        "event_log_financial_kpis_enabled"
                    ],
                "marketing_sales_kpis_available":
                    True,
            }
        ]
    )

    executive_summary.to_csv(
        EXECUTIVE_SUMMARY_FILE,
        index=False,
    )

    analytics_detail = pd.concat(
        [
            business_kpis.assign(
                report_type="BUSINESS_KPI"
            ),
            health_report.rename(
                columns={
                    "metric": "metric",
                    "value": "value",
                    "unit": "unit",
                }
            ).assign(
                category="Pipeline Health",
                source="pipeline_monitor",
                status="AVAILABLE",
                description="",
                report_type="HEALTH_METRIC",
            ),
        ],
        ignore_index=True,
        sort=False,
    )

    analytics_detail.to_csv(
        ANALYTICS_DETAIL_FILE,
        index=False,
    )

    logger.info(
        "Business analytics completed | "
        "KPIs: %d | Health score: %.2f",
        len(business_kpis),
        health_summary[
            "pipeline_health_score"
        ],
    )

    print("\nBUSINESS ANALYTICS SUMMARY")
    print("-" * 86)

    summary_metrics = business_kpis[
        business_kpis["metric"].isin(
            [
                "Total Sales",
                "Average Daily Sales",
                "Average Active Users",
                "Total New Customers",
                "Processed Events",
                "Unique Users",
                "Quarantined Records",
                "Pipeline Health Score",
            ]
        )
    ][
        [
            "category",
            "metric",
            "value",
            "unit",
        ]
    ]

    print(
        summary_metrics.to_string(
            index=False
        )
    )

    print("-" * 86)
    print(
        "Pipeline Health Status: "
        f"{health_summary['pipeline_health_status']}"
    )
    print(
        "Pipeline Health Score: "
        f"{health_summary['pipeline_health_score']}"
    )
    print(
        "Event-log Financial KPIs Enabled: "
        f"{fallback_result.financial_kpis_enabled}"
    )
    print(
        "Marketing Sales KPIs Available: True"
    )
    print("-" * 86)

    return (
        business_kpis,
        health_report,
        executive_summary,
        powerbi_dataset,
    )