{{
    config(
        materialized='table',
        tags=['marts', 'gmv']
    )
}}

SELECT
    category_name,
    COUNT(DISTINCT product_id) AS products_count,
    SUM(price * quantity) AS total_gmv,
    AVG(price) AS avg_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM {{ ref('dim_products') }}
WHERE status = 'active'
GROUP BY category_name
ORDER BY total_gmv DESC