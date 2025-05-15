# job-ads-ai-project/data_injest_dlt/get_job_data.py

import dlt
import requests

OCCUPATIONS = {
"X82t_awd_Qyc": "Administration, ekonomi, juridik",
"j7Cq_ZJe_GkT": "Bygg och anläggning",
"apaJ_2ja_LuF":    "Data/IT",
}   


# Fetch one page with a limit of 100 ads
def fetch_page_api(occupation: str, offset: int):
    """
    SRP: This method fetches a page from the API based on occupation and offset
    """
    url = f"https://jobsearch.api.jobtechdev.se/search"
    params = {
        "occupation-field": occupation,
        "limit": 100,
        "offset": offset,
        "published-after": 360 # Everything the lastest 25 hours to ensure overlap
    }
    response = requests.get(url, params=params)
    return response

# Dlt Resource objekt method. Paginates until there is no more ads or max API hits 2000.
@dlt.resource(write_disposition="merge", name="raw_job_ads", primary_key="id")
def load_data_from_api(occupation_fields: list[str]):
    """
    This function loads raw data from the Tech job ads API
    """

    for occupation in occupation_fields:
        offset = 0
        
        field_name = OCCUPATIONS[occupation] #DEBUG

        while True:
            resp = fetch_page_api(occupation, offset)
            if resp.status_code != 200:
                print(f"Error from API: {resp.status_code}")
                break
            hits = resp.json().get("hits", [])
            print(f"Offset {offset}, fetched {len(hits)} ads from {field_name}")
            # If hits is empty, BREAK
            if not hits:
                break
            # Else you yield every hit in hits 
            for hit in hits:
                yield hit
            # If hits less than 100, BREAK since there is no more hits after that run.
            if len(hits) < 100:
                break
            offset += 100


#Initiate the pipeline and running it with the dlt resource method.
def run_pipeline(occupation_fields):
    pipeline =  dlt.pipeline(
        pipeline_name="ads",
        destination=dlt.destinations.duckdb(destination_name="./ai_dbt_project/ads"),  #Correct location for ads.duckdb 
        dataset_name="raw"
    )

    load_info = pipeline.run(load_data_from_api(occupation_fields))
    print(load_info)


if __name__ == "__main__":
    occupation_fields = ["X82t_awd_Qyc", "j7Cq_ZJe_GkT", "apaJ_2ja_LuF"]

    run_pipeline(occupation_fields)
    

