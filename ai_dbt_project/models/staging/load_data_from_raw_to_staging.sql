SELECT
  _dlt_id AS ad_id,
  number_of_vacancies AS number_vacancies,
  -- relevance, -- INT , Only nr 1 - Why is this relevant?
  application_deadline,
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
  employer__name AS employer_name,
  employer__workplace AS workplace,
  employer__organization_number AS employer_org_nr,
  workplace_address__street_address AS street_address,
  workplace_address__postcode AS postal_code,
  workplace_address__region AS region,
  workplace_address__city AS city,
  workplace_address__country AS country,
  experience_required,
  driving_license_required AS requires_drivers_license,
  access_to_own_car AS has_car 
FROM raw.raw_job_ads