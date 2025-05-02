SELECT 
    headline, duration, application_deadline AS last_date_to_apply
FROM
    refined.dim_job_details
JOIN 
    refined.fct_jobs ON refined.dim_job_details.job_details_id = refined.fct_jobs.job_details_id