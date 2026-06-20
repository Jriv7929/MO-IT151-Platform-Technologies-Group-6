def clean_data(event_logs, marketing_summary, trend_report):

    event_logs = event_logs.drop_duplicates()
    marketing_summary = marketing_summary.drop_duplicates()
    trend_report = trend_report.drop_duplicates()

    # Amount null values are business-valid for non-transaction events
    event_logs["amount"] = event_logs["amount"].fillna(0)

    marketing_summary = marketing_summary.fillna(0)
    trend_report = trend_report.fillna(0)

    print("Data cleaning completed.")

    return event_logs, marketing_summary, trend_report