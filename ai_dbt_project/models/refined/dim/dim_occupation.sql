-- dim_occupation.sql
WITH base AS (
    SELECT DISTINCT
        occupation,
        occupation_group,
        occupation_field
    FROM {{ ref('stg_job_ads') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'occupation',
        'occupation_group',
        'occupation_field'
    ]) }} as occupation_id,

    {{ clean_and_coalesce('occupation') }} AS occupation,
    {{ clean_and_coalesce('occupation_group') }} AS occupation_group,
    {{ clean_and_coalesce('occupation_field') }} AS occupation_field

FROM base
