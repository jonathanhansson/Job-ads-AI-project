from datetime import datetime, date, timedelta
import plotly.express as px
import streamlit as st
from st_db_con import get_connection, render_sql, run_query
import pandas as pd

def top_jobs_view():
    CATEGORY_MAP = {
        "Yrke": "occupation",
        "Yrkesgrupp": "occupation_group",
        "Sektor": "occupation_field"
    }

    st.title("🔥 HR Dashboard – För att hitta enkelt era områden ni ska lägga resurser på!")

    today = date.today()

    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        # Filter: välj tidsspann
        filter_val = st.selectbox(
            "Välj tidsintervall:",
            ["Senaste dagen", "Senaste veckan", "Senaste 2 veckorna", "Senaste 30 dagarna", "Ange själv"],
            index=1 # Lastest week as DEAFULT index 1
        )

    today = date.today()
    if filter_val == "Senaste dagen":
        start_date = today - timedelta(days=1)
        end_date = today
    elif filter_val == "Senaste veckan":
        start_date = today - timedelta(weeks=1)
        end_date = today
    elif filter_val == "Senaste 2 veckorna":
        start_date = today - timedelta(weeks=2)
        end_date = today
    elif filter_val == "Senaste 30 dagarna":
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Från:")
        with col_b:
            end_date = st.date_input("Till:")

    with col2:
        # Filter: Välj filtrering på Yrke, Yrkesgrupp, Sector. (DEFAULT Ska vara inom Yrkesgrupp)
        filter_occupation = st.selectbox(
            "Välj yrke, yrkesgrupp eller sektor:",
            ["Yrke", "Yrkesgrupp", "Sektor"],
            index=1
        )

    category_col = CATEGORY_MAP[filter_occupation]
    # Skapar en occupation query för top 5 hetast inom vald catogory_col
    occupation_sql = render_sql("occupation", category_col=category_col)

    with get_connection() as con:
        df_occupation = run_query(con, occupation_sql, params=[start_date, end_date])
        # Baserat på filter occupation, skapa en dataframe för trender för dessa top 3-5 hetaste category_col
        top_target_groups = df_occupation["TargetGroup"].tolist() 
        placeholders = ", ".join(["?"] * len(top_target_groups))
        trends_chosen_sql = render_sql("trends_chosen", category_col=category_col, placeholders=placeholders)
        params = [start_date, end_date] + top_target_groups
        df_trends = run_query(con, trends_chosen_sql, params=params)


    total_vacancies = df_occupation["Vacancies"].sum()
    df_occupation["Andel (%)"] = (df_occupation["Vacancies"] / total_vacancies * 100).round(1).astype(str) + "%"
    df_occupation["TargetGroup_wrapped"] = df_occupation["TargetGroup"].apply(
        lambda s: s if len(s) <= 30 else s[:s[:45].rfind(" ")] + "<br>" + s[s[:45].rfind(" ") + 1:]
    )

    st.subheader(f"Top 5 hetast inom '{filter_occupation}' just nu")

    col1,col2 = st.columns(2)  

    with col1:
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
                "Andel (%)": "Andel av totalen"
            },
            text="Vacancies",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={
                "Vacancies": False,
                "Industry": False,
                "Andel (%)": True,
                "TargetGroup": False  
            }
        )
        fig.update_traces(
            textposition="auto",
            marker_line_color='black',
            marker_line_width=0.5,
            hoverlabel=dict(
                bgcolor="gray",
                font_size=20,
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
    
    df_trends["publication_date"] = pd.to_datetime(df_trends["publication_date"])
    df_trends["date_only"] = df_trends["publication_date"].dt.date
    min_date = df_trends["date_only"].min()
    max_date = df_trends["date_only"].max()


    st.subheader(f"Trender för {filter_occupation} ")
    date_range = st.slider(
        "Välj ett spann",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    df_filtered = df_trends[
        (df_trends["date_only"] >= date_range[0]) &
        (df_trends["date_only"] <= date_range[1])
    ]


        # Skapa linjediagram
    fig = px.line(
        df_filtered,
        x="date_only",
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


        

