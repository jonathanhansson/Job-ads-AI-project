--dim_auxilliary_attributes.sql
WITH base AS (
  SELECT DISTINCT
    experience_required,
    requires_drivers_license,
    has_car
  FROM {{ ref('stg_job_ads') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key([
      'experience_required',
      'requires_drivers_license',
      'has_car'
  ]) }} as auxilliary_id,

  experience_required,
  requires_drivers_license,
  has_car

FROM base
