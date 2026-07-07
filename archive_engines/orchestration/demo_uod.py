import pandas as pd
from archive_engines.orchestration.uod_ingestion import global_uod_ingestion

def run_demo():
    print("--- UOD Engine: Validation Demo ---")
    
    # 1. Define a mapping
    mapping = {
        "User": "user_id",
        "Earnings": "revenue",
        "Date": "timestamp"
    }
    
    # 2. Case: Valid Data
    valid_data = {
        "User": ["user_001", "user_002"],
        "Earnings": [1200.50, 4500.00],
        "Date": ["2024-01-01", "2024-01-02"]
    }
    df_valid = pd.DataFrame(valid_data)
    print("\n[STEP 1] Ingesting VALID data...")
    path = global_uod_ingestion.ingest_dataframe(df_valid, "valid_sales", mapping)
    print(f"SUCCESS: Saved to {path}")
    
    # 3. Case: Invalid Data (Type Mismatch)
    invalid_data = {
        "User": ["user_003"],
        "Earnings": ["FRAUD_DATA"], # Should be float
        "Date": ["2024-01-03"]
    }
    df_invalid = pd.DataFrame(invalid_data)
    print("\n[STEP 2] Ingesting INVALID data (type mismatch)...")
    try:
        global_uod_ingestion.ingest_dataframe(df_invalid, "invalid_sales", mapping)
    except ValueError as e:
        print(f"REJECTED: {e}")

    # 4. Case: Unknown Property
    unknown_mapping = {
        "SecretColumn": "secret_code" # Not in registry
    }
    df_unknown = pd.DataFrame({"SecretColumn": [123]})
    print("\n[STEP 3] Ingesting UNKNOWN property...")
    try:
        global_uod_ingestion.ingest_dataframe(df_unknown, "unknown_sales", unknown_mapping)
    except Exception as e:
        print(f"REJECTED: {e}")

if __name__ == "__main__":
    run_demo()
