from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Путь к dbt-проекту внутри контейнера
DBT_PROJECT_DIR = "/opt/airflow/bystroed_dbt"

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

    dbt_run >> dbt_test