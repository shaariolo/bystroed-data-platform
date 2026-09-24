from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import csv
import psycopg2
from psycopg2.extras import execute_values
import logging
import time

# Конфигурация
DB_CONFIG = {
    "host": "postgres",
    "port": "5432",
    "dbname": "bystroed_db",
    "user": "airflow",
    "password": "airflow",
}

DATA_DIR = "/opt/airflow/data"
BATCH_SIZE = 10_000

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

default_args = {
    "owner": "bystroed",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "start_date": datetime(2026, 9, 24),
}


# ---------- ОБЩАЯ ФУНКЦИЯ ЗАГРУЗКИ ----------
def load_csv_to_table(csv_path, table_name, columns, transform_func, expected_min_rows):
    """Универсальная функция загрузки CSV в таблицу."""
    start_time = time.time()
    conn = None
    cur = None

    try:
        logging.info(f"Начинаем загрузку {table_name}...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        logging.info(f"Очищаем {table_name}...")
        cur.execute(f"TRUNCATE TABLE {table_name};")

        logging.info(f"Читаем {csv_path}...")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)

            batch = []
            total = 0

            for row in reader:
                batch.append(transform_func(row))

                if len(batch) >= BATCH_SIZE:
                    execute_values(
                        cur,
                        f"INSERT INTO {table_name} ({columns}) VALUES %s",
                        batch,
                    )
                    total += len(batch)
                    logging.info(f"Вставлено {total} строк...")
                    batch = []

            if batch:
                execute_values(
                    cur,
                    f"INSERT INTO {table_name} ({columns}) VALUES %s",
                    batch,
                )
                total += len(batch)

        # Проверка качества: минимум строк
        if total < expected_min_rows:
            raise ValueError(
                f"Загружено {total} строк, ожидалось минимум {expected_min_rows}"
            )

        conn.commit()
        logging.info(f"Загрузка {table_name} завершена. Всего: {total} строк.")

    except Exception as e:
        logging.error(f"Ошибка при загрузке {table_name}: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        duration = time.time() - start_time
        logging.info(f"Время загрузки {table_name}: {duration:.2f} сек.")
        if cur:
            cur.close()
        if conn:
            conn.close()


# ---------- ФУНКЦИИ ЗАГРУЗКИ ----------
def load_products():
    load_csv_to_table(
        csv_path=f"{DATA_DIR}/products.csv",
        table_name="raw.products",
        columns="product_id, name, category, price, quantity, is_active",
        transform_func=lambda row: (
            int(row[0]),
            row[1],
            row[2],
            float(row[3]),
            int(row[4]),
            row[5].lower() == "true",
        ),
        expected_min_rows=100_000,
    )


def load_customers():
    load_csv_to_table(
        csv_path=f"{DATA_DIR}/customers.csv",
        table_name="raw.customers",
        columns="customer_id, name, city, signup_date",
        transform_func=lambda row: (
            int(row[0]),
            row[1],
            row[2],
            row[3],
        ),
        expected_min_rows=1_000,
    )


def load_orders():
    load_csv_to_table(
        csv_path=f"{DATA_DIR}/orders.csv",
        table_name="raw.orders",
        columns="order_id, customer_id, product_id, quantity, order_date",
        transform_func=lambda row: (
            int(row[0]),
            int(row[1]),
            int(row[2]),
            int(row[3]),
            row[4],
        ),
        expected_min_rows=10_000,
    )


# ---------- DAG ----------
with DAG(
    "load_raw_data",
    default_args=default_args,
    description="Загрузка всех сырых данных в PostgreSQL (products, customers, orders)",
    schedule_interval="0 3 * * *",  # Каждый день в 3:00
    catchup=False,
    tags=["bystroed", "raw", "loading"],
) as dag:

    load_products_task = PythonOperator(
        task_id="load_products",
        python_callable=load_products,
    )

    load_customers_task = PythonOperator(
        task_id="load_customers",
        python_callable=load_customers,
    )

    load_orders_task = PythonOperator(
        task_id="load_orders",
        python_callable=load_orders,
    )

    trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt_transform",
        trigger_dag_id="dbt_transform",
        wait_for_completion=True,
        poke_interval=30,
    )

    [load_products_task, load_customers_task, load_orders_task] >> trigger_dbt