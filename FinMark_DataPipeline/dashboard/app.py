from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components import (
    dataframe_to_csv,
    find_column,
    format_currency,
    format_number,
    get_metric_value,
    render_alerts,
    render_kpi_card,
    render_page_header,
    render_status_badge,
)
from dashboard.data_loader import load_dashboard_data
from dashboard.styles import APP_CSS



THEME = {
    "teal_950": "#042F2E",
    "teal_900": "#134E4A",
    "teal_700": "#0F766E",
    "teal_600": "#0D9488",
    "cyan_500": "#06B6D4",
    "cyan_400": "#22D3EE",
    "cyan_300": "#67E8F9",
    "cyan_100": "#CFFAFE",
    "surface": "#FFFFFF",
    "surface_soft": "#F0FDFA",
    "grid": "#D9F3F0",
    "text": "#083344",
    "muted": "#5F7A7D",
    "success": "#10B981",
    "warning": "#F59E0B",
    "critical": "#EF4444",
}

st.set_page_config(
    page_title="FinMark Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    APP_CSS,
    unsafe_allow_html=True,
)


@st.cache_data
def get_dashboard_data() -> dict[str, pd.DataFrame]:
    return load_dashboard_data()


def create_line_chart(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    y_axis_title: str,
) -> go.Figure:
    figure = px.line(
        dataframe,
        x=x_column,
        y=y_column,
        markers=True,
        title=title,
        color_discrete_sequence=[
            THEME["cyan_500"],
        ],
    )

    figure.update_traces(
        line={
            "width": 3,
            "color": THEME["cyan_500"],
        },
        marker={
            "size": 7,
            "color": THEME["teal_700"],
            "line": {
                "width": 2,
                "color": THEME["cyan_300"],
            },
        },
    )

    figure.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
        xaxis_title="",
        yaxis_title=y_axis_title,
        hovermode="x unified",
        plot_bgcolor=THEME["surface"],
        paper_bgcolor=THEME["surface"],
        font={"color": THEME["text"]},
        title_font={
            "color": THEME["teal_950"],
            "size": 18,
        },
    )

    figure.update_xaxes(
        showgrid=False,
    )

    figure.update_yaxes(
        gridcolor=THEME["grid"],
    )

    return figure


def create_bar_chart(
    dataframe: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    y_axis_title: str,
) -> go.Figure:
    figure = px.bar(
        dataframe,
        x=x_column,
        y=y_column,
        title=title,
        color_discrete_sequence=[
            THEME["teal_600"],
        ],
    )

    figure.update_traces(
        marker={
            "color": THEME["teal_600"],
            "line": {
                "color": THEME["cyan_300"],
                "width": 1,
            },
        }
    )

    figure.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=65,
            b=20,
        ),
        xaxis_title="",
        yaxis_title=y_axis_title,
        plot_bgcolor=THEME["surface"],
        paper_bgcolor=THEME["surface"],
        font={"color": THEME["text"]},
        title_font={
            "color": THEME["teal_950"],
            "size": 18,
        },
    )

    figure.update_xaxes(
        showgrid=False,
    )

    figure.update_yaxes(
        gridcolor=THEME["grid"],
    )

    return figure


def filter_by_date(
    dataframe: pd.DataFrame,
    date_column: str,
    start_date,
    end_date,
) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    return dataframe[
        dataframe[date_column].dt.date.between(
            start_date,
            end_date,
        )
    ].copy()


data = get_dashboard_data()

event_logs = data["event_logs"]
marketing_summary = data["marketing_summary"]
trend_report = data["trend_report"]
business_kpis = data["business_kpis"]
pipeline_health = data["pipeline_health"]
executive_summary = data["executive_summary"]
dashboard_alerts = data["dashboard_alerts"]
dashboard_status = data["dashboard_status"]
powerbi_dataset = data["powerbi_dataset"]


st.sidebar.markdown(
    """
    <div style="
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    ">
        FinMark Analytics
    </div>
    <div style="
        font-size: 0.82rem;
        color: #CFFAFE;
        margin-bottom: 1.2rem;
    ">
        Executive data monitoring platform
    </div>
    """,
    unsafe_allow_html=True,
)

