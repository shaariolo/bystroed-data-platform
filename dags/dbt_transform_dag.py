from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

DBT_PROJECT_DIR = "/opt/airflow/bystroed_dbt"
SODA_DIR = "/opt/airflow/bystroed_dbt/soda"

default_args = {
    "owner": "bystroed",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "start_date": datetime(2026, 9, 24),
}

with DAG(
    "dbt_transform",
    default_args=default_args,
    description="Трансформации данных через dbt (staging → core → marts)",
    schedule_interval=None,
    catchup=False,
    tags=["bystroed", "dbt", "transform"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    soda_marts_check = BashOperator(
        task_id="soda_marts_check",
        bash_command=f"cd {SODA_DIR} && soda scan -d bystroed_db -c configuration.yml checks/marts_retention.yml",
    )

    dbt_run >> dbt_test >> soda_marts_check