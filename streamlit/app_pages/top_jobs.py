from datetime import datetime, date, timedelta
import plotly.express as px
import streamlit as st
from st_db_con import get_connection, render_sql, run_query
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

def top_jobs_view():
    CATEGORY_MAP = {
        "Yrke": "occupation",
        "Yrkesgrupp": "occupation_group",
        "Sektor": "occupation_field"
    }

    st.title("🔥 HR Dashboard – För att hitta enkelt era områden ni ska lägga resurser på!")

    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        # Filter: choose timespan
        filter_val = st.selectbox(
            "Välj tidsintervall:",
            ["Senaste dagen", "Senaste veckan", "Senaste 2 veckorna", "Senaste 30 dagarna", "Ange själv"],
            index=1 # Standard choice "Senaste veckan"
        )


    today = date.today()

    # Map the choice to dict delta_map"
    delta_map = {
        "Senaste dagen": timedelta(days=1),
        "Senaste veckan": timedelta(weeks=1),
        "Senaste 2 veckorna": timedelta(weeks=2),
        "Senaste 30 dagarna": timedelta(days=30)
    }

    # One ternary for both varibles
    start_date, end_date = (
        (today - delta_map[filter_val], today)
        if filter_val in delta_map
        else (st.date_input("Från:"), st.date_input("Till:"))
    )

    with col2:
        # Filter: Choose filter on occupation group, standard is "yrkesgrupp"
        filter_occupation = st.selectbox(
            "Välj yrke, yrkesgrupp eller sektor:",
            ["Yrke", "Yrkesgrupp", "Sektor"],
            index=1
        )

    category_col = CATEGORY_MAP[filter_occupation]
    # Create a occupation_sql variabel rendered based on filter above containing SQL code as string
    occupation_sql = render_sql("occupation", category_col=category_col)

    with get_connection() as con:
        df_occupation = run_query(con, occupation_sql, params=[start_date, end_date]) # running occupation_sql query to ads.duckdb with two parameters.
        top_target_groups = df_occupation["TargetGroup"].tolist() 
        placeholders = ", ".join(["?"] * len(top_target_groups))  # Creating number of placeholder for next sql file to be rewritten either 3 or 5 "?" 
        trends_chosen_sql = render_sql("trends_chosen", category_col=category_col, placeholders=placeholders) # Rendering it with "?"
        params = [start_date, end_date] + top_target_groups # adding the current top target groups as params to the sql query
        df_trends = run_query(con, trends_chosen_sql, params=params) # running the query towards duckdb
        df_trends["publication_day"] = pd.to_datetime(df_trends["publication_day"]).dt.date


    total_vacancies = df_occupation["Vacancies"].sum() # taking the sum of all the vaccancies and storing it in a varibel, 
    df_occupation["Andel (%)"] = (df_occupation["Vacancies"] / total_vacancies * 100).round(1).astype(str) + "%" # do the math, round it up and convert to string add "%"
    # Add line breaks to long occupation titles in 'TargetGroup' for better display in graphs.
    df_occupation["TargetGroup_wrapped"] = df_occupation["TargetGroup"].apply(
        lambda s: s if len(s) <= 30 else s[:s[:45].rfind(" ")] + "<br>" + s[s[:45].rfind(" ") + 1:]
    )

    # use gemini to analyse each occupation and add info to the hooverdata
#    load_dotenv()
#    api_key = os.getenv("gemini_api_key")
#    client = genai.Client(api_key=api_key)
#    for index, row in df_occupation.iterrows():
#        prompt = f"""
#        Jag vill att du lyfter fram de fem mest värdefulla färdigheterna för detta yrke: {row['TargetGroup']}.
#        Strukturera ditt svar så här, inget annat:
#
#        - Dessa färdigheter är viktiga som {row['TargetGroup']}
#
#        1. Färdighet1 
#        2. Färdighet2 
#        3. Färdighet3
#        4. Färdighet4 
#        5. Färdighet5 

#        """
#        
#        response = client.models.generate_content(
#            model="gemini-2.0-flash",
#            contents=prompt,
#            config=types.GenerateContentConfig(
#                temperature=0.001 # testing the temperature
#            )
#        )
#        
#        df_occupation.at[index, "Gemini"] = response.text



    col1,col2 = st.columns(2)  

    # First graph to the LEFT
    with col1:
        st.subheader(f"Top 5 hetast inom '{filter_occupation}' just nu")
        fig = px.bar(
            df_occupation,
            x="Vacancies",
            y="TargetGroup_wrapped",
            color="Industry", 
            orientation="h",  
            title=f"Top 5 {filter_occupation} (baserat på lediga jobb)",
            labels={
                "TargetGroup": filter_occupation,
                "Vacancies": "Antal lediga jobb",
                "Industry": "Bransch",
                "Andel (%)": "Andel av totalen",
               # "Gemini": "Ai analys av yrket"
            },
            text="Vacancies",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={
                "Vacancies": False,
                "Industry": False,
                "Andel (%)": True,
                "TargetGroup": False,
                #"Gemini": False,
                "TargetGroup_wrapped": False,              
                }
                
        )
        fig.update_traces(
            textposition="auto",
            marker_line_color='black',
            marker_line_width=0.5,
            hoverlabel=dict(
                bgcolor="gray",
                font_size=16,
                font_family="Arial"
            )
        )

        fig.update_layout(
            yaxis=dict(
                title="Målgrupp",
                categoryorder="total ascending",
                tickfont=dict(size=16)  
            ),
            font=dict(size=16),
            legend_title_text="Bransch"
        )

        st.plotly_chart(fig, use_container_width=True)
    
    # Second graph to the RIGHT
    with col2:
        min_date = df_trends["publication_day"].min()
        max_date = df_trends["publication_day"].max()

        # Increment max_date with one day since it rounds backwards
        max_date += timedelta(days=1)

        st.subheader(f"Trender för {filter_occupation} ")
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


            # Skapa linjediagram
        fig = px.line(
            df_filtered,
            x="publication_day",
            y="Vacancies",
            color="TargetGroup",
            markers=True,
            line_shape="linear",
            title="Daglig utveckling av annonser"
        )

        max_vac = df_filtered["Vacancies"].max()

        fig.update_yaxes(
            range=[0, max_vac * 1.1],    # 0 till 110 % av max
            tick0=0,                     # börja tick vid 0
            dtick=max(1, max_vac // 5)   # ungefär 5 steg
        )

        st.plotly_chart(fig, use_container_width=True)

    anlysis_col, tabel_details_col = st.columns([1,4])
    with anlysis_col:
        
        with st.expander("AI-analys av yrkesgrupper"):
            for index, row in df_occupation.iterrows():
                st.markdown(f"### {row['TargetGroup']}")
                #st.markdown(row['Gemini'])

    with tabel_details_col:
        with st.expander("Detaljerad vy av yrkesgrupper"):
            st.write(df_occupation)
            st.write(df_trends)

        

