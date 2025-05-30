import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from datetime import timedelta
import locale
from st_db_con import get_connection, render_sql, run_query
from google import genai
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Define a consistent color map for industries
COLOR_MAP = {
    "Data/IT": "#66C2A5",
    "Administration, ekonomi, juridik": "#FC8D62",
    "Bygg och anläggning": "#8DA0CB",
}

# --- Helper function to manage municipality filter state ---
def get_municipality_filter():
    if "selected_kommun" in st.session_state:
        return st.session_state["selected_kommun"]
    return "Alla kommuner"

# --- Helper to display municipality selectbox ---
def select_municipality(df_municipalities, current_filter):
    try:
        locale.setlocale(locale.LC_COLLATE, 'sv_SE.UTF-8')
    except locale.Error:
        pass
    sorted_df = df_municipalities.sort_values(
        "municipality", key=lambda col: col.map(locale.strxfrm)
    ).reset_index(drop=True)
    options = ["Alla kommuner"] + sorted_df["municipality"].tolist()
    index = options.index(current_filter) if current_filter in options else 0
    return st.selectbox("Välj kommun:", options, index=index)

# --- Retrive all municipalities and their job vaccancies
def retrieve_municipalities_vaccancies(start_date, end_date):
    # ...efter att du hämtat df_occupation...
    with get_connection() as con:
        kommun_vacancies_sql = """
            SELECT
                em.municipality AS municipality,
                SUM(fj.number_vacancies) AS Vacancies
            FROM refined.fct_jobs AS fj
            JOIN refined.dim_employer em ON fj.employer_id = em.employer_id
            WHERE fj.publication_date BETWEEN ? AND ?
            GROUP BY em.municipality
        """
        municipalities_vacancies_df = run_query(con, kommun_vacancies_sql, params=[start_date, end_date])
    
    return municipalities_vacancies_df

# --- Prepare coordinates dataframe for map ---
def compute_coords(filter_municipality, df_municipality_vacancies):
    df_coords = pd.read_csv("../municipalities_lat_lon_clean.csv")
    df_coords["municipality"] = df_coords["municipality"].str.lower().str.strip()
    df_municipality_vacancies["municipality"] = df_municipality_vacancies["municipality"].str.lower().str.strip()
    df_coords = df_coords.merge(
        df_municipality_vacancies[["municipality", "Vacancies"]],
        on="municipality",
        how="left"
    )
    df_coords["Vacancies"] = df_coords["Vacancies"].fillna(0)
    df_coords["color"] = df_coords["municipality"].apply(
        lambda x: [255, 0, 0] if x == filter_municipality.lower() else [0, 120, 255]
    )
    df_coords["radius"] = df_coords["Vacancies"].apply(lambda x: 1500 + 2000 * np.log1p(x))
    return df_coords


# --- Build PyDeck Deck object for map ---
def build_deck(df_coords):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_coords,
        id="kommuner",  # set layer id to match event selection key
        get_position='[lon, lat]',
        get_color='color',
        get_radius='radius',
        pickable=True,
        auto_highlight=True,
        tooltip=True
    )
    view_state = pdk.ViewState(
        latitude=62,
        longitude=16,
        zoom=3.5,
        pitch=0,
    )
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{municipality}"},
        map_style=None,
        width=200,
        height=600
    )

# --- Render map and handle click events ---
def render_map(deck, key="kommun_map"):
    st.write("### Klicka på en kommun för att filtrera dashboarden")
    event = st.pydeck_chart(
        deck,
        on_select="rerun",
        selection_mode="single-object",
        key=key
    )
    if event and "selection" in event and event["selection"].get("objects", {}).get("kommuner"):
        kommun = event["selection"]["objects"]["kommuner"][0]["municipality"]
        kommun = kommun.strip().title()  # Ensure title case for matching
        if kommun != st.session_state.get("selected_kommun", "Alla kommuner"):
            st.session_state["selected_kommun"] = kommun
            st.rerun()

