import pandas as pd

def load_datasets():
    event_logs = pd.read_csv("data/event_logs.csv")
    marketing_summary = pd.read_csv("data/marketing_summary.csv")
    trend_report = pd.read_csv("data/trend_report.csv")

    print("Datasets loaded successfully.")

    return event_logs, marketing_summary, trend_report