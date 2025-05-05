# app.py

import streamlit as st
from app_pages.top_jobs import top_jobs_view

st.set_page_config(layout="wide")

page = st.sidebar.radio("Välj vy:", [
    "Hetaste jobben just nu",
    "Regioner med flest jobb TOMT JUST NU",
    "Anställningstyper & trender TOMT JUST NU",
    "Kompetensinsikter TOM JUST NU LLM?"
])

if page == "Hetaste jobben just nu":
    top_jobs_view()
