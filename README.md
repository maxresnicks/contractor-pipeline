# 🏥 Two Chairs: Market Capacity & Operations Pipeline

An end-to-end data engineering and analytics project designed to model clinician supply vs. patient demand. This project simulates the extraction, transformation, and visualization of disparate healthcare data to identify operational bottlenecks.

## 🎯 Project Overview
In a hybrid healthcare model like Two Chairs, balancing the "Hiring Pipeline" (Supply) with the "Patient Intake" (Demand) is the core operational challenge. This pipeline bridges the gap between:
* **HR/ATS Systems:** Tracking clinician offers, starts, and target weekly capacity.
* **EMR/Intake Systems:** Tracking patient sessions, market routing, and churn.

## 🛠 The Tech Stack
* **Language:** Python 3.11
* **Database:** DuckDB (OLAP-optimized for fast analytical queries)
* **Dashboard:** Streamlit (Interactive Web App)
* **Data Modeling:** SQL (Complex Joins & Conditional Logic)

## 🏗 Data Architecture & Pipeline
1. **Ingestion (`ingest.py`):** Generates 6,000+ rows of synthetic, "messy" healthcare data including common anomalies (missing markets, illogical churn dates).
2. **Transformation (`transform.py`):** Uses DuckDB to clean and normalize the data, enforcing business logic (e.g., a patient cannot churn before they intake).
3. **Analytics & Auditing (`metrics.py` & `audit.py`):** * Computes **Market Utilization %** (Weekly Demand / Active Supply).
    * Conducts **Forecast vs. Actuals Audit** on offer acceptance rates and patient attrition.

## 📊 Key Insights Captured
* **Supply Shortages:** Identification of "Bottleneck" markets where patient demand exceeds clinician capacity.
* **Hiring Efficiency:** Monitoring whether the recruiting team is hitting the 85% offer-to-start target.
* **Churn Logic:** Identifying regions where patient attrition is higher than the 15% model baseline.

---
*Developed by Max Resnick for the Operations Analyst role at Two Chairs.*