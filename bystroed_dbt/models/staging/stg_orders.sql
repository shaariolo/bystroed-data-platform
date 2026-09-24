{{
    config(
        materialized='view',
        tags=['staging', 'orders']
    )
}}

SELECT
    order_id,
    customer_id,
    product_id,
    quantity,
    order_date,
    ingested_at,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM {{ source('raw', 'orders') }}
WHERE order_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND quantity > 0