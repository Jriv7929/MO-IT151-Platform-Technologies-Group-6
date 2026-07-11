"""
Pipeline performance monitoring.

This module measures:
- Start time
- End time
- Duration per stage
- Percentage of total runtime
- Slowest pipeline stage
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

import pandas as pd

from config import PIPELINE_PERFORMANCE_FILE
from logger_config import get_logger


class PipelineMonitor:
    """Measure and record execution time for pipeline stages."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.records: list[dict] = []

    @contextmanager
    def track(self, stage_name: str) -> Iterator[None]:
        """
        Context manager that measures one pipeline stage.

        Example
        -------
        with monitor.track("Ingestion"):
            datasets = load_datasets()
        """

        start_clock = time.perf_counter()
        start_time = datetime.now()

        self.logger.info("Stage started: %s", stage_name)

        status = "SUCCESS"
        error_message = ""

        try:
            yield

        except Exception as error:
            status = "FAILED"
            error_message = str(error)

            self.logger.exception(
                "Stage failed: %s | Error: %s",
                stage_name,
                error,
            )

            raise

        finally:
            end_clock = time.perf_counter()
            end_time = datetime.now()
            duration = end_clock - start_clock

            self.records.append(
                {
                    "stage": stage_name,
                    "start_time": start_time.isoformat(
                        timespec="milliseconds"
                    ),
                    "end_time": end_time.isoformat(
                        timespec="milliseconds"
                    ),
                    "duration_seconds": round(duration, 6),
                    "percentage_of_total": 0.0,
                    "status": status,
                    "error_message": error_message,
                }
            )

            self.logger.info(
                "Stage finished: %s | Status: %s | Duration: %.6f seconds",
                stage_name,
                status,
                duration,
            )

    def build_report(self) -> pd.DataFrame:
        """
        Build the pipeline performance report.

        Returns
        -------
        pandas.DataFrame
            Execution-time report for all recorded stages.
        """

        report = pd.DataFrame(self.records)

        if report.empty:
            return report

        total_duration = report["duration_seconds"].sum()

        if total_duration > 0:
            report["percentage_of_total"] = (
                report["duration_seconds"] / total_duration * 100
            ).round(2)

        return report

    def save_report(self) -> pd.DataFrame:
        """
        Save execution-time results to CSV.

        Returns
        -------
        pandas.DataFrame
            Saved performance report.
        """

        report = self.build_report()

        if report.empty:
            self.logger.warning(
                "Performance report was not saved because no stages were recorded."
            )
            return report

        report.to_csv(
            PIPELINE_PERFORMANCE_FILE,
            index=False,
        )

        self.logger.info(
            "Pipeline performance report saved to: %s",
            PIPELINE_PERFORMANCE_FILE,
        )

        return report

    def get_bottleneck(self) -> dict | None:
        """
        Return the slowest successful pipeline stage.

        Returns
        -------
        dict | None
            Bottleneck stage information.
        """

        report = self.build_report()

        if report.empty:
            return None

        successful = report[report["status"] == "SUCCESS"]

        if successful.empty:
            return None

        bottleneck_row = successful.loc[
            successful["duration_seconds"].idxmax()
        ]

        return bottleneck_row.to_dict()

    def print_summary(self) -> None:
        """Display a readable performance summary."""

        report = self.build_report()

        print("\nPIPELINE PERFORMANCE REPORT")
        print("-" * 72)

        if report.empty:
            print("No pipeline stages were measured.")
            return

        for _, row in report.iterrows():
            print(
                f"{row['stage']:<22}"
                f"{row['duration_seconds']:>12.6f} seconds"
                f"{row['percentage_of_total']:>10.2f}%"
                f"{row['status']:>12}"
            )

        total_duration = report["duration_seconds"].sum()

        print("-" * 72)
        print(f"{'Total Runtime':<22}{total_duration:>12.6f} seconds")

        bottleneck = self.get_bottleneck()

        if bottleneck:
            print(
                f"{'Bottleneck Stage':<22}"
                f"{bottleneck['stage']}"
                f" ({bottleneck['duration_seconds']:.6f} seconds)"
            )