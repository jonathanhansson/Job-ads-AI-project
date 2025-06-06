--fct_jobs.sql
WITH stg AS (
    SELECT * FROM {{ ref('stg_job_ads') }}
)

SELECT 
    occ.occupation_id,      
    jd.job_details_id,
    emp.employer_id,       
    aux.auxilliary_id,      
    stg.number_vacancies,
    stg.publication_date,
    stg.application_deadline
FROM stg

LEFT JOIN {{ ref('dim_occupation') }} AS occ
  ON stg.occupation = occ.occupation
 AND stg.occupation_group = occ.occupation_group
 AND stg.occupation_field = occ.occupation_field


LEFT JOIN {{ ref('dim_job_details') }} AS jd
  ON stg.ad_id = jd.ad_id

LEFT JOIN {{ ref('dim_employer') }} AS emp
  ON stg.employer_org_nr = emp.employer_org_nr -- Matchar nyckel 1
 AND stg.municipality = emp.municipality -- Matchar nyckel 2

LEFT JOIN {{ ref('dim_auxilliary_attributes') }} AS aux
  ON stg.experience_required = aux.experience_required
 AND stg.requires_drivers_license = aux.requires_drivers_license
 AND stg.has_car = aux.has_car

WHERE emp.employer_id IS NOT NULL