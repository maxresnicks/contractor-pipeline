import streamlit as st
import duckdb
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(page_title="Two Chairs: Capacity Dashboard", page_icon="🪑", layout="wide")

# --- Database Connection ---
@st.cache_data
def load_data(query):
    conn = duckdb.connect("db/warehouse.duckdb")
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

# ==========================================
# SIDEBAR & NAVIGATION
# ==========================================
st.sidebar.title("🪑 Operations Menu")
page = st.sidebar.radio("Go to:", ["📊 Executive Dashboard", "🛠️ Under the Hood", "📖 Architecture README"])

st.sidebar.divider()

# FEATURE 1: WHAT-IF HIRING SLIDER (Only shows on Dashboard)
extra_hires = 0
avg_capacity = 25
if page == "📊 Executive Dashboard":
    st.sidebar.subheader("Strategic Planning")
    st.sidebar.markdown("Simulate hiring impact on market utilization.")
    extra_hires = st.sidebar.slider("New Hires per Market", 0, 10, 0)

# ==========================================
# PAGE 1: EXECUTIVE DASHBOARD
# ==========================================
if page == "📊 Executive Dashboard":
    st.title("🪑🪑 Two Chairs: Market Capacity & Operations Dashboard")
    st.markdown("""
    Monitoring Supply (Clinicians) vs. Demand (Patients) across regional markets.
    *Simulating active capacity plus hiring forecasts.*
    """)

    # Apply the "What-If" logic using ACTUAL column names and dynamic statuses
    query = f"""
        SELECT 
            market,
            supply_capacity,
            supply_capacity + ({extra_hires} * {avg_capacity}) as simulated_capacity,
            demand_volume,
            waitlisted_patients,
            CASE 
                WHEN (demand_volume / (supply_capacity + ({extra_hires} * {avg_capacity}))) > 1.0 THEN '🚨 BOTTLENECK'
                WHEN (demand_volume / (supply_capacity + ({extra_hires} * {avg_capacity}))) > 0.85 THEN '⚠️ WARNING'
                ELSE '✅ HEALTHY'
            END as simulated_status,
            ROUND((demand_volume / (supply_capacity + ({extra_hires} * {avg_capacity}))) * 100, 1) as simulated_utilization
        FROM market_health_dashboard
        ORDER BY simulated_utilization DESC
    """
    
    try:
        health_df = load_data(query)
        patient_df = load_data("SELECT * FROM audit_patient_churn")
        clinician_df = load_data("SELECT * FROM audit_clinician_hiring")
    except Exception as e:
        st.error(f"Database Error: {e}")
        st.stop()

    # --- TOP ROW: KPI Metrics ---
    col1, col2, col3 = st.columns(3)
    avg_util = health_df['simulated_utilization'].mean()
    col1.metric("Avg Market Utilization", f"{avg_util:.1f}%", 
                delta=f"{avg_util - 92:.1f}%", delta_color="inverse")
    col2.metric("Simulated New Supply", f"+{extra_hires * len(health_df)} Clinicians", f"+{extra_hires * len(health_df) * avg_capacity} sessions/wk")
    col3.metric("Critical Markets", len(health_df[health_df['simulated_utilization'] > 100]))

    st.divider()

    # --- SECOND ROW: Regional Table ---
    st.subheader("Regional Utilization & Capacity")
    display_cols = ['market', 'supply_capacity', 'simulated_capacity', 'demand_volume', 'simulated_utilization', 'simulated_status']
    
    # Make a copy and format it
    display_df = health_df[display_cols].copy()
    display_df.index = display_df.index + 1 
    
    # Rename columns for absolute clarity in healthcare operations
    display_df = display_df.rename(columns={
        'market': 'Market',
        'supply_capacity': 'Current Capacity (Weekly Appointments)',
        'simulated_capacity': 'Projected Capacity (With Hires)',
        'demand_volume': 'Patient Demand (Weekly Appointments)',
        'simulated_utilization': 'Projected Utilization (%)',
        'simulated_status': 'Capacity Status'
    })
    
    st.dataframe(display_df, use_container_width=True)
    
    with st.expander("ℹ️ How to read this table (Metrics & Logic)"):
        st.markdown("""
        * **Current Capacity:** The baseline weekly patient slots available across all *Active* clinicians.
        * **Projected Capacity:** Baseline supply + the simulated new hires from the sidebar slider.
        * **Patient Demand:** The total weekly sessions required by patients.
        * **Projected Utilization:** `(Demand / Projected Capacity) * 100`. Represents how "full" a market is. 
        * **Capacity Status:** * **BOTTLENECK:** Utilization is >100%. We cannot serve our current demand.
            * **WARNING:** Utilization is >85%. Nearing capacity; prioritize hiring.
            * **HEALTHY:** Utilization is <85%. Ample room for new patient intake.
        """)

    st.divider()

    # --- THIRD ROW: Demand Map ---
    st.subheader("📍 Demand & Health Map")
    
    # Map coordinates cleanly for ALL 50 states
    coords = {
        "AL": [32.8, -86.8], "AK": [61.4, -152.4], "AZ": [33.4, -111.9], "AR": [35.0, -92.4], 
        "CA": [36.1, -119.7], "CO": [39.1, -105.3], "CT": [41.6, -72.8], "DE": [39.3, -75.5], 
        "FL": [27.8, -81.7], "GA": [33.0, -83.6], "HI": [21.1, -157.5], "ID": [44.2, -114.5], 
        "IL": [40.3, -89.0], "IN": [39.8, -86.3], "IA": [42.0, -93.2], "KS": [38.5, -96.7], 
        "KY": [37.7, -84.7], "LA": [31.2, -91.9], "ME": [44.7, -69.4], "MD": [39.1, -76.8], 
        "MA": [42.2, -71.5], "MI": [43.3, -84.5], "MN": [45.7, -93.9], "MS": [32.7, -89.7], 
        "MO": [38.5, -92.3], "MT": [46.9, -110.5], "NE": [41.1, -98.3], "NV": [38.3, -117.1], 
        "NH": [43.5, -71.6], "NJ": [40.3, -74.5], "NM": [34.8, -106.2], "NY": [42.2, -74.9], 
        "NC": [35.6, -79.8], "ND": [47.5, -99.8], "OH": [40.4, -82.8], "OK": [35.6, -96.9], 
        "OR": [44.6, -122.1], "PA": [40.6, -77.2], "RI": [41.7, -71.5], "SC": [33.9, -80.9], 
        "SD": [44.3, -99.4], "TN": [35.7, -86.7], "TX": [31.1, -97.6], "UT": [40.2, -111.9], 
        "VT": [44.0, -72.7], "VA": [37.8, -78.2], "WA": [47.4, -121.5], "WV": [38.5, -81.0], 
        "WI": [44.3, -89.6], "WY": [42.8, -107.3]
    }
    
    map_df = health_df.copy()
    
    # Add Lat/Lon and filter out "Null Island" (0,0)
    map_df['lat'] = map_df['market'].map(lambda x: coords.get(x, [0,0])[0])
    map_df['lon'] = map_df['market'].map(lambda x: coords.get(x, [0,0])[1])
    map_df = map_df[(map_df['lat'] != 0) & (map_df['lon'] != 0)] 
    
    # Scale the size exponentially
    map_df['scaled_demand'] = map_df['demand_volume'] * 800 
    
    # REAL-TIME DYNAMIC COLORING
    def get_dynamic_color(utilization):
        if utilization > 100: return '#EF4444' # Red
        elif utilization > 85: return '#F59E0B'  # Yellow
        else: return '#10B981'                   # Green
        
    map_df['status_color'] = map_df['simulated_utilization'].apply(get_dynamic_color)
    
    st.map(map_df, latitude='lat', longitude='lon', size='scaled_demand', color='status_color')

    # --- FOURTH ROW: Churn & Hiring ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Patient Churn vs. Target (15%)")
        churn_chart = patient_df[['market', 'actual_churn_rate_pct', 'target_churn_rate_pct']].set_index('market')
        st.bar_chart(churn_chart)
        
        with st.expander("ℹ️ Understanding this chart"):
            st.markdown("""
            This audits our demand assumptions by comparing actual market attrition against financial models.
            * **Target Churn Rate:** The business model assumes a baseline 15% patient drop-off.
            * **Actual Churn Rate:** The real historical churn rate derived from EMR data.
            * **Insight:** Markets where actual churn significantly exceeds the 15% target indicate potential operational issues (poor clinician matching, long wait times).
            """)
        
    with col_b:
        st.subheader("Clinician Offer Acceptance Audit")
        st.dataframe(clinician_df[['market', 'total_offers_extended', 'actual_starts', 'actual_start_rate_pct']], use_container_width=True)
        
        with st.expander("ℹ️ How to read this table (Metrics & Logic)"):
            st.markdown("""
            Monitoring actual starts against the **85% Offer Acceptance** target baseline.
            * **total_offers_extended:** Total job offers sent to clinician candidates in the HR system.
            * **actual_starts:** Count of clinicians who reached 'Active' or 'Onboarding' status.
            * **actual_start_rate_pct:** `(actual_starts / total_offers) * 100`. 
            * **Insight:** If a market's start rate falls far below 85%, Recruiting needs to audit compensation competitiveness or onboarding delays in that region.
            """)

