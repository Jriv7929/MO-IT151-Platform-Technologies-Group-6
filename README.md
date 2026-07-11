# FinMark Resilient Data Pipeline

> A production-inspired Python data pipeline for processing, validating, cleaning, analyzing, and visualizing business data with built-in data quality monitoring, performance analytics, and fault tolerance.

---

## Project Overview

The **FinMark Resilient Data Pipeline** is a Python-based prototype developed for the Data Analytics Track. It demonstrates how raw business datasets can be transformed into reliable analytical outputs through a structured Extract-Transform-Load (ETL) workflow.

Unlike a basic ETL pipeline, this project emphasizes **data quality**, **pipeline resilience**, and **performance monitoring**. The pipeline is capable of detecting missing or corrupted business columns, applying business-rule-based recovery, generating data quality reports, measuring execution time for every pipeline stage, and preparing datasets for dashboarding and future forecasting.

This project was developed as part of the FinMark case study and follows the scalable architecture proposed during Milestone 1 while extending the implementation completed in Milestone 2.

---

# Features

## Data Ingestion

- Reads multiple business datasets
- Validates file availability
- Supports structured CSV ingestion
- Logs ingestion status

---

## Schema Validation

- Required column verification
- Missing column detection
- Data type validation
- Corrupted value detection
- Validation logging

---

## Data Quality Monitoring

- Missing value analysis
- Duplicate detection
- Invalid record detection
- Data completeness scoring
- Data quality reporting

---

## Business Rule Engine

Instead of blindly replacing missing values with zero, the pipeline applies business-aware rules:

- Retains valid null values for behavioral events
- Repairs recoverable missing columns
- Flags corrupted transaction data
- Supports future quarantine processing

---

## Data Cleaning

- Duplicate removal
- Standardization
- Null value handling
- Invalid record management

---

## Data Transformation

Creates additional analytical features including:

- Event Date
- Event Hour
- Week Start Date
- Daily summaries
- Monthly summaries

---

## Analytics

Generates business KPIs such as:

- Total Sales
- Total Events
- Unique Users
- Average Active Users
- Sales Growth Rate
- Customer Metrics

---

## Pipeline Performance Monitoring

Measures execution time for every pipeline stage.

Example:

```
Ingestion
Validation
Cleaning
Transformation
Storage
Analytics
Dashboard
```

The pipeline identifies performance bottlenecks for future optimization.

---

## Dashboard

The pipeline generates a management dashboard containing:

- Sales Trends
- Business KPIs
- Event Distribution
- Pipeline Performance
- Data Quality Metrics

Designed to support future Power BI integration.

---

## Fault Tolerance

The pipeline is designed to continue operating when recoverable issues occur.

Examples include:

- Missing columns
- Corrupted values
- Invalid numeric fields
- Missing datasets (future enhancement)

---

# Pipeline Architecture

```
                Raw Data Sources
                       │
                       ▼
               Data Ingestion
                       │
                       ▼
             Schema Validation
                       │
                       ▼
         Data Quality Assessment
                       │
                       ▼
        Business Rule Engine
                       │
                       ▼
              Data Cleaning
                       │
                       ▼
            Data Transformation
                       │
                       ▼
              Initial Storage
                       │
                       ▼
         Analytics & KPI Generation
                       │
                       ▼
          Dashboard & Reporting
```

---

# Project Structure

```
FinMark_DataPipeline/

│
├── main.py
├── config.py
├── ingestion.py
├── validation.py
├── profiling.py
├── fallback.py
├── cleaning.py
├── transformation.py
├── storage.py
├── analytics.py
├── forecasting.py
├── monitoring.py
├── dashboard.py
│
├── data/
│   ├── raw/
│   ├── clean/
│   ├── curated/
│   └── quarantine/
│
├── output/
│
├── dashboard/
│
├── logs/
│
├── notebooks/
│
└── README.md
```

---

# Technologies Used

- Python 3.x
- Pandas
- NumPy
- Matplotlib
- Plotly
- Jupyter Notebook
- CSV
- Power BI (Planned)
- ARIMA / SARIMA (Planned)

---

# Sample Pipeline Flow

```
Raw CSV Files
      │
      ▼
Data Ingestion
      │
      ▼
Schema Validation
      │
      ▼
Data Quality Checks
      │
      ▼
Cleaning
      │
      ▼
Transformation
      │
      ▼
Storage
      │
      ▼
Analytics
      │
      ▼
Dashboard
```

---

# Running the Project

Clone the repository

```bash
git clone https://github.com/yourusername/FinMark_DataPipeline.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the pipeline

```bash
python main.py
```

---

# Current Status

| Module | Status |
|---------|--------|
| Data Ingestion | ✅ Completed |
| Schema Validation | ✅ Completed |
| Data Cleaning | ✅ Completed |
| Data Transformation | ✅ Completed |
| Initial Storage | ✅ Completed |
| Analytics | ✅ Completed |
| Dashboard | ✅ Completed |
| Data Quality Monitoring | 🚧 In Progress |
| Performance Monitoring | 🚧 In Progress |
| Business Rule Engine | 🚧 In Progress |
| Forecasting | ⏳ Planned |
| Power BI Integration | ⏳ Planned |

---

# Future Enhancements

- Apache Kafka Integration
- Azure Data Lake
- Azure Synapse Analytics
- Real-Time Streaming
- Machine Learning Forecasting
- SARIMA Forecast Model
- Power BI Live Dashboard
- Email Alerting
- Data Quality Dashboard
- Pipeline Health Dashboard

---

# Contributors

**Jonathan Rivera**

BS Information Technology – Data Analytics Track

---

# License

This project is intended for academic and educational purposes.

---

# Acknowledgements

Developed as part of the **FinMark Data Analytics Case Study** for the Data Analytics Track.

Special thanks to our instructors and mentors for their valuable feedback on improving data quality, pipeline resilience, and performance monitoring.
