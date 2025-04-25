import dlt
import requests


@dlt.resource(write_disposition="replace", name="raw_job_ads")
def load_data_from_api(occupation_field: str):
    """
    This function loads raw data from the Tech job ads API
    """
    url = f"https://jobsearch.api.jobtechdev.se/search"
    params = {
        "occupation-field": occupation_field,
        "limit": 100
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        yield data
    
    else:
        print("Couldn't fetch data")

def run_pipeline(occupation_field):
    pipeline =  dlt.pipeline(
        pipeline_name="ads",
        destination="duckdb",
        dataset_name="staging"
    )

    for f in occupation_field:
        load_info = pipeline.run(load_data_from_api(f))
        print(load_info)




if __name__ == "__main__":
    occupation_fields = ("X82t_awd_Qyc", "j7Cq_ZJe_GkT", "apaJ_2ja_LuF")
    run_pipeline(occupation_fields)
    

