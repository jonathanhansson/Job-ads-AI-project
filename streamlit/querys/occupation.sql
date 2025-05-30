-- occupation.sql
SELECT
    oc.{{ category_col }} AS TargetGroup,
    SUM(fj.number_vacancies) AS Vacancies,
    MIN(oc.occupation_field) AS Industry,
    MIN(em.municipality) AS municipality,
    STRING_AGG(jd.description_text, ' ' ORDER BY fj.number_vacancies DESC) AS job_descriptions
FROM refined.fct_jobs AS fj
JOIN refined.dim_occupation oc ON fj.occupation_id = oc.occupation_id
JOIN refined.dim_employer em ON fj.employer_id = em.employer_id
JOIN refined.dim_job_details jd ON fj.job_details_id = jd.job_details_id
WHERE fj.publication_date BETWEEN ? AND ?
{% if municipality %}
  AND em.municipality = ?
{% endif %}
GROUP BY TargetGroup
ORDER BY Vacancies DESC