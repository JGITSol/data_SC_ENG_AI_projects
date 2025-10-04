"""
Dagster schedules for automated pipeline execution.
"""
from dagster import ScheduleDefinition, DefaultScheduleStatus
from src.orchestration.jobs import daily_pipeline_job

# Run pipeline daily at 2 AM
daily_schedule = ScheduleDefinition(
    name="daily_taxi_pipeline",
    job=daily_pipeline_job,
    cron_schedule="0 2 * * *",  # 2 AM daily
    default_status=DefaultScheduleStatus.STOPPED,
)
