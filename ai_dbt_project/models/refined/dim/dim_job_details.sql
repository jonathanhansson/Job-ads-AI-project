WITH base AS (
  SELECT DISTINCT
    ad_id,
    headline,
    description_text,
    employment_type,
    duration,
    salary_description,
    salary_type,
  FROM {{ ref('load_data_from_raw_to_staging') }}
),
cleaned_data AS (
  SELECT
    TRIM(COALESCE(ad_id, 'ej angiven')) AS ad_id,
    TRIM(LOWER(COALESCE(headline, 'ej angiven'))) AS headline,
    TRIM(LOWER(COALESCE(description_text, 'ej angiven'))) AS description_text,
    TRIM(LOWER(COALESCE(employment_type, 'ej angiven'))) AS employment_type,
    TRIM(LOWER(COALESCE(duration, 'ej angiven'))) AS duration,
    TRIM(LOWER(COALESCE(salary_description, 'ej angiven'))) AS salary_description,
    TRIM(LOWER(COALESCE(salary_type, 'ej angiven'))) AS salary_type
  FROM base
)

SELECT
    {{dbt_utils.generate_surrogate_key ([
        'ad_id'       
    ])}} AS job_details_id,
    ad_id,
    headline,
    description_text,
    employment_type,
    duration,
    salary_description,
    salary_type
FROM cleaned_data




























