import pandas as pd
from utils import processing_salary_columns


def test_thoa_thuan():
    df = pd.DataFrame({
        "salary": ["Thoả thuận"]
    })

    result = processing_salary_columns(df)

    assert pd.isna(result.loc[0, "min_salary"])
    assert pd.isna(result.loc[0, "max_salary"])
    assert result.loc[0, "salary_unit"] == "Unknown"


def test_tren_vnd():
    df = pd.DataFrame({
        "salary": [
            "Trên 15 triệu",
            "Trên 1.3 triệu",
            "Trên 7.5 triệu"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "min_salary"] == 15
    assert result.loc[0, "salary_unit"] == "VND"

    assert result.loc[1, "min_salary"] == 1.3
    assert result.loc[1, "salary_unit"] == "VND"

    assert result.loc[2, "min_salary"] == 7.5
    assert result.loc[2, "salary_unit"] == "VND"


def test_toi_vnd():
    df = pd.DataFrame({
        "salary": [
            "Tới 30 triệu",
            "Tới 1.3 triệu",
            "Tới 7.5 triệu"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "max_salary"] == 30
    assert result.loc[0, "salary_unit"] == "VND"

    assert result.loc[1, "max_salary"] == 1.3
    assert result.loc[1, "salary_unit"] == "VND"


def test_tren_usd():
    df = pd.DataFrame({
        "salary": [
            "Trên 1,000 USD",
            "Trên 700 USD"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "min_salary"] == 1000
    assert result.loc[0, "salary_unit"] == "USD"

    assert result.loc[1, "min_salary"] == 700
    assert result.loc[1, "salary_unit"] == "USD"


def test_toi_usd():
    df = pd.DataFrame({
        "salary": [
            "Tới 1,500 USD",
            "Tới 2,500 USD"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "max_salary"] == 1500
    assert result.loc[0, "salary_unit"] == "USD"

    assert result.loc[1, "max_salary"] == 2500
    assert result.loc[1, "salary_unit"] == "USD"


def test_range_vnd():
    df = pd.DataFrame({
        "salary": [
            "15 - 25 triệu",
            "1.2 - 2 triệu",
            "7.5 - 14 triệu"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "min_salary"] == 15
    assert result.loc[0, "max_salary"] == 25
    assert result.loc[0, "salary_unit"] == "VND"

    assert result.loc[1, "min_salary"] == 1.2
    assert result.loc[1, "max_salary"] == 2
    assert result.loc[1, "salary_unit"] == "VND"


def test_range_usd():
    df = pd.DataFrame({
        "salary": [
            "600 - 1,500 USD",
            "1,000 - 1,500 USD"
        ]
    })

    result = processing_salary_columns(df)

    assert result.loc[0, "min_salary"] == 600
    assert result.loc[0, "max_salary"] == 1500
    assert result.loc[0, "salary_unit"] == "USD"

    assert result.loc[1, "min_salary"] == 1000
    assert result.loc[1, "max_salary"] == 1500
    assert result.loc[1, "salary_unit"] == "USD"