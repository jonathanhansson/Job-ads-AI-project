WITH base AS (
    SELECT
        MIN(employer_name) AS employer_name,
        MIN(workplace) AS workplace,
        employer_org_nr,
        street_address,
        MIN(postal_code) AS postal_code,
        MIN(region) AS region,
        MIN(city) AS city,
        MIN(country) AS country
    FROM {{ ref('load_data_from_raw_to_staging') }} 
    GROUP BY employer_org_nr, street_address
),
cleaned_data AS (
    SELECT
        TRIM(LOWER(COALESCE(employer_name, 'ej angiven'))) AS employer_name,
        TRIM(LOWER(COALESCE(workplace, 'ej angiven'))) AS workplace,
        TRIM(COALESCE(employer_org_nr, 'ej angiven')) AS employer_org_nr,
        TRIM(LOWER(COALESCE(street_address, 'ej angiven'))) AS street_address,
        TRIM(LOWER(COALESCE(postal_code, 'ej angiven'))) AS postal_code,     
        TRIM(LOWER(COALESCE(region, 'ej angiven'))) AS region,
        TRIM(LOWER(COALESCE(city, 'ej angiven'))) AS city,
        TRIM(LOWER(COALESCE(country, 'ej angiven'))) AS country
    FROM base
)

-- Transformed each column to ensure data quality. Lower - only in lower case. Coalesce - replacing NULL-values with "ej angiven"
SELECT
    {{dbt_utils.generate_surrogate_key([
        'employer_org_nr', 
        'street_address'
    ])}} AS employer_id,
    employer_name,
    workplace,
    employer_org_nr,
    street_address,
    postal_code,     
    region,
    city,
    country
FROM cleaned_data