import pandas as pd

df = pd.read_csv("../data/data.csv")

patterns = [
    r"^Thoả thuận$",
    r"^Trên\s+\d+(?:\.\d+)*\s+triệu$",
    r"^Trên\s+\d+(?:,\d+)*\s+USD$",
    r"^Tới\s+\d+(?:\.\d+)*\s+triệu$",
    r"^Tới\s+\d+(?:,\d+)*\s+USD$",
    r"^\d+(?:\.\d+)*\s+-\s+\d+(?:\.\d+)*\s+triệu$",
    r"^\d+(?:,\d+)*\s+-\s+\d+(?:,\d+)*+\s+USD$"
]

lenght = 0
for pattern in patterns:
    lenght += df['salary'].str.match(pattern).sum()

assert lenght == len(df)