# job-ads-ai-project/data_injest_dlt/get_job_data.py

import dlt
import requests
import datetime
import duckdb
from pathlib import Path

OCCUPATIONS = {
"X82t_awd_Qyc": "Administration, ekonomi, juridik",
"j7Cq_ZJe_GkT": "Bygg och anläggning",
"apaJ_2ja_LuF":    "Data/IT",
}   


# Fetch one page with a limit of 100 ads, now with published-after/before as ISO8601 strings
def fetch_page_api(occupation: str, offset: int, published_after: str, published_before: str):
    """
    Fetches a page from the API based on occupation, offset, and date interval
    """
    url = f"https://jobsearch.api.jobtechdev.se/search"
    params = {
        "occupation-field": occupation,
        "limit": 100,
        "offset": offset,
        "published-after": published_after,
        "published-before": published_before,
    }
    response = requests.get(url, params=params)
    return response

# Dlt Resource objekt method. Paginates by date interval (5 days at a time, 1 day overlap)
@dlt.resource(write_disposition="merge", name="raw_job_ads", primary_key="id")
def load_data_from_api(
    occupation_fields: list[str],
    published_after: str = None,
    published_before: str = None
):
    """
    Loads job ads data from the API for specified occupations and date range.
    """
    # Set default published_before to now
    if published_before is None:
        published_before = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    # Set default published_after to latest date minus 1 day, or 6 days bakwards if no data exists.
    if published_after is None:
        latest = get_latest_publication_date()
        if latest:
            latest_dt = datetime.datetime.strptime(latest[:19], "%Y-%m-%dT%H:%M:%S")
            published_after = (latest_dt - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        else:
            now = datetime.datetime.now()
            published_after = (now - datetime.timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S")

    for occupation in occupation_fields:
        offset = 0
        field_name = OCCUPATIONS[occupation]
        while True:
            resp = fetch_page_api(occupation, offset, published_after, published_before)
            if resp.status_code != 200:
                print(f"Error from API: {resp.status_code}")
                break
            hits = resp.json().get("hits", [])
            print(f"{field_name}: {published_after} to {published_before}, offset {offset}, fetched {len(hits)} ads")
            if not hits:
                break
            for hit in hits:
                yield hit
            if len(hits) < 100:
                break
            offset += 100


def get_latest_publication_date(db_path: str = None) -> str | None:
    if db_path is None:
        # build searchpath relative to this file, no mather where you run from
        db_path = str((Path(__file__).parent.parent / "ai_dbt_project" / "ads.duckdb").resolve())
    try:
        con = duckdb.connect(db_path)
        result = con.execute("SELECT MAX(publication_date) FROM raw.raw_job_ads").fetchone()[0]
        con.close()
        if result:
            if isinstance(result, datetime.datetime):
                return result.strftime("%Y-%m-%dT%H:%M:%S")
            return str(result)
        return None
    except Exception as e:
        print(f"Kunde inte hämta senaste publication_date: {e}")
        return None


#Initiate the pipeline and running it with the dlt resource method.
def run_pipeline(occupation_fields):
    latest = get_latest_publication_date()
    if latest:
        latest_dt = datetime.datetime.strptime(latest[:19], "%Y-%m-%dT%H:%M:%S")
        published_after = (latest_dt - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    else:
        now = datetime.datetime.now()
        published_after = (now - datetime.timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S")
    published_before = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    pipeline = dlt.pipeline(
        pipeline_name="ads",
        destination=dlt.destinations.duckdb(destination_name="./ai_dbt_project/ads"),
        dataset_name="raw"
    )
    load_info = pipeline.run(load_data_from_api(occupation_fields, published_after, published_before))
    print(f"Kör från {published_after} till {published_before}")
    print(load_info)

if __name__ == "__main__":
    occupation_fields = ["X82t_awd_Qyc", "j7Cq_ZJe_GkT", "apaJ_2ja_LuF"]
    run_pipeline(occupation_fields)


