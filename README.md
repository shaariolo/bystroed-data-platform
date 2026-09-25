# BystroED Data Platform

Платформа данных для сервиса доставки еды «БыстроЕд»: от загрузки сырых данных до аналитических витрин.

## Что это

Проект демонстрирует **полный цикл работы Data Engineer**:
- Загрузка данных из CSV в PostgreSQL
- Оркестрация пайплайнов через Airflow
- Трансформации через dbt (staging → core → marts)
- Проверки качества данных через Soda Core
- Построение витрин для бизнеса (GMV, Retention)

## Архитектура

```text
[CSV files] → [Airflow] → [PostgreSQL raw]
                              ↓
                          [Soda: raw DQ]
                              ↓
                          [dbt: staging]
                              ↓
                          [dbt: core]
                              ↓
                          [dbt: marts]
                              ↓
                          [Soda: marts DQ]
```

## Технологический стек

| Слой | Технологии |
|------|------------|
| Оркестрация | Apache Airflow 2.9.1 |
| Хранилище | PostgreSQL 13 |
| Трансформации | dbt-core 1.7.0 |
| Data Quality | dbt tests (23), Soda Core 3.3.5 (20 checks) |
| Контейнеризация | Docker, Docker Compose |

## Быстрый старт

```bash
git clone git@github.com:shaariolo/bystroed-data-platform.git
cd bystroed-data-platform
cp dbt_profiles/profiles.example.yml dbt_profiles/profiles.yml
docker compose up -d
```

Airflow UI: http://localhost:8080 (логин: admin, пароль: admin)

## Витрины

| Витрина | Описание |
|---------|----------|
| marts.mart_gmv_by_category | Выручка по категориям |
| marts.mart_retention | Когортный анализ удержания |

## Документация

ARCHITECTURE.md — архитектура
DATA_DICTIONARY.md — описание таблиц


