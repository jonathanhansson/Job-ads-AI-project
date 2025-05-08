# orchestration/orchestration/definitions.py
from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import ingest_job_ads, ai_dbt_project_dbt_assets
from .schedules import schedules, daily_job
from .project import ai_dbt_project
from pathlib import Path

defs = Definitions(
    assets=[ingest_job_ads, ai_dbt_project_dbt_assets],
    jobs=[daily_job],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(
            project_dir=ai_dbt_project.project_dir,
            profiles_dir=Path.home() / ".dbt",   # ← och här
        ),
    },
)
