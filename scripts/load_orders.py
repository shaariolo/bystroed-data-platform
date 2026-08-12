import csv
import json
import logging
import os
from datetime import datetime

# 1. Настраиваем логирование
# В проде print() использовать запрещено. Только logging.
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=f'{log_dir}/python_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_orders(input_csv, output_json):
    clean_orders = []
    bad_rows_count = 0
    
    logging.info(f"Starting ingestion from {input_csv}")
    
    # 2. Открываем файл
    try:
        with open(input_csv, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # 3. Итерируемся по строкам
            for row_num, row in enumerate(reader, start=2): # start=2, т.к. 1 - это заголовки
                try:
                    # Проверяем, что все нужные поля на месте
                    if not all(k in row and row[k] for k in ['order_id', 'customer_id', 'amount']):
                        raise ValueError("Missing required fields")
                    
                    # Пытаемся преобразовать amount в float
                    amount = float(row['amount'])
                    
                    # Если всё ок - добавляем в список чистых данных
                    clean_orders.append({
                        "order_id": int(row['order_id']),
                        "customer_id": int(row['customer_id']),
                        "amount": amount,
                        "status": row['status'],
                        "processed_at": datetime.now().isoformat()
                    })
                    
                except (ValueError, TypeError) as e:
                    # 4. Ловим ошибку конкретной строки и логируем её
                    bad_rows_count += 1
                    logging.warning(f"Bad data at row {row_num}: {row}. Error: {e}")
                    
    except FileNotFoundError:
        logging.error(f"File {input_csv} not found!")
        return

    # 5. Сохраняем чистые данные в JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(clean_orders, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Ingestion finished. Clean rows: {len(clean_orders)}, Bad rows: {bad_rows_count}")
    print(f"Done. Check {output_json} and logs/python_app.log")

if __name__ == "__main__":
    process_orders('data/orders_1c.csv', 'data/orders_clean.json')

    