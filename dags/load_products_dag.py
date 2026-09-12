from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time
import csv
import psycopg2
from psycopg2.extras import execute_values
import logging

CSV_PATH = "/opt/airflow/data/products.csv"
BATCH_SIZE = 10_000

DB_CONFIG = {
    "host": "postgres",
    "port": "5432",
    "dbname": "bystroed_db",
    "user": "airflow",
    "password": "airflow"
}

default_args = {
    "owner": "bystroed",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "start_date": datetime(2026, 9, 12)
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_products():
    start_time = time.time()
    conn = None
    cur = None
    try:
        logging.info("Начинаем загрузку данных...")

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Очищаем таблицу
        logging.info("Очищаем таблицу raw.products...")
        cur.execute('TRUNCATE TABLE raw.products;')

        # Читаем CSV - файл
        logging.info(f"Читаем файл {CSV_PATH}...")
        with open(CSV_PATH, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            batch = []
            total_rows = 0

            for row in reader:
                # Преобразуем типы
                product_id = int(row[0])
                name = row[1]
                category = row[2]
                price = float(row[3])
                quantity = int(row[4])
                is_active = True if row[5].lower() == "true" else False

                # Вставляем в пачку
                batch.append((product_id, name, category, price, quantity, is_active))

                # Если пачка наполнилась - вставляем пачку в БД
                if len(batch) >= BATCH_SIZE:
                    execute_values(
                        cur, 
                        "INSERT INTO raw.products(product_id, name, category, price, quantity, is_active) VALUES %s",
                        batch
                        )
                    total_rows += len(batch)
                    logging.info(f"Вставлено {total_rows} строк...")

                    batch = []

                # Если остались данные (неполная пачка)
            if batch:
                execute_values(
                    cur,
                    "INSERT INTO raw.products(product_id, name, category, price, quantity, is_active) VALUES %s",
                    batch
                )  
                total_rows += len(batch)  

        # Коммитим транзакцию
        conn.commit()
        logging.info(f"Загрузка завершена! Добавлено {total_rows} строк.")                

    except Exception as e:
        logging.error(f'Ошибка при загрузке: {e}.')
        if conn:
            conn.rollback()

    finally:
        duration_time = time.time() - start_time
        logging.info(f'Загрузка закончилась за: {duration_time:.2f} сек.')
        if cur:
            cur.close()
        if conn:    
            conn.close()

def check_products_count():
    EXPECTED_ROWS_COUNT = 10_000
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM raw.products;")
        count = cur.fetchone()[0]
        logging.info(f"Проверка: в таблице {count} строк.")

        if count < EXPECTED_ROWS_COUNT:
            raise ValueError(f"Ожидалось {EXPECTED_ROWS_COUNT} строк, а получено {count} строк.")
        else:
            logging.info("Проверка пройдена!")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()            

with DAG(
    "load_products",
    default_args=default_args,
    description="Загрузка товаров из CSV в PostgreSQL",
    schedule_interval="0 3 * * *",
    catchup=False,
    tags=["bystroed", "csv", "postgres"]
) as dag:
    
    load_products_task = PythonOperator(
        task_id="load_products",
        python_callable=load_products
    )

    check_count_task = PythonOperator(
        task_id="check_products_count",
        python_callable=check_products_count
    )
    
    load_products_task >> check_count_task          