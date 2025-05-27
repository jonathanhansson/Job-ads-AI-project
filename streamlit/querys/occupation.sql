-- occupation.sql
SELECT
    oc.{{ category_col }} AS TargetGroup,
    SUM(fj.number_vacancies) AS Vacancies,
    MIN(oc.occupation_field) AS Industry,
FROM refined.fct_jobs AS fj
JOIN refined.dim_occupation oc ON fj.occupation_id = oc.occupation_id
JOIN refined.dim_employer em ON fj.employer_id = em.employer_id
WHERE fj.publication_date BETWEEN ? AND ?
{% if municipality %}
  AND em.municipality = ?
{% endif %}
GROUP BY TargetGroup
ORDER BY Vacancies DESC