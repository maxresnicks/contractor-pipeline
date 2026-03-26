import streamlit as st
import duckdb
import pandas as pd
import altair as alt

# --- Page Configuration ---
st.set_page_config(page_title="Two Chairs: Capacity Dashboard", page_icon="🪑", layout="wide")

# --- Database Connection ---
@st.cache_data
def load_data(query):
    # Ensure the path matches your repo structure
    conn = duckdb.connect("db/warehouse.duckdb")
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

# ==========================================
# SIDEBAR & NAVIGATION
# ==========================================
st.sidebar.title("🪑 Operations Menu")
page = st.sidebar.radio("Go to:", ["📊 Executive Dashboard", "🛠️ Under the Hood"])

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
    Monitoring Supply (Clinicians) vs. Demand (Patients) across 10 regional markets.
    *Simulating active capacity plus hiring forecasts.*
    """)

    # Apply the "What-If" logic to our supply via SQL
    query = f"""
        SELECT 
            market,
            active_clinicians,
            total_active_capacity + ({extra_hires} * {avg_capacity}) as simulated_capacity,
            weekly_session_demand,
            waitlisted_patients,
            operational_status,
            ROUND((weekly_session_demand / (total_active_capacity + ({extra_hires} * {avg_capacity}))) * 100, 1) as simulated_utilization
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
    col2.metric("Simulated New Supply", f"+{extra_hires * 10} Clinicians", f"{extra_hires * 10 * avg_capacity} sessions/wk")
    col3.metric("Critical Markets", len(health_df[health_df['simulated_utilization'] > 100]))

    st.divider()

    # --- SECOND ROW: Table & Map ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Regional Utilization & Capacity")
        st.dataframe(health_df[['market', 'active_clinicians', 'simulated_capacity', 'weekly_session_demand', 'simulated_utilization']], use_container_width=True)
    
    with c2:
        # FEATURE 4: THE WAITLIST MAP (Mock Coordinates)
        st.subheader("📍 Demand Heat Map")
        map_data = pd.DataFrame({
            'lat': [37.77, 34.05, 40.71, 32.77, 47.60, 39.73, 25.76, 33.74, 39.95, 42.36],
            'lon': [-122.41, -118.24, -74.00, -96.79, -122.33, -104.99, -80.19, -84.38, -75.16, -71.05],
            'market': ['CA', 'CA-S', 'NY', 'TX', 'WA', 'CO', 'FL', 'GA', 'PA', 'MA'],
            'demand': health_df['weekly_session_demand']
        })
        st.map(map_data, size='demand', color='#ff4b4b')

    # --- THIRD ROW: Churn & Hiring ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Patient Churn vs. Target (15%)")
        churn_chart = patient_df[['market', 'actual_churn_rate_pct', 'target_churn_rate_pct']].set_index('market')
        st.bar_chart(churn_chart)
        
    with col_b:
        st.subheader("Clinician Offer Acceptance Audit")
        st.dataframe(clinician_df[['market', 'total_offers_extended', 'actual_starts', 'actual_start_rate_pct']], use_container_width=True)

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
    except:
        st.error("Raw data files not found in /data folder.")