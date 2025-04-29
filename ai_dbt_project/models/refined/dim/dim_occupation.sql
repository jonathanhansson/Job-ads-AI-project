WITH base AS (
    SELECT DISTINCT
        occupation,
        occupation_group,
        occupation_field
    FROM {{ ref('load_data_from_raw_to_staging') }}
),

cleaned_data AS (
    SELECT
        TRIM(LOWER(COALESCE(occupation, 'ej angiven'))) AS occupation,
        TRIM(LOWER(COALESCE(occupation_group, 'ej angiven'))) AS occupation_group,
        TRIM(LOWER(COALESCE(occupation_field, 'ej angiven'))) AS occupation_field
    FROM base
)

SELECT
    {{ dbt_utils.generate_surrogate_key ([
        'occupation', 'occupation_group', 'occupation_field'
    ]) }} as occupation_id,
    occupation,
    occupation_group,
    occupation_field,
FROM cleaned_data