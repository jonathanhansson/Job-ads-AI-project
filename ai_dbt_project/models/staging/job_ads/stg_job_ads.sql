-- stg_job_ads.sql
SELECT
  _dlt_id AS ad_id,
  -- Job details
  number_of_vacancies AS number_vacancies,
  application_deadline,
  publication_date,
  headline,
  description__text AS description_text,
  duration__label AS duration,

  -- Ocupation details
  occupation__label AS occupation,
  occupation_group__label AS occupation_group,
  occupation_field__label AS occupation_field,

  -- Employment details
  employer__name AS employer_name,
  employer__workplace AS workplace,
  employer__organization_number AS employer_org_nr,
  workplace_address__region AS region,
  workplace_address__country AS country,
  workplace_address__municipality AS municipality,

  -- Auxiliary details
  experience_required,
  driving_license_required AS requires_drivers_license,
  access_to_own_car AS has_car 
FROM {{ source('job_ads_source', 'raw_job_ads') }}