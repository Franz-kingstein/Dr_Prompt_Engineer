import pandas as pd
import os
import mlflow
from datetime import datetime, timedelta

# --- Configuration ---
RAW_DATA_PATH = "data/raw_users.csv"
PROCESSED_DATA_PATH = "feature_repo/feature_repo/data/user_features.parquet"
MLFLOW_EXPERIMENT = "Data_Lineage_Pipeline"

def create_mock_raw_data():
    """Simulates raw data ingestion from a source (DB/CSV)."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    data = {
        "user_id": [1001, 1002, 1003, 1004],
        "expertise_level": ["Expert", "Beginner", "Intermediate", "Professional"],
        "preferred_language": ["Python", "JavaScript", "C++", "Python"],
        "last_task_type": ["code", "image", "document", "code"],
        "signup_date": ["2026-01-01", "2026-02-15", "2026-03-10", "2026-04-01"]
    }
    df = pd.DataFrame(data)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"✅ Raw mock data created at {RAW_DATA_PATH}")

def run_preprocessing():
    """Standardizes data and adds Feast-specific timestamps."""
    print("⏳ Starting preprocessing for Feast...")
    
    # 1. Load Raw
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 2. Add Feast columns (event_timestamp is required for point-in-time joins)
    df['event_timestamp'] = datetime.now()
    df['created_timestamp'] = datetime.now()
    
    # 3. Type Conversion
    df['user_id'] = df['user_id'].astype(int)
    
    # 4. Versioning Logic (Simple incremental version)
    version = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 5. Log to MLflow
    mlflow.set_experiment(MLFLOW_EXPERIMENT)
    with mlflow.start_run(run_name=f"data_ingestion_{version}"):
        mlflow.log_param("raw_source", RAW_DATA_PATH)
        mlflow.log_param("target_parquet", PROCESSED_DATA_PATH)
        mlflow.log_param("row_count", len(df))
        
        # Save as Parquet (Feast requirement)
        df.to_parquet(PROCESSED_DATA_PATH)
        mlflow.log_artifact(PROCESSED_DATA_PATH)
        
        print(f"🚀 Data version {version} processed and saved to {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    create_mock_raw_data()
    run_preprocessing()
    print("✨ Data Lineage Pipeline task complete.")
