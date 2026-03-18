import pandas as pd
import sqlite3
import os

def process_brokerage_csv(csv_filepath, db_filepath="portfolio.db"):
    """Reads a brokerage CSV, cleans it, and inserts it into the database."""
    
    if not os.path.exists(csv_filepath):
        print(f"Error: Could not find the file {csv_filepath}")
        return
        
    try:
        # 1. Read the CSV file into a pandas DataFrame
        print(f"Reading data from {csv_filepath}...")
        df = pd.read_csv(csv_filepath)
        
        # 2. Clean the Data
        # Ensure column names exactly match our database schema
        df.columns = df.columns.str.lower().str.strip()
        
        # Remove any commas from numbers (e.g., "1,000.50" -> 1000.50)
        for col in ['quantity', 'price', 'fees']:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '', regex=False).astype(float)
        
        # Standardize the 'type' column to strict lowercase
        df['type'] = df['type'].str.lower().str.strip()
        
        # Standardize tickers and append '.CM' for Yahoo Finance compatibility later
        df['ticker'] = df['ticker'].str.upper().str.strip()
        df['ticker'] = df['ticker'].apply(lambda x: f"{x}.CM" if not str(x).endswith('.CM') else x)

        # 3. Connect to the database and insert
        print("Connecting to database...")
        conn = sqlite3.connect(db_filepath)
        
        # Select only the columns that exist in our 'transactions' table
        columns_to_insert = ['date', 'ticker', 'type', 'quantity', 'price', 'fees']
        
        # Insert the data. 'if_exists='append'' adds it to our existing table
        df[columns_to_insert].to_sql('transactions', conn, if_exists='append', index=False)
        
        print(f"Success! {len(df)} trades have been inserted into the 'transactions' table.")
        
        conn.close()
        
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == '__main__':
    # Run the function using our dummy file
    process_brokerage_csv('dummy_trades.csv')