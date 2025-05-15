from datetime import datetime, date, timedelta
import plotly.express as px
import streamlit as st
from st_db_con import get_connection, render_sql, run_query
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


def top_employers_view():
    st.title("🔥 HR Dashboard – Sverige heatmap och")
    st.map()