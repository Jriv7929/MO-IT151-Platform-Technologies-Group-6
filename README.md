# 📊 FinMark Data Analytics Pipeline

> **An End-to-End Enterprise Data Analytics & Business Intelligence Platform**

FinMark Data Analytics Pipeline is a complete Python-based data engineering project that demonstrates how raw business data is transformed into executive-level insights through an automated analytics pipeline.

The project simulates a real-world enterprise workflow beginning from raw CSV data ingestion, followed by validation, cleaning, transformation, storage, business analytics, pipeline monitoring, and finally an interactive executive dashboard built with Streamlit.

---

# 🚀 Features

- Automated Data Pipeline
- Data Validation & Profiling
- Data Cleaning & Fallback Handling
- Data Transformation
- Processed, Curated & Quarantine Storage
- Business KPI Generation
- Executive Summary Reports
- Pipeline Health Monitoring
- Interactive Executive Dashboard
- Production-style Project Structure

---

# 🛠 Technology Stack

- Python 3.11
- Pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook
- CSV Data Warehouse
- Git & GitHub

---

# 📁 Project Structure

```
FinMark_DataPipeline/

│
├── dashboard/
│   ├── app.py
│   ├── styles.py
│   ├── components.py
│   └── data_loader.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   └── quarantine/
│
├── output/
│   ├── business_kpis.csv
│   ├── executive_summary.csv
│   ├── pipeline_health_metrics.csv
│   ├── dashboard_status.csv
│   ├── dashboard_alerts.csv
│   └── powerbi_dashboard_dataset.csv
│
├── src/
│   ├── ingestion.py
│   ├── validation.py
│   ├── profiling.py
│   ├── fallback.py
│   ├── cleaning.py
│   ├── transformation.py
│   ├── storage.py
│   ├── business_analytics.py
│   └── dashboard_monitoring.py
│
├── tests/
│
├── execute.ipynb
├── pipeline_stage_test.ipynb
├── main.py
├── run_pipeline.py
└── README.md
```

---

# 📊 Pipeline Architecture

```
             RAW DATASETS
                   │
                   ▼
      STAGE 1 — DATA INGESTION
                   │
                   ▼
 STAGE 2 — VALIDATION & PROFILING
                   │
                   ▼
 STAGE 3 — CLEANING & FALLBACK
                   │
                   ▼
 STAGE 4 — TRANSFORMATION & STORAGE
                   │
                   ▼
 STAGE 5 — BUSINESS ANALYTICS
                   │
                   ▼
 STAGE 6 — DASHBOARD MONITORING
                   │
                   ▼
 STAGE 7 — EXECUTIVE DASHBOARD
```

---

# 📌 Pipeline Stages

## Stage 1 — Data Ingestion

Loads raw CSV datasets into memory.

**Outputs**

- Dataset Inventory
- Metadata
- Loaded DataFrames

---

## Stage 2 — Validation & Profiling

Checks the quality of the incoming datasets.

Performs:

- Missing Value Detection
- Duplicate Detection
- Schema Validation
- Completeness Analysis
- Data Quality Scoring

**Outputs**

- Validation Report
- Data Quality Report

---

## Stage 3 — Cleaning & Fallback

Automatically repairs common data issues.

Performs:

- Missing Value Imputation
- Record Cleaning
- Fallback Rules
- Record Quarantine

**Outputs**

- Cleaned Dataset
- Cleaning Report
- Fallback Report

---

## Stage 4 — Transformation & Storage

Transforms raw data into analytics-ready datasets.

Stores outputs into:

- Processed Zone
- Curated Zone
- Quarantine Zone

**Outputs**

- Storage Report

---

## Stage 5 — Business Analytics Layer

Generates business-ready analytics including:

- Sales KPIs
- Customer KPIs
- User Activity KPIs
- Growth Metrics
- Executive Summary

Generated Files

- business_kpis.csv
- executive_summary.csv
- pipeline_health_metrics.csv

---

## Stage 6 — Dashboard Monitoring

Monitors pipeline health.

Tracks:

- Health Score
- Warning Alerts
- Critical Alerts
- Dashboard Status

Generated Files

- dashboard_status.csv
- dashboard_alerts.csv

---

## Stage 7 — Executive Dashboard

Interactive Streamlit dashboard providing:

- Executive Overview
- Marketing Performance
- User Interaction Analytics
- Weekly Trends
- Pipeline Monitoring

---

# ▶ Running the Pipeline

Execute the complete analytics pipeline.

```bash
python main.py
```

or

```bash
python run_pipeline.py
```

---

# 📈 Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard URL

```
http://localhost:8501
```

---

# 📂 Generated Reports

The pipeline automatically generates:

- business_kpis.csv
- executive_summary.csv
- pipeline_health_metrics.csv
- dashboard_status.csv
- dashboard_alerts.csv
- powerbi_dashboard_dataset.csv

These reports are located inside:

```
output/
```

---

# 🎯 Dashboard Pages

### Executive Overview

Displays:

- Total Sales
- Active Users
- New Customers
- Pipeline Health
- Executive KPIs

---

### Marketing Performance

Displays:

- Sales Trend
- Customer Growth
- Marketing Performance
- Downloadable Reports

---

### User Interaction Analytics

Displays:

- User Activity
- Event Frequency
- Product Interactions
- User Behavior

---

### Weekly Trends

Displays:

- Weekly Users
- Sales Growth
- Trend Classification

---

### Pipeline Monitoring

Displays:

- Pipeline Health Gauge
- Health Metrics
- Warning Alerts
- Critical Alerts
- Dashboard Status

---

# 📌 Future Improvements

- SQL Database Integration
- Power BI Live Connection
- Apache Airflow Scheduling
- Docker Deployment
- REST API
- Cloud Deployment
- Machine Learning Forecasting
- Real-time Streaming Data

---

# 👨‍💻 Author

**Jonathan Rivera**

Bachelor of Science in Information Technology

Data Analytics Specialization

---

# ⭐ Project Highlights

✔ End-to-End Data Pipeline

✔ Automated Data Processing

✔ Business Intelligence Reporting

✔ Interactive Executive Dashboard

✔ Enterprise Monitoring

✔ Production-style Architecture

✔ Portfolio-ready Data Engineering Project
