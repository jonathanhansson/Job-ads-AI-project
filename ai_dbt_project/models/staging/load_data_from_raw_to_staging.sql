SELECT
  _dlt_id AS ad_id,
  number_of_vacancies AS number_vacancies,
  -- relevance, -- INT , Only nr 1 - Why is this relevant?
  application_deadline,
  publication_date,
  headline,
  description__text AS description_text,
  -- description__text_formatted, - Why is this relevant?
  employment_type__label AS employment_type,
  duration__label AS duration,
  salary_description,
  salary_type__label AS salary_type,
  -- scope_of_work__min, - Why is this relevant?
  -- scope_of_work__max, - Why is this relevant?

  TRIM(LOWER(COALESCE(occupation__label, 'ej angiven'))) AS occupation,
  TRIM(LOWER(COALESCE(occupation_group__label, 'ej angiven'))) AS occupation_group,
  TRIM(LOWER(COALESCE(occupation_field__label, 'ej angiven'))) AS occupation_field,
  
  TRIM(LOWER(COALESCE(employer__name, 'ej angiven'))) AS employer_name,
  TRIM(LOWER(COALESCE(employer__workplace, 'ej angiven'))) AS workplace,
  TRIM(COALESCE(employer__organization_number, 'ej angiven')) AS employer_org_nr,
  TRIM(LOWER(COALESCE(workplace_address__street_address, 'ej angiven'))) AS street_address,
  TRIM(LOWER(COALESCE(workplace_address__postcode, 'ej angiven'))) AS postal_code,     
  TRIM(LOWER(COALESCE(workplace_address__region, 'ej angiven'))) AS region,
  TRIM(LOWER(COALESCE(workplace_address__city, 'ej angiven'))) AS city,
  TRIM(LOWER(COALESCE(workplace_address__country, 'ej angiven'))) AS country,

  experience_required,
  driving_license_required AS requires_drivers_license,
  access_to_own_car AS has_car 
FROM {{ source('job_ads_source', 'raw_job_ads') }}