from ingestion import load_datasets
from validation import validate_schema
from cleaning import clean_data
from transformation import transform_data
from storage import save_cleaned_data
from analytics import generate_kpis
from dashboard import create_dashboard

event_logs, marketing_summary, trend_report = load_datasets()

event_logs, marketing_summary, trend_report = validate_schema(
    event_logs,
    marketing_summary,
    trend_report
)

event_logs, marketing_summary, trend_report = clean_data(
    event_logs,
    marketing_summary,
    trend_report
)

event_logs, marketing_summary, trend_report = transform_data(
    event_logs,
    marketing_summary,
    trend_report
)

save_cleaned_data(
    event_logs,
    marketing_summary,
    trend_report
)

generate_kpis(
    event_logs,
    marketing_summary,
    trend_report
)

create_dashboard(marketing_summary)

print("\nFinMark data pipeline prototype completed successfully.")