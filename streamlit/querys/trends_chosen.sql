--trends_chosen.sql
SELECT
    CAST(fj.publication_date AS DATE) AS publication_day,
    oc.{{ category_col }} AS TargetGroup, -- ocupation
    SUM(number_vacancies) AS Vacancies
FROM refined.fct_jobs AS fj
JOIN refined.dim_occupation oc ON fj.occupation_id = oc.occupation_id
WHERE CAST(fj.publication_date AS DATE) BETWEEN ? AND ?
AND oc.{{ category_col }} IN ( {{ placeholders }} )
GROUP BY publication_day, TargetGroup
ORDER BY publication_day
