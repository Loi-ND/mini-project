import pandas as pd

def process_salary_columns(df: pd.DataFrame) -> pd.DataFrame:
    patterns = [
        r"^Thoả thuận$",
        r"^Trên\s+\d+(?:\.\d+)*\s+triệu$",
        r"^Trên\s+\d+(?:,\d+)*\s+USD$",
        r"^Tới\s+\d+(?:\.\d+)*\s+triệu$",
        r"^Tới\s+\d+(?:,\d+)*\s+USD$",
        r"^\d+(?:\.\d+)*\s+-\s+\d+(?:\.\d+)*\s+triệu$",
        r"^\d+(?:,\d+)*\s+-\s+\d+(?:,\d+)*+\s+USD$"
    ]

    new_df = []

    for pattern in patterns:
        mask = df['salary'].str.match(pattern)
        filtered_df = df.loc[mask]

        match pattern:
            case r"^Thoả thuận$":
                filtered_df = filtered_df.assign(
                    min_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    max_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    salary_unit=pd.Series("Unknown", index=filtered_df.index, dtype="string")
                )

            case r"^Trên\s+\d+(?:\.\d+)*\s+triệu$":
                filtered_df["min_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:\.\d+)*")
                    .str[0]
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    max_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    salary_unit=pd.Series("VND", index=filtered_df.index, dtype="string")
                )

            case r"^Trên\s+\d+(?:,\d+)*\s+USD$":
                filtered_df["min_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:,\d+)*")
                    .str[0]
                    .str.replace(",", "", regex=False)
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    max_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    salary_unit=pd.Series("USD", index=filtered_df.index, dtype="string")
                )

            case r"^Tới\s+\d+(?:\.\d+)*\s+triệu$":
                filtered_df["max_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:\.\d+)*")
                    .str[0]
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    min_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    salary_unit=pd.Series("VND", index=filtered_df.index, dtype="string")
                )

            case r"^Tới\s+\d+(?:,\d+)*\s+USD$":
                filtered_df["max_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:,\d+)*")
                    .str[0]
                    .str.replace(",", "", regex=False)
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    min_salary=pd.Series(pd.NA, index=filtered_df.index, dtype="Float64"),
                    salary_unit=pd.Series("USD", index=filtered_df.index, dtype="string")
                )

            case r"^\d+(?:\.\d+)*\s+-\s+\d+(?:\.\d+)*\s+triệu$":
                filtered_df["min_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:\.\d+)*")
                    .str[0]
                    .astype("Float64")
                )

                filtered_df["max_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:\.\d+)*")
                    .str[1]
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    salary_unit=pd.Series("VND", index=filtered_df.index, dtype="string")
                )

            case r"^\d+(?:,\d+)*\s+-\s+\d+(?:,\d+)*+\s+USD$":
                filtered_df["min_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:,\d+)*")
                    .str[0]
                    .str.replace(",", "", regex=False)
                    .astype("Float64")
                )

                filtered_df["max_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:,\d+)*")
                    .str[1]
                    .str.replace(",", "", regex=False)
                    .astype("Float64")
                )

                filtered_df = filtered_df.assign(
                    salary_unit=pd.Series("USD", index=filtered_df.index, dtype="string")
                )

        new_df.append(filtered_df)

    new_df = pd.concat(new_df, ignore_index=True)

    return new_df