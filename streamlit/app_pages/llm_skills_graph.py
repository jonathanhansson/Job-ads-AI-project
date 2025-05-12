import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from st_db_con import get_connection, render_sql, run_query
import os


"""
Vad behöver jag göra?
1. Hämta insights om olika kvalitéer, och få ut siffrorna. Kommer nog behöva returnera strängar där "kvalitéen" står och sedan siffran, kommer nog behöva string-slica
2. Displaya kvalitéerna i en plotly/matplotlib
"""

def fetch_descriptions():
    with get_connection() as con:
        q = """
        SELECT DISTINCT 
            description_text
        FROM 
            refined.dim_job_details
        """
        descriptions = run_query(con, q)
        return descriptions


def get_skills_from_gemini(description):
    load_dotenv()
    api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=api_key)
    prompt = f"""
    {description}
    Based on this dataframe, can you pick out the most sought after skills in all the text.

    Output format, only the things below:

    {{
        "Skill1": number of times it appears,
        "Skill2": number of times it appears,
        "Skill3": number of times it appears,
        ... do this for all the skills you find in the dataframe
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.001 # testing the temperature
        )
    )

    return response.text

def display_skills():
    description = fetch_descriptions()
    skills = get_skills_from_gemini(description)
    print(skills)
    # st.write(skills)

