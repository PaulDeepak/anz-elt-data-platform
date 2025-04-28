import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_data():
    """
    Generates synthetic transaction and macroeconomic data, mimicking the bank's requirements.
    """
    # 1. Transaction Data (Daily - mimicking on-premise source)
    num_transactions_per_day = 1000  # Reduced for demonstration
    num_days = 21
    num_terminals = 500
    num_customers = 1000

    end_date = datetime.today()
    dates = pd.date_range(end=end_date, periods=num_days).date
    terminals = [f"TERM_{i:05d}" for i in range(1, num_terminals + 1)]
    customers = [f"CUST_{i:08d}" for i in range(1, num_customers + 1)]

    # Create a list to hold daily DataFrames
    daily_dataframes = []

    for i, transaction_date in enumerate(dates):
        transactions_data = {
            "transaction_id": [f"TXN_{i * num_transactions_per_day + j:010d}" for j in range(1, num_transactions_per_day + 1)],
            "terminal_id": np.random.choice(terminals, num_transactions_per_day),
            "customer_id": np.random.choice(customers, num_transactions_per_day),
            "amount": np.round(np.random.lognormal(mean=3, sigma=0.5, size=num_transactions_per_day), 2),
            "currency": "AUD",
            "status": np.random.choice(["SUCCESS", "FAILED"], num_transactions_per_day, p=[0.98, 0.02]),
            "transaction_date": transaction_date,
        }
        daily_df = pd.DataFrame(transactions_data)
        daily_dataframes.append(daily_df)

    transactions_df = pd.concat(daily_dataframes, ignore_index=True)

    # 2. Macroeconomics Data (Monthly - mimicking external vendor)
    start_date = "2020-01-01"
    months = pd.date_range(start=start_date, end=end_date, freq="MS")
    num_months = len(months)

    economics_data = {
        "month": months,
        "cash_rate": np.random.uniform(0.1, 4.5, num_months),
        "unemployment_rate": np.random.uniform(3.5, 6.5, num_months),
        "cpi": np.round(np.random.uniform(1.5, 7.5, num_months), 1),
    }
    economics = pd.DataFrame(economics_data)

    # 3. Save the data
    os.makedirs("data", exist_ok=True)
    transactions_df.to_parquet("data/transactions.parquet", partition_cols=["transaction_date"])
    economics.to_csv("data/economics.csv", index=False)

    print("Data files (transactions.parquet, economics.csv) have been generated in the data/ directory.")

if __name__ == "__main__":
    generate_data()
