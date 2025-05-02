-- öppna jobb per yrkesroll
SELECT 
    occupation, 
    COUNT(number_vacancies) AS open_positions 
FROM 
    refined.fct_jobs fj 
JOIN 
    refined.dim_occupation doc ON fj.occupation_id = doc.occupation_id 
WHERE 
    occupation_field = 'Data/IT' 
GROUP BY 
    occupation 
ORDER BY 
    open_positions DESC;
