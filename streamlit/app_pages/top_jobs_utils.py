import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from datetime import timedelta
import locale
from st_db_con import get_connection, render_sql, run_query

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

# --- Prepare coordinates dataframe for map ---
def compute_coords(filter_municipality):
    df_coords = pd.read_csv("../municipalities_lat_lon_clean.csv")
    df_coords["color"] = df_coords["municipality"].apply(
        lambda x: [255,0,0] if x == filter_municipality else [0,120,255]
    )
    df_coords["radius"] = df_coords["municipality"].apply(
        lambda x: 8000 if x == filter_municipality else 5000
    )
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

# --- Render analysis expander and detailed table ---
def render_analysis_and_table(df_occupation, df_trends):
    analysis_col, details_col = st.columns([1, 4])
    with analysis_col:
        with st.expander("AI-analys av yrkesgrupper"):
            for _, row in df_occupation.iterrows():
                st.markdown(f"### {row['TargetGroup']}")
    with details_col:
        with st.expander("Detaljerad vy av yrkesgrupper"):
            st.write(df_occupation)
            st.write(df_trends)

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
