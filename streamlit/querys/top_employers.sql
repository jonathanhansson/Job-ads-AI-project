-- top_employers.sql
SELECT
  em.employer_name AS Employer,
  COUNT(*) AS Vacancies
FROM refined.fct_jobs AS fj
JOIN refined.dim_employer AS em
  ON fj.employer_id = em.employer_id
WHERE fj.publication_date BETWEEN ? AND ?
{% if municipality %}
  AND em.municipality = ?
{% endif %}
GROUP BY em.employer_name
ORDER BY Vacancies DESC
LIMIT ?
