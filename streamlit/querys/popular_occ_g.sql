-- Populäraste yrkesområdena idag!

SELECT
    occupation_group, 
    COUNT(number_vacancies) AS open_positions
FROM 
    refined.dim_occupation
JOIN 
    refined.fct_jobs ON refined.dim_occupation.occupation_id = refined.fct_jobs.occupation_id
GROUP BY
    occupation_group
ORDER BY 
    open_positions DESC