import streamlit as st
import duckdb
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Two Chairs: Capacity Dashboard", page_icon="🪑", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📊 Executive Dashboard", "⚙️ Under the Hood (Methodology)"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Context:**\nBuilt to demonstrate data engineering, SQL, and capacity modeling for healthcare operations.")

# --- Database Connection ---
@st.cache_data
def load_data(query):
    conn = duckdb.connect("db/warehouse.duckdb")
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

# ==========================================
# PAGE 1: EXECUTIVE DASHBOARD
# ==========================================
if page == "📊 Executive Dashboard":
    st.title("🪑🪑 Two Chairs: Market Capacity & Operations Dashboard")
    st.markdown("""
    Monitoring Supply (Clinicians) vs. Demand (Patients) across 10 regional markets.
    
    The following is a data analysis and engineering dashboard app designed to mimic the 
    type of work I think I'd be doing at Two Chairs.
    """)
    try:
        health_df = load_data("SELECT * FROM market_health_dashboard ORDER BY utilization_pct DESC")
        clinician_df = load_data("SELECT * FROM audit_clinician_hiring")
        patient_df = load_data("SELECT * FROM audit_patient_churn")
    except Exception as e:
        st.error(f"Error loading data. Did you run the pipeline scripts first? Error: {e}")
        st.stop()

    # --- TOP ROW: Regional Market Health ---
    st.header("Regional Market Health")

    bottlenecks = health_df[health_df['operational_status'].str.contains('BOTTLENECK')]
    if not bottlenecks.empty:
        st.error(f"WARNING: {len(bottlenecks)} markets are currently operating over capacity. Demand exceeds active clinician supply.")
    else:
        st.success("All markets are operating within healthy capacity limits.")

    # Clean emojis for the table
    health_df['operational_status'] = health_df['operational_status'].str.replace('🚨 ', '').str.replace('⚠️ ', '').str.replace('✅ ', '')

    # Apply modern hex colors
    def highlight_status(val):
        if 'BOTTLENECK' in str(val):
            return 'background-color: #EF4444; color: white; font-weight: bold'
        elif 'WARNING' in str(val):
            return 'background-color: #F59E0B; color: black; font-weight: bold'
        elif 'HEALTHY' in str(val):
            return 'background-color: #10B981; color: white; font-weight: bold'
        return ''

    # Note: Using .applymap for Pandas versions < 2.1.0. If you get an error, change this to .map
    styled_health_df = health_df.style.applymap(highlight_status, subset=['operational_status'])
    st.dataframe(styled_health_df, use_container_width=True)

    with st.expander("ℹ️ How to read this table (Metrics & Logic)"):
        st.markdown("""
        * **supply_capacity:** The total number of weekly patient slots available across all *Active* clinicians in the market.
        * **demand_volume:** The total weekly sessions required by patients currently matched or waitlisted.
        * **waitlisted_patients:** Count of patients who have completed intake but do not have an active clinician.
        * **utilization_pct:** `(Demand / Supply) * 100`. Represents how "full" a market is. 
        * **operational_status:** * **BOTTLENECK (Red):** Utilization is over 100%. We cannot serve our current patient demand.
            * **WARNING (Yellow):** Utilization is over 85%. Nearing capacity; hiring should be prioritized.
            * **HEALTHY (Green):** Utilization is under 85%. Ample room for new patient intake.
        """)

    st.divider()

    # --- SECOND ROW: Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Supply vs. Demand by Market")
        chart_data = health_df[['market', 'supply_capacity', 'demand_volume']].set_index('market')
        st.bar_chart(chart_data)
        
        with st.expander("ℹ️ Understanding this chart"):
            st.markdown("""
            This chart visualizes the core capacity constraint.
            * **Supply Capacity (Line 1):** The current maximum throughput of our active clinicians.
            * **Demand Volume (Line 2):** The required weekly sessions from our patient base.
            * **Insight:** If the Demand bar is taller than the Supply bar in a specific market, that market is actively bottlenecked and requires immediate supply-side intervention (hiring or re-routing).
            """)

    with col2:
        st.subheader("Patient Churn vs. Target (15%)")
        churn_data = patient_df[['market', 'actual_churn_rate_pct', 'target_churn_rate_pct']].set_index('market')
        st.bar_chart(churn_data)
        
        with st.expander("ℹ️ Understanding this chart"):
            st.markdown("""
            This chart audits our demand assumptions by comparing actual market attrition against our financial models.
            * **Target Churn Rate (Line 1):** The business model assumes a baseline 15% patient churn rate.
            * **Actual Churn Rate (Line 2):** The real historical churn rate derived from EMR data.
            * **Insight:** Markets where the actual churn significantly exceeds the 15% target indicate potential operational issues (poor clinician matching, long wait times) that need investigation.
            """)

    st.divider()

    # --- THIRD ROW: Hiring Funnel Audit ---
    st.header("Clinician Hiring Audit")
    st.markdown("Monitoring actual starts against the **85% Offer Acceptance** target baseline.")
    st.dataframe(
        clinician_df[['market', 'total_offers_extended', 'forecasted_starts', 'actual_starts', 'actual_start_rate_pct']], 
        use_container_width=True
    )
    
    with st.expander("ℹ️ How to read this table (Metrics & Logic)"):
        st.markdown("""
        * **total_offers_extended:** Total number of job offers sent to clinician candidates in the HR system.
        * **forecasted_starts:** `total_offers * 0.85`. The expected number of starts based on Finance's 85% offer acceptance assumption.
        * **actual_starts:** The true count of clinicians who reached 'Active' or 'Onboarding' status.
        * **actual_start_rate_pct:** `(actual_starts / total_offers) * 100`. 
        * **Insight:** If a market's actual start rate falls far below 85%, Recruiting needs to audit compensation competitiveness or onboarding bottlenecks in that specific region.
        """)

