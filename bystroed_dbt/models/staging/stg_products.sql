{{
    config(
        materialized='view',
        tags=['staging', 'products']
    )
}}

SELECT
    product_id,
    name,
    category,
    price,
    quantity,
    is_active,
    ingested_at,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM {{ source('raw', 'products') }}
WHERE price > 0
    AND product_id IS NOT NULL