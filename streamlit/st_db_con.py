import duckdb

def get_connection():
    return duckdb.connect("../ai_dbt_project/ads.duckdb")

def load_query(filename: str):
    with open(f"querys/{filename}.sql", "r") as f:
        return f.read()

def run_query(con, query):
    return con.execute(query).fetch_df()




