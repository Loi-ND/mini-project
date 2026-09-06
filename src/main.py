import pandas as pd

df = pd.read_csv("../data/data.csv")
df['job_title'].to_csv("sample.csv", index=False)