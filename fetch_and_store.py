import yfinance as yf
import psycopg2

def fetch_stock_data(ticker="AAPL"):
    """
    Fetch historical stock data from Yahoo Finance.
    Returns a DataFrame with columns: Date, Open, High, Low, Close, Adj Close, Volume
    """
    df = yf.download(ticker, period="1y", interval="1d")
    df.reset_index(inplace=True)
    return df


def update_postgres(df, ticker="AAPL"):
    """
    Insert stock data into Postgres database.
    """
    conn = psycopg2.connect(
        host="postgres",   # service name from docker-compose.yml
        port=5432,
        database="airflow",  # matches POSTGRES_DB
        user="airflow",      # matches POSTGRES_USER
        password="airflow"   # matches POSTGRES_PASSWORD
    )
    cur = conn.cursor()

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

    # Insert rows, skip duplicates
    insert_query = """
        INSERT INTO stock_data (date, ticker, open, high, low, close, adj_close, volume)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (date, ticker) DO NOTHING
    """

    cur.executemany(insert_query, [
        (row["Date"], ticker, row["Open"], row["High"], row["Low"],
         row["Close"], row["Adj Close"], row["Volume"])
        for _, row in df.iterrows()
    ])

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inserted {len(df)} rows for {ticker} into Postgres")
