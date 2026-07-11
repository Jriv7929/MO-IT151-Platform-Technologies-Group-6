"""
Business-rule fallback engine for the FinMark data pipeline.

This module:
- Classifies event types
- Distinguishes valid missing values from data-quality errors
- Avoids replacing every missing amount with zero
- Imputes small amounts of missing transaction data
- Quarantines unreliable transaction records
- Supports degraded pipeline operation
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from config import (
    BEHAVIORAL_EVENTS,
    FALLBACK_ACTION_FILE,
    MAX_IMPUTATION_RATE,
    MAX_QUARANTINE_RATE,
    PIPELINE_MODE_DEGRADED,
    PIPELINE_MODE_NORMAL,
    TRANSACTION_EVENTS,
)
from logger_config import get_logger


logger = get_logger()


@dataclass
class FallbackResult:
    """Store the result of applying fallback rules."""

    pipeline_mode: str = PIPELINE_MODE_NORMAL
    financial_kpis_enabled: bool = True

    valid_behavioral_nulls: int = 0
    imputed_transaction_amounts: int = 0
    quarantined_transaction_rows: int = 0
    unknown_event_nulls: int = 0

    warnings: list[str] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)


def normalize_event_type(value) -> str:
    """
    Standardize event names for rule matching.
    """

    if pd.isna(value):
        return "unknown"

    normalized = str(value).strip().lower()
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")

    return " ".join(normalized.split())


def classify_event_type(event_type: str) -> str:
    """
    Classify an event as transaction, behavioral, or unknown.
    """

    normalized = normalize_event_type(event_type)

    transaction_set = {
        normalize_event_type(event)
        for event in TRANSACTION_EVENTS
    }

    behavioral_set = {
        normalize_event_type(event)
        for event in BEHAVIORAL_EVENTS
    }

    if normalized in transaction_set:
        return "transaction"

    if normalized in behavioral_set:
        return "behavioral"

    return "unknown"


def record_action(
    result: FallbackResult,
    dataset: str,
    column: str,
    issue: str,
    action: str,
    affected_rows: int,
    details: str = "",
) -> None:
    """
    Add one action to the fallback report.
    """

    result.actions.append(
        {
            "dataset": dataset,
            "column": column,
            "issue": issue,
            "action": action,
            "affected_rows": affected_rows,
            "details": details,
        }
    )


def handle_missing_amount_column(
    event_logs: pd.DataFrame,
    result: FallbackResult,
) -> pd.DataFrame:
    """
    Handle a completely missing amount column safely.

    The column is created as NaN rather than zero because zero would
    represent a real financial amount and could bias analytics.
    """

    event_logs = event_logs.copy()

    event_logs["amount"] = np.nan
    event_logs["amount_status"] = "column_missing"

    result.pipeline_mode = PIPELINE_MODE_DEGRADED
    result.financial_kpis_enabled = False

    warning = (
        "The amount column was missing. It was recreated using NaN values. "
        "Financial KPIs were disabled to prevent misleading results."
    )

    result.warnings.append(warning)
    logger.warning(warning)

    record_action(
        result=result,
        dataset="event_logs",
        column="amount",
        issue="entire_column_missing",
        action="created_as_null_and_disabled_financial_kpis",
        affected_rows=len(event_logs),
        details="The pipeline continued in degraded mode.",
    )

    return event_logs


def handle_amount_values(
    event_logs: pd.DataFrame,
    result: FallbackResult,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply business rules to missing and corrupted amount values.

    Returns
    -------
    processed_event_logs:
        Records allowed to continue through the pipeline.

    quarantine:
        Records excluded because their transaction amount was unreliable.
    """

    event_logs = event_logs.copy()

    original_amount = event_logs["amount"]

    event_logs["amount"] = pd.to_numeric(
        original_amount,
        errors="coerce",
    )

    event_logs["event_category"] = (
        event_logs["event_type"]
        .apply(classify_event_type)
    )

    event_logs["amount_status"] = "valid"

    corrupted_mask = (
        original_amount.notna()
        & event_logs["amount"].isna()
    )

    corrupted_count = int(corrupted_mask.sum())

    if corrupted_count > 0:
        logger.warning(
            "%d corrupted amount values were converted to missing values.",
            corrupted_count,
        )

        record_action(
            result=result,
            dataset="event_logs",
            column="amount",
            issue="corrupted_numeric_values",
            action="converted_to_null_for_business_rule_processing",
            affected_rows=corrupted_count,
        )

    missing_amount_mask = event_logs["amount"].isna()

    behavioral_missing_mask = (
        missing_amount_mask
        & (event_logs["event_category"] == "behavioral")
    )

    transaction_missing_mask = (
        missing_amount_mask
        & (event_logs["event_category"] == "transaction")
    )

    unknown_missing_mask = (
        missing_amount_mask
        & (event_logs["event_category"] == "unknown")
    )

    # --------------------------------------------------------
    # Business-valid missing amounts
    # --------------------------------------------------------

    event_logs.loc[
        behavioral_missing_mask,
        "amount_status",
    ] = "not_applicable"

    result.valid_behavioral_nulls = int(
        behavioral_missing_mask.sum()
    )

    record_action(
        result=result,
        dataset="event_logs",
        column="amount",
        issue="missing_behavioral_amount",
        action="retained_as_valid_null",
        affected_rows=result.valid_behavioral_nulls,
        details=(
            "Behavioral activities do not necessarily involve money."
        ),
    )

    # --------------------------------------------------------
    # Unknown event types
    # --------------------------------------------------------

    event_logs.loc[
        unknown_missing_mask,
        "amount_status",
    ] = "requires_review"

    result.unknown_event_nulls = int(
        unknown_missing_mask.sum()
    )

    if result.unknown_event_nulls > 0:
        result.pipeline_mode = PIPELINE_MODE_DEGRADED

        warning = (
            f"{result.unknown_event_nulls} missing amount values belonged "
            "to unknown event types and require review."
        )

        result.warnings.append(warning)
        logger.warning(warning)

        record_action(
            result=result,
            dataset="event_logs",
            column="amount",
            issue="missing_amount_unknown_event",
            action="retained_and_flagged_for_review",
            affected_rows=result.unknown_event_nulls,
        )

    # --------------------------------------------------------
    # Transaction-event missing values
    # --------------------------------------------------------

    transaction_rows = (
        event_logs["event_category"] == "transaction"
    )

    transaction_count = int(transaction_rows.sum())

    missing_transaction_count = int(
        transaction_missing_mask.sum()
    )

    missing_transaction_rate = (
        missing_transaction_count / transaction_count
        if transaction_count > 0
        else 0.0
    )

    quarantine = event_logs.iloc[0:0].copy()

    if missing_transaction_count == 0:
        return event_logs, quarantine

    valid_transaction_amounts = event_logs.loc[
        transaction_rows
        & event_logs["amount"].notna(),
        "amount",
    ]

    # Small number of missing transaction values:
    # median imputation is permitted.
    if (
        missing_transaction_rate <= MAX_IMPUTATION_RATE
        and not valid_transaction_amounts.empty
    ):
        median_amount = float(
            valid_transaction_amounts.median()
        )

        event_logs.loc[
            transaction_missing_mask,
            "amount",
        ] = median_amount

        event_logs.loc[
            transaction_missing_mask,
            "amount_status",
        ] = "imputed_median"

        result.imputed_transaction_amounts = (
            missing_transaction_count
        )

        record_action(
            result=result,
            dataset="event_logs",
            column="amount",
            issue="missing_transaction_amount",
            action="median_imputation",
            affected_rows=missing_transaction_count,
            details=(
                f"Missing rate: {missing_transaction_rate:.2%}; "
                f"Median used: {median_amount:.2f}"
            ),
        )

    # Moderate missing rate:
    # quarantine affected rows instead of inventing amounts.
    elif missing_transaction_rate <= MAX_QUARANTINE_RATE:

        quarantine = event_logs.loc[
            transaction_missing_mask
        ].copy()

        quarantine["quarantine_reason"] = (
            "missing_or_corrupted_transaction_amount"
        )

        event_logs = event_logs.loc[
            ~transaction_missing_mask
        ].copy()

        result.quarantined_transaction_rows = (
            missing_transaction_count
        )

        result.pipeline_mode = PIPELINE_MODE_DEGRADED

        warning = (
            f"{missing_transaction_count} transaction records were "
            "quarantined because their amounts were missing or corrupted."
        )

        result.warnings.append(warning)
        logger.warning(warning)

        record_action(
            result=result,
            dataset="event_logs",
            column="amount",
            issue="missing_transaction_amount",
            action="quarantined",
            affected_rows=missing_transaction_count,
            details=(
                f"Missing rate: {missing_transaction_rate:.2%}"
            ),
        )

    # Severe data-quality issue:
    # quarantine and disable financial KPIs.
    else:

        quarantine = event_logs.loc[
            transaction_missing_mask
        ].copy()

        quarantine["quarantine_reason"] = (
            "critical_transaction_amount_failure"
        )

        event_logs = event_logs.loc[
            ~transaction_missing_mask
        ].copy()

        result.quarantined_transaction_rows = (
            missing_transaction_count
        )

        result.pipeline_mode = PIPELINE_MODE_DEGRADED
        result.financial_kpis_enabled = False

        warning = (
            "The missing transaction amount rate exceeded the safe "
            "threshold. Affected records were quarantined and financial "
            "KPIs were disabled."
        )

        result.warnings.append(warning)
        logger.warning(warning)

        record_action(
            result=result,
            dataset="event_logs",
            column="amount",
            issue="critical_missing_transaction_amount",
            action="quarantined_and_disabled_financial_kpis",
            affected_rows=missing_transaction_count,
            details=(
                f"Missing rate: {missing_transaction_rate:.2%}"
            ),
        )

    return event_logs, quarantine


