# orchestration/orchestration/assets.py
from pathlib import Path
import subprocess
from dagster import asset, AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets
from .project import ai_dbt_project
import sys

DLT_SCRIPT = Path(__file__).parents[2] / "dlt" / "get_job_data.py"

@asset(description="Kör DLT-skriptet som laddar data till DuckDB")
def ingest_job_ads(context: AssetExecutionContext):
    result = subprocess.run([sys.executable, str(DLT_SCRIPT)], capture_output=True, text=True)
    context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise RuntimeError("DLT-skriptet misslyckades")

@dbt_assets(manifest=ai_dbt_project.manifest_path)   # ← ingen extra parameter
def ai_dbt_project_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
