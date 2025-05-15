-- dim_job_details.sql
WITH base AS (
  SELECT DISTINCT
    ad_id,
    headline,
    description_text
  FROM {{ ref('stg_job_ads') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['ad_id']) }} AS job_details_id,

    {{ clean_and_coalesce('ad_id') }} AS ad_id,
    {{ clean_and_coalesce('headline') }} AS headline,
    {{ clean_and_coalesce('description_text') }} AS description_text

FROM base





























