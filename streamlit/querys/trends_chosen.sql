SELECT
    fj.publication_date,
    oc.{{ category_col }} AS TargetGroup, -- ocupation
    COUNT(*) AS Vacancies
FROM refined.fct_jobs AS fj
JOIN refined.dim_occupation oc ON fj.occupation_id = oc.occupation_id
WHERE fj.publication_date BETWEEN ? AND ?
AND oc.{{ category_col }} IN ( {{ placeholders }} )
GROUP BY fj.publication_date, TargetGroup
ORDER BY fj.publication_date