# ==========================================
# PAGE 2: UNDER THE HOOD
# ==========================================
elif page == "🛠️ Under the Hood":
    st.title("🏗️ Engineering Methodology")
    st.markdown("This page documents the data integrity audits and onboarding velocity metrics.")

    # FEATURE 2: ONBOARDING VELOCITY
    st.subheader("⏱️ Onboarding Velocity (Supply Drag)")
    velocity_query = """
        SELECT 
            market,
            AVG(date_diff('day', CAST(offer_date AS DATE), CAST(start_date AS DATE))) as avg_days_to_start
        FROM raw_clinicians
        WHERE status = 'Active'
        GROUP BY 1 ORDER BY 2 DESC
    """
    velocity_df = load_data(velocity_query)
    st.altair_chart(
        alt.Chart(velocity_df).mark_bar().encode(
            x=alt.X('avg_days_to_start', title='Avg Days (Offer -> Start)'),
            y=alt.Y('market', sort='-x'),
            color=alt.condition(alt.datum.avg_days_to_start > 30, alt.value('#ff4b4b'), alt.value('#29b5e8'))
        ), use_container_width=True
    )

    # FEATURE 3: DATA QUALITY SCORECARD
    st.divider()
    st.subheader("🛡️ Data Integrity Audit")
    try:
        raw_p = pd.read_csv("data/raw_patients.csv")
        bad_dates = len(raw_p[raw_p['churn_date'] < raw_p['intake_date']])
        missing_mkt = raw_p['market'].isna().sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Data Health Score", f"{((len(raw_p) - (bad_dates + missing_mkt))/len(raw_p))*100:.1f}%")
        c2.metric("Rejected: Date Logic", bad_dates)
        c3.metric("Rejected: Missing Routing", missing_mkt)
        
        st.dataframe(raw_p[(raw_p['market'].isna()) | (raw_p['churn_date'] < raw_p['intake_date'])].head(10), use_container_width=True)
        st.caption("Auto-flagged records for Source System Cleanup.")
    except:
        st.error("Raw data files not found in /data folder.")

