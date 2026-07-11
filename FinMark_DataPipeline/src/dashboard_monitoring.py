from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class DashboardMonitoring:
    """
    Prepares dashboard monitoring records and operational alerts.

    This stage does not modify the original curated datasets.
    It creates monitoring outputs that can be consumed by
    Streamlit, Power BI, or another visualization platform.
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
    def _get_metric_value(
        dataframe: pd.DataFrame,
        metric_name: str,
        default: float = 0.0,
    ) -> float:
        """
        Retrieves one metric from the business KPI or health metric table.
        """

        if dataframe is None or dataframe.empty:
            return default

        required_columns = {"metric", "value"}

        if not required_columns.issubset(dataframe.columns):
            return default

        matching_rows = dataframe[
            dataframe["metric"].astype(str).str.lower()
            == metric_name.lower()
        ]

        if matching_rows.empty:
            return default

        value = pd.to_numeric(
            matching_rows.iloc[0]["value"],
            errors="coerce",
        )

        if pd.isna(value):
            return default

        return float(value)

    def generate_alerts(
        self,
        business_kpis: pd.DataFrame,
        pipeline_health_metrics: pd.DataFrame,
        fallback_summary: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """
        Generates dashboard alerts based on KPI and pipeline-health rules.
        """

        alerts: list[dict[str, Any]] = []

        health_score = self._get_metric_value(
            pipeline_health_metrics,
            "Pipeline Health Score",
        )

        quarantined_records = self._get_metric_value(
            business_kpis,
            "Quarantined Records",
        )

        if health_score >= 90:
            alerts.append(
                {
                    "alert_category": "Pipeline Health",
                    "severity": "INFO",
                    "status": "HEALTHY",
                    "message": (
                        f"Pipeline health score is {health_score:.2f}. "
                        "The overall pipeline is operating normally."
                    ),
                }
            )
        elif health_score >= 75:
            alerts.append(
                {
                    "alert_category": "Pipeline Health",
                    "severity": "WARNING",
                    "status": "ATTENTION",
                    "message": (
                        f"Pipeline health score is {health_score:.2f}. "
                        "Review data-quality and processing warnings."
                    ),
                }
            )
        else:
            alerts.append(
                {
                    "alert_category": "Pipeline Health",
                    "severity": "CRITICAL",
                    "status": "UNHEALTHY",
                    "message": (
                        f"Pipeline health score is {health_score:.2f}. "
                        "Immediate pipeline investigation is required."
                    ),
                }
            )

        if quarantined_records > 0:
            alerts.append(
                {
                    "alert_category": "Data Quality",
                    "severity": "WARNING",
                    "status": "REVIEW REQUIRED",
                    "message": (
                        f"{int(quarantined_records)} records were "
                        "quarantined and excluded from selected analytics."
                    ),
                }
            )
        else:
            alerts.append(
                {
                    "alert_category": "Data Quality",
                    "severity": "INFO",
                    "status": "CLEAR",
                    "message": "No records are currently quarantined.",
                }
            )

        if fallback_summary:
            financial_kpis_enabled = fallback_summary.get(
                "financial_kpis_enabled",
                True,
            )

            pipeline_mode = fallback_summary.get(
                "pipeline_mode",
                "NORMAL",
            )

            if not financial_kpis_enabled:
                alerts.append(
                    {
                        "alert_category": "Financial Analytics",
                        "severity": "WARNING",
                        "status": "PARTIALLY DISABLED",
                        "message": (
                            "Event-log financial KPIs are disabled because "
                            "the missing transaction amount threshold was "
                            "exceeded. Marketing sales KPIs remain available."
                        ),
                    }
                )

            if str(pipeline_mode).upper() == "DEGRADED":
                alerts.append(
                    {
                        "alert_category": "Pipeline Mode",
                        "severity": "WARNING",
                        "status": "DEGRADED",
                        "message": (
                            "The pipeline completed using fallback controls. "
                            "Review the fallback action report."
                        ),
                    }
                )

        alerts_dataframe = pd.DataFrame(alerts)

        alerts_path = self.output_directory / "dashboard_alerts.csv"
        alerts_dataframe.to_csv(alerts_path, index=False)

        self._log_info(
            f"Dashboard alerts saved to: {alerts_path}"
        )

        return alerts_dataframe

    def generate_dashboard_status(
        self,
        business_kpis: pd.DataFrame,
        pipeline_health_metrics: pd.DataFrame,
        alerts: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Creates one summary record for the dashboard header.
        """

        total_sales = self._get_metric_value(
            business_kpis,
            "Total Sales",
        )

        average_daily_sales = self._get_metric_value(
            business_kpis,
            "Average Daily Sales",
        )

        active_users = self._get_metric_value(
            business_kpis,
            "Average Active Users",
        )

        new_customers = self._get_metric_value(
            business_kpis,
            "Total New Customers",
        )

        health_score = self._get_metric_value(
            pipeline_health_metrics,
            "Pipeline Health Score",
        )

        warning_count = 0
        critical_count = 0

        if alerts is not None and not alerts.empty:
            if "severity" in alerts.columns:
                warning_count = int(
                    alerts["severity"]
                    .astype(str)
                    .str.upper()
                    .eq("WARNING")
                    .sum()
                )

                critical_count = int(
                    alerts["severity"]
                    .astype(str)
                    .str.upper()
                    .eq("CRITICAL")
                    .sum()
                )

        if critical_count > 0:
            dashboard_status = "CRITICAL"
        elif warning_count > 0:
            dashboard_status = "WARNING"
        else:
            dashboard_status = "HEALTHY"

        status_dataframe = pd.DataFrame(
            [
                {
                    "dashboard_status": dashboard_status,
                    "pipeline_health_score": round(health_score, 2),
                    "total_sales": round(total_sales, 2),
                    "average_daily_sales": round(
                        average_daily_sales,
                        2,
                    ),
                    "average_active_users": round(active_users, 2),
                    "total_new_customers": int(new_customers),
                    "warning_count": warning_count,
                    "critical_count": critical_count,
                    "last_updated": pd.Timestamp.now().isoformat(),
                }
            ]
        )

        status_path = self.output_directory / "dashboard_status.csv"
        status_dataframe.to_csv(status_path, index=False)

        self._log_info(
            f"Dashboard status saved to: {status_path}"
        )

        return status_dataframe

    def run(
        self,
        business_kpis: pd.DataFrame,
        pipeline_health_metrics: pd.DataFrame,
        fallback_summary: dict[str, Any] | None = None,
    ) -> dict[str, pd.DataFrame]:
        """
        Executes the complete dashboard monitoring process.
        """

        self._log_info("Dashboard monitoring started.")

        alerts = self.generate_alerts(
            business_kpis=business_kpis,
            pipeline_health_metrics=pipeline_health_metrics,
            fallback_summary=fallback_summary,
        )

        dashboard_status = self.generate_dashboard_status(
            business_kpis=business_kpis,
            pipeline_health_metrics=pipeline_health_metrics,
            alerts=alerts,
        )

        self._log_info(
            "Dashboard monitoring completed | "
            f"Alerts: {len(alerts)} | "
            f"Status: {dashboard_status.iloc[0]['dashboard_status']}"
        )

        return {
            "dashboard_alerts": alerts,
            "dashboard_status": dashboard_status,
        }