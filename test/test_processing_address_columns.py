import pandas as pd
from pandas.testing import assert_frame_equal
from utils import processing_address_columns


def test_address_only_city():
    df = pd.DataFrame({
        "address": [
            "Hà Nội",
            "Đà Nẵng",
        ],
    })

    result = processing_address_columns(df)

    expected = pd.DataFrame({
        "address": [
            "Hà Nội",
            "Đà Nẵng",
        ],
        "city": [
            "Hà Nội",
            "Đà Nẵng",
        ],
        "district": [
            "Unknown",
            "Unknown",
        ],
    })

    assert_frame_equal(
        result.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_address_city_one_district():
    df = pd.DataFrame({
        "address": [
            "Hà Nội: Cầu Giấy",
            "Đà Nẵng: Hải Châu",
        ],
    })

    result = processing_address_columns(df)

    expected = pd.DataFrame({
        "address": [
            "Hà Nội: Cầu Giấy",
            "Đà Nẵng: Hải Châu",
        ],
        "city": [
            "Hà Nội",
            "Đà Nẵng",
        ],
        "district": [
            "Cầu Giấy",
            "Hải Châu",
        ],
    })

    assert_frame_equal(
        result.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_address_city_multiple_districts():
    df = pd.DataFrame({
        "address": [
            "Hà Nội: Cầu Giấy, Ba Đình",
        ],
    })

    result = processing_address_columns(df)

    expected = pd.DataFrame({
        "address": [
            "Hà Nội: Cầu Giấy, Ba Đình",
            "Hà Nội: Cầu Giấy, Ba Đình",
        ],
        "city": [
            "Hà Nội",
            "Hà Nội",
        ],
        "district": [
            "Cầu Giấy",
            "Ba Đình",
        ],
    })

    assert_frame_equal(
        result.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_address_multiple_city_districts():
    df = pd.DataFrame({
        "address": [
            "Hà Nội",
            "Hà Nội: Cầu Giấy, Ba Đình",
            "Hải Dương: TP Hải Dương, Thanh Hà",
        ],
    })

    result = processing_address_columns(df)

    expected = pd.DataFrame({
        "address": [
            "Hà Nội",
            "Hà Nội: Cầu Giấy, Ba Đình",
            "Hà Nội: Cầu Giấy, Ba Đình",
            "Hải Dương: TP Hải Dương, Thanh Hà",
            "Hải Dương: TP Hải Dương, Thanh Hà",
        ],
        "city": [
            "Hà Nội",
            "Hà Nội",
            "Hà Nội",
            "Hải Dương",
            "Hải Dương",
        ],
        "district": [
            "Unknown",
            "Cầu Giấy",
            "Ba Đình",
            "TP Hải Dương",
            "Thanh Hà",
        ],
    })

    assert_frame_equal(
        result.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
    )