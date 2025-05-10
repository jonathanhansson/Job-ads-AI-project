# job-ads-ai-project/orchestration/orchestration/assets.py
# --- gör repo-roten import-bar ---------------------------------
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
# ----------------------------------------------------------------



from pathlib import Path
from dagster import AssetExecutionContext, AssetKey
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dbt import DbtCliResource, dbt_assets

# --- 1) importera funktionerna från ditt DLT-skript -------------------
#    (förutsätter att du skapat data_injest_dlt/__init__.py)
from data_injest_dlt.get_job_data import load_data_from_api, OCCUPATIONS

import dlt
from dlt.destinations import duckdb

ADS_DUCKDB = Path(__file__).parents[2] / "ai_dbt_project" / "ads"

# --- 2) definiera en DltSource ---------------------------------------
@dlt.source(name="job_ads_source")
def job_ads_source():
    return load_data_from_api(list(OCCUPATIONS.keys()))

# --- 3) DLT-asset som Dagster känner till ----------------------------
@dlt_assets(
    dlt_source=job_ads_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="ads",
        dataset_name="raw",
        destination=duckdb(destination_name=str(ADS_DUCKDB)),
        progress="log",
    ),
    name="raw_job_ads",
    group_name="raw",
)
def raw_job_ads_assets(
    context: AssetExecutionContext, dlt: DagsterDltResource
):
    yield from dlt.run(context=context)

# --- 4) dbt-asset som beror på rådatan -------------------------------
from .project import ai_dbt_project

@dbt_assets(
    manifest=ai_dbt_project.manifest_path,

)
def ai_dbt_project_dbt_assets(
    context: AssetExecutionContext, dbt: DbtCliResource
):
    yield from dbt.cli(["build"], context=context).stream()
