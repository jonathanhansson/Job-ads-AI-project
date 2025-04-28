WITH base AS (
  SELECT
    ad_id,
    headline,
    description_text,
    employment_type,
    duration,
    salary_description,
    salary_type,
    --scope_of_work__min,
    --scope_of_work__max,
  FROM {{ ref('load_data_from_raw_to_staging') }}
)

SELECT
    {{dbt_utils.generate_surrogate_key ([
        'ad_id'       
    ])}} AS job_details_id,
    headline,
    description_text,
    employment_type,
    duration,
    salary_description,
    salary_type,
    --scope_of_work__min,
    --scope_of_work__max,
FROM base




























