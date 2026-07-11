from __future__ import annotations

import html

import pandas as pd
import streamlit as st


def find_column(
    dataframe: pd.DataFrame,
    possible_names: list[str],
) -> str | None:
    """
    Finds a column using exact and partial matching.
    """

    if dataframe is None or dataframe.empty:
        return None

    normalized_columns = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }

    for name in possible_names:
        normalized_name = name.strip().lower()

        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    for column in dataframe.columns:
        normalized_column = str(column).strip().lower()

        for name in possible_names:
            if name.strip().lower() in normalized_column:
                return column

    return None


def get_metric_value(
    dataframe: pd.DataFrame,
    metric_name: str,
    default: float = 0.0,
) -> float:
    """
    Retrieves a numeric metric from a KPI dataframe.
    """

    if dataframe is None or dataframe.empty:
        return default

    if not {"metric", "value"}.issubset(dataframe.columns):
        return default

    rows = dataframe[
        dataframe["metric"]
        .astype(str)
        .str.lower()
        .eq(metric_name.lower())
    ]

    if rows.empty:
        return default

    value = pd.to_numeric(
        rows.iloc[0]["value"],
        errors="coerce",
    )

    if pd.isna(value):
        return default

    return float(value)


def format_currency(
    value: float,
) -> str:
    return f"₱{value:,.2f}"


def format_number(
    value: float,
    decimals: int = 0,
) -> str:
    return f"{value:,.{decimals}f}"


def render_page_header(
    title: str,
    subtitle: str,
) -> None:
    st.markdown(
        f"""
        <div class="dashboard-title">
            {html.escape(title)}
        </div>
        <div class="dashboard-subtitle">
            {html.escape(subtitle)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    caption: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">
                {html.escape(label)}
            </div>
            <div class="kpi-value">
                {html.escape(value)}
            </div>
            <div class="kpi-caption">
                {html.escape(caption)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(
    status: str,
) -> None:
    normalized_status = status.upper()

    if normalized_status in {"HEALTHY", "NORMAL", "CLEAR"}:
        css_class = "status-healthy"
    elif normalized_status in {
        "WARNING",
        "ATTENTION",
        "DEGRADED",
    }:
        css_class = "status-warning"
    else:
        css_class = "status-critical"

    st.markdown(
        f"""
        <span class="{css_class}">
            {html.escape(normalized_status)}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_alerts(
    alerts: pd.DataFrame,
) -> None:
    """
    Displays dashboard monitoring alerts.
    """

    if alerts is None or alerts.empty:
        st.info("No monitoring alerts are available.")
        return

    for _, row in alerts.iterrows():
        severity = str(
            row.get("severity", "INFO")
        ).upper()

        category = str(
            row.get("alert_category", "System")
        )

        message = str(
            row.get("message", "")
        )

        text = f"**{category}:** {message}"

        if severity == "CRITICAL":
            st.error(text)
        elif severity == "WARNING":
            st.warning(text)
        else:
            st.info(text)


def dataframe_to_csv(
    dataframe: pd.DataFrame,
) -> bytes:
    """
    Converts a dataframe into downloadable CSV bytes.
    """

    return dataframe.to_csv(
        index=False
    ).encode("utf-8")