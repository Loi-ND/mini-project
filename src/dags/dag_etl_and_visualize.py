import os
from datetime import datetime, timedelta

from utils.notity import (discord_notification_on_failure,
                    discord_notification_on_success)
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME")
llm_sumarize_addresses_path = os.path.join(AIRFLOW_HOME, "..", "jobs/llm_sumarize_addresses.py")
processing_data_path = os.path.join(AIRFLOW_HOME, "..", "jobs/processing_data.py")
visualize_path = os.path.join(AIRFLOW_HOME, "..", "jobs/visualize.py")
send_charts_to_discord_path = os.path.join(AIRFLOW_HOME, "..", "jobs/send_charts_to_discord.py")
python = os.path.join(AIRFLOW_HOME, ".venv/bin/python")

default_args = {
    "owner": 'admin',
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "email_on_failure": False,
    "on_failure_callback": discord_notification_on_failure
}

with DAG(
    dag_id="dag_etl_and_visualize",
    description="This dag mission is pull all the jobs data",
    default_args=default_args,
    on_success_callback=discord_notification_on_success,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["daily", "orchestration"],
    schedule="0 7 * * *"
    ) as dag:

    llm_sumarize_addresses_task = BashOperator(
        task_id = "llm_sumarize_addresses_task",
        bash_command=(
            f"{python} {llm_sumarize_addresses_path}"
        ),
        execution_timeout = timedelta(minutes=20)
    )

    processing_data_task = BashOperator(
        task_id = "processing_data_task",
        bash_command=(
            f"{python} {processing_data_path}"
        ),
        execution_timeout = timedelta(minutes=20)
    )

    visualize_task = BashOperator(
        task_id = "visualize_task",
        bash_command=(
            f"{python} {visualize_path}"
        ),
        execution_timeout = timedelta(minutes=20)
    )

    send_charts_to_discord_task = BashOperator(
        task_id = "send_charts_to_discord_task",
        bash_command=(
            f"{python} {send_charts_to_discord_path}"
        ),
        execution_timeout = timedelta(minutes=20)
    )

    (
        llm_sumarize_addresses_task >>
        processing_data_task >>
        visualize_task >>
        send_charts_to_discord_task
    )