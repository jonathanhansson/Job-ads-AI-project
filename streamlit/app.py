import streamlit as st
from st_db_con import get_connection, load_query, run_query

q1 = load_query("get_vacancies_per_city")
q2 = load_query("get_open_positions_per_occupation")
q3 = load_query("popular_occ")
q4 = load_query("popular_occ_g")
q5 = load_query("specific_jobs")


with get_connection() as con:
    df1 = run_query(con, q1)
    df2 = run_query(con, q2)
    df3 = run_query(con, q3)
    df4 = run_query(con, q4)
    df5 = run_query(con, q5)
 

with st.sidebar:
    st.write("Kontrollpanel")
    top_5_jobs = st.checkbox("Topp fem hetaste yrkena just nu")
    top_5_job_groups = st.checkbox("Topp fem hetaste yrkesområdena just nu")
    all_jobs = st.checkbox("Alla jobb med filter")

if top_5_jobs:
    st.header("Occupation")
    st.dataframe(df3, use_container_width=True)
if top_5_job_groups:
    st.header("Occupation group")
    st.dataframe(df4, use_container_width=True)
if all_jobs:
    st.header("ALLA JOBB")
    with st.expander("Välj längd på jobbet"):
        checkbox1 = st.checkbox("Tillsvidare")
        checkbox2 = st.checkbox("6 månader+")
        checkbox3 = st.checkbox("3-6 månader")
        checkbox4 = st.checkbox("11 dagar - 3 månader")
        checkbox5 = st.checkbox("1-10 dagar")
        checkbox6 = st.checkbox("Jobb utan angiven längd")

        selected_durations = []
        if checkbox1:
            selected_durations.append("tills vidare")

        if checkbox2:
            selected_durations.append("6 månader eller längre")

        if checkbox3:
            selected_durations.append("3 månader - upp till 6 månader")

        if checkbox4:
            selected_durations.append("11 dagar - upp till 3 månader")

        if checkbox5:
            selected_durations.append("upp till 10 dagar")

        if checkbox6:
            selected_durations.append("ej angiven")

        if selected_durations:
            df5 = df5[df5["duration"].isin(selected_durations)]

    st.dataframe(df5, use_container_width=True)

        
  
    
    










    