def apply_fallback_rules(
    datasets: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    FallbackResult,
    pd.DataFrame,
]:
    """
    Apply fallback rules to all relevant datasets.

    Returns
    -------
    processed_datasets:
        Datasets allowed to continue.

    quarantined_datasets:
        Rejected records grouped by dataset.

    fallback_result:
        Summary of pipeline mode and financial availability.

    action_report:
        Detailed list of actions applied.
    """

    processed_datasets = {
        name: dataframe.copy()
        for name, dataframe in datasets.items()
    }

    quarantined_datasets: dict[str, pd.DataFrame] = {}

    result = FallbackResult()

    event_logs = processed_datasets["event_logs"]

    if "amount" not in event_logs.columns:

        event_logs = handle_missing_amount_column(
            event_logs,
            result,
        )

        quarantine = event_logs.iloc[0:0].copy()

    else:

        event_logs, quarantine = handle_amount_values(
            event_logs,
            result,
        )

    processed_datasets["event_logs"] = event_logs
    quarantined_datasets["event_logs"] = quarantine

    action_report = pd.DataFrame(result.actions)

    if action_report.empty:
        action_report = pd.DataFrame(
            columns=[
                "dataset",
                "column",
                "issue",
                "action",
                "affected_rows",
                "details",
            ]
        )

    action_report.to_csv(
        FALLBACK_ACTION_FILE,
        index=False,
    )

    logger.info(
        "Fallback action report saved to: %s",
        FALLBACK_ACTION_FILE,
    )

    print("\nBUSINESS-RULE FALLBACK SUMMARY")
    print("-" * 72)
    print(
        f"Pipeline Mode: "
        f"{result.pipeline_mode}"
    )
    print(
        f"Financial KPIs Enabled: "
        f"{result.financial_kpis_enabled}"
    )
    print(
        f"Valid Behavioral Nulls: "
        f"{result.valid_behavioral_nulls}"
    )
    print(
        f"Imputed Transaction Amounts: "
        f"{result.imputed_transaction_amounts}"
    )
    print(
        f"Quarantined Transaction Rows: "
        f"{result.quarantined_transaction_rows}"
    )
    print(
        f"Unknown Event Nulls: "
        f"{result.unknown_event_nulls}"
    )
    print("-" * 72)

    return (
        processed_datasets,
        quarantined_datasets,
        result,
        action_report,
    )