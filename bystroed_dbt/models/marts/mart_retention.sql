{{
    config(
        materialized='table',
        tags=['marts', 'retention']
    )
}}

WITH customer_first_order AS (
    -- Определяем первый заказ каждого клиента
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        DATE_TRUNC('month', MIN(order_date))::DATE AS cohort_month
    FROM {{ ref('fct_orders') }}
    GROUP BY customer_id
),

customer_activity AS (
    -- Определяем, в какие месяцы клиент делал заказы
    SELECT DISTINCT
        o.customer_id,
        DATE_TRUNC('month', o.order_date)::DATE AS activity_month
    FROM {{ ref('fct_orders') }} o
),

cohort_data AS (
    -- Соединяем первый заказ с активностью
    SELECT
        cfo.cohort_month,
        ca.activity_month,
        cfo.customer_id
    FROM customer_first_order cfo
    JOIN customer_activity ca
        ON cfo.customer_id = ca.customer_id
    WHERE ca.activity_month >= cfo.cohort_month
),

cohort_size AS (
    -- Размер когорты (сколько клиентов в каждой когорте)
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_first_order
    GROUP BY cohort_month
),

cohort_retention AS (
    -- Считаем retention
    SELECT
        cd.cohort_month,
        cd.activity_month,
        COUNT(DISTINCT cd.customer_id) AS retained_customers,
        cs.cohort_size,
        ROUND(
            100.0 * COUNT(DISTINCT cd.customer_id) / cs.cohort_size,
            2
        ) AS retention_rate
    FROM cohort_data cd
    JOIN cohort_size cs
        ON cd.cohort_month = cs.cohort_month
    GROUP BY cd.cohort_month, cd.activity_month, cs.cohort_size
)

SELECT
    cohort_month,
    activity_month,
    EXTRACT(MONTH FROM AGE(activity_month, cohort_month)) AS month_number,
    retained_customers,
    cohort_size,
    retention_rate
FROM cohort_retention
ORDER BY cohort_month, activity_month