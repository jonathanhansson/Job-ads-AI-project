from pathlib import Path
import duckdb
from jinja2 import Template

def get_connection():
    return duckdb.connect("../ai_dbt_project/ads.duckdb")

def render_sql(filename: str, **params):
    try:
        path = Path("querys") / f"{filename}.sql"
        template_text = path.read_text()
        template = Template(template_text)
        return template.render(**params)
        
    except FileNotFoundError:
        print(f"FEL: SQL-mallen '{filename}.sql' hittades inte i mappen 'querys'.")
        return None

    except Exception as e:
        print(f"Ett fel inträffade vid hantering av SQL-mallen '{filename}.sql': {e}")
        return None

def run_query(con, query: str, params: list = ()):
    return con.execute(query, params).fetch_df()
