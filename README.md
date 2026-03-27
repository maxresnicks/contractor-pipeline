# Healthcare Operations & Capacity Dashboard

An end-to-end data pipeline and interactive web application built to model clinical supply against patient demand across regional markets. 

Instead of just visualizing static data, this tool is designed for operational strategy. It identifies active capacity bottlenecks and allows operations teams to simulate the impact of new hires on regional waitlists in real-time.

## Tech Stack
* **Frontend:** Streamlit, Altair
* **Database / Analytical Engine:** DuckDB
* **Data Manipulation:** Python, Pandas
* **Data Generation:** Faker (for synthetic HR/EMR datasets)

## Core Features

* **In-Memory Data Warehouse:** Utilizes DuckDB to ingest, clean, and join simulated HR (ATS) and Patient (EMR) datasets via SQL.
* **Interactive Capacity Modeling:** A "What-If" sensitivity slider allows users to project how adding new clinical supply impacts utilization metrics and capacity status.
* **Geospatial Demand Mapping:** An interactive map that scales region size by patient demand and dynamically updates colors based on simulated market health.
* **Forecast vs. Actuals Auditing:** Built-in analytics tracking historical patient churn against financial targets and measuring clinician offer acceptance rates.
* **Data Integrity Scorecards:** Automated anomaly detection isolating source-system errors like missing routing data, illogical intake dates, and supply drag (onboarding velocity).

## Architecture 

1. **Ingest (`src/ingest.py`):** Generates 6,000+ rows of synthetic operational data, intentionally injecting real-world anomalies (missing labels, bad dates).
2. **Transform (`src/transform.py`):** Loads raw CSVs into DuckDB, enforcing data integrity and business logic via SQL.
3. **Analyze (`src/metrics.py` & `src/audit.py`):** Calculates core KPIs, aligning weekly clinician capacity with monthly patient session demand.
4. **Visualize (`app.py`):** Serves the clean metrics to a Streamlit frontend for executive stakeholder interaction.

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/maxresnicks/contractor-pipeline.git](https://github.com/maxresnicks/contractor-pipeline.git)
   cd contractor-pipeline