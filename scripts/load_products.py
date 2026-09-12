import csv
import psycopg2
from psycopg2.extras import execute_values
import logging
import time

# 1.Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 2. Настройка подключения к БД
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "bystroed_db",
    "user": "airflow",
    "password": "airflow"
}

# 3. Путь к CSV-файлу и размер пачки
CSV_PATH = "data/products.csv"
BATCH_SIZE = 10000

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

if __name__ == '__main__':
    load_products()