selected_page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Marketing Performance",
        "User Interaction Analytics",
        "Weekly Trends",
        "Pipeline Monitoring",
    ],
)

st.sidebar.markdown("---")

if not dashboard_status.empty:
    current_status = str(
        dashboard_status.iloc[0].get(
            "dashboard_status",
            "UNKNOWN",
        )
    )

    st.sidebar.caption("Current system status")
    render_status_badge(current_status)

st.sidebar.markdown("---")

if st.sidebar.button(
    "Refresh dashboard",
    use_container_width=True,
):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    "Source: FinMark pipeline outputs and analytical datasets"
)


if selected_page == "Executive Overview":
    render_page_header(
        "Executive Overview",
        (
            "A consolidated view of business performance, "
            "customer activity, and pipeline health."
        ),
    )

    total_sales = get_metric_value(
        business_kpis,
        "Total Sales",
    )

    average_daily_sales = get_metric_value(
        business_kpis,
        "Average Daily Sales",
    )

    total_new_customers = get_metric_value(
        business_kpis,
        "Total New Customers",
    )

    average_active_users = get_metric_value(
        business_kpis,
        "Average Active Users",
    )

    processed_events = get_metric_value(
        business_kpis,
        "Processed Events",
    )

    unique_users = get_metric_value(
        business_kpis,
        "Unique Users",
    )

    pipeline_health_score = get_metric_value(
        pipeline_health,
        "Pipeline Health Score",
    )

    first_row = st.columns(4)

    with first_row[0]:
        render_kpi_card(
            "Total Sales",
            format_currency(total_sales),
            "Total recorded marketing sales",
        )

    with first_row[1]:
        render_kpi_card(
            "Average Daily Sales",
            format_currency(average_daily_sales),
            "Average across available daily records",
        )

    with first_row[2]:
        render_kpi_card(
            "New Customers",
            format_number(total_new_customers),
            "Total acquired customers",
        )

    with first_row[3]:
        render_kpi_card(
            "Average Active Users",
            format_number(
                average_active_users,
                decimals=2,
            ),
            "Average users active per day",
        )

    st.write("")

    second_row = st.columns(3)

    with second_row[0]:
        render_kpi_card(
            "Processed Events",
            format_number(processed_events),
            "User interaction events analyzed",
        )

    with second_row[1]:
        render_kpi_card(
            "Unique Users",
            format_number(unique_users),
            "Distinct users in the event log",
        )

    with second_row[2]:
        render_kpi_card(
            "Pipeline Health",
            f"{pipeline_health_score:.2f}/100",
            "Overall data-pipeline health score",
        )

    st.write("")

    left_column, right_column = st.columns(
        [1.7, 1],
    )

    with left_column:
        marketing_date_column = find_column(
            marketing_summary,
            [
                "date",
                "marketing_date",
                "record_date",
            ],
        )

        sales_column = find_column(
            marketing_summary,
            [
                "total_sales",
                "sales",
                "revenue",
                "sales_amount",
            ],
        )

        if (
            marketing_date_column
            and sales_column
            and not marketing_summary.empty
        ):
            chart_data = (
                marketing_summary[
                    [
                        marketing_date_column,
                        sales_column,
                    ]
                ]
                .dropna()
                .sort_values(
                    marketing_date_column
                )
            )

            figure = create_line_chart(
                dataframe=chart_data,
                x_column=marketing_date_column,
                y_column=sales_column,
                title="Daily Sales Performance",
                y_axis_title="Sales",
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Daily sales chart data is unavailable."
            )

    with right_column:
        st.subheader("Operational Alerts")
        render_alerts(dashboard_alerts)

    st.subheader("Executive Summary")

    if executive_summary.empty:
        st.info(
            "Executive summary is unavailable."
        )
    else:
        summary_row = executive_summary.iloc[0]

        st.markdown(
            f"""
            <div class="section-card">
                <strong>Pipeline mode:</strong>
                {summary_row.get("pipeline_mode", "UNKNOWN")}
                <br><br>

                <strong>Health status:</strong>
                {summary_row.get("pipeline_health_status", "UNKNOWN")}
                <br><br>

                <strong>Summary:</strong>
                {summary_row.get("executive_message", "")}
            </div>
            """,
            unsafe_allow_html=True,
        )


