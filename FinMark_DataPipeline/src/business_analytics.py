from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class BusinessAnalytics:
    """
    Stage 5 – Business Analytics Layer

    Generates:
    1. Business KPI records
    2. Pipeline-health metrics
    3. Executive summary
    4. Power BI-ready dashboard dataset

    The class is designed to continue working even when some datasets
    or expected columns are unavailable.
    """

    def __init__(
        self,
        output_directory: str | Path,
        logger: Any | None = None,
    ) -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logger

    def _log_info(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)

    def _log_warning(self, message: str) -> None:
        if self.logger:
            self.logger.warning(message)

    @staticmethod
    def _find_column(
        dataframe: pd.DataFrame,
        possible_names: list[str],
    ) -> str | None:
        """
        Finds a column using exact or partial case-insensitive matching.
        """

        if dataframe is None or dataframe.empty:
            return None

        normalized_columns = {
            str(column).strip().lower(): column
            for column in dataframe.columns
        }

        for possible_name in possible_names:
            normalized_name = possible_name.strip().lower()

            if normalized_name in normalized_columns:
                return normalized_columns[normalized_name]

        for column in dataframe.columns:
            normalized_column = str(column).strip().lower()

            for possible_name in possible_names:
                normalized_name = possible_name.strip().lower()

                if normalized_name in normalized_column:
                    return column

        return None

    @staticmethod
    def _numeric_series(
        dataframe: pd.DataFrame,
        column: str | None,
    ) -> pd.Series:
        """
        Converts a dataframe column to numeric values.
        """

        if (
            dataframe is None
            or dataframe.empty
            or column is None
            or column not in dataframe.columns
        ):
            return pd.Series(dtype="float64")

        return pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    @staticmethod
    def _datetime_series(
        dataframe: pd.DataFrame,
        column: str | None,
    ) -> pd.Series:
        """
        Converts a dataframe column to datetime values.
        """

        if (
            dataframe is None
            or dataframe.empty
            or column is None
            or column not in dataframe.columns
        ):
            return pd.Series(dtype="datetime64[ns]")

        return pd.to_datetime(
            dataframe[column],
            errors="coerce",
        )

    @staticmethod
    def _safe_divide(
        numerator: float,
        denominator: float,
        default: float = 0.0,
    ) -> float:
        if denominator == 0:
            return default

        return numerator / denominator

    @staticmethod
    def _create_metric(
        category: str,
        metric: str,
        value: float | int | str,
        unit: str,
        source_dataset: str,
        status: str = "AVAILABLE",
        description: str = "",
    ) -> dict[str, Any]:
        return {
            "category": category,
            "metric": metric,
            "value": value,
            "unit": unit,
            "source_dataset": source_dataset,
            "status": status,
            "description": description,
        }

    def calculate_event_log_kpis(
        self,
        event_logs: pd.DataFrame,
        financial_kpis_enabled: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Calculates KPIs from the processed event-log dataset.
        """

        metrics: list[dict[str, Any]] = []

        if event_logs is None:
            event_logs = pd.DataFrame()

        total_records = len(event_logs)

        user_column = self._find_column(
            event_logs,
            [
                "user_id",
                "customer_id",
                "userid",
                "customerid",
                "user",
            ],
        )

        event_column = self._find_column(
            event_logs,
            [
                "event_type",
                "event_name",
                "event",
                "activity_type",
            ],
        )

        transaction_column = self._find_column(
            event_logs,
            [
                "transaction_amount",
                "amount",
                "sales_amount",
                "revenue",
                "order_value",
            ],
        )

        date_column = self._find_column(
            event_logs,
            [
                "event_date",
                "timestamp",
                "event_timestamp",
                "date",
                "created_at",
            ],
        )

        unique_users = 0

        if user_column:
            unique_users = int(
                event_logs[user_column]
                .dropna()
                .astype(str)
                .nunique()
            )

        unique_event_types = 0

        if event_column:
            unique_event_types = int(
                event_logs[event_column]
                .dropna()
                .astype(str)
                .nunique()
            )

        date_values = self._datetime_series(
            event_logs,
            date_column,
        ).dropna()

        active_days = int(date_values.dt.date.nunique()) if not date_values.empty else 0

        average_events_per_day = self._safe_divide(
            total_records,
            active_days,
        )

        average_events_per_user = self._safe_divide(
            total_records,
            unique_users,
        )

        metrics.extend(
            [
                self._create_metric(
                    category="Customer Activity",
                    metric="Processed Events",
                    value=total_records,
                    unit="records",
                    source_dataset="event_logs",
                    description="Total processed event-log records.",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Unique Users",
                    value=unique_users,
                    unit="users",
                    source_dataset="event_logs",
                    description="Number of distinct users in event logs.",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Unique Event Types",
                    value=unique_event_types,
                    unit="event types",
                    source_dataset="event_logs",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Active Event Days",
                    value=active_days,
                    unit="days",
                    source_dataset="event_logs",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Average Events Per Day",
                    value=round(average_events_per_day, 2),
                    unit="events/day",
                    source_dataset="event_logs",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Average Events Per User",
                    value=round(average_events_per_user, 2),
                    unit="events/user",
                    source_dataset="event_logs",
                ),
            ]
        )

        if financial_kpis_enabled and transaction_column:
            transaction_values = self._numeric_series(
                event_logs,
                transaction_column,
            ).dropna()

            total_transaction_value = float(
                transaction_values.sum()
            )

            average_transaction_value = float(
                transaction_values.mean()
            ) if not transaction_values.empty else 0.0

            transaction_count = int(
                transaction_values.gt(0).sum()
            )

            metrics.extend(
                [
                    self._create_metric(
                        category="Financial Performance",
                        metric="Event Log Transaction Value",
                        value=round(total_transaction_value, 2),
                        unit="currency",
                        source_dataset="event_logs",
                    ),
                    self._create_metric(
                        category="Financial Performance",
                        metric="Average Event Transaction Value",
                        value=round(average_transaction_value, 2),
                        unit="currency",
                        source_dataset="event_logs",
                    ),
                    self._create_metric(
                        category="Financial Performance",
                        metric="Event Transaction Count",
                        value=transaction_count,
                        unit="transactions",
                        source_dataset="event_logs",
                    ),
                ]
            )
        else:
            metrics.extend(
                [
                    self._create_metric(
                        category="Financial Performance",
                        metric="Event Log Transaction Value",
                        value=0.0,
                        unit="currency",
                        source_dataset="event_logs",
                        status="DISABLED",
                        description=(
                            "Disabled because transaction data exceeded "
                            "the accepted missing-value threshold."
                        ),
                    ),
                    self._create_metric(
                        category="Financial Performance",
                        metric="Average Event Transaction Value",
                        value=0.0,
                        unit="currency",
                        source_dataset="event_logs",
                        status="DISABLED",
                    ),
                    self._create_metric(
                        category="Financial Performance",
                        metric="Event Transaction Count",
                        value=0,
                        unit="transactions",
                        source_dataset="event_logs",
                        status="DISABLED",
                    ),
                ]
            )

        return metrics

    def calculate_marketing_kpis(
        self,
        marketing_summary: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Calculates business KPIs from the marketing-summary dataset.
        """

        metrics: list[dict[str, Any]] = []

        if marketing_summary is None:
            marketing_summary = pd.DataFrame()

        sales_column = self._find_column(
            marketing_summary,
            [
                "sales",
                "total_sales",
                "revenue",
                "sales_amount",
                "transaction_amount",
            ],
        )

        customer_column = self._find_column(
            marketing_summary,
            [
                "new_customers",
                "customers",
                "customer_count",
                "new_customer",
            ],
        )

        active_user_column = self._find_column(
            marketing_summary,
            [
                "active_users",
                "daily_active_users",
                "monthly_active_users",
                "users",
            ],
        )

        transaction_column = self._find_column(
            marketing_summary,
            [
                "transactions",
                "transaction_count",
                "orders",
                "order_count",
            ],
        )

        conversion_column = self._find_column(
            marketing_summary,
            [
                "conversion_rate",
                "conversion",
            ],
        )

        sales_values = self._numeric_series(
            marketing_summary,
            sales_column,
        ).dropna()

        customer_values = self._numeric_series(
            marketing_summary,
            customer_column,
        ).dropna()

        active_user_values = self._numeric_series(
            marketing_summary,
            active_user_column,
        ).dropna()

        transaction_values = self._numeric_series(
            marketing_summary,
            transaction_column,
        ).dropna()

        conversion_values = self._numeric_series(
            marketing_summary,
            conversion_column,
        ).dropna()

        total_sales = float(sales_values.sum())
        average_daily_sales = (
            float(sales_values.mean())
            if not sales_values.empty
            else 0.0
        )

        highest_daily_sales = (
            float(sales_values.max())
            if not sales_values.empty
            else 0.0
        )

        lowest_daily_sales = (
            float(sales_values.min())
            if not sales_values.empty
            else 0.0
        )

        total_new_customers = int(customer_values.sum()) if not customer_values.empty else 0

        average_new_customers = (
            float(customer_values.mean())
            if not customer_values.empty
            else 0.0
        )

        average_active_users = (
            float(active_user_values.mean())
            if not active_user_values.empty
            else 0.0
        )

        peak_active_users = (
            float(active_user_values.max())
            if not active_user_values.empty
            else 0.0
        )

        total_transactions = (
            int(transaction_values.sum())
            if not transaction_values.empty
            else 0
        )

        average_conversion_rate = (
            float(conversion_values.mean())
            if not conversion_values.empty
            else 0.0
        )

        metrics.extend(
            [
                self._create_metric(
                    category="Sales Performance",
                    metric="Total Sales",
                    value=round(total_sales, 2),
                    unit="currency",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Sales Performance",
                    metric="Average Daily Sales",
                    value=round(average_daily_sales, 2),
                    unit="currency/day",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Sales Performance",
                    metric="Highest Daily Sales",
                    value=round(highest_daily_sales, 2),
                    unit="currency",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Sales Performance",
                    metric="Lowest Daily Sales",
                    value=round(lowest_daily_sales, 2),
                    unit="currency",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Customer Growth",
                    metric="Total New Customers",
                    value=total_new_customers,
                    unit="customers",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Customer Growth",
                    metric="Average New Customers",
                    value=round(average_new_customers, 2),
                    unit="customers/period",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Average Active Users",
                    value=round(average_active_users, 2),
                    unit="users",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Customer Activity",
                    metric="Peak Active Users",
                    value=round(peak_active_users, 2),
                    unit="users",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Sales Performance",
                    metric="Total Transactions",
                    value=total_transactions,
                    unit="transactions",
                    source_dataset="marketing_summary",
                ),
                self._create_metric(
                    category="Marketing Performance",
                    metric="Average Conversion Rate",
                    value=round(average_conversion_rate, 2),
                    unit="percent",
                    source_dataset="marketing_summary",
                ),
            ]
        )

        return metrics

    def calculate_trend_kpis(
        self,
        trend_report: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Calculates trend-related KPIs.
        """

        if trend_report is None:
            trend_report = pd.DataFrame()

        metrics: list[dict[str, Any]] = []

        growth_column = self._find_column(
            trend_report,
            [
                "growth_rate",
                "sales_growth",
                "growth",
                "percentage_change",
            ],
        )

        trend_column = self._find_column(
            trend_report,
            [
                "trend",
                "trend_direction",
                "status",
            ],
        )

        growth_values = self._numeric_series(
            trend_report,
            growth_column,
        ).dropna()

        average_growth = (
            float(growth_values.mean())
            if not growth_values.empty
            else 0.0
        )

        positive_periods = 0

        if trend_column:
            positive_periods = int(
                trend_report[trend_column]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "up",
                        "positive",
                        "increasing",
                        "growth",
                    ]
                )
                .sum()
            )
        elif not growth_values.empty:
            positive_periods = int(growth_values.gt(0).sum())

        metrics.extend(
            [
                self._create_metric(
                    category="Trend Analytics",
                    metric="Average Growth Rate",
                    value=round(average_growth, 2),
                    unit="percent",
                    source_dataset="trend_report",
                ),
                self._create_metric(
                    category="Trend Analytics",
                    metric="Positive Growth Periods",
                    value=positive_periods,
                    unit="periods",
                    source_dataset="trend_report",
                ),
            ]
        )

        return metrics

    def generate_business_kpis(
        self,
        event_logs: pd.DataFrame,
        marketing_summary: pd.DataFrame,
        trend_report: pd.DataFrame,
        financial_kpis_enabled: bool = True,
        quarantined_records: int = 0,
    ) -> pd.DataFrame:
        """
        Generates the complete business KPI table.
        """

        metrics: list[dict[str, Any]] = []

        metrics.extend(
            self.calculate_event_log_kpis(
                event_logs=event_logs,
                financial_kpis_enabled=financial_kpis_enabled,
            )
        )

        metrics.extend(
            self.calculate_marketing_kpis(
                marketing_summary=marketing_summary,
            )
        )

        metrics.extend(
            self.calculate_trend_kpis(
                trend_report=trend_report,
            )
        )

        metrics.append(
            self._create_metric(
                category="Data Quality",
                metric="Quarantined Records",
                value=int(quarantined_records),
                unit="records",
                source_dataset="pipeline",
                status=(
                    "WARNING"
                    if quarantined_records > 0
                    else "AVAILABLE"
                ),
                description=(
                    "Records excluded from selected analytics because "
                    "they failed validation or fallback rules."
                ),
            )
        )

        business_kpis = pd.DataFrame(metrics)

        business_kpis_path = (
            self.output_directory / "business_kpis.csv"
        )

        business_kpis.to_csv(
            business_kpis_path,
            index=False,
        )

        self._log_info(
            f"Business KPIs saved to: {business_kpis_path}"
        )

        return business_kpis

    def generate_pipeline_health_metrics(
        self,
        dataset_summaries: dict[str, dict[str, Any]] | None = None,
        pipeline_mode: str = "NORMAL",
        warning_count: int = 0,
        error_count: int = 0,
        quarantined_records: int = 0,
        total_processing_seconds: float = 0.0,
    ) -> pd.DataFrame:
        """
        Generates pipeline-health metrics from validation and quality summaries.
        """

        dataset_summaries = dataset_summaries or {}

        row_count = 0
        missing_count = 0
        duplicate_rows = 0
        completeness_scores: list[float] = []
        quality_scores: list[float] = []

        for summary in dataset_summaries.values():
            row_count += int(summary.get("row_count", 0) or 0)
            missing_count += int(
                summary.get("missing_count", 0) or 0
            )
            duplicate_rows += int(
                summary.get("duplicate_rows", 0) or 0
            )

            completeness = summary.get(
                "completeness_score",
            )

            quality = summary.get(
                "quality_score",
                summary.get("completeness_score"),
            )

            if completeness is not None:
                try:
                    completeness_scores.append(
                        float(completeness)
                    )
                except (TypeError, ValueError):
                    pass

            if quality is not None:
                try:
                    quality_scores.append(float(quality))
                except (TypeError, ValueError):
                    pass

        average_completeness = (
            sum(completeness_scores) / len(completeness_scores)
            if completeness_scores
            else 100.0
        )

        average_quality = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores
            else average_completeness
        )

        pipeline_health_score = average_quality

        pipeline_health_score -= min(warning_count * 0.5, 10)
        pipeline_health_score -= min(error_count * 5, 30)

        if quarantined_records > 0 and row_count > 0:
            quarantine_rate = (
                quarantined_records / row_count
            ) * 100

            pipeline_health_score -= min(
                quarantine_rate,
                15,
            )

        pipeline_health_score = max(
            0.0,
            min(100.0, pipeline_health_score),
        )

        metrics = [
            self._create_metric(
                category="Pipeline Health",
                metric="Pipeline Health Score",
                value=round(pipeline_health_score, 2),
                unit="score/100",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Average Completeness Score",
                value=round(average_completeness, 2),
                unit="percent",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Average Data Quality Score",
                value=round(average_quality, 2),
                unit="percent",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Total Processed Rows",
                value=row_count,
                unit="rows",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Total Missing Values",
                value=missing_count,
                unit="values",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Duplicate Rows",
                value=duplicate_rows,
                unit="rows",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Pipeline Warning Count",
                value=int(warning_count),
                unit="warnings",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Pipeline Error Count",
                value=int(error_count),
                unit="errors",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Pipeline Mode",
                value=str(pipeline_mode).upper(),
                unit="status",
                source_dataset="pipeline",
            ),
            self._create_metric(
                category="Pipeline Health",
                metric="Total Processing Time",
                value=round(total_processing_seconds, 4),
                unit="seconds",
                source_dataset="pipeline",
            ),
        ]

        health_dataframe = pd.DataFrame(metrics)

        health_path = (
            self.output_directory
            / "pipeline_health_metrics.csv"
        )

        health_dataframe.to_csv(
            health_path,
            index=False,
        )

        self._log_info(
            f"Pipeline health metrics saved to: {health_path}"
        )

        return health_dataframe

    @staticmethod
    def get_metric_value(
        metrics: pd.DataFrame,
        metric_name: str,
        default: float = 0.0,
    ) -> float:
        """
        Retrieves a numeric metric value from a metric table.
        """

        if metrics is None or metrics.empty:
            return default

        if not {"metric", "value"}.issubset(metrics.columns):
            return default

        matching_rows = metrics[
            metrics["metric"]
            .astype(str)
            .str.lower()
            .eq(metric_name.lower())
        ]

        if matching_rows.empty:
            return default

        numeric_value = pd.to_numeric(
            matching_rows.iloc[0]["value"],
            errors="coerce",
        )

        if pd.isna(numeric_value):
            return default

        return float(numeric_value)

    def generate_executive_summary(
        self,
        business_kpis: pd.DataFrame,
        pipeline_health_metrics: pd.DataFrame,
        pipeline_mode: str,
        financial_kpis_enabled: bool,
        quarantined_records: int,
    ) -> pd.DataFrame:
        """
        Creates a one-row executive summary.
        """

        total_sales = self.get_metric_value(
            business_kpis,
            "Total Sales",
        )

        average_daily_sales = self.get_metric_value(
            business_kpis,
            "Average Daily Sales",
        )

        total_new_customers = self.get_metric_value(
            business_kpis,
            "Total New Customers",
        )

        average_active_users = self.get_metric_value(
            business_kpis,
            "Average Active Users",
        )

        processed_events = self.get_metric_value(
            business_kpis,
            "Processed Events",
        )

        pipeline_health_score = self.get_metric_value(
            pipeline_health_metrics,
            "Pipeline Health Score",
        )

        if pipeline_health_score >= 90:
            health_status = "HEALTHY"
        elif pipeline_health_score >= 75:
            health_status = "ATTENTION"
        else:
            health_status = "CRITICAL"

        summary = pd.DataFrame(
            [
                {
                    "report_generated_at": (
                        pd.Timestamp.now().isoformat()
                    ),
                    "pipeline_mode": str(
                        pipeline_mode
                    ).upper(),
                    "pipeline_health_status": health_status,
                    "pipeline_health_score": round(
                        pipeline_health_score,
                        2,
                    ),
                    "total_sales": round(total_sales, 2),
                    "average_daily_sales": round(
                        average_daily_sales,
                        2,
                    ),
                    "total_new_customers": int(
                        total_new_customers
                    ),
                    "average_active_users": round(
                        average_active_users,
                        2,
                    ),
                    "processed_events": int(
                        processed_events
                    ),
                    "quarantined_records": int(
                        quarantined_records
                    ),
                    "financial_kpis_enabled": bool(
                        financial_kpis_enabled
                    ),
                    "executive_message": (
                        "Pipeline completed successfully with "
                        "controlled fallback actions."
                        if str(pipeline_mode).upper() == "DEGRADED"
                        else
                        "Pipeline completed successfully under "
                        "normal processing conditions."
                    ),
                }
            ]
        )

        summary_path = (
            self.output_directory / "executive_summary.csv"
        )

        summary.to_csv(
            summary_path,
            index=False,
        )

        self._log_info(
            f"Executive summary saved to: {summary_path}"
        )

        return summary

    def generate_powerbi_dataset(
        self,
        marketing_summary: pd.DataFrame,
        pipeline_health_score: float,
        pipeline_mode: str,
        financial_kpis_enabled: bool,
        quarantined_records: int,
    ) -> pd.DataFrame:
        """
        Creates a flat Power BI-ready dataset.

        The original marketing-summary columns are preserved and monitoring
        fields are appended to every row.
        """

        if marketing_summary is None:
            powerbi_dataset = pd.DataFrame()
        else:
            powerbi_dataset = marketing_summary.copy()

        powerbi_dataset["pipeline_health_score"] = round(
            pipeline_health_score,
            2,
        )

        powerbi_dataset["pipeline_mode"] = str(
            pipeline_mode
        ).upper()

        powerbi_dataset["financial_kpis_enabled"] = bool(
            financial_kpis_enabled
        )

        powerbi_dataset["quarantined_records"] = int(
            quarantined_records
        )

        powerbi_dataset["analytics_generated_at"] = (
            pd.Timestamp.now().isoformat()
        )

        powerbi_path = (
            self.output_directory
            / "powerbi_dashboard_dataset.csv"
        )

        powerbi_dataset.to_csv(
            powerbi_path,
            index=False,
        )

        self._log_info(
            f"Power BI dataset saved to: {powerbi_path}"
        )

        return powerbi_dataset

    def run(
        self,
        event_logs: pd.DataFrame,
        marketing_summary: pd.DataFrame,
        trend_report: pd.DataFrame,
        dataset_summaries: dict[str, dict[str, Any]] | None = None,
        pipeline_mode: str = "NORMAL",
        financial_kpis_enabled: bool = True,
        quarantined_records: int = 0,
        warning_count: int = 0,
        error_count: int = 0,
        total_processing_seconds: float = 0.0,
    ) -> dict[str, pd.DataFrame]:
        """
        Executes the complete Stage 5 business analytics layer.
        """

        self._log_info(
            "Stage 5 business analytics started."
        )

        business_kpis = self.generate_business_kpis(
            event_logs=event_logs,
            marketing_summary=marketing_summary,
            trend_report=trend_report,
            financial_kpis_enabled=financial_kpis_enabled,
            quarantined_records=quarantined_records,
        )

        pipeline_health_metrics = (
            self.generate_pipeline_health_metrics(
                dataset_summaries=dataset_summaries,
                pipeline_mode=pipeline_mode,
                warning_count=warning_count,
                error_count=error_count,
                quarantined_records=quarantined_records,
                total_processing_seconds=(
                    total_processing_seconds
                ),
            )
        )

        pipeline_health_score = self.get_metric_value(
            pipeline_health_metrics,
            "Pipeline Health Score",
        )

        executive_summary = self.generate_executive_summary(
            business_kpis=business_kpis,
            pipeline_health_metrics=(
                pipeline_health_metrics
            ),
            pipeline_mode=pipeline_mode,
            financial_kpis_enabled=(
                financial_kpis_enabled
            ),
            quarantined_records=quarantined_records,
        )

        powerbi_dataset = self.generate_powerbi_dataset(
            marketing_summary=marketing_summary,
            pipeline_health_score=(
                pipeline_health_score
            ),
            pipeline_mode=pipeline_mode,
            financial_kpis_enabled=(
                financial_kpis_enabled
            ),
            quarantined_records=quarantined_records,
        )

        self._log_info(
            "Stage 5 business analytics completed | "
            f"Business KPIs: {len(business_kpis)} | "
            f"Health metrics: "
            f"{len(pipeline_health_metrics)} | "
            f"Power BI rows: {len(powerbi_dataset)}"
        )

        return {
            "business_kpis": business_kpis,
            "pipeline_health_metrics": (
                pipeline_health_metrics
            ),
            "executive_summary": executive_summary,
            "powerbi_dashboard_dataset": (
                powerbi_dataset
            ),
        }