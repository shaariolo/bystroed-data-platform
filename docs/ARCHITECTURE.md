# Архитектура BystroED Data Platform

## 🎯 Общая схема

```text
[CSV] → [Airflow] → [raw] → [Soda DQ] → [dbt: stg] → [dbt: core] → [dbt: marts] → [Soda DQ] → [BI]
```

## Слои данных

**RAW (сырые данные)**

Схема: raw
Материализация: table
Загрузка: Airflow
Идемпотентность: TRUNCATE + INSERT
Таблицы: raw.products, raw.customers, raw.orders

**STAGING (очистка)**

Схема: stg
Материализация: view
Инструмент: dbt
Модели: stg_products, stg_customers, stg_orders

**CORE (измерения и факты)**

Схема: core
Материализация: table
Инструмент: dbt
Модели: dim_products, dim_customers, fct_orders

**MARTS (витрины)**

Схема: marts
Материализация: table
Инструмент: dbt
Модели: mart_gmv_by_category, mart_retention

## Идемпотентность

| Слой | Как обеспечивается |
|------|--------------------|
| raw | TRUNCATE + INSERT |
| stg | CREATE OR REPLACE VIEW |
| core | CREATE TABLE AS (atomic swap) |
| marts | CREATE TABLE AS (atomic swap) |