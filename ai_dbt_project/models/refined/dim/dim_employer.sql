--dim_employer.sql
WITH base AS (
    SELECT
        MIN(employer_name) AS employer_name,
        MIN(workplace) AS workplace,
        employer_org_nr,
        municipality,
        MIN(region) AS region,
        MIN(country) AS country
    FROM {{ ref('stg_job_ads') }}
    WHERE employer_org_nr IS NOT NULL AND municipality IS NOT NULL 
    GROUP BY employer_org_nr, municipality
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['employer_org_nr', 'municipality']) }} AS employer_id,

    {{ clean_and_coalesce('employer_name') }} AS employer_name,
    {{ clean_and_coalesce('workplace') }} AS workplace,
    {{ clean_and_coalesce('employer_org_nr') }} AS employer_org_nr,
    {{ clean_and_coalesce('municipality') }} AS municipality,
    {{ clean_and_coalesce('region') }} AS region,
    {{ clean_and_coalesce('country') }} AS country

FROM base

