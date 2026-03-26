# This script conducts multiple 'Forecast vs. Actuals' audits by comparing real-world clinician starts (from raw_clinicians.csv) and patient churn (from raw_patients.csv) against financial model assumptions (that I've assumed).

from utils import get_connection
import pandas as pd

def run_audit():
    conn = get_connection()
    print("🔍 Running Forecast vs. Actuals Audit...\n")

    # --- 1. Clinician Hiring Funnel (Offer Acceptance & Ramp-up) ---
    # The JD mentions tracking "offer acceptance rates"
    conn.execute("""
        CREATE OR REPLACE TABLE audit_clinician_hiring AS
        SELECT 
            market,
            COUNT(clinician_id) AS total_offers_extended,
            COUNT(CASE WHEN status IN ('Active', 'Onboarding') THEN 1 END) AS actual_starts,
            COUNT(CASE WHEN status = 'Churned' THEN 1 END) AS pre_start_churns,
            
            -- Hypothetical Baseline: Finance forecasted an 85% offer-to-start rate
            ROUND(COUNT(clinician_id) * 0.85, 0) AS forecasted_starts,
            
            -- Actual Rate
            ROUND((COUNT(CASE WHEN status IN ('Active', 'Onboarding') THEN 1 END) * 100.0) / NULLIF(COUNT(clinician_id), 0), 1) AS actual_start_rate_pct
        FROM clean_clinicians
        GROUP BY market
    """)

    # --- 2. Patient Churn Audit (Demand Attrition) ---
    # The JD mentions tracking "patient churn" to improve model assumptions
    conn.execute("""
        CREATE OR REPLACE TABLE audit_patient_churn AS
        SELECT 
            market,
            COUNT(patient_id) AS total_intakes,
            COUNT(CASE WHEN status = 'Churned' THEN 1 END) AS total_churned,
            
            -- Hypothetical Target: The business modeled demand assuming a 15% churn rate
            15.0 AS target_churn_rate_pct,
            
            -- Actual Rate
            ROUND((COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0) / NULLIF(COUNT(patient_id), 0), 1) AS actual_churn_rate_pct
        FROM clean_patients
        GROUP BY market
    """)

    # --- 3. Print the Audit Reports ---
    print("--- 📉 Clinician Hiring: Forecast vs. Actual Starts ---")
    # Fetch top 5 markets to keep the terminal clean
    clinician_audit_df = conn.execute("""
        SELECT market, total_offers_extended, forecasted_starts, actual_starts, actual_start_rate_pct 
        FROM audit_clinician_hiring 
        ORDER BY actual_start_rate_pct ASC 
        LIMIT 5
    """).fetchdf()
    print(clinician_audit_df.to_markdown(index=False))
    print("\n")

    print("--- 🏃‍♂️ Patient Demand: Churn Rate Audit ---")
    # Fetch the 5 markets with the highest churn
    patient_audit_df = conn.execute("""
        SELECT market, total_intakes, total_churned, target_churn_rate_pct, actual_churn_rate_pct 
        FROM audit_patient_churn 
        ORDER BY actual_churn_rate_pct DESC 
        LIMIT 5
    """).fetchdf()
    print(patient_audit_df.to_markdown(index=False))
    
    print("\n✅ Audit complete. Historical trends ready to be fed back into capacity models.")

if __name__ == "__main__":
    run_audit()