from datetime import datetime, date, timedelta
import streamlit as st
from st_db_con import get_connection, render_sql, run_query
import pandas as pd
import locale
from app_pages.top_jobs_utils import get_municipality_filter, select_municipality, compute_coords, build_deck, render_map, render_top_jobs_chart, render_trends_chart, render_analysis_and_table, fetch_top_employers, render_top_employers_chart, retrieve_municipalities_vaccancies

def top_jobs_view():
    CATEGORY_MAP = {
        "Yrke": "occupation",
        "Yrkesgrupp": "occupation_group",
        "Sektor": "occupation_field"
    }

    st.title("🔥 HR Dashboard – För att hitta enkelt era områden ni ska lägga resurser på!")

    col1, col2, col3, col4, rest_col = st.columns(5)
    with col1:
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

    with get_connection() as con:
        df_municipalities = run_query(con, """
            SELECT DISTINCT em.municipality AS municipality
            FROM refined.dim_employer AS em
            ORDER BY em.municipality ASC
        """)

    # --- Centralized filter state ---
    if "selected_kommun" not in st.session_state:
        st.session_state["selected_kommun"] = "Alla kommuner"

    with col3:
        kommuner = ["Alla kommuner"] + df_municipalities["municipality"].tolist()
        selectbox_index = kommuner.index(st.session_state["selected_kommun"]) if st.session_state["selected_kommun"] in kommuner else 0
        selected = st.selectbox("Välj kommun:", kommuner, index=selectbox_index)
        if selected != st.session_state["selected_kommun"]:
            st.session_state["selected_kommun"] = selected
            st.rerun()

    # Always use the current value from session state
    filter_municipality = st.session_state["selected_kommun"]
    category_col = CATEGORY_MAP[filter_occupation]
    # Create a occupation_sql variabel rendered based on filter above containing SQL code as string
    occupation_sql = render_sql(
        filename="occupation",
        category_col=category_col,
        municipality=filter_municipality if filter_municipality != "Alla kommuner" else None
    )

        
    with get_connection() as con:
        params = [start_date, end_date]
        if filter_municipality != "Alla kommuner":
            params.append(filter_municipality)
        df_occupation = run_query(con, occupation_sql, params=params) # running occupation_sql query to ads.duckdb with two parameters.
        with col4:
            nr_of_target = len(df_occupation["TargetGroup"]) if len(df_occupation["TargetGroup"]) != 0 else 1
            
            nr_targetgroup = st.slider(
                label=f"Välj hur många rader inom gruppen {filter_occupation} som ska visas",
                min_value=0,
                max_value= nr_of_target,
                value = 5 if len(df_occupation["TargetGroup"]) >= 5 else len(df_occupation["TargetGroup"])
                )

        df_occupation = df_occupation.head(nr_targetgroup)

        # Get the selected target groups after the slider
        top_target_groups = df_occupation["TargetGroup"].tolist()

        # Build the correct number of SQL placeholders for the IN clause
        placeholders = ", ".join(["?"] * len(top_target_groups) )

        # Always pass municipality to render_sql, so Jinja can add/remove the filter
        trends_chosen_sql = render_sql(
            "trends_chosen",
            category_col=category_col,
            placeholders=placeholders,
            municipality=filter_municipality if filter_municipality != "Alla kommuner" else None
        )

        # Build the params list for the query
        params = [start_date, end_date] + top_target_groups
        if filter_municipality != "Alla kommuner":
            params.append(filter_municipality)

        try:
            df_trends = run_query(con=con, query=trends_chosen_sql, params=params)
            if df_trends.empty or "publication_day" not in df_trends.columns:
                st.warning(f"Saknas data för dessa dagar för {filter_municipality}.")
                df_trends = pd.DataFrame()  # Ensure it's empty for later checks
            else:
                df_trends["publication_day"] = pd.to_datetime(df_trends["publication_day"]).dt.date
        except Exception as e:
            st.warning(f"Saknas data för dessa dagar för {filter_municipality}.")
            df_trends = pd.DataFrame()
        total_vacancies = df_occupation["Vacancies"].sum() # taking the sum of all the vaccancies and storing it in a varibel, 
        df_occupation["Andel (%)"] = (df_occupation["Vacancies"] / total_vacancies * 100).round(1).astype(str) + "%" # do the math, round it up and convert to string add "%"
        # Add line breaks to long occupation titles in 'TargetGroup' for better display in graphs.
        df_occupation["TargetGroup_wrapped"] = df_occupation["TargetGroup"].apply(
            lambda s: s if len(s) <= 30 else s[:s[:45].rfind(" ")] + "<br>" + s[s[:45].rfind(" ") + 1:]
        )
    with rest_col:
        st.subheader(filter_municipality)

    # --- Fetch all municipalites and their total vacancies for map ---
    municipalities_df = retrieve_municipalities_vaccancies(start_date, end_date)
    df_coords = compute_coords(filter_municipality, municipalities_df)
    deck = build_deck(df_coords)
    map_col, bar_col, job_col = st.columns([1, 2, 2])
    with map_col:
        render_map(deck, key="kommun_map_top_jobs")

    # After map: get the (possibly) new value from session state
    filter_municipality = st.session_state["selected_kommun"]

    with bar_col:
        render_top_jobs_chart(df_occupation, filter_occupation, nr_targetgroup)
    with job_col:
        # Slider to choose how many top employers to show
        employer_limit = st.slider(
            "Antal topparbetsgivare att visa", min_value=1, max_value=20, value=5
        )
        st.subheader(f"Topp {employer_limit} arbetsgivare i {filter_municipality}")
        df_top_employers = fetch_top_employers(start_date, end_date, filter_municipality, employer_limit)
        if df_top_employers.empty:
            st.write("Inga data att visa för topp arbetsgivare.")
        else:
            render_top_employers_chart(df_top_employers)

    # Render trends chart below
    render_trends_chart(df_trends, filter_occupation)

    # Render AI analysis and detailed tables
    render_analysis_and_table(df_occupation, df_trends, df_top_employers, filter_municipality)




