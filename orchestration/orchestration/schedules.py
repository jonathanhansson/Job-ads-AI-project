# orchestration/orchestration/schedules.py
from dagster import define_asset_job, ScheduleDefinition

daily_job = define_asset_job(
    name="daily_pipeline",
    selection="*",          # kör både ingest_job_ads + alla dbt-assets
)

schedules = [
    ScheduleDefinition(
        job=daily_job,
        cron_schedule="*/3 * * * *",       # TESTAR ATT KÖRA VAR 2 MIN
        execution_timezone="Europe/Stockholm",
    ),
]
