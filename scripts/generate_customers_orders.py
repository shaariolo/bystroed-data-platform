import csv
import random
from datetime import datetime, timedelta

CUSTOMERS_COUNT = 1000
ORDERS_COUNT = 10000

# Генерируем клиентов
cities = ["Москва", "Санкт-Петербург", "Казань", "Новосибирск", "Екатеринбург"]

with open('data/customers.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['customer_id', 'name', 'city', 'signup_date'])

    base_date = datetime(2026, 1, 1)
    for i in range(1, CUSTOMERS_COUNT + 1):
        signup_date = base_date + timedelta(days=random.randint(0, 180))
        writer.writerow([
            i,
            f"Клиент {i}",
            random.choice(cities),
            signup_date.strftime("%Y-%m-%d"),
        ])

print(f"Сгенерировано {CUSTOMERS_COUNT} клиентов в data/customers.csv")

# Генерируем заказы
with open('data/orders.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'customer_id', 'product_id', 'quantity', 'order_date'])

    base_date = datetime(2026, 1, 1)
    for i in range(1, ORDERS_COUNT + 1):
        order_date = base_date + timedelta(days=random.randint(0, 270))
        writer.writerow([
            i,
            random.randint(1, CUSTOMERS_COUNT),
            random.randint(1, 100000),
            random.randint(1, 5),
            order_date.strftime("%Y-%m-%d"),
        ])

print(f"Сгенерировано {ORDERS_COUNT} заказов в data/orders.csv")