# ==========================================
# PAGE 2: UNDER THE HOOD
# ==========================================
elif page == "⚙️ Under the Hood (Methodology)":
    st.title("⚙️ Under the Hood: Pipeline & Methodology")
    st.markdown("""
    This section breaks down the data engineering pipeline used to power the Executive Dashboard. 
    It demonstrates the ability to ingest messy raw data, clean it using SQL, and build reliable operational models.
    """)

    st.divider()

    # --- 1. Raw Data ---
    st.header("1. Ingestion: The Messy Raw Data")
    st.markdown("Data is simulated to mimic two disparate, messy systems: an **ATS/HR System** (Clinicians) and an **EMR/Intake System** (Patients).")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Raw Clinician Data (HR)")
        try:
            raw_clinicians = pd.read_csv("data/raw_clinicians.csv")
            
            # 1. Isolate the anomalies
            anomalous_clinicians = raw_clinicians[(raw_clinicians['target_capacity'] > 100) | (raw_clinicians['start_date'].isna() & raw_clinicians['status'].isin(['Active', 'Onboarding']))]
            # 2. Isolate the normal rows
            normal_clinicians = raw_clinicians[~raw_clinicians.index.isin(anomalous_clinicians.index)]
            # 3. Combine 3 bad rows with 7 good rows for a perfect visual example
            display_clinicians = pd.concat([anomalous_clinicians.head(3), normal_clinicians.head(7)])
            
            st.dataframe(display_clinicians, use_container_width=True)
            st.caption("Notice the injected anomalies forced to the top: missing start dates and 'fat-fingered' capacity targets (e.g., 400 instead of 40).")
        except:
            st.error("Could not load raw_clinicians.csv. Ensure the ingest.py script has been run.")

    with col2:
        st.subheader("Raw Patient Data (EMR)")
        try:
            raw_patients = pd.read_csv("data/raw_patients.csv")
            
            # 1. Isolate the anomalies
            anomalous_patients = raw_patients[(raw_patients['market'].isna()) | (raw_patients['churn_date'] < raw_patients['intake_date'])]
            # 2. Isolate the normal rows
            normal_patients = raw_patients[~raw_patients.index.isin(anomalous_patients.index)]
            # 3. Combine 3 bad rows with 7 good rows
            display_patients = pd.concat([anomalous_patients.head(3), normal_patients.head(7)])
            
            st.dataframe(display_patients, use_container_width=True)
            st.caption("Notice the injected anomalies forced to the top: missing market routing and illogical churn dates (churning before intake).")
        except:
            st.error("Could not load raw_patients.csv. Ensure the ingest.py script has been run.")

    st.divider()

    # --- 2. Transformation ---
    st.header("2. Transformation: Cleaning with DuckDB & SQL")
    st.markdown("Raw CSVs are loaded into a local **DuckDB** warehouse. SQL is used to enforce data integrity and clean operational logic errors.")

    st.subheader("SQL Snippet: Cleaning Patient Demand Data")
    sql_code = '''
CREATE OR REPLACE TABLE clean_patients AS
SELECT DISTINCT
    patient_id,
    COALESCE(market, 'Unknown') AS market, -- Handle missing routing
    status,
    CAST(intake_date AS DATE) AS intake_date,
    CAST(churn_date AS DATE) AS churn_date,
    sessions_per_month
FROM raw_patients
-- Fix logic error where churn date happened BEFORE intake date
WHERE churn_date IS NULL OR CAST(churn_date AS DATE) >= CAST(intake_date AS DATE)
    '''
    st.code(sql_code, language="sql")

    st.divider()

    # --- 3. Modeling ---
    st.header("3. Modeling: Supply vs. Demand Logic")
    st.markdown("The core capacity KPI requires aligning two different time scales: Weekly Clinician Capacity vs. Monthly Patient Sessions.")

    st.subheader("SQL Snippet: Computing Market Demand")
    demand_code = '''
CREATE OR REPLACE TABLE market_demand AS
SELECT 
    market,
    COUNT(patient_id) AS total_patients,
    -- Divide by 4 to get a rough weekly demand estimate to align with supply
    SUM(CASE WHEN status IN ('Matched', 'Waitlisted') THEN sessions_per_month ELSE 0 END) / 4.0 AS weekly_session_demand,
    COUNT(CASE WHEN status = 'Waitlisted' THEN patient_id END) AS waitlisted_patients
FROM clean_patients
GROUP BY market
    '''
    st.code(demand_code, language="sql")
    
    st.success("This structured approach ensures that the KPIs on the main dashboard are built on a reliable, transparent foundation.")