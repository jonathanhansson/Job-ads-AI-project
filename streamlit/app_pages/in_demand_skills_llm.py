import streamlit as st
import pandas as pd
from st_db_con import get_connection, render_sql, run_query
from google import genai
from dotenv import load_dotenv
import os



def get_gemini_insight(job_description):
    load_dotenv()
    api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    Jag vill att du lyfter fram de fem mest värdefulla färdigheterna för detta yrke: {job_description}.
    Strukturera ditt svar så här:
    1. Färdighet1
        Förklaring till varför detta är viktigt
    2. Färdighet2
        Förklaring till varför detta är viktigt
    3. Färdighet3
        Förklaring till varför detta är viktigt
    4. Färdighet4
        Förklaring till varför detta är viktigt
    5. Färdighet5
        Förklaring till varför detta är viktigt
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text

def get_description_text(selected_occupation):
    with get_connection() as con:
        q = f"""
        SELECT DISTINCT
            occupation, description_text
        FROM
            refined.dim_occupation
        JOIN 
            refined.fct_jobs ON refined.dim_occupation.occupation_id = refined.fct_jobs.occupation_id
        JOIN
            refined.dim_job_details ON refined.fct_jobs.job_details_id = refined.dim_job_details.job_details_id
        WHERE 
            occupation = ?
        ORDER BY 
            description_text DESC;
        """
        unique_values = con.execute(q, [selected_occupation]).fetch_df()
        choices = unique_values["description_text"].to_list()
        cleaned_description = [description.replace("\n", "") for description in choices]
        return cleaned_description
    

def get_occupations(selected_group):
    with get_connection() as con:
        q = f"""
        SELECT DISTINCT 
            occupation 
        FROM 
            refined.dim_occupation
        WHERE 
            occupation_group = ?
        ORDER BY 
            occupation DESC;
        """
        unique_values = con.execute(q, [selected_group]).fetch_df()
        choices = unique_values["occupation"].to_list()
        return choices
    
def get_occupation_groups(selected_field):
    with get_connection() as con:
        q = f"""
        SELECT DISTINCT 
            occupation_group
        FROM 
            refined.dim_occupation
        WHERE 
            occupation_field = ?
        ORDER BY 
            occupation_group DESC;
        """
        unique_values = con.execute(q, [selected_field]).fetch_df()
        choices = unique_values["occupation_group"].to_list()
        return choices
    
def get_occupation_fields():
    with get_connection() as con:
        q = """
        SELECT DISTINCT 
            occupation_field 
        FROM 
            refined.dim_occupation
        ORDER BY 
            occupation_field DESC;
        """
        unique_values = con.execute(q).fetch_df()
        choices = unique_values["occupation_field"].to_list()
        return choices

def display_llm_competence_insight():
    occupation_fields = ["data/it", "administration, ekonomi, juridik", "bygg och anläggning"]

    col1, col2 = st.columns(2)

    with col1:
        # Välj yrkesfält
        selected_field = st.selectbox("Välj yrkesfält: ", occupation_fields)
        
        # Hämta yrkesgrupper baserat på valt yrkesfält
        choices_group = get_occupation_groups(selected_field)
        selected_group = st.selectbox("Välj yrkesgrupp: ", choices_group)

        # Hämta yrken baserat på vald yrkesgrupp
        choices_occupation = get_occupations(selected_group)
        selected_occupation = st.selectbox("Välj yrke: ", choices_occupation)

        desc = get_description_text(selected_occupation)
        
        # Visa den valda informationen för kontroll
        st.write(f"Valt yrke: {selected_occupation}")
    
    with col2:
        st.write(f"Alla jobb inom {selected_occupation}")

        desc = get_description_text(selected_occupation)
        gemini_insight = get_gemini_insight(desc)
        st.write(gemini_insight)
        


        
   


