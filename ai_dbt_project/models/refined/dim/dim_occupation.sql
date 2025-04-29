WITH base AS (
    SELECT DISTINCT
        occupation,
        occupation_group,
        occupation_field
    FROM {{ ref('load_data_from_raw_to_staging') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key ([
        'occupation', 'occupation_group', 'occupation_field'
    ]) }} as occupation_id,
    occupation,
    occupation_group,
    occupation_field,
FROM base