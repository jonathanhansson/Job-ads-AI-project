# app.py

import streamlit as st
from app_pages.top_jobs import top_jobs_view
from app_pages.in_demand_skills_llm import display_llm_competence_insight
from app_pages.regions_in_demand import get_regions

st.set_page_config(layout="wide")

page = st.sidebar.radio("Välj vy:", [
    "Hetaste jobben just nu",
    "Regioner med flest jobb",
    "Anställningstyper & trender TOMT JUST NU",
    "Kompetensinsikter med Gemini"
])

if page == "Hetaste jobben just nu":
    top_jobs_view()
elif page == "Regioner med flest jobb":
    get_regions()
elif page == "Kompetensinsikter med Gemini":
    display_llm_competence_insight()