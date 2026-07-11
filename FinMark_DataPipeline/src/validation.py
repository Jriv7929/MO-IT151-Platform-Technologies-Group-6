"""
Schema validation for the FinMark data pipeline.

This module checks:
- Required columns
- Missing critical columns
- Missing optional columns
- Unexpected columns
- Corrupted numeric values
- Invalid datetime values
- Pipeline operating mode
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from config import (
    CRITICAL_COLUMNS,
    DATETIME_COLUMNS,
    NUMERIC_COLUMNS,
    OPTIONAL_COLUMNS,
    PIPELINE_MODE_DEGRADED,
    PIPELINE_MODE_FAILED,
    PIPELINE_MODE_NORMAL,
    REQUIRED_COLUMNS,
)
from logger_config import get_logger


logger = get_logger()


@dataclass
class ValidationResult:
    """Store the result of validating one dataset."""

    dataset_name: str
    is_valid: bool = True
    pipeline_mode: str = PIPELINE_MODE_NORMAL

    missing_required_columns: list[str] = field(default_factory=list)
    missing_critical_columns: list[str] = field(default_factory=list)
    missing_optional_columns: list[str] = field(default_factory=list)
    unexpected_columns: list[str] = field(default_factory=list)

    corrupted_numeric_values: dict[str, int] = field(default_factory=dict)
    invalid_datetime_values: dict[str, int] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_record(self) -> dict:
        """Convert the result into one report row."""

        return {
            "dataset": self.dataset_name,
            "is_valid": self.is_valid,
            "pipeline_mode": self.pipeline_mode,
            "missing_required_columns": ", ".join(
                self.missing_required_columns
            ),
            "missing_critical_columns": ", ".join(
                self.missing_critical_columns
            ),
            "missing_optional_columns": ", ".join(
                self.missing_optional_columns
            ),
            "unexpected_columns_count": len(
                self.unexpected_columns
            ),
            "unexpected_columns": ", ".join(
                self.unexpected_columns
            ),
            "corrupted_numeric_values": str(
                self.corrupted_numeric_values
            ),
            "invalid_datetime_values": str(
                self.invalid_datetime_values
            ),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "warnings": " | ".join(self.warnings),
            "errors": " | ".join(self.errors),
        }


def detect_missing_columns(
    dataframe: pd.DataFrame,
    dataset_name: str,
    result: ValidationResult,
) -> None:
    """
    Detect missing required, critical, and optional columns.
    """

    actual_columns = set(dataframe.columns)

    required = set(REQUIRED_COLUMNS.get(dataset_name, []))
    critical = set(CRITICAL_COLUMNS.get(dataset_name, []))
    optional = set(OPTIONAL_COLUMNS.get(dataset_name, []))

    result.missing_required_columns = sorted(
        required - actual_columns
    )

    result.missing_critical_columns = sorted(
        critical - actual_columns
    )

    result.missing_optional_columns = sorted(
        optional - actual_columns
    )

    expected_columns = required | critical | optional

    result.unexpected_columns = sorted(
        actual_columns - expected_columns
    )

    if result.missing_critical_columns:
        result.is_valid = False
        result.pipeline_mode = PIPELINE_MODE_FAILED

        message = (
            f"{dataset_name}: Missing critical columns: "
            f"{result.missing_critical_columns}"
        )

        result.errors.append(message)
        logger.error(message)

    elif result.missing_required_columns:
        result.pipeline_mode = PIPELINE_MODE_DEGRADED

        message = (
            f"{dataset_name}: Missing required columns: "
            f"{result.missing_required_columns}"
        )

        result.warnings.append(message)
        logger.warning(message)

    if result.missing_optional_columns:
        message = (
            f"{dataset_name}: Missing optional columns: "
            f"{result.missing_optional_columns}"
        )

        result.warnings.append(message)
        logger.warning(message)

    if result.unexpected_columns:
        message = (
            f"{dataset_name}: "
            f"{len(result.unexpected_columns)} unexpected columns detected."
        )

        result.warnings.append(message)
        logger.warning(message)


def detect_corrupted_numeric_values(
    dataframe: pd.DataFrame,
    dataset_name: str,
    result: ValidationResult,
) -> None:
    """
    Count values that cannot be converted into valid numbers.

    Original null values are not counted as corrupted values.
    """

    for column in NUMERIC_COLUMNS.get(dataset_name, []):

        if column not in dataframe.columns:
            continue

        original = dataframe[column]

        converted = pd.to_numeric(
            original,
            errors="coerce",
        )

        corrupted_mask = (
            original.notna()
            & converted.isna()
        )

        corrupted_count = int(corrupted_mask.sum())

        result.corrupted_numeric_values[column] = (
            corrupted_count
        )

        if corrupted_count > 0:
            result.pipeline_mode = (
                PIPELINE_MODE_DEGRADED
                if result.pipeline_mode != PIPELINE_MODE_FAILED
                else PIPELINE_MODE_FAILED
            )

            message = (
                f"{dataset_name}.{column}: "
                f"{corrupted_count} corrupted numeric values detected."
            )

            result.warnings.append(message)
            logger.warning(message)


def detect_invalid_datetime_values(
    dataframe: pd.DataFrame,
    dataset_name: str,
    result: ValidationResult,
) -> None:
    """
    Count datetime values that cannot be parsed.

    Original null values are not counted as invalid dates.
    """

    for column in DATETIME_COLUMNS.get(dataset_name, []):

        if column not in dataframe.columns:
            continue

        original = dataframe[column]

        converted = pd.to_datetime(
            original,
            errors="coerce",
        )

        invalid_mask = (
            original.notna()
            & converted.isna()
        )

        invalid_count = int(invalid_mask.sum())

        result.invalid_datetime_values[column] = (
            invalid_count
        )

        if invalid_count > 0:
            result.pipeline_mode = (
                PIPELINE_MODE_DEGRADED
                if result.pipeline_mode != PIPELINE_MODE_FAILED
                else PIPELINE_MODE_FAILED
            )

            message = (
                f"{dataset_name}.{column}: "
                f"{invalid_count} invalid datetime values detected."
            )

            result.warnings.append(message)
            logger.warning(message)


def validate_dataset(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> ValidationResult:
    """
    Validate one FinMark dataset.

    Parameters
    ----------
    dataframe:
        Dataset to validate.

    dataset_name:
        Logical dataset name.

    Returns
    -------
    ValidationResult
        Complete validation result.
    """

    logger.info(
        "Schema validation started for dataset: %s",
        dataset_name,
    )

    result = ValidationResult(
        dataset_name=dataset_name
    )

    detect_missing_columns(
        dataframe,
        dataset_name,
        result,
    )

    detect_corrupted_numeric_values(
        dataframe,
        dataset_name,
        result,
    )

    detect_invalid_datetime_values(
        dataframe,
        dataset_name,
        result,
    )

    logger.info(
        "Schema validation completed for %s | "
        "Mode: %s | Warnings: %d | Errors: %d",
        dataset_name,
        result.pipeline_mode,
        len(result.warnings),
        len(result.errors),
    )

    return result


def determine_overall_pipeline_mode(
    results: dict[str, ValidationResult],
) -> str:
    """
    Determine the overall operating mode from all datasets.
    """

    modes = {
        result.pipeline_mode
        for result in results.values()
    }

    if PIPELINE_MODE_FAILED in modes:
        return PIPELINE_MODE_FAILED

    if PIPELINE_MODE_DEGRADED in modes:
        return PIPELINE_MODE_DEGRADED

    return PIPELINE_MODE_NORMAL


def validate_datasets(
    datasets: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, ValidationResult],
    pd.DataFrame,
    str,
]:
    """
    Validate all datasets.

    Returns
    -------
    validation_results:
        ValidationResult object for every dataset.

    validation_report:
        Tabular report.

    overall_pipeline_mode:
        NORMAL, DEGRADED, or FAILED.
    """

    validation_results = {}

    for dataset_name, dataframe in datasets.items():

        validation_results[dataset_name] = (
            validate_dataset(
                dataframe=dataframe,
                dataset_name=dataset_name,
            )
        )

    report = pd.DataFrame(
        [
            result.to_record()
            for result in validation_results.values()
        ]
    )

    overall_mode = determine_overall_pipeline_mode(
        validation_results
    )

    print("\nSCHEMA VALIDATION SUMMARY")
    print("-" * 100)

    display_columns = [
        "dataset",
        "pipeline_mode",
        "missing_required_columns",
        "unexpected_columns_count",
        "warning_count",
        "error_count",
    ]

    print(
        report[display_columns].to_string(
            index=False
        )
    )

    print("-" * 100)
    print(f"Overall Pipeline Mode: {overall_mode}")

    return validation_results, report, overall_mode