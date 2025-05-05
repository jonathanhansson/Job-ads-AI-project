from pathlib import Path
import duckdb
from jinja2 import Template

def get_connection():
    return duckdb.connect("../ai_dbt_project/ads.duckdb")

def render_sql(filename: str, **params):
    path = Path("querys") / f"{filename}.sql"
    template = Template(path.read_text())
    return template.render(**params)

def run_query(con, query: str, params: list = ()):
    return con.execute(query, params).fetch_df()
