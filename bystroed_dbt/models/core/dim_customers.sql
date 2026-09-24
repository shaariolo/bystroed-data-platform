{{
    config(
        materialized='table',
        tags=['core', 'dimensions', 'customers']
    )
}}

SELECT
    customer_id,
    customer_name,
    city,
    signup_date,
    DATE_TRUNC('month', signup_date)::DATE AS signup_month,
    ingested_at,
    dbt_updated_at
FROM {{ ref('stg_customers') }}