# Contractor Productivity Pipeline

Simulated CDC-style data pipeline for tracking contractor productivity, detecting anomalies, and ensuring data reliability in an operations environment.

## Overview

This project replicates real-world technical operations workflows involving:

- Ingestion of messy, inconsistent data
- Incremental data updates (CDC-style)
- Data cleaning and normalization
- Metric computation (productivity, efficiency)
- Anomaly detection for operational issues

## Tech Stack

- Python (pandas)
- DuckDB (local data warehouse)
- SQL
- (Planned) Streamlit dashboard

## Pipeline Stages

1. **Ingestion**
   - Simulated contractor activity data
   - Includes missing values and anomalies

2. **Transformation**
   - Cleans and normalizes raw data
   - Handles nulls and invalid records

3. **Metrics**
   - Calculates productivity metrics (tasks/hour)

4. **Anomaly Detection**
   - Flags abnormal productivity patterns

## Goal

Demonstrate how to design reliable data workflows that handle messy inputs and surface operational issues proactively.

## Status

!! In progress !!
