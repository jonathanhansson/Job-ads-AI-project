-- jobs_generic.sql
SELECT
    oc.{{ category_col }} AS TargetGroup,
    SUM(fj.number_vacancies) AS Vacancies,
    MIN(oc.occupation_field) AS Industry
FROM refined.fct_jobs AS fj
JOIN refined.dim_occupation oc ON fj.occupation_id = oc.occupation_id
WHERE fj.publication_date BETWEEN ? AND ?
GROUP BY TargetGroup
ORDER BY Vacancies DESC
LIMIT 5