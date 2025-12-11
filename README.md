# Dockerized-Data-Pipeline-with-Airflow-DagsterObjective

## Objective
This project implements a Dockerized data pipeline that fetches stock market data from Yahoo Finance, processes it, and stores it in PostgreSQL. The pipeline is orchestrated using Airflow and is designed to run daily.

---

## Features
- **Data Fetching:** Retrieves historical stock data for specified tickers (\`AAPL\`, \`MSFT\`, \`GOOGL\`) using \`yfinance\`.
- **Database Update:** Stores stock data in PostgreSQL, creating the table if it doesn't exist. Handles duplicate entries gracefully.
- **Error Handling:** Comprehensive try-except logic to manage empty or missing data.
- **Dockerized:** Entire pipeline runs using Docker Compose for easy setup and deployment.
- **Airflow Orchestration:** DAG schedules daily data fetch and insert operations.

---

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Python only required if you want to run scripts outside Docker (otherwise all runs in containers).

---

## Setup Instructions

### 1. Clone the repository
\`\`\`bash
git clone <your-repo-url>
cd <your-project-directory>
\`\`\`

### 2. Build and start Docker containers
\`\`\`bash
docker-compose up --build
\`\`\`

This will start:
- PostgreSQL database (\`postgres\`)
- Airflow Webserver (\`http://localhost:8081\`)
- Airflow Scheduler

### 3. Initialize Airflow database (first run only)
Open a new terminal and run:
\`\`\`bash
docker-compose run airflow-webserver airflow db init
\`\`\`

### 4. Access Airflow UI
Visit: [http://localhost:8081](http://localhost:8081)  
- DAG name: \`stock_data_pipeline\`
- Trigger DAG manually for testing or let it run daily automatically.

### 5. Verify PostgreSQL data
Connect to Postgres to check inserted stock data:
\`\`\`bash
docker exec -it <postgres-container-id> psql -U airflow -d airflow
# Then in psql:
SELECT * FROM stock_data;

---

## File Structure
\`\`\`
.
├── dags/
│   └── stock_data_dag.py       # Airflow DAG
├── fetch_and_store.py           # Python script for fetching and storing stock data
├── docker-compose.yml           # Docker Compose file
├── requirements.txt             # Python dependencies
├── logs/                        # Airflow logs (auto-generated)
├── plugins/                     # Airflow plugins (if any)
└── README.md

\`\`\`

---

## Environment Variables
The pipeline uses the following environment variables for PostgreSQL credentials:
- \`POSTGRES_HOST\` (default: \`postgres\`)
- \`POSTGRES_PORT\` (default: \`5432\`)
- \`POSTGRES_DB\` (default: \`airflow\`)
- \`POSTGRES_USER\` (default: \`airflow\`)
- \`POSTGRES_PASSWORD\` (default: \`airflow\`)

These are already defined in \`docker-compose.yml\`.

---

## Notes
- The DAG fetches **1 year of daily stock data** on each run. You can adjust the period in \`stock_data_dag.py\`.
- For additional tickers, add them to the \`TICKERS\` list in the DAG.
- Logs for each DAG task can be viewed from Airflow UI or in the \`logs/\` directory.
- This setup is fully portable; relative paths are used for DAGs, logs, and plugins.
- If using Alpha Vantage instead of Yahoo Finance, make sure to store your API key in an environment variable and update the DAG/script accordingly.

---

## Troubleshooting
- If DAG does not show in the UI, ensure \`airflow db init\` has been run.
- If tasks fail to insert into Postgres, check the container logs for error details.
- Ensure Docker Compose version is 3.8+ for compatibility.

---

