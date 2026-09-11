import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import json
import geopandas as gpd
from shapely.geometry import shape
import matplotlib.colors as colors
from datetime import datetime
import os
import requests

url = "https://api.frankfurter.dev/v2/rate/USD/VND"

response = requests.get(url)
response.raise_for_status()

data = response.json()

rate = data["rate"]
AIRFLOW_HOME=os.environ.get("AIRFLOW_HOME")


processing_date = datetime.today().date().strftime(f"%Y-%m-%d")

conn = mysql.connector.connect(
    host="mysql",
    port=3306,
    user="mysql",
    password="mysql",
    database="jobs_db"
)

query = f"""
SELECT
    t.job_category,
    t.salary_unit,
    t.min_salary,
    t.max_salary
FROM (
    SELECT
        c.group_cat AS job_category,
        j.salary_unit,
        j.min_salary,
        j.max_salary
    FROM jobs AS j
    CROSS JOIN categories AS c
    WHERE FIND_IN_SET(
        c.name,
        REPLACE(j.tag, ', ', ',')
    ) > 0
    AND j.created_date = '{processing_date}'
) AS t;
"""

df = pd.read_sql(query, conn)


USD_TO_VND = rate / 1000

df["min_salary_vnd"] = df["min_salary"]
df["max_salary_vnd"] = df["max_salary"]

usd_mask = df["salary_unit"].eq("USD")

df.loc[usd_mask, "min_salary_vnd"] *= USD_TO_VND
df.loc[usd_mask, "max_salary_vnd"] *= USD_TO_VND


df["salary_mid"] = (
    df["min_salary_vnd"] +
    df["max_salary_vnd"]
) / 2


df = df.dropna(
    subset=["min_salary_vnd", "max_salary_vnd"]
)


bins = [
    0,
    10_000_000,
    20_000_000,
    30_000_000,
    40_000_000,
    50_000_000,
    float("inf")
]

labels = [
    "0–10M",
    "10–20M",
    "20–30M",
    "30–40M",
    "40–50M",
    "50M+"
]

df["salary_bucket"] = pd.cut(
    df["salary_mid"],
    bins=bins,
    labels=labels,
    right=False
)


heatmap_data = pd.crosstab(
    df["job_category"],
    df["salary_bucket"]
)

heatmap_data = heatmap_data.reindex(
    columns=labels,
    fill_value=0
)

heatmap_data = heatmap_data.loc[
    heatmap_data.sum(axis=1)
    .sort_values(ascending=False)
    .index
]

fig, ax = plt.subplots(figsize=(12, 8))

image = ax.imshow(
    heatmap_data.values,
    aspect="auto"
)

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)

ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

ax.set_xlabel("Advertised Salary Range")
ax.set_ylabel("Job Category")

ax.set_title(
    "Salary Distribution by Job Category"
)


for i in range(heatmap_data.shape[0]):
    for j in range(heatmap_data.shape[1]):

        value = heatmap_data.iloc[i, j]

        ax.text(
            j,
            i,
            value,
            ha="center",
            va="center"
        )

colorbar = plt.colorbar(
    image,
    ax=ax
)

colorbar.set_label(
    "Number of Job Postings"
)

plt.tight_layout()
plt.savefig(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "img/salary_distribution.png"
    ), dpi=300, bbox_inches="tight")
plt.close()

###################
# Jobs distribution
###################
def count_jobs_by_city(df):
    job_counts = (
        df.groupby("city")
        .size()
        .reset_index(name="job_count")
    )

    return job_counts

def load_vietnam_map(geojson_path="Provinces.geojson"):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []

    for feature in data["features"]:
        properties = feature["properties"].copy()
        properties["geometry"] = shape(feature["geometry"])
        records.append(properties)

    vietnam = gpd.GeoDataFrame(
        records,
        geometry="geometry",
        crs="EPSG:4326"
    )

    return vietnam


def merge_job_data(vietnam, job_counts):
    merged = vietnam.merge(
        job_counts,
        left_on="TinhThanh",
        right_on="city",
        how="left"
    )

    merged["job_count"] = (
        merged["job_count"]
        .fillna(0)
        .astype(int)
    )

    return merged


def plot_heatmap(vietnam):

    fig, ax = plt.subplots(figsize=(10, 14))

    max_val = vietnam["job_count"].max()

    if max_val > 0:
        norm = colors.LogNorm(
            vmin=1,
            vmax=max_val
        )
    else:
        norm = None

    vietnam.plot(
        column="job_count",
        ax=ax,
        cmap="YlOrRd",
        legend=True,
        edgecolor="black",
        linewidth=0.3,
        norm=norm,
        missing_kwds={
            "color": "#e0e0e0",
            "label": "Không có dữ liệu",
        },
        legend_kwds={
            "label": "Số lượng tin tuyển dụng",
            "orientation": "vertical",
            "shrink": 0.6,
            "pad": 0.02,
        },
    )

    ax.set_title(
        "BẢN ĐỒ PHÂN BỐ VIỆC LÀM TẠI VIỆT NAM",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    ax.axis("off")

    ax.set_xlim([102.0, 110.0])
    ax.set_ylim([8.0, 24.0])

    plt.tight_layout()
    plt.savefig(
        os.path.join(
            AIRFLOW_HOME,
            "..",
            "img/job_heatmap.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    # Giải phóng figure
    plt.close(fig)

print("Đang kết nối CSDL và lấy dữ liệu...")

query = f"""
    SELECT city
    FROM jobs
    WHERE city IS NOT NULL
        AND city <> ''
        AND created_date = '{processing_date}'
"""

df = pd.read_sql(query, conn)

# 2. Đếm số job theo tỉnh/thành
job_counts = count_jobs_by_city(df)

# 3. Đọc GeoJSON 34 tỉnh/thành
vietnam_map = load_vietnam_map(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "data/Provinces.geojson"
    )
)

# 4. Merge dữ liệu
vietnam_merged = merge_job_data(
    vietnam_map,
    job_counts
)

# 5. Vẽ heatmap
plot_heatmap(vietnam_merged)

################
# Top technologies
################
query = rf"""
SELECT
    t.name,
    COUNT(DISTINCT j.job_title) AS frequency
FROM technologies t, jobs j
WHERE LOWER(j.job_title) REGEXP CONCAT('\\b', LOWER(t.name), '\\b')
    AND created_date = '{processing_date}'
GROUP BY t.name
ORDER BY frequency ASC;
"""

df = pd.read_sql(query, conn)

fig, ax = plt.subplots(figsize=(10, 6))


plt.barh(
    df["name"],
    df["frequency"]
)

plt.title("Top công nghệ được yêu cầu")
plt.xlabel("Technology")
plt.ylabel("Frequency")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "img/top_technologies.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

# Giải phóng figure
plt.close(fig)

conn.close()