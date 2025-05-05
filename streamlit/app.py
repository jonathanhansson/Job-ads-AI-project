from datetime import date, timedelta
import plotly.express as px
import streamlit as st
from st_db_con import get_connection, render_sql, run_query

CATEGORY_MAP = {
    "Yrke": "occupation",
    "Yrkesgrupp": "occupation_group",
    "Sektor": "occupation_field"
}

st.set_page_config(layout="wide")
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
sql = render_sql("occupation", category_col=category_col)
with get_connection() as con:
    df = run_query(con, sql, params=[start_date, end_date])


total_vacancies = df["Vacancies"].sum()
df["Andel (%)"] = (df["Vacancies"] / total_vacancies * 100).round(1).astype(str) + "%"


st.subheader(f"Top 5 hetast inom '{filter_occupation}' just nu")

col1,col2 = st.columns([4,1])  

with col1:
    fig = px.bar(
        df,
        x="Vacancies",
        y="TargetGroup",
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
            categoryorder="total ascending",
            tickfont=dict(size=16)  
        ),
        font=dict(size=16),
        legend_title_text="Bransch"
    )

    st.plotly_chart(fig, use_container_width=True)