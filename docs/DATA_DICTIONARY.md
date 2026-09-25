# Data Dictionary

## Схема raw

### raw.products
| Колонка | Тип | Описание |
|---------|-----|----------|
| product_id | INTEGER | ID товара (PK) |
| name | TEXT | Название |
| category | TEXT | Категория |
| price | DECIMAL(10,2) | Цена |
| quantity | INTEGER | Количество |
| is_active | BOOLEAN | Активен |
| ingested_at | TIMESTAMP | Когда загружено |

### raw.customers
| Колонка | Тип | Описание |
|---------|-----|----------|
| customer_id | INTEGER | ID клиента (PK) |
| name | TEXT | Имя |
| city | TEXT | Город |
| signup_date | DATE | Дата регистрации |
| ingested_at | TIMESTAMP | Когда загружено |

### raw.orders
| Колонка | Тип | Описание |
|---------|-----|----------|
| order_id | INTEGER | ID заказа (PK) |
| customer_id | INTEGER | ID клиента (FK) |
| product_id | INTEGER | ID товара (FK) |
| quantity | INTEGER | Количество |
| order_date | DATE | Дата заказа |
| ingested_at | TIMESTAMP | Когда загружено |

## Схема stg

- `stg.stg_products` — очищенные товары (view)
- `stg.stg_customers` — очищенные клиенты (view)
- `stg.stg_orders` — очищенные заказы (view)

## Схема core

### core.dim_products
| Колонка | Описание |
|---------|----------|
| product_id | ID товара |
| product_name | Название |
| category_name | Категория |
| price | Цена |
| price_tier | high/medium/low |
| status | active/inactive |

### core.dim_customers
| Колонка | Описание |
|---------|----------|
| customer_id | ID клиента |
| customer_name | Имя |
| city | Город |
| signup_date | Дата регистрации |
| signup_month | Месяц регистрации |

### core.fct_orders
| Колонка | Описание |
|---------|----------|
| order_id | ID заказа |
| customer_id | ID клиента |
| product_id | ID товара |
| quantity | Количество |
| order_date | Дата заказа |
| order_amount | Сумма (price * quantity) |

## Схема marts

### marts.mart_gmv_by_category
| Колонка | Описание |
|---------|----------|
| category_name | Категория |
| products_count | Кол-во товаров |
| total_gmv | Выручка |
| avg_price | Средняя цена |

### marts.mart_retention
| Колонка | Описание |
|---------|----------|
| cohort_month | Месяц первого заказа |
| activity_month | Месяц активности |
| month_number | Номер месяца |
| retained_customers | Вернулось клиентов |
| cohort_size | Размер когорты |
| retention_rate | % удержания |

## Метрики

### GMV
**Формула:** `SUM(price * quantity)`
**Где:** `marts.mart_gmv_by_category`

### Retention Rate
**Формула:** `retained_customers / cohort_size * 100`
**Где:** `marts.mart_retention`