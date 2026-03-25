# Healthcare Operations Pipeline: Supply & Demand Modeling

## Overview
This project simulates the data infrastructure and operational reporting required to manage capacity planning in a high-growth healthcare setting. It focuses on solving a core business problem: aligning Clinician Supply (hiring velocity, ramp-up time) with Patient Demand (intake volume, churn) across multiple regional markets.

## Goal
Demonstrate the ability to build scalable reporting infrastructure, handle messy cross-functional data (ATS/HR vs. EMR/Intake), and surface actionable KPIs that allow for "apples-to-apples" comparisons across disparate markets.

## Tech Stack
* **Python (pandas):** Data generation and pipeline orchestration
* **DuckDB:** Local analytical data warehouse 
* **SQL:** Data transformation, cleaning, and metric computation
* *(Planned) Streamlit:* Interactive stakeholder dashboard

## Pipeline Stages

### 1. Ingestion (`src/ingest.py`)
* Simulates pulling records from two disconnected systems: an HR/ATS system (Clinicians) and an Intake/EMR system (Patients).
* Intentionally injects realistic operational anomalies: missing start dates, fat-fingered capacity metrics, duplicate API syncs, and logical system errors.

### 2. Transformation (`src/transform.py`) - *In Progress*
* Loads raw CSVs into DuckDB.
* Cleans data, handles null values, and standardizes data types.
* Normalizes market data for regional comparisons.

### 3. Metrics & Modeling (`src/metrics.py`) - *Planned*
* Computes utilization rates, forecast vs. actuals, and time-to-ramp.
* Flags capacity bottlenecks and supply/demand imbalances.

## Status
!! In progress !!