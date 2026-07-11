"""
Central configuration for the FinMark data pipeline.

This file contains:
- Project paths
- Dataset filenames
- Required schemas
- Critical columns
- Event classifications
- Data-quality thresholds
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
CURATED_DIR = DATA_DIR / "curated"
QUARANTINE_DIR = DATA_DIR / "quarantine"

OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
DASHBOARD_DIR = BASE_DIR / "dashboard"
NOTEBOOK_DIR = BASE_DIR / "notebooks"
TEST_DIR = BASE_DIR / "tests"


# ============================================================
# INPUT DATASET PATHS
# ============================================================

DATASET_PATHS = {
    "event_logs": RAW_DIR / "event_logs.csv",
    "marketing_summary": RAW_DIR / "marketing_summary.csv",
    "trend_report": RAW_DIR / "trend_report.csv",
}

# ============================================================
# OUTPUT FILE PATHS
# ============================================================

BUSINESS_KPI_FILE = OUTPUT_DIR / "business_kpis.csv"
DATA_QUALITY_FILE = OUTPUT_DIR / "data_quality_report.csv"
PIPELINE_PERFORMANCE_FILE = OUTPUT_DIR / "pipeline_performance.csv"
FORECAST_FILE = OUTPUT_DIR / "forecast.csv"
POWERBI_DATASET_FILE = OUTPUT_DIR / "powerbi_dataset.csv"

PIPELINE_LOG_FILE = LOG_DIR / "pipeline.log"

BUSINESS_DASHBOARD_FILE = DASHBOARD_DIR / "business_dashboard.html"
PIPELINE_HEALTH_DASHBOARD_FILE = (
    DASHBOARD_DIR / "pipeline_health_dashboard.html"
)
DASHBOARD_LINK_FILE = DASHBOARD_DIR / "dashboard_link.txt"
FALLBACK_ACTION_FILE = OUTPUT_DIR / "fallback_actions.csv"
CLEANING_REPORT_FILE = OUTPUT_DIR / "cleaning_report.csv"

EVENT_CLASSIFICATION_FILE = (
    OUTPUT_DIR / "event_classification_report.csv"
)

DAILY_SALES_FILE = (
    CURATED_DIR / "daily_sales_summary.csv"
)

MONTHLY_SALES_FILE = (
    CURATED_DIR / "monthly_sales_summary.csv"
)

DAILY_ACTIVITY_FILE = (
    CURATED_DIR / "daily_activity_summary.csv"
)

EVENT_TYPE_SUMMARY_FILE = (
    CURATED_DIR / "event_type_summary.csv"
)

PIPELINE_HEALTH_FILE = (
    OUTPUT_DIR / "pipeline_health.csv"
)

EXECUTIVE_SUMMARY_FILE = (
    OUTPUT_DIR / "executive_summary.csv"
)

ANALYTICS_DETAIL_FILE = (
    OUTPUT_DIR / "analytics_detail.csv"
)

# ============================================================
# REQUIRED DATASET SCHEMAS
# ============================================================

REQUIRED_COLUMNS = {
    "event_logs": [
        "user_id",
        "event_type",
        "event_time",
        "product_id",
        "amount",
    ],
    "marketing_summary": [
        "date",
        "users_active",
        "total_sales",
        "new_customers",
        "report_generated",
    ],
    "trend_report": [
        "week",
        "avg_users",
        "sales_growth_rate",
    ],
}


# ============================================================
# CRITICAL AND OPTIONAL COLUMNS
# ============================================================

CRITICAL_COLUMNS = {
    "event_logs": [
        "user_id",
        "event_type",
        "event_time",
    ],
    "marketing_summary": [
        "date",
        "total_sales",
    ],
    "trend_report": [
        "week",
        "sales_growth_rate",
    ],
}

OPTIONAL_COLUMNS = {
    "event_logs": [
        "product_id",
        "amount",
    ],
    "marketing_summary": [
        "users_active",
        "new_customers",
        "report_generated",
    ],
    "trend_report": [
        "avg_users",
    ],
}


# ============================================================
# EXPECTED DATA TYPES
# ============================================================

NUMERIC_COLUMNS = {
    "event_logs": [
        "amount",
    ],
    "marketing_summary": [
        "users_active",
        "total_sales",
        "new_customers",
    ],
    "trend_report": [
        "avg_users",
        "sales_growth_rate",
    ],
}

DATETIME_COLUMNS = {
    "event_logs": [
        "event_time",
    ],
    "marketing_summary": [
        "date",
        "report_generated",
    ],
    "trend_report": [],
}


# ============================================================
# EVENT CLASSIFICATIONS
# ============================================================


TRANSACTION_EVENTS = {
    "checkout",
    "purchase",
    "payment",
    "transaction",
    "refund",
    "order",
    "completed purchase",
    "successful checkout",
}

BEHAVIORAL_EVENTS = {
    "login",
    "logout",
    "page_view",
    "page view",
    "wishlist_add",
    "wishlist",
    "profile_update",
    "profile update",
    "support_interaction",
    "support interaction",
    "click",
    "search",
    "add_to_cart",
}

# ============================================================
# DATA-QUALITY THRESHOLDS
# ============================================================

# A noncritical column with less than 60% usable values may be dropped.
MINIMUM_COLUMN_COMPLETENESS = 0.60

# A small percentage of missing transaction values may be imputed.
MAX_IMPUTATION_RATE = 0.10

# Above this rate, affected transaction records should be quarantined.
MAX_QUARANTINE_RATE = 0.40

# Dataset-level completeness scores
QUALITY_STATUS_GOOD = 0.90
QUALITY_STATUS_WARNING = 0.60

# A column below this completeness level may be considered unusable
# when it is not critical to the business process.
COLUMN_DROP_THRESHOLD = 0.60

# ============================================================
# INGESTION SETTINGS
# ============================================================

CSV_ENCODING = "utf-8"
INGESTION_RETRY_COUNT = 2


# ============================================================
# PIPELINE MODES
# ============================================================

PIPELINE_MODE_NORMAL = "NORMAL"
PIPELINE_MODE_DEGRADED = "DEGRADED"
PIPELINE_MODE_FAILED = "FAILED"


# ============================================================
# DIRECTORY INITIALIZATION
# ============================================================

def create_project_directories() -> None:
    """Create all required project directories."""

    directories = [
        RAW_DIR,
        CLEAN_DIR,
        CURATED_DIR,
        QUARANTINE_DIR,
        OUTPUT_DIR,
        LOG_DIR,
        DASHBOARD_DIR,
        NOTEBOOK_DIR,
        TEST_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)