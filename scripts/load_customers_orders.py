import csv
import psycopg2
from psycopg2.extras import execute_values
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "bystroed_db",
    "user": "airflow",
    "password": "airflow",
}

BATCH_SIZE = 1000

def load_csv_to_table(csv_path, table_name, columns, transform_func):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
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
                    batch = []

            if batch:
                execute_values(
                    cur,
                    f"INSERT INTO {table_name} ({columns}) VALUES %s",
                    batch,
                )
                total += len(batch)

        conn.commit()
        logging.info(f"Загружено {total} строк в {table_name}")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def load_all():
    start = time.time()

    # Клиенты
    load_csv_to_table(
        'data/customers.csv',
        'raw.customers',
        'customer_id, name, city, signup_date',
        lambda row: (int(row[0]), row[1], row[2], row[3]),
    )

    # Заказы
    load_csv_to_table(
        'data/orders.csv',
        'raw.orders',
        'order_id, customer_id, product_id, quantity, order_date',
        lambda row: (int(row[0]), int(row[1]), int(row[2]), int(row[3]), row[4]),
    )

    logging.info(f"Общее время: {time.time() - start:.2f} сек.")


if __name__ == '__main__':
    load_all()