# --- Render bar chart for top jobs ---
def render_top_jobs_chart(df_occupation, filter_occupation, nr_targetgroup):
    fig = px.bar(
        df_occupation,
        x="Vacancies",
        y="TargetGroup_wrapped",
        color="Industry",
        orientation="h",
        title=f"Top {nr_targetgroup} {filter_occupation} (baserat på lediga jobb)",
        labels={"Vacancies": "Antal lediga jobb", "Industry": "Bransch"},
        text="Vacancies",
        color_discrete_map=COLOR_MAP,
        hover_data={"Andel (%)": True}
    )
    fig.update_traces(textposition="auto", marker_line_color='black', marker_line_width=0.5)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), font=dict(size=16))
    st.plotly_chart(fig, use_container_width=True)

# --- Render trend line chart ---
def render_trends_chart(df_trends, filter_occupation):
    st.subheader(f"Trender för {filter_occupation}")
    if df_trends.empty or "publication_day" not in df_trends.columns:
        st.info("Ingen trenddata att visa.")
        return
    min_date = df_trends["publication_day"].min()
    max_date = df_trends["publication_day"].max() + timedelta(days=1)
    date_range = st.slider(
        "Välj ett spann",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )
    df_filtered = df_trends[
        (df_trends["publication_day"] >= date_range[0]) &
        (df_trends["publication_day"] <= date_range[1])
    ]
    fig = px.line(
        df_filtered,
        x="publication_day",
        y="Vacancies",
        color="TargetGroup",
        markers=True,
        title="Daglig utveckling av annonser",
        color_discrete_map=COLOR_MAP  # use consistent industry colors
    )
    fig.update_yaxes(range=[0, df_filtered["Vacancies"].max() * 1.1])
    st.plotly_chart(fig, use_container_width=True)

# create a function that will take in two dataframes with data df occupation and df trends and municipality as arguments. Geminis instructions are to generate insights based on the data and return a response adapted for a HR agency.
def gemini_reply(df_occupation, df_trends, df_top_employers, filter_municipality):
    """
    Generate AI insights for HR agency based on job data.
    """
    # Send the full dataframes as string representations
    occ_snippet = df_occupation.drop(columns=["job_descriptions"], errors="ignore").to_string(index=False)
    trend_snippet = df_trends.to_string(index=False)
    emp_snippet = df_top_employers.to_string(index=False)

    prompt = f"""
    Du är en HR-analytiker som hjälper ett svenskt rekryteringsbolag att prioritera sitt arbete.
    Din uppgift är att analysera jobbannonser-data för kommunen: {filter_municipality}.

    Projektbeskrivning:
    Talent acquisition-specialister analyserar jobbannonser för att förstå vilka kandidater de bör kontakta och marknadsföra till arbetsgivare. De vill snabbt få insikter om vilka yrkesgrupper och arbetsgivare som är viktigast att fokusera på, baserat på aktuella annonser.

    Här är sammanfattad data:
    1. Yrkesgrupper och statistik:\n{occ_snippet}
    2. Dagliga annonstrender:\n{trend_snippet}
    3. Arbetsgivare och antal annonser:\n{emp_snippet}

    Analysera datan och identifiera tydliga trender eller förändringar jämfört med tidigare dagar. Lyft fram om någon yrkesgrupp eller arbetsgivare sticker ut, ökar eller minskar i efterfrågan. Ge en kort (max 200 ord) och konkret rekommendation till en talent acquisition-specialist: 
    - Vilka yrkesgrupper och arbetsgivare bör prioriteras för effektivare kandidatsök denna vecka?
    - Motivera utifrån både volym och förändring över tid.
    - Föreslå gärna en konkret åtgärd eller strategi.
    """
    client = genai.Client(api_key=os.getenv("gemini_api_key"))
    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return resp.text



