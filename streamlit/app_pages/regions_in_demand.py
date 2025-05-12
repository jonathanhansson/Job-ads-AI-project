import streamlit as st
from st_db_con import get_connection, render_sql, run_query
import plotly.express as px
from datetime import date

def get_regions():
    order_style = ["ASC", "DESC"]

    col1, col2 = st.columns(2)

    
    with col1:
        sorting_choice = st.radio(
            "Välj sortering:",
            ["Stigande", "Fallande"]
        )

        date_start = date(2025, 4, 25)
        date_end = date.today()

        date_range = st.date_input(
            "Välj datumintervall: ",
            value=(date_start, date_end),
            min_value=date(2025, 4, 25),
            max_value=date.today()
        )

        # Vår date_input förväntar sig en tuple. Därför gör vi en check för att se längden på användarens svar (att den valt två stycken datum)
        if isinstance(date_range, tuple):
            if len(date_range) == 2:
                start, end = date_range
            elif len(date_range) == 1:
                start = end = date_range[0]
            else:
                start, end = date_start, date_end
        else:
            start = end = date_range

        with get_connection() as con:
            if sorting_choice == "Stigande":
                query = render_sql("region", order_style=order_style[0])
            else:
                query = render_sql("region", order_style=order_style[1])

            df = run_query(con, query, params=[start, end])
        
        # filtrerar bort "ej angiven"
        df = df[df["region"] != "ej angiven"]

    with col2:
        st.button("INFO", help="I vår databas finns det jobb som inte har någon region specificerad.")
        st.subheader("Svenska regioner med flest jobbmöjligheter")
        fig = px.bar(
            df,
            x = "region",
            y = "open_jobs"
        )
        
        fig.update_layout(xaxis_tickangle=290)
        

        st.plotly_chart(fig, use_container_width=True)
        
    
