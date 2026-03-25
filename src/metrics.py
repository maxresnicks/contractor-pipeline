from utils import get_connection
import pandas as pd

def run_metrics():
    conn = get_connection()
    print("📊 Computing Supply & Demand Metrics...")

    # --- 1. Calculate Market Supply (Clinician Capacity) ---
    # We only count 'Active' capacity for current supply, but track 'Onboarding' for future forecasting.
    conn.execute("""
        CREATE OR REPLACE TABLE market_supply AS
        SELECT 
            market,
            COUNT(clinician_id) AS total_clinicians,
            SUM(CASE WHEN status = 'Active' THEN target_capacity ELSE 0 END) AS active_weekly_capacity,
            SUM(CASE WHEN status = 'Onboarding' THEN target_capacity ELSE 0 END) AS pipeline_weekly_capacity
        FROM clean_clinicians
        GROUP BY market
    """)
    print("✅ Market Supply modeled.")

    # --- 2. Calculate Market Demand (Patient Sessions) ---
    # We convert monthly sessions to a weekly metric to align with clinician capacity.
    conn.execute("""
        CREATE OR REPLACE TABLE market_demand AS
        SELECT 
            market,
            COUNT(patient_id) AS total_patients,
            -- Divide by 4 to get a rough weekly demand estimate
            SUM(CASE WHEN status IN ('Matched', 'Waitlisted') THEN sessions_per_month ELSE 0 END) / 4.0 AS weekly_session_demand,
            COUNT(CASE WHEN status = 'Waitlisted' THEN patient_id END) AS waitlisted_patients
        FROM clean_patients
        GROUP BY market
    """)
    print("✅ Market Demand modeled.")

    # --- 3. Supply vs. Demand Comparison (The core Two Chairs KPI) ---
    conn.execute("""
        CREATE OR REPLACE TABLE market_health_dashboard AS
        SELECT 
            s.market,
            s.active_weekly_capacity AS supply_capacity,
            d.weekly_session_demand AS demand_volume,
            d.waitlisted_patients,
            -- Calculate utilization percentage
            ROUND((d.weekly_session_demand / NULLIF(s.active_weekly_capacity, 0)) * 100, 1) AS utilization_pct,
            -- Identify operational bottlenecks
            CASE 
                WHEN d.weekly_session_demand > s.active_weekly_capacity THEN '🚨 BOTTLENECK: Demand > Supply'
                WHEN (d.weekly_session_demand / NULLIF(s.active_weekly_capacity, 0)) > 0.85 THEN '⚠️ WARNING: Near Capacity'
                ELSE '✅ HEALTHY'
            END AS operational_status
        FROM market_supply s
        JOIN market_demand d ON s.market = d.market
        ORDER BY utilization_pct DESC
    """)
    print("✅ Bottlenecks identified and cross-market comparisons generated.\n")

    # --- 4. Display the Results ---
    print("--- 🌍 Regional Market Health Overview ---")
    
    # Fetch the final table into a pandas DataFrame so it prints nicely in the terminal
    df = conn.execute("SELECT * FROM market_health_dashboard").fetchdf()
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    run_metrics()