# Genereate a Dataframe of top skills
def extract_skills_with_llm(df_occupation):
    """
    Extract key skills from job descriptions using Gemini.
    Returns DataFrame with skills and their importance scores.
    """
    if "job_descriptions" not in df_occupation.columns or df_occupation.empty:
        return pd.DataFrame(columns=["Kompetens", "Efterfrågan"])
    
    # Begränsa textmängden för LLM
    all_descriptions = " ".join(df_occupation["job_descriptions"].tolist())
    text_sample = all_descriptions[:25000]  # Begränsa för att undvika token limits
    
    # Få occupation field för kontext
    occupation_field = df_occupation["TargetGroup"].iloc[0] if not df_occupation.empty else "okänd bransch"
    
    prompt = f"""
    Du är en expert på kompetensanalys inom HR.
    
    Analysera dessa jobbeskrivningar inom {occupation_field} och identifiera de 10 viktigaste
    kvalifikationerna/kompetenserna/egenskaperna som arbetsgivare söker efter hos kandidater.
    
    För varje kompetens, ange ett poängtal (1-100) som representerar hur viktig/efterfrågad den är.
    
    Svara i exakt detta JSON-format:
    {{
      "skills": [
        {{"name": "Kompetens1", "score": 85}},
        {{"name": "Kompetens2", "score": 72}},
        {{"name": "Kompetens3", "score": 68}}
      ]
    }}
    
    Inkludera ingenting annat i ditt svar än denna JSON.
    
    Här är jobbeskrivningarna att analysera:
    {text_sample}
    """
    
    client = genai.Client(api_key=os.getenv("gemini_api_key"))
    resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    
    import json
    import re
    text = resp.text.strip()
    # Klipp ut JSON mellan första och sista klammer
    if text.startswith("```"):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
    try:
        skills_data = json.loads(text)
        return skills_data
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {resp.text}")
        return {"skills": []}


def render_skills_chart(skills_df):
    """Visualize skills as horizontal bar chart."""
    if skills_df.empty:
        st.warning("Inga kompetenser hittades i jobbannonserna.")
        return
    
    # Creat bar chart
    fig = px.bar(
        skills_df,
        x="Efterfrågan", 
        y="Kompetens",
        orientation="h",
        title="Topp 10 efterfrågade kompetenser och kvalifikationer",
        color="Efterfrågan",
        color_continuous_scale=px.colors.sequential.Bluered,
        text="Efterfrågan"
    )
    
    fig.update_traces(textposition="auto", texttemplate="%{x}", marker_line_width=0.5)
    fig.update_layout(
        yaxis=dict(categoryorder='total ascending'), 
        height=500,
        font=dict(size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- Render analysis expander and detailed table ---
def render_analysis_and_table(df_occupation, df_trends, df_top_employers, filter_municipality):
    analysis_col, details_col = st.columns([1, 2])
    with analysis_col:
        st.write("**OBS!** AI-genererade svar är inte alltid korrekta. Använd dem som en vägledning.")
        with st.expander(f"AI-analys av yrkesgrupper för {filter_municipality}"):
            if st.button("Generera AI-analys"):
                if df_occupation.empty or df_trends.empty:
                    st.warning("Ingen data tillgänglig för analys.")
                else:
                    st.write("Genererar AI-analys, detta kan ta några sekunder...")
                    response = gemini_reply(df_occupation, df_trends, df_top_employers, filter_municipality)
                    st.write(response)
    with details_col:
        st.write("**OBS!** AI-genererade svar är inte alltid korrekta. Använd dem som en vägledning.")
        with st.expander("Top skill graph"):
            if st.button(f"Generera AI-top-skills för {filter_municipality}"):
                if df_occupation.empty or df_trends.empty:
                    st.warning("Ingen data tillgänglig för analys.")
                else:
                    st.write("Genererar AI-analys, detta kan ta några sekunder...")
                    dict_competence_score = extract_skills_with_llm(df_occupation)
                    # Byt namn på kolumnerna direkt här!
                    df_competence_score = pd.DataFrame(dict_competence_score["skills"]).rename(
                        columns={"name": "Kompetens", "score": "Efterfrågan"}
                    )
                    render_skills_chart(df_competence_score)
                    st.write(dict_competence_score)

            


# --- Fetch top employers based on filters and date range using SQL template ---
def fetch_top_employers(start_date, end_date, municipality, limit):
    # Use Jinja SQL template to fetch top employers
    query = render_sql(
        filename="top_employers",  # uses querys/top_employers.sql
        municipality=municipality if municipality != "Alla kommuner" else None
    )
    params = [start_date, end_date]
    if municipality != "Alla kommuner":
        params.append(municipality)
    params.append(limit)
    with get_connection() as con:
        return run_query(con, query, params=params)

# --- Render bar chart for top employers ---
def render_top_employers_chart(df_employers):
    fig = px.bar(
        df_employers,
        x="Vacancies",
        y="Employer",
        orientation="h",
        title="Top Employers",
        text="Vacancies",
        color_discrete_sequence=[list(COLOR_MAP.values())[0]]  # single consistent color
    )
    fig.update_traces(textposition="auto")
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        font=dict(size=14)
    )
    st.plotly_chart(fig, use_container_width=True)
