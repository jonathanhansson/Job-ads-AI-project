WITH base AS (
  SELECT
    experience_required,
    requires_drivers_license,
    has_car
  FROM {{ ref('load_data_from_raw_to_staging') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key([
      'experience_required',
      'requires_drivers_license',
      'has_car'
    ]) }} as auxilliary_id,       -- er surrogate PK
  experience_required,
  requires_drivers_license,
  has_car
FROM base
