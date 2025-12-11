# /opt/airflow/dags/stock_data_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import yfinance as yf
import psycopg2
import os

# Read DB credentials from environment variables
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "airflow")
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")

# List of tickers
TICKERS = ["AAPL", "MSFT", "GOOGL"]

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

def fetch_and_store(ticker):
    """
    Fetch daily stock data for a ticker and insert into PostgreSQL.
    Handles empty/missing data gracefully.
    """
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        if df.empty:
            print(f"⚠️ No data fetched for {ticker}")
            return

        df.reset_index(inplace=True)
        df.drop_duplicates(subset=["Date"], inplace=True)

        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                # Create table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        date DATE,
                        ticker TEXT,
                        open FLOAT,
                        high FLOAT,
                        low FLOAT,
                        close FLOAT,
                        adj_close FLOAT,
                        volume BIGINT,
                        PRIMARY KEY (date, ticker)
                    )
                """)

                # Insert data, skip duplicates
                insert_query = """
                    INSERT INTO stock_data (date, ticker, open, high, low, close, adj_close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date, ticker) DO NOTHING
                """
                cur.executemany(insert_query, [
                    (row['Date'], ticker, row['Open'], row['High'], row['Low'],
                     row['Close'], row['Adj Close'], row['Volume'])
                    for _, row in df.iterrows()
                ])
        print(f"✅ Inserted {len(df)} rows for {ticker}")

    except Exception as e:
        raise RuntimeError(f"❌ Failed for {ticker}: {e}")

# Define DAG
with DAG(
    dag_id="stock_data_pipeline",
    default_args=default_args,
    description="Fetch daily stock data from Yahoo Finance and store in PostgreSQL",
    schedule_interval="@daily",
    start_date=datetime(2025, 8, 28),
    catchup=False,
    tags=["stocks", "yfinance", "postgres"]
) as dag:

    # Create one task per ticker
    for ticker in TICKERS:
        PythonOperator(
            task_id=f"fetch_and_store_{ticker.lower()}",
            python_callable=fetch_and_store,
            op_args=[ticker]
        )
