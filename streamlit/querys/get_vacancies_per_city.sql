-- Mängden öppna jobb per stad
SELECT 
    city, 
    COUNT(number_vacancies) AS number_vacancies 
FROM 
    refined.dim_employer 
JOIN 
    refined.fct_jobs ON refined.dim_employer.employer_id = refined.fct_jobs.employer_id 
WHERE
    city != 'ej angiven'
GROUP BY 
    refined.dim_employer.city 
ORDER BY 
    number_vacancies DESC;
