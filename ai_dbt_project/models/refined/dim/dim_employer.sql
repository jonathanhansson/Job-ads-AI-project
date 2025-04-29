WITH base AS (
    SELECT DISTINCT
        employer_name,
        workplace,
        employer_org_nr,
        street_address,
        postal_code,
        region,
        city,
        country
    FROM {{ ref('load_data_from_raw_to_staging') }} 
)

SELECT
    {{dbt_utils.generate_surrogate_key([
        'employer_org_nr', 
        'street_address'
    ])}} AS employer_id,
    LOWER(COALESCE(employer_name, 'ej angiven')) as employer_name,
    LOWER(COALESCE(workplace, 'ej angiven')) as workplace,
    LOWER(COALESCE(employer_org_nr, 'ej angiven')) as employer_org_nr,
    LOWER(COALESCE(street_address, 'ej angiven')) as street_address,
    LOWER(COALESCE(postal_code, 'ej angiven')) as postal_code,     
    LOWER(COALESCE(region, 'ej angiven')) as region,
    LOWER(COALESCE(city, 'ej angiven')) as city,
    country
FROM base