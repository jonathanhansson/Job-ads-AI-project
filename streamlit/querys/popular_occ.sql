-- Populäraste topp fem jobben idag!
SELECT 
    occupation,
    SUM(number_vacancies) AS open_positions,
    application_deadline
FROM 
    refined.dim_occupation
JOIN 
    refined.fct_jobs ON refined.dim_occupation.occupation_id = refined.fct_jobs.occupation_id
GROUP BY
    occupation, application_deadline
ORDER BY 
    open_positions DESC
LIMIT 5
