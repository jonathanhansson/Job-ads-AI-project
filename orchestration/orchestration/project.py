# orchestration/orchestration/project.py
from pathlib import Path
from dagster_dbt import DbtProject

# Peka direkt mot ditt dbt-projekt
ai_dbt_project = DbtProject(
    project_dir=Path(__file__).parents[2] / "ai_dbt_project",
    # valfritt: peka på ditt profiles.yml om det ligger utanför home
    profiles_dir=Path.home() / ".dbt"
)

# (Behövs bara i dev-läge, kan tas bort om du inte paketerar nu)
ai_dbt_project.prepare_if_dev()
