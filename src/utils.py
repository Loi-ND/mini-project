import pandas as pd
from typing import List

def processing_salary_columns(df: pd.DataFrame) -> pd.DataFrame:
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

def processing_address_columns(df: pd.DataFrame) -> pd.DataFrame:

    def split_city_address_tuple(addresses: List) -> List:
        length = len(addresses)
        res = []
        for i in range(0, length // 2):
            res.append([addresses[i * 2], addresses[i * 2 + 1]])
        return res
    
    patterns = [
        r"^[\w\s]+$",
        r"^[\w\s]+(: [\w,\s]+)+$"
    ]

    new_df = []

    for pattern in patterns:
        mask = df['address'].str.match(pattern)
        filtered_df = df.loc[mask]

        match pattern:
            #  city và district
            case r"^[\w\s]+$":
                filtered_df = filtered_df.assign(
                    city=filtered_df['address'],
                    district=pd.Series("Unkonwn", index=filtered_df.index, dtype="string"),
                )

            case r"^[\w\s]+(: [\w,\s]+)+$":
                filtered_df = filtered_df.reset_index(names="id")
                addreses_df = filtered_df[["id", "address"]]

                addreses_df["splited_addresses"] = (
                    addreses_df['address']
                    .str
                    .findall(r"[\w,\s]+")
                    .apply(lambda x: [item.strip() for item in x])
                )

                addreses_df = addreses_df.drop(columns=["address"])

                addreses_df["splited_addresses"] = (
                    addreses_df["splited_addresses"]
                    .apply(split_city_address_tuple)
                )

                addreses_df = addreses_df.explode("splited_addresses", ignore_index=True)
                addreses_df[["city", "district"]] = pd.DataFrame(
                    addreses_df["splited_addresses"].tolist(),
                    index=addreses_df.index
                )
                addreses_df = addreses_df.drop(columns=["splited_addresses"])

                addreses_df['district'] = (
                    addreses_df["district"]
                    .str
                    .findall(r"[\w\s]+")
                )

                addreses_df = addreses_df.explode('district', ignore_index=True)

                filtered_df = filtered_df.join(
                    addreses_df,
                    on="id",
                    how="inner"
                )

                filtered_df = filtered_df.drop(columns=['id'])

        new_df.append(filtered_df)

    new_df = pd.concat(new_df, ignore_index=True)

    return new_df