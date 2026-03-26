#This script creates 2 csvs that simulate HR/ATS data about clinicians and EMR data about patients 

import pandas as pd
import random
from faker import Faker
import os
from datetime import datetime, timedelta

fake = Faker()

def generate_healthcare_ops_data(num_clinicians=250, num_patients=6000):
    # JD mentions 20+ markets. We'll simulate 10 for the data model.
    markets = ["CA", "NY", "TX", "FL", "IL", "WA", "PA", "GA", "NC", "VA"]

    # --- 1. CLINICIAN SUPPLY DATA (Simulating an HR/ATS System) ---
    clinicians = []
    for i in range(num_clinicians):
        clinician_id = f"CLIN-{i:04d}"
        status = random.choices(["Active", "Onboarding", "Offered", "Churned"], weights=[0.6, 0.15, 0.1, 0.15])[0]
        
        offer_date = fake.date_between(start_date='-1y', end_date='today')
        # Simulate hiring velocity: time between offer and start date
        start_date = offer_date + timedelta(days=random.randint(14, 45)) if status in ["Active", "Onboarding", "Churned"] else None
        
        # JD specific: ramp-up time and expected patient capacity
        target_capacity = random.choice([20, 30, 40]) # Patient slots per week
        ramp_up_weeks = random.randint(2, 6)

        row = {
            "clinician_id": clinician_id,
            "market": random.choice(markets),
            "status": status,
            "offer_date": offer_date.isoformat(),
            "start_date": start_date.isoformat() if start_date else None,
            "target_capacity": target_capacity,
            "ramp_up_weeks": ramp_up_weeks
        }

        # --- Inject Messy HR Data ---
        if random.random() < 0.05:
            # Operational failure: HR forgot to log the start date in the ATS
            row["start_date"] = None 
        elif random.random() < 0.03:
            # Fat-finger data entry (e.g., typing 400 instead of 40 for capacity)
            row["target_capacity"] *= 10 

        clinicians.append(row)

    df_clinicians = pd.DataFrame(clinicians)


    # --- 2. PATIENT DEMAND DATA (Simulating an Intake/EMR System) ---
    patients = []
    for i in range(num_patients):
        patient_id = f"PAT-{i:05d}"
        intake_date = fake.date_between(start_date='-1y', end_date='today')
        
        status = random.choices(["Matched", "Waitlisted", "Churned"], weights=[0.7, 0.15, 0.15])[0]
        
        churn_date = None
        if status == "Churned":
            # JD specific: patient churn modeling
            churn_date = intake_date + timedelta(days=random.randint(5, 120))

        row = {
            "patient_id": patient_id,
            "market": random.choice(markets),
            "intake_date": intake_date.isoformat(),
            "status": status,
            "churn_date": churn_date.isoformat() if churn_date else None,
            "sessions_per_month": random.choice([2, 4]) # Bi-weekly or weekly
        }

        # --- Inject Messy Intake Data ---
        if random.random() < 0.04:
            # Missing market routing (prevents accurate regional forecasting)
            row["market"] = None 
        elif random.random() < 0.02 and churn_date:
            # Logic Error: System says they churned BEFORE their intake date
            row["churn_date"] = (intake_date - timedelta(days=10)).isoformat() 
        
        patients.append(row)

    df_patients = pd.DataFrame(patients)
    
    # Introduce duplicates (very common in automated integration syncing)
    df_patients = pd.concat([df_patients, df_patients.sample(frac=0.03)], ignore_index=True)

    return df_clinicians, df_patients

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Generate the data
    df_supply, df_demand = generate_healthcare_ops_data()
    
    # Save to two separate CSVs
    df_supply.to_csv("data/raw_clinicians.csv", index=False)
    df_demand.to_csv("data/raw_patients.csv", index=False)
    
    print(f"✅ Generated {len(df_supply)} clinician records (HR System).")
    print(f"✅ Generated {len(df_demand)} patient records (Intake System).")
    print("📁 Saved to data/ folder.")