import pandas as pd

def transform_data(event_logs, marketing_summary, trend_report):

    # Convert event time
    event_logs["event_time"] = pd.to_datetime(
        event_logs["event_time"],
        errors="coerce"
    )

    event_logs["event_date"] = event_logs["event_time"].dt.date
    event_logs["event_hour"] = event_logs["event_time"].dt.hour

    # Convert marketing date
    marketing_summary["date"] = pd.to_datetime(
        marketing_summary["date"],
        errors="coerce"
    )

    # Convert week format like 2023-W21 into a real date
    trend_report["week_start_date"] = pd.to_datetime(
        trend_report["week"].astype(str) + "-1",
        format="%G-W%V-%u",
        errors="coerce"
    )

    print("Data transformation completed.")

    return event_logs, marketing_summary, trend_report