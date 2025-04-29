import streamlit as st
import pandas as pd
import duckdb

def get_connection():
    return duckdb.connect("../ai_dbt_project/ads.duckdb")

def run_query(con, query: str):
    return con.execute(query).fetch_df()

open_position_query = """
SELECT 
    occupation AS job_name, 
    COUNT(number_vacancies) AS open_positions 
FROM 
    refined.fct_jobs fj 
JOIN 
    refined.dim_occupation doc 
    ON fj.occupation_id = doc.occupation_id 
WHERE 
    occupation_field = 'Data/IT' 
GROUP BY 
    occupation 
ORDER BY 
    open_positions DESC;
"""

vacancies_per_city_query = """
SELECT 
    city, 
    COUNT(number_vacancies) AS number_vacancies 
FROM 
    refined.dim_employer 
JOIN 
    refined.fct_jobs 
    ON refined.dim_employer.employer_id = refined.fct_jobs.employer_id 
GROUP BY 
    refined.dim_employer.city 
ORDER BY 
    number_vacancies DESC;
"""

with get_connection() as con:
    df1 = run_query(con, open_position_query)
    df2 = run_query(con, vacancies_per_city_query)

# Här börjar UI för streamlit
st.title("Talent acqusition dashboard")

st.write("Number of positions open in the Data/IT field")
st.dataframe(df1)

st.write("Number of positions open/city")
st.dataframe(df2)
