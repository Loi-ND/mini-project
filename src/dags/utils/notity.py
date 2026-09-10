import os
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed


def get_webhook_url():
    """
    Load WEBHOOK_URL từ file .env
    """
    airflow_home = os.environ.get("AIRFLOW_HOME")

    if not airflow_home:
        raise RuntimeError("AIRFLOW_HOME is not set")

    dotenv_path = os.path.join(
        airflow_home,
        "..",
        ".env"
    )

    load_dotenv(dotenv_path)

    webhook_url = os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL is not set")

    return webhook_url


def discord_notification_on_failure(context: Dict):
    """
    Callback khi một TASK thất bại.
    """

    task_instance = context["task_instance"]
    dag_run = context.get("dag_run")
    exception = context.get("exception")

    webhook_url = get_webhook_url()

    execution_date = context.get("logical_date")

    if execution_date:
        execution_date = execution_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        execution_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    webhook = DiscordWebhook(
        url=webhook_url,
        username="Airflow",
    )

    embed = DiscordEmbed(
        title="❌ Airflow Task Failed",
        description=(
            "Một task trong Airflow DAG đã thất bại."
        ),
        color="FF0000",
    )

    embed.add_embed_field(
        name="DAG",
        value=f"`{task_instance.dag_id}`",
        inline=False,
    )

    embed.add_embed_field(
        name="Task",
        value=f"`{task_instance.task_id}`",
        inline=False,
    )

    embed.add_embed_field(
        name="Execution date",
        value=f"`{execution_date}`",
        inline=False,
    )

    if dag_run:
        embed.add_embed_field(
            name="Run ID",
            value=f"`{dag_run.run_id}`",
            inline=False,
        )

    if exception:
        embed.add_embed_field(
            name="Exception",
            value=f"```{str(exception)[:1000]}```",
            inline=False,
        )

    embed.add_embed_field(
        name="Log",
        value=f"[Xem task log]({task_instance.log_url})",
        inline=False,
    )

    embed.set_footer(
        text="Airflow Task Failure Notification"
    )

    webhook.add_embed(embed)

    webhook.execute()


def discord_notification_on_success(context: Dict):
    """
    Callback khi toàn bộ DAG chạy thành công.
    """

    dag = context["dag"]
    dag_run = context.get("dag_run")

    webhook_url = get_webhook_url()

    execution_date = context.get("logical_date")

    if execution_date:
        execution_date = execution_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        execution_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    webhook = DiscordWebhook(
        url=webhook_url,
        username="Airflow",
    )

    embed = DiscordEmbed(
        title="✅ Airflow DAG Success",
        description=(
            "DAG đã chạy thành công."
        ),
        color="00FF00",
    )

    embed.add_embed_field(
        name="DAG",
        value=f"`{dag.dag_id}`",
        inline=False,
    )

    embed.add_embed_field(
        name="Execution date",
        value=f"`{execution_date}`",
        inline=False,
    )

    if dag_run:
        embed.add_embed_field(
            name="Run ID",
            value=f"`{dag_run.run_id}`",
            inline=False,
        )

    embed.set_footer(
        text="Airflow DAG Success Notification"
    )

    webhook.add_embed(embed)

    webhook.execute()

