import dlt
import requests

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
        "published-after": 1500 # Everything the lastest 25 hours to ensure overlap
    }
    response = requests.get(url, params=params)
    return response

# Dlt Resource objekt method. Paginates until there is no more ads or max API hits 2000.
@dlt.resource(write_disposition="merge", name="raw_job_ads", primary_key="id")
def load_data_from_api(occupation_fields: str):
    """
    This function loads raw data from the Tech job ads API
    """

    for occupation in occupation_fields:
        offset = 0
        
        field_name = None                                           ##DEBUG
        if occupation == "X82t_awd_Qyc":                            ##DEBUG
            field_name = "Administration, ekonomi, juridik"         ##DEBUG
        elif occupation == "j7Cq_ZJe_GkT":                          ##DEBUG
            field_name = "Bygg och anläggning"                      ##DEBUG
        elif occupation == "apaJ_2ja_LuF":                          ##DEBUG
            field_name = "Data/IT"                                  ##DEBUG
        print()                                                     ##DEBUG
        print()                                                     ##DEBUG
        print(f"FETCHES THE LATEST 24 hours from {field_name}...")  ##DEBUG

        while True:



            # Calling the function to read one page of 100 ads since its the api LIMIT. With The Occupation and offset as arguments
            response = fetch_page_api(occupation, offset)

            # If the response is approved and its less then 100 ads, meaning its about to end, then we should yield the last
            # and then break the loop back to the pipeline
            if response.status_code == 200:
                data = response.json()
                print(f"Offset for occupation code '{occupation}': {offset}")
                print(f"Fetches {len(data['hits'])} ads from {field_name}")
                if len(data['hits']) < 100 and len(data['hits'] ) > 0:
                    yield data["hits"]
                    break 
                else:
                    yield data["hits"]

            else:
                print(f"Response code: {response.status_code}")
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
    

