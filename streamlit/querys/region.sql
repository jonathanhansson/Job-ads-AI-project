-- region.sql
SELECT DISTINCT 
  region,
  COUNT(refined.fct_jobs.employer_id) AS open_jobs 
FROM 
  refined.dim_employer
JOIN 
  refined.fct_jobs ON refined.dim_employer.employer_id = refined.fct_jobs.employer_id
WHERE
  refined.fct_jobs.publication_date BETWEEN ? AND ?
GROUP BY 
  region
ORDER BY 
  open_jobs {{ order_style }}