from discord_webhook import (
    DiscordWebhook,
    DiscordEmbed
)
from datetime import datetime
from dotenv import load_dotenv
import os

AIRFLOW_HOME=os.environ.get("AIRFLOW_HOME")

load_dotenv(os.path.join(
    AIRFLOW_HOME,
    "..",
    ".env"
))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
webhook = DiscordWebhook(
    url=WEBHOOK_URL,
    content=f"Biểu đồ phân tích thị trường việc làm ngành IT - {datetime.today().date().strftime("%Y-%m-%d")}"
)

with open(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "img/job_heatmap.png"
    ), 
    "rb") as f:
    webhook.add_file(file=f.read(), filename="job_heatmap.png")

with open(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "img/salary_distribution.png"
    ), "rb") as f:
    webhook.add_file(file=f.read(), filename="salary_distribution.png")

with open(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "img/top_technologies.png"
    ), "rb") as f:
    webhook.add_file(file=f.read(), filename="top_technologies.png")

embed1 = DiscordEmbed(
    title="📍 Phân bố việc làm",
    color="03b2f8"
)
embed1.set_image(url="attachment://job_heatmap.png")

# Embed 2
embed2 = DiscordEmbed(
    title="💰 Phân bố mức lương",
    color="03b2f8"
)
embed2.set_image(url="attachment://salary_distribution.png")

# Embed 3
embed3 = DiscordEmbed(
    title="💻 Top các công nghệ được yêu cầu phổ biến",
    color="03b2f8"
)
embed3.set_image(url="attachment://top_technologies.png")

webhook.add_embed(embed1)
webhook.add_embed(embed2)
webhook.add_embed(embed3)
webhook.execute(remove_embeds=True)