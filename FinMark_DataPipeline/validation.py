def validate_schema(event_logs, marketing_summary, trend_report):

    event_columns = [
        "user_id",
        "event_type",
        "event_time",
        "product_id",
        "amount"
    ]

    marketing_columns = [
        "date",
        "users_active",
        "total_sales",
        "new_customers",
        "report_generated"
    ]

    trend_columns = [
        "week",
        "avg_users",
        "sales_growth_rate"
    ]

    event_logs = event_logs[event_columns]
    marketing_summary = marketing_summary[marketing_columns]
    trend_report = trend_report[trend_columns]

    print("Schema validation completed.")

    return event_logs, marketing_summary, trend_report