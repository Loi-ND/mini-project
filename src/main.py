import pandas as pd

df = pd.read_csv("../data/data.csv")
patterns = [
    r"^[\w\s]+$",
    # r"^[\w\s]+(: [\w,\s]+)+$"
]

df['address'].to_csv("sample.csv", index=False)
lenght = 0
for pattern in patterns:
    lenght += df['address'].str.match(pattern).sum()

print(lenght)
assert lenght == len(df)