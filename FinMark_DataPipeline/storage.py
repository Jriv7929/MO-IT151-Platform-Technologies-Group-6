import os

def save_cleaned_data(event_logs, marketing_summary, trend_report):

    os.makedirs("output", exist_ok=True)

    event_logs.to_csv("output/event_logs_clean.csv", index=False)
    marketing_summary.to_csv("output/marketing_summary_clean.csv", index=False)
    trend_report.to_csv("output/trend_report_clean.csv", index=False)

    print("Cleaned datasets saved successfully.")