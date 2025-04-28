WITH base AS (
    SELECT
        employer_name,
        workplace,
        employer_org_nr,
        street_address,
        postal_code,
        region,
        city,
        country,
        experience_required,
        requires_drivers_license,
        has_car
    FROM {{ ref('load_data_from_raw_to_staging') }} 
)

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
    country,
    experience_required,
    requires_drivers_license,
    has_car
FROM base