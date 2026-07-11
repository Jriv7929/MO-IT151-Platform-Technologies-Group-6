# 📊 FinMark Data Analytics Pipeline

> An end-to-end data analytics pipeline that ingests raw business data, validates and transforms it, performs business analytics, monitors data quality, and presents insights through an interactive executive dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

# 📖 Overview

FinMark Data Analytics Pipeline is a simulated enterprise-grade data engineering and business analytics project developed using Python.

The project demonstrates how raw business data flows through a complete analytics pipeline—from ingestion and validation to executive reporting and interactive dashboard visualization.

Rather than focusing on a single machine learning model or dashboard, this project emphasizes the complete analytics lifecycle used by modern organizations.

---

# 🎯 Project Objectives

- Build a modular ETL (Extract, Transform, Load) pipeline
- Validate incoming business datasets
- Detect and handle poor-quality data
- Apply automated cleaning and transformation
- Generate business KPIs
- Monitor pipeline health
- Produce executive-ready analytics
- Visualize insights using Streamlit

---

# 🏗 System Architecture

```
Raw CSV Data
      │
      ▼
Stage 1
Data Ingestion
      │
      ▼
Stage 2
Validation & Profiling
      │
      ▼
Stage 3
Cleaning & Transformation
      │
      ▼
Stage 4
Storage Layer
      │
      ▼
Stage 5
Business Analytics
      │
      ▼
Stage 6
Monitoring & Alerts
      │
      ▼
Stage 7
Executive Dashboard
```

---

# 🚀 Pipeline Stages

## ✅ Stage 1 — Data Ingestion

- Load multiple business datasets
- Validate file availability
- Handle missing datasets
- Standardized dataset loading

Datasets

- Event Logs
- Marketing Summary
- Trend Report

---

## ✅ Stage 2 — Validation & Profiling

Features

- Schema validation
- Missing value analysis
- Duplicate detection
- Completeness score
- Data quality score
- Dataset profiling

---

## ✅ Stage 3 — Cleaning & Transformation

Features

- Missing value handling
- Data normalization
- Type conversion
- Date conversion
- Feature engineering
- Business rule validation

---

## ✅ Stage 4 — Storage Layer

Features

- Curated dataset generation
- Processed dataset storage
- CSV export
- Output versioning

---

## ✅ Stage 5 — Business Analytics

Automatically generates

- Business KPIs
- Executive Summary
- Pipeline Health Metrics
- Power BI Dataset

Example KPIs

- Total Sales
- Average Daily Sales
- New Customers
- Active Users
- Event Statistics
- Sales Growth
- Pipeline Health Score

---

## ✅ Stage 6 — Monitoring & Alerts

Features

- Dashboard Status
- Pipeline Health
- Warning Detection
- Critical Alerts
- Quarantine Monitoring
- Executive Notifications

---

## ✅ Stage 7 — Executive Dashboard

Built using

- Streamlit
- Plotly

Dashboard Pages

- Executive Overview
- Marketing Performance
- User Interaction Analytics
- Weekly Trends
- Pipeline Monitoring

Interactive Features

- KPI Cards
- Interactive Charts
- Date Filters
- Download CSV
- Alert Monitoring
- Executive Summary

---

# 📂 Project Structure

```text
FinMark_DataPipeline/
│
├── dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   ├── quarantine/
│   └── archive/
│
├── docs/
├── logs/
├── notebooks/
├── output/
├── src/
├── tests/
│
├── README.md
├── requirements.txt
└── run_pipeline.py
```

---

# 📈 Sample Pipeline Outputs

The pipeline automatically generates

```
business_kpis.csv

pipeline_health_metrics.csv

executive_summary.csv

dashboard_status.csv

dashboard_alerts.csv

powerbi_dashboard_dataset.csv
```

---

# 📊 Dashboard Preview

> *(Insert screenshots here)*

Example pages

- Executive Overview
- Marketing Dashboard
- Weekly Trends
- Pipeline Monitoring

---

# 🛠 Technologies Used

Programming

- Python 3.11

Data Processing

- Pandas
- NumPy

Visualization

- Plotly
- Streamlit

Development Environment

- Jupyter Notebook
- VS Code
- Anaconda

Version Control

- Git
- GitHub

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/FinMark_DataPipeline.git
```

Navigate to the project

```bash
cd FinMark_DataPipeline
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the Project

Run the analytics pipeline

```bash
python run_pipeline.py
```

Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

# 📊 Example Dashboard Metrics

The dashboard displays

- Revenue
- Daily Sales
- Active Users
- New Customers
- Event Frequency
- Pipeline Health
- Quality Score
- Alerts
- Weekly Trends

---

# 📚 Learning Outcomes

This project demonstrates practical skills in

- ETL Development
- Data Engineering
- Data Cleaning
- Business Analytics
- Data Quality Management
- Dashboard Development
- Data Visualization
- Python Programming
- Modular Software Design

---

# 🔮 Future Improvements

Planned enhancements

- Machine Learning Forecasting
- Customer Segmentation
- Sales Prediction
- Automated Scheduling
- Cloud Deployment
- REST API Integration
- Database Support
- Docker Containerization

---

# 👨‍💻 Author

**Jonathan Rivera**

BS Information Technology  
Specialization in Data Analytics

GitHub:
> *(Add your GitHub profile here)*

LinkedIn:
> *(Add your LinkedIn profile here)*

---

# 📄 License

This project is intended for educational and portfolio purposes.
