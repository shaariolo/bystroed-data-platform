{{
    config(
        materialized='table',
        tags=['core', 'dimensions', 'products']
    )
}}

SELECT
    product_id,
    name AS product_name,
    category AS category_name,
    price,
    quantity,
    CASE
        WHEN price >= 1000 THEN 'high'
        WHEN price >= 500 THEN 'medium'
        ELSE 'low'
    END AS price_tier,
    CASE
        WHEN is_active = TRUE THEN 'active'
        ELSE 'inactive'
    END AS status,
    ingested_at,
    dbt_updated_at
FROM {{ ref('stg_products') }}