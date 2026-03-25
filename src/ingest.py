import pandas as pd
import random
from faker import Faker
import os

fake = Faker()

def generate_cue_point_data(num_records=1000):
    data = []
    # Simulate a team of 15 contractors
    contractors = [f"C-{i:03d}" for i in range(1, 16)]

    for _ in range(num_records):
        contractor_id = random.choice(contractors)
        
        # Base productivity: 100-400 videos per day
        videos_processed = int(random.gauss(250, 60))
        if videos_processed < 0: videos_processed = 0

        # Cue points naturally scale with the number of videos processed
        intro_cues = videos_processed + random.randint(-15, 15)
        ad_cues = (videos_processed * random.randint(2, 6))
        credits_cues = videos_processed + random.randint(-10, 10)
        early_credits_cues = int(videos_processed * 0.4) # Not all videos have these

        # Errors flagged during QA
        errors_flagged = max(0, int(random.gauss(8, 4)))

        # Hours logged for the shift
        hours_logged = round(random.uniform(4.0, 8.5), 2)

        row = {
            "contractor_id": contractor_id,
            "shift_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
            "videos_processed": videos_processed,
            "intro_cues": max(0, intro_cues),
            "ad_cues": max(0, ad_cues),
            "credits_cues": max(0, credits_cues),
            "early_credits_cues": max(0, early_credits_cues),
            "errors_flagged": errors_flagged,
            "hours_logged": hours_logged
        }

        # --- INTRODUCE MESSY DATA (The real-world anomalies) ---
        anomaly_roll = random.random()

        if anomaly_roll < 0.04:
            # Human error: Forgot to clock out (Missing hours)
            row["hours_logged"] = None
        elif anomaly_roll < 0.07:
            # Fat-finger data entry (Unrealistic volume for one shift)
            row["videos_processed"] *= 15
        elif anomaly_roll < 0.09:
            # System glitch: Negative ad cues
            row["ad_cues"] = -45
        elif anomaly_roll < 0.12:
            # Completely null record from an API timeout or system crash
            row["videos_processed"] = None
            row["ad_cues"] = None

        data.append(row)

    df = pd.DataFrame(data)

    # Introduce duplicate rows (very common in automated log ingestion)
    duplicates = df.sample(frac=0.03)
    df = pd.concat([df, duplicates], ignore_index=True)

    return df

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Generate the data and save to CSV
    df = generate_cue_point_data(1500)
    file_path = "data/raw_contractor_logs.csv"
    df.to_csv(file_path, index=False)
    
    print(f"✅ Successfully generated {len(df)} rows of messy contractor data!")
    print(f"📁 Saved to: {file_path}")