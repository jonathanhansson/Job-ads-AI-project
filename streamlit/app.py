# app.py

import streamlit as st
from app_pages.top_jobs import top_jobs_view
from app_pages.in_demand_skills_llm import display_llm_competence_insight
from app_pages.regions_in_demand import get_regions
from app_pages.llm_skills_graph import display_skills

st.set_page_config(layout="wide")

page = st.sidebar.radio("Välj vy:", [
    "Hetaste jobben just nu",
    "Regioner med flest jobb",
    "Anställningstyper & trender TOMT JUST NU",
    "Kompetensinsikter med Gemini",
    "APA"
])

if page == "Hetaste jobben just nu":
    top_jobs_view()
elif page == "Regioner med flest jobb":
    get_regions()
elif page == "Kompetensinsikter med Gemini":
    display_llm_competence_insight()
elif page == "APA":
    display_skills()