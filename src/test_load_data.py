import pandas as pd

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data from {file_path}")
        print(f"Shape of data: {df.shape}")
        print("Sample data:")
        print(df.head())
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")

# Replace 'customer_risk_markers' with a file in your data folder to test
load_data("data/customer_risk_markers.csv")