# ==========================================
# PAGE 3: ARCHITECTURE README
# ==========================================
elif page == "📖 Architecture README":
    st.title("📖 Project Architecture & README")
    st.markdown("""
    This project simulates a complete data engineering and analytics pipeline for a hybrid healthcare provider. 
    The core operational challenge is balancing **Supply (Clinicians)** with **Demand (Patients)** across multiple regional markets. 
    
    This application automates the ingestion, transformation, and visualization of disparate HR and EMR data to identify capacity bottlenecks.
    """)

    st.divider()

    st.header("Step 1: Synthetic Data Generation (`ingest.py`)")
    st.markdown("""
    Because real healthcare data is protected by HIPAA, this pipeline starts by generating over 6,000 rows of highly realistic, synthetic data using Python's `Faker` library. 
    
    Crucially, this script intentionally injects **operational anomalies** (e.g., missing market routing, illogical dates, and fat-fingered capacity targets) to simulate the messy reality of enterprise source systems.
    """)
    st.code("""
# src/ingest.py snippet: Injecting real-world anomalies into EMR data
def generate_patients(num_records=5000):
    patients = []
    for _ in range(num_records):
        intake = fake.date_between(start_date='-1y', end_date='today')
        
        # Inject illogical churn dates (churning before intake) ~3% of the time
        if random.random() < 0.03:
            churn = intake - timedelta(days=random.randint(1, 30))
        else:
            churn = intake + timedelta(days=random.randint(10, 100)) if random.random() < 0.15 else None
            
        patients.append({
            "patient_id": f"PAT-{fake.unique.random_int(min=10000, max=99999)}",
            "market": random.choice(MARKETS) if random.random() > 0.04 else None, # 4% missing routing
            "intake_date": intake,
            "churn_date": churn,
            "status": random.choices(['Matched', 'Waitlisted', 'Churned'], weights=[0.7, 0.15, 0.15])[0]
        })
    return pd.DataFrame(patients)
    """, language="python")

    st.header("Step 2: The Data Warehouse (`transform.py`)")
    st.markdown("""
    The raw CSVs are loaded into **DuckDB**, an in-process SQL OLAP database. DuckDB acts as the analytical data warehouse. 
    
    Here, SQL is used to clean the data, enforce business logic, and drop the anomalies generated in Step 1 before they corrupt the downstream metrics.
    """)
    st.code("""
-- src/transform.py snippet: Enforcing data integrity
CREATE OR REPLACE TABLE clean_patients AS
SELECT DISTINCT
    patient_id,
    COALESCE(market, 'Unknown') AS market,
    status,
    CAST(intake_date AS DATE) AS intake_date,
    CAST(churn_date AS DATE) AS churn_date
FROM raw_patients
-- Business Logic: A patient cannot churn before they complete intake
WHERE churn_date IS NULL OR CAST(churn_date AS DATE) >= CAST(intake_date AS DATE);
    """, language="sql")

    st.header("Step 3: Analytical Modeling (`metrics.py` & `audit.py`)")
    st.markdown("""
    With clean tables in DuckDB, the analytics layer calculates the core KPIs. It translates monthly patient volume into weekly session demand, and compares it against the active capacity of the clinician workforce.
    
    It also runs 'Forecast vs. Actuals' audits to track HR offer acceptance rates and operational patient attrition.
    """)
    st.code("""
-- src/metrics.py snippet: Calculating Market Bottlenecks
CREATE OR REPLACE TABLE market_health_dashboard AS
SELECT 
    s.market,
    s.active_clinicians,
    s.total_active_capacity AS supply_capacity,
    d.weekly_session_demand AS demand_volume,
    ROUND((d.weekly_session_demand / s.total_active_capacity) * 100, 1) AS utilization_pct,
    CASE 
        WHEN (d.weekly_session_demand / s.total_active_capacity) > 1.0 THEN 'BOTTLENECK'
        WHEN (d.weekly_session_demand / s.total_active_capacity) > 0.85 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as operational_status
FROM market_supply s
JOIN market_demand d ON s.market = d.market;
    """, language="sql")

    st.header("Step 4: The Interactive Frontend (`app.py`)")
    st.markdown("""
    Finally, **Streamlit** is used to serve the data to executive stakeholders. It connects directly to the DuckDB warehouse and provides an interactive interface. 
    
    The dashboard includes a 'What-If' strategic planning slider, allowing Operations Managers to simulate the impact of new hires on market utilization in real-time.
    """)
    st.code("""
# app.py snippet: Real-time What-If Analysis
st.sidebar.subheader("Strategic Planning")
extra_hires = st.sidebar.slider("New Hires per Market", 0, 10, 0)
avg_capacity = 25 

# Dynamically update the SQL query based on user input
query = f'''
    SELECT 
        market,
        supply_capacity + ({extra_hires} * {avg_capacity}) as simulated_capacity,
        ROUND((demand_volume / (supply_capacity + ({extra_hires} * {avg_capacity}))) * 100, 1) as simulated_utilization
    FROM market_health_dashboard
'''
health_df = load_data(query)
st.dataframe(health_df)
    """, language="python")

    st.success("By controlling the entire pipeline from raw data generation to executive visualization, this architecture ensures high data integrity and provides actionable operational leverage.")