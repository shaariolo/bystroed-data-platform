{{
    config(
        materialized='table',
        tags=['core', 'facts', 'orders']
    )
}}

SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    o.quantity,
    o.order_date,
    DATE_TRUNC('month', o.order_date)::DATE AS order_month,
    p.price * o.quantity AS order_amount,
    o.ingested_at,
    o.dbt_updated_at
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_products') }} p
    ON o.product_id = p.product_id