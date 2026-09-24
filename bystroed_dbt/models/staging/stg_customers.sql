{{
    config(
        materialized='view',
        tags=['staging', 'customers']
    )
}}

SELECT
    customer_id,
    name AS customer_name,
    city,
    signup_date,
    ingested_at,
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM {{ source('raw', 'customers') }}
WHERE customer_id IS NOT NULL