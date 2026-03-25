from utils import get_connection

def run_transform():
    conn = get_connection()
    print("🔄 Starting transformation layer...")

    # --- 1. Load Raw CSVs into DuckDB ---
    # DuckDB can read CSVs directly and create tables on the fly
    conn.execute("""
        CREATE OR REPLACE TABLE raw_clinicians AS 
        SELECT * FROM read_csv_auto('data/raw_clinicians.csv');
        
        CREATE OR REPLACE TABLE raw_patients AS 
        SELECT * FROM read_csv_auto('data/raw_patients.csv');
    """)
    print("✅ Raw data loaded into DuckDB.")

    # --- 2. Clean Clinician Data (Supply) ---
    conn.execute("""
        CREATE OR REPLACE TABLE clean_clinicians AS
        SELECT DISTINCT -- Removes those duplicate API syncs we injected
            clinician_id,
            market,
            status,
            CAST(offer_date AS DATE) AS offer_date,
            CAST(start_date AS DATE) AS start_date,
            
            -- Fix the fat-finger data entry (e.g., 400 instead of 40)
            CASE 
                WHEN target_capacity > 100 THEN target_capacity / 10 
                ELSE target_capacity 
            END AS target_capacity,
            
            ramp_up_weeks
        FROM raw_clinicians
    """)
    print("✅ Clinician data cleaned (Duplicates removed, capacity anomalies fixed).")

    # --- 3. Clean Patient Data (Demand) ---
    conn.execute("""
        CREATE OR REPLACE TABLE clean_patients AS
        SELECT DISTINCT
            patient_id,
            
            -- Handle the missing market routing issue
            COALESCE(market, 'Unknown') AS market, 
            
            status,
            CAST(intake_date AS DATE) AS intake_date,
            CAST(churn_date AS DATE) AS churn_date,
            sessions_per_month
        FROM raw_patients
        
        -- Fix the logic error where churn date happened BEFORE intake date
        WHERE churn_date IS NULL OR CAST(churn_date AS DATE) >= CAST(intake_date AS DATE)
    """)
    print("✅ Patient data cleaned (Missing markets and time-travel logic errors handled).")

    # --- 4. Verify Results ---
    clinician_count = conn.execute("SELECT COUNT(*) FROM clean_clinicians").fetchone()[0]
    patient_count = conn.execute("SELECT COUNT(*) FROM clean_patients").fetchone()[0]
    
    print(f"🎉 Transformation complete! Ready for modeling:")
    print(f"   📊 Clean Clinicians: {clinician_count}")
    print(f"   📊 Clean Patients: {patient_count}")

if __name__ == "__main__":
    run_transform()