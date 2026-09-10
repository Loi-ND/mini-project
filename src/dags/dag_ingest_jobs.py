import os
from datetime import datetime, timedelta

from utils.notity import (discord_notification_on_failure,
                    discord_notification_on_success)
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME")
ingest_task_path = os.path.join(AIRFLOW_HOME, "..", "jobs/crawl_data.py")
python = os.path.join(AIRFLOW_HOME, ".venv/bin/python")

default_args = {
    "owner": 'admin',
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "on_failure_callback": discord_notification_on_failure
}

with DAG(
    dag_id="dag_ingest_jobs",
    description="This dag mission is pull all the reference data",
    default_args=default_args,
    on_success_callback=discord_notification_on_success,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["daily", "orchestration"],
    schedule="0 2 * * *"
    ) as dag:

    ingest_task = BashOperator(
        task_id = "ingest_task",
        bash_command=(
            f"{python} {ingest_task_path}"
        ),
        execution_timeout = timedelta(hours=2)
    )
    ingest_task