# job-ads-ai-project/orchestration/orchestration/definitions.py
from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import raw_job_ads_assets, ai_dbt_project_dbt_assets
from .schedules import schedules, daily_job
from .project import ai_dbt_project
from pathlib import Path
# orchestration/definitions.py
from dagster_dlt import DagsterDltResource      # ← importera

dlt_resource = DagsterDltResource()             # ← skapa resursen

defs = Definitions(
    assets=[raw_job_ads_assets, ai_dbt_project_dbt_assets],
    jobs=[daily_job],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(
            project_dir=ai_dbt_project.project_dir,
            profiles_dir=Path.home() / ".dbt",
        ),
        "dlt": dlt_resource,                    # ← lägg till den här raden
    },
)