elif selected_page == "Marketing Performance":
    render_page_header(
        "Marketing Performance",
        (
            "Interactive analysis of daily active users, "
            "sales, and customer acquisition."
        ),
    )

    date_column = find_column(
        marketing_summary,
        [
            "date",
            "marketing_date",
            "record_date",
        ],
    )

    users_column = find_column(
        marketing_summary,
        [
            "users_active",
            "active_users",
            "daily_active_users",
        ],
    )

    sales_column = find_column(
        marketing_summary,
        [
            "total_sales",
            "sales",
            "revenue",
            "sales_amount",
        ],
    )

    new_customers_column = find_column(
        marketing_summary,
        [
            "new_customers",
            "customer_count",
        ],
    )

    filtered_marketing = marketing_summary.copy()

    if date_column and not marketing_summary.empty:
        valid_dates = (
            marketing_summary[date_column]
            .dropna()
            .sort_values()
        )

        if not valid_dates.empty:
            minimum_date = valid_dates.min().date()
            maximum_date = valid_dates.max().date()

            selected_dates = st.date_input(
                "Filter by date range",
                value=(
                    minimum_date,
                    maximum_date,
                ),
                min_value=minimum_date,
                max_value=maximum_date,
            )

            if (
                isinstance(selected_dates, tuple)
                and len(selected_dates) == 2
            ):
                filtered_marketing = filter_by_date(
                    marketing_summary,
                    date_column,
                    selected_dates[0],
                    selected_dates[1],
                )

    if not filtered_marketing.empty:
        metric_columns = st.columns(4)

        with metric_columns[0]:
            filtered_sales = (
                filtered_marketing[sales_column].sum()
                if sales_column
                else 0
            )

            render_kpi_card(
                "Filtered Sales",
                format_currency(filtered_sales),
                "Sales within selected period",
            )

        with metric_columns[1]:
            filtered_users = (
                filtered_marketing[users_column].mean()
                if users_column
                else 0
            )

            render_kpi_card(
                "Average Active Users",
                format_number(
                    filtered_users,
                    decimals=2,
                ),
                "Average within selected period",
            )

        with metric_columns[2]:
            filtered_customers = (
                filtered_marketing[
                    new_customers_column
                ].sum()
                if new_customers_column
                else 0
            )

            render_kpi_card(
                "New Customers",
                format_number(filtered_customers),
                "Total acquired in selected period",
            )

        with metric_columns[3]:
            record_count = len(filtered_marketing)

            render_kpi_card(
                "Daily Records",
                format_number(record_count),
                "Number of daily observations",
            )

    st.write("")

    first_chart_column, second_chart_column = st.columns(2)

    with first_chart_column:
        if date_column and users_column:
            users_chart_data = (
                filtered_marketing[
                    [
                        date_column,
                        users_column,
                    ]
                ]
                .dropna()
                .sort_values(date_column)
            )

            figure = create_line_chart(
                users_chart_data,
                date_column,
                users_column,
                "Daily Active Users",
                "Users",
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Active-user chart data is unavailable."
            )

    with second_chart_column:
        if date_column and sales_column:
            sales_chart_data = (
                filtered_marketing[
                    [
                        date_column,
                        sales_column,
                    ]
                ]
                .dropna()
                .sort_values(date_column)
            )

            figure = create_bar_chart(
                sales_chart_data,
                date_column,
                sales_column,
                "Daily Total Sales",
                "Sales",
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Daily-sales chart data is unavailable."
            )

    if date_column and new_customers_column:
        customer_chart_data = (
            filtered_marketing[
                [
                    date_column,
                    new_customers_column,
                ]
            ]
            .dropna()
            .sort_values(date_column)
        )

        figure = create_line_chart(
            customer_chart_data,
            date_column,
            new_customers_column,
            "Daily New Customers",
            "New Customers",
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    st.subheader("Marketing Dataset")

    st.download_button(
        label="Download filtered marketing data",
        data=dataframe_to_csv(
            filtered_marketing
        ),
        file_name="filtered_marketing_summary.csv",
        mime="text/csv",
    )

    st.dataframe(
        filtered_marketing,
        use_container_width=True,
        hide_index=True,
    )


elif selected_page == "User Interaction Analytics":
    render_page_header(
        "User Interaction Analytics",
        (
            "Explore event frequency, user behavior, "
            "product interactions, and transaction values."
        ),
    )

    user_column = find_column(
        event_logs,
        [
            "user_id",
            "customer_id",
            "userid",
        ],
    )

    event_column = find_column(
        event_logs,
        [
            "event_type",
            "event_name",
            "event",
        ],
    )

    product_column = find_column(
        event_logs,
        [
            "product_id",
            "product",
        ],
    )

    amount_column = find_column(
        event_logs,
        [
            "amount",
            "transaction_amount",
            "sales_amount",
        ],
    )

    filtered_events = event_logs.copy()

    filter_columns = st.columns(3)

    with filter_columns[0]:
        selected_event_types = []

        if event_column:
            event_options = sorted(
                filtered_events[event_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_event_types = st.multiselect(
                "Event type",
                options=event_options,
            )

    with filter_columns[1]:
        selected_users = []

        if user_column:
            user_options = sorted(
                filtered_events[user_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_users = st.multiselect(
                "User",
                options=user_options,
            )

    with filter_columns[2]:
        selected_products = []

        if product_column:
            product_options = sorted(
                filtered_events[product_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_products = st.multiselect(
                "Product",
                options=product_options,
            )

    if selected_event_types and event_column:
        filtered_events = filtered_events[
            filtered_events[event_column]
            .astype(str)
            .isin(selected_event_types)
        ]

    if selected_users and user_column:
        filtered_events = filtered_events[
            filtered_events[user_column]
            .astype(str)
            .isin(selected_users)
        ]

    if selected_products and product_column:
        filtered_events = filtered_events[
            filtered_events[product_column]
            .astype(str)
            .isin(selected_products)
        ]

    event_metrics = st.columns(4)

    with event_metrics[0]:
        render_kpi_card(
            "Filtered Events",
            format_number(
                len(filtered_events)
            ),
            "Records after applying filters",
        )

    with event_metrics[1]:
        filtered_unique_users = (
            filtered_events[user_column].nunique()
            if user_column
            else 0
        )

        render_kpi_card(
            "Unique Users",
            format_number(
                filtered_unique_users
            ),
            "Distinct users in current view",
        )

    with event_metrics[2]:
        filtered_event_types = (
            filtered_events[event_column].nunique()
            if event_column
            else 0
        )

        render_kpi_card(
            "Event Types",
            format_number(
                filtered_event_types
            ),
            "Distinct interaction categories",
        )

    with event_metrics[3]:
        total_amount = (
            filtered_events[amount_column]
            .fillna(0)
            .sum()
            if amount_column
            else 0
        )

        render_kpi_card(
            "Recorded Amount",
            format_currency(total_amount),
            "Total amount in filtered events",
        )

    st.write("")

    left_column, right_column = st.columns(
        [1.5, 1],
    )

    with left_column:
        if event_column:
            frequency = (
                filtered_events[event_column]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .rename_axis("event_type")
                .reset_index(name="count")
            )

            figure = px.bar(
                frequency,
                x="event_type",
                y="count",
                title="Event Types by Frequency",
                color_discrete_sequence=[
                    THEME["cyan_500"],
                ],
            )

            figure.update_layout(
                height=440,
                xaxis_title="Event Type",
                yaxis_title="Count",
                plot_bgcolor=THEME["surface"],
                paper_bgcolor=THEME["surface"],
                font={"color": THEME["text"]},
                title_font={"color": THEME["teal_950"]},
            )

            figure.update_xaxes(
                tickangle=-35,
                showgrid=False,
            )

            figure.update_yaxes(
                gridcolor=THEME["grid"],
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Event frequency data is unavailable."
            )

    with right_column:
        st.subheader("Top Event Types")

        if event_column:
            top_events = (
                filtered_events[event_column]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .head(5)
            )

            for rank, (
                event_name,
                count,
            ) in enumerate(
                top_events.items(),
                start=1,
            ):
                st.markdown(
                    f"""
                    <div class="section-card">
                        <strong>{rank}. {event_name}</strong>
                        <br>
                        {count:,} occurrences
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.subheader("Interaction Logs")

    st.download_button(
        label="Download filtered interaction logs",
        data=dataframe_to_csv(
            filtered_events
        ),
        file_name="filtered_event_logs.csv",
        mime="text/csv",
    )

    st.dataframe(
        filtered_events,
        use_container_width=True,
        hide_index=True,
    )


elif selected_page == "Weekly Trends":
    render_page_header(
        "Weekly Trends",
        (
            "Review weekly changes in user activity, "
            "sales growth, and trend classifications."
        ),
    )

    week_column = find_column(
        trend_report,
        [
            "week",
            "week_number",
        ],
    )

    average_users_column = find_column(
        trend_report,
        [
            "avg_users",
            "average_users",
        ],
    )

    growth_column = find_column(
        trend_report,
        [
            "sales_growth_rate",
            "growth_rate",
            "sales_growth",
        ],
    )

    trend_columns = [
        column
        for column in trend_report.columns
        if trend_report[column]
        .astype(str)
        .str.lower()
        .isin(
            [
                "rising",
                "falling",
                "stable",
            ]
        )
        .any()
    ]

    trend_metrics = st.columns(4)

    with trend_metrics[0]:
        average_users = (
            trend_report[
                average_users_column
            ].mean()
            if average_users_column
            else 0
        )

        render_kpi_card(
            "Average Weekly Users",
            format_number(
                average_users,
                decimals=2,
            ),
            "Average across all weekly periods",
        )

    with trend_metrics[1]:
        peak_users = (
            trend_report[
                average_users_column
            ].max()
            if average_users_column
            else 0
        )

        render_kpi_card(
            "Peak Weekly Users",
            format_number(peak_users),
            "Highest weekly user level",
        )

    with trend_metrics[2]:
        average_growth = (
            trend_report[growth_column].mean()
            if growth_column
            else 0
        )

        render_kpi_card(
            "Average Sales Growth",
            f"{average_growth * 100:.2f}%",
            "Average weekly sales growth",
        )

    with trend_metrics[3]:
        positive_growth_periods = (
            int(
                trend_report[
                    growth_column
                ].gt(0).sum()
            )
            if growth_column
            else 0
        )

        render_kpi_card(
            "Positive Growth Weeks",
            format_number(
                positive_growth_periods
            ),
            "Weeks with sales growth above zero",
        )

    st.write("")

    first_column, second_column = st.columns(2)

    with first_column:
        if week_column and average_users_column:
            chart_data = (
                trend_report[
                    [
                        week_column,
                        average_users_column,
                    ]
                ]
                .dropna()
            )

            figure = create_line_chart(
                chart_data,
                week_column,
                average_users_column,
                "Average Users Over Time",
                "Average Users",
            )

            figure.update_xaxes(
                tickangle=-35,
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Weekly user trend data is unavailable."
            )

    with second_column:
        if week_column and growth_column:
            chart_data = (
                trend_report[
                    [
                        week_column,
                        growth_column,
                    ]
                ]
                .dropna()
                .copy()
            )

            chart_data["growth_percent"] = (
                chart_data[growth_column] * 100
            )

            figure = create_bar_chart(
                chart_data,
                week_column,
                "growth_percent",
                "Weekly Sales Growth Rate",
                "Growth Rate (%)",
            )

            figure.update_xaxes(
                tickangle=-35,
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )
        else:
            st.info(
                "Weekly sales-growth data is unavailable."
            )

    if trend_columns:
        trend_values = pd.concat(
            [
                trend_report[column]
                .astype(str)
                .str.title()
                for column in trend_columns
            ],
            ignore_index=True,
        )

        trend_distribution = (
            trend_values[
                trend_values.isin(
                    [
                        "Rising",
                        "Falling",
                        "Stable",
                    ]
                )
            ]
            .value_counts()
            .rename_axis("trend")
            .reset_index(name="count")
        )

        if not trend_distribution.empty:
            figure = px.pie(
                trend_distribution,
                names="trend",
                values="count",
                title="Trend Classification Distribution",
                hole=0.45,
                color_discrete_sequence=[
                    THEME["cyan_500"],
                    THEME["teal_600"],
                    THEME["cyan_300"],
                ],
            )

            figure.update_layout(
                height=420,
                paper_bgcolor=THEME["surface"],
                font={"color": THEME["text"]},
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    st.subheader("Weekly Metrics")

    st.download_button(
        label="Download weekly trend data",
        data=dataframe_to_csv(
            trend_report
        ),
        file_name="weekly_trend_report.csv",
        mime="text/csv",
    )

    st.dataframe(
        trend_report,
        use_container_width=True,
        hide_index=True,
    )


elif selected_page == "Pipeline Monitoring":
    render_page_header(
        "Pipeline Monitoring",
        (
            "Track data quality, warnings, quarantine activity, "
            "and overall processing health."
        ),
    )

    pipeline_health_score = get_metric_value(
        pipeline_health,
        "Pipeline Health Score",
    )

    completeness_score = get_metric_value(
        pipeline_health,
        "Average Completeness Score",
    )

    quality_score = get_metric_value(
        pipeline_health,
        "Average Data Quality Score",
    )

    processed_rows = get_metric_value(
        pipeline_health,
        "Total Processed Rows",
    )

    missing_values = get_metric_value(
        pipeline_health,
        "Total Missing Values",
    )

    duplicate_rows = get_metric_value(
        pipeline_health,
        "Duplicate Rows",
    )

    quarantined_records = get_metric_value(
        business_kpis,
        "Quarantined Records",
    )

    monitoring_cards = st.columns(4)

    with monitoring_cards[0]:
        render_kpi_card(
            "Pipeline Health",
            f"{pipeline_health_score:.2f}/100",
            "Overall system health score",
        )

    with monitoring_cards[1]:
        render_kpi_card(
            "Completeness",
            f"{completeness_score:.2f}%",
            "Average completeness across datasets",
        )

    with monitoring_cards[2]:
        render_kpi_card(
            "Data Quality",
            f"{quality_score:.2f}%",
            "Average quality score",
        )

    with monitoring_cards[3]:
        render_kpi_card(
            "Quarantined Records",
            format_number(
                quarantined_records
            ),
            "Records excluded for quality reasons",
        )

    st.write("")

    lower_cards = st.columns(3)

    with lower_cards[0]:
        render_kpi_card(
            "Processed Rows",
            format_number(processed_rows),
            "Rows evaluated by the pipeline",
        )

    with lower_cards[1]:
        render_kpi_card(
            "Missing Values",
            format_number(missing_values),
            "Missing cells across source data",
        )

    with lower_cards[2]:
        render_kpi_card(
            "Duplicate Rows",
            format_number(duplicate_rows),
            "Duplicate records detected",
        )

    st.write("")

    chart_column, alert_column = st.columns(
        [1.25, 1],
    )

    with chart_column:
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pipeline_health_score,
                number={
                    "suffix": "/100",
                },
                title={
                    "text": "Pipeline Health Score",
                },
                gauge={
                    "axis": {
                        "range": [0, 100],
                    },
                    "steps": [
                        {
                            "range": [0, 75],
                            "color": "#FEE2E2",
                        },
                        {
                            "range": [75, 90],
                            "color": "#FEF3C7",
                        },
                        {
                            "range": [90, 100],
                            "color": "#CCFBF1",
                        },
                    ],
                    "bar": {
                        "color": THEME["cyan_500"],
                    },
                },
            )
        )

        gauge.update_layout(
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=70,
                b=20,
            ),
            paper_bgcolor=THEME["surface"],
            font={"color": THEME["text"]},
        )

        st.plotly_chart(
            gauge,
            use_container_width=True,
        )

    with alert_column:
        st.subheader("Pipeline Alerts")
        render_alerts(dashboard_alerts)

    st.subheader("Pipeline Health Metrics")

    st.download_button(
        label="Download pipeline health metrics",
        data=dataframe_to_csv(
            pipeline_health
        ),
        file_name="pipeline_health_metrics.csv",
        mime="text/csv",
    )

    st.dataframe(
        pipeline_health,
        use_container_width=True,
        hide_index=True,
    )