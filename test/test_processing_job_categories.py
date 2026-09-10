import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from jobs.utils import processing_job_categories


def test_software_development():
    df = pd.DataFrame({
        "job_title": [
            "Java Developer",
            "Python Developer",
            "Backend Developer",
            "Frontend Developer",
            "React Developer",
            "Flutter Developer",
            "Android Developer",
            "Software Developer",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Java Developer",
            "Python Developer",
            "Backend Developer",
            "Frontend Developer",
            "React Developer",
            "Flutter Developer",
            "Android Developer",
            "Software Developer",
        ],
        "job_category": [
            "Software Development",
            "Software Development",
            "Software Development",
            "Software Development",
            "Software Development",
            "Software Development",
            "Software Development",
            "Software Development",
        ]
    })

    assert_frame_equal(result, expected)


def test_business_analyst_product():
    df = pd.DataFrame({
        "job_title": [
            "Business Analyst",
            "Product Manager",
            "Product Owner",
            "Project Manager",
            "Scrum Master",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Business Analyst",
            "Product Manager",
            "Product Owner",
            "Project Manager",
            "Scrum Master",
        ],
        "job_category": [
            "Business Analyst & Product",
            "Business Analyst & Product",
            "Business Analyst & Product",
            "Business Analyst & Product",
            "Business Analyst & Product",
        ]
    })

    assert_frame_equal(result, expected)


def test_testing_qa():
    df = pd.DataFrame({
        "job_title": [
            "Tester",
            "QA Engineer",
            "QC Engineer",
            "Kiểm thử phần mềm",
            "Automation Tester",
            "Manual Test Engineer",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Tester",
            "QA Engineer",
            "QC Engineer",
            "Kiểm thử phần mềm",
            "Automation Tester",
            "Manual Test Engineer",
        ],
        "job_category": [
            "Testing & QA",
            "Testing & QA",
            "Testing & QA",
            "Testing & QA",
            "Testing & QA",
            "Testing & QA",
        ]
    })

    assert_frame_equal(result, expected)


def test_data_ai():
    df = pd.DataFrame({
        "job_title": [
            "Data Engineer",
            "Data Analyst",
            "AI Engineer",
            "Machine Learning Engineer",
            "Big Data Engineer",
            "Database Administrator",
            "Computer Vision Engineer",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Data Engineer",
            "Data Analyst",
            "AI Engineer",
            "Machine Learning Engineer",
            "Big Data Engineer",
            "Database Administrator",
            "Computer Vision Engineer",
        ],
        "job_category": [
            "Data & AI",
            "Data & AI",
            "Data & AI",
            "Data & AI",
            "Data & AI",
            "Data & AI",
            "Data & AI",
        ]
    })

    assert_frame_equal(result, expected)


def test_devops_system():
    df = pd.DataFrame({
        "job_title": [
            "DevOps Engineer",
            "SRE Engineer",
            "System Administrator",
            "Network Engineer",
            "Cloud Engineer",
            "AWS Engineer",
            "Azure Engineer",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "DevOps Engineer",
            "SRE Engineer",
            "System Administrator",
            "Network Engineer",
            "Cloud Engineer",
            "AWS Engineer",
            "Azure Engineer",
        ],
        "job_category": [
            "DevOps & System",
            "DevOps & System",
            "DevOps & System",
            "DevOps & System",
            "DevOps & System",
            "DevOps & System",
            "DevOps & System",
        ]
    })

    assert_frame_equal(result, expected)


def test_embedded_iot():
    df = pd.DataFrame({
        "job_title": [
            "Embedded Engineer",
            "IoT Engineer",
            "Firmware Engineer",
            "Kỹ sư nhúng",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Embedded Engineer",
            "IoT Engineer",
            "Firmware Engineer",
            "Kỹ sư nhúng",
        ],
        "job_category": [
            "Embedded & IoT",
            "Embedded & IoT",
            "Embedded & IoT",
            "Embedded & IoT",
        ]
    })

    assert_frame_equal(result, expected)


def test_security():
    df = pd.DataFrame({
        "job_title": [
            "Security Engineer",
            "Pentest Engineer",
            "SOC Analyst",
            "Chuyên viên bảo mật",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Security Engineer",
            "Pentest Engineer",
            "SOC Analyst",
            "Chuyên viên bảo mật",
        ],
        "job_category": [
            "Security",
            "Security",
            "Security",
            "Security",
        ]
    })

    assert_frame_equal(result, expected)


def test_unknown_job():
    df = pd.DataFrame({
        "job_title": [
            "Graphic Designer",
            "Accountant",
            "Sales Manager",
            "Marketing Specialist",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "Graphic Designer",
            "Accountant",
            "Sales Manager",
            "Marketing Specialist",
        ],
        "job_category": [
            "Unknown",
            "Unknown",
            "Unknown",
            "Unknown",
        ]
    })

    assert_frame_equal(result, expected)


def test_non_string_job_title():
    df = pd.DataFrame({
        "job_title": [
            None,
            np.nan,
            123,
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            None,
            np.nan,
            123,
        ],
        "job_category": [
            "Khác",
            "Khác",
            "Khác",
        ]
    })

    assert_frame_equal(result, expected)


def test_case_insensitive():
    df = pd.DataFrame({
        "job_title": [
            "JAVA DEVELOPER",
            "PYTHON DEVELOPER",
            "DATA ENGINEER",
            "DEVOPS ENGINEER",
        ]
    })

    result = processing_job_categories(df)

    expected = pd.DataFrame({
        "job_title": [
            "JAVA DEVELOPER",
            "PYTHON DEVELOPER",
            "DATA ENGINEER",
            "DEVOPS ENGINEER",
        ],
        "job_category": [
            "Software Development",
            "Software Development",
            "Data & AI",
            "DevOps & System",
        ]
    })

    assert_frame_equal(result, expected)