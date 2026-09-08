from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import json
from pprint import pprint
import time
from datetime import datetime
import random
import os

BASE_URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257"

def set_url(page: int):
    return f"https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?sort=new&type_keyword=1&disable_auto_detect_type_keyword=1&page={page}&category_family=r257&saturday_status=0"

def create_driver():
    options = Options()

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
    options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def random_scroll(driver):
    total_height = driver.execute_script(
        "return document.body.scrollHeight"
    )

    current_position = 0

    while current_position < total_height:
        step = random.randint(300, 700)
        current_position += step

        driver.execute_script(
            "window.scrollTo(0, arguments[0]);",
            current_position
        )

        time.sleep(random.uniform(2, 5))

        total_height = driver.execute_script(
            "return document.body.scrollHeight"
        )
    time.sleep(random.uniform(10, 20))

def processing_job_item(job_item: WebElement):
    company_txt = job_item.find_element(
        by=By.CSS_SELECTOR,
        value="span.company-name"
    ).text

    job_title_txt = job_item.find_element(
        by=By.CSS_SELECTOR,
        value="div.title-block > div > h3.title > a > span:nth-child(1)"
    ).text

    link_description_txt = job_item.find_element(
        by=By.CSS_SELECTOR,
        value="div.title-block > div > h3.title > a"
    ).get_attribute("href")
    box_header_job = None

    while box_header_job is None:
        driver_detail = None

        try:
            driver_detail = create_driver()

            driver_detail.get(link_description_txt)

            box_header_job = WebDriverWait(
                driver_detail, 
                10
            ).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.box-header-job")
                )
            )
        except TimeoutException:
            print(
                f"Timeout khi xử lý: {job_title_txt}"
            )

            print("Đợi 60 giây rồi thử lại...")

            if driver_detail:
                try:
                    driver_detail.quit()
                except:
                    pass

            time.sleep(180)

            print("Thử lại...")

        except Exception as e:
            print(
                f"Lỗi khác khi xử lý {job_title_txt}: {e}"
            )

            if driver_detail:
                try:
                    driver_detail.quit()
                except:
                    pass

            time.sleep(60)

    salary_txt = box_header_job.find_element(
        by=By.CSS_SELECTOR,
        value="span.box-header-job__salary--title"
    ).text

    items = box_header_job.find_elements(
        By.CSS_SELECTOR,
        "div.box-header-job-list-info__item"
    )

    last_item = items[-1]

    application_deadline = last_item.find_element(
        By.CSS_SELECTOR,
        "div.list-info__content__desc"
    ).text.strip()

    deadline = datetime.strptime(
        application_deadline.strip(),
        "%d/%m/%Y"
    ).date()

    today = datetime.today().date()
    created_date_txt = today.strftime("%Y-%m-%d")
    days_left = (deadline - today).days
    time_txt = f"Còn {days_left} ngày để ứng tuyển"

    box_job_information_detail = driver_detail.find_element(
        by=By.CSS_SELECTOR,
        value="div.box-job-information-detail"
    )
    address_and_application_time = box_job_information_detail.find_element(
        by=By.CSS_SELECTOR,
        value=".box-job-information-detail-item.box-job-information-address-and-time"
    )
    addresses = address_and_application_time.find_elements(
        by=By.CSS_SELECTOR,
        value="div.box-job-information-address-and-time-list__item--content"
    )[0]
    items = addresses.find_elements(By.CSS_SELECTOR, "li")

    address_text = " | ".join(item.text.strip() for item in items)
    random_scroll(driver_detail)
    driver_detail.close()
    print(company_txt)
    print(address_text)
    return {
        "created_date": created_date_txt,
        "job_title": job_title_txt,
        "company": company_txt,
        "salary": salary_txt,
        "address": address_text,
        "time": time_txt,
        "link_description": link_description_txt
    }

def is_cloudflare_page(driver):
    title = driver.title.lower()
    html = driver.page_source.lower()

    indicators = [
        "attention required",
        "cloudflare",
        "you have been blocked",
        "access denied",
        "sorry, you have been blocked",
        "cf-chl-",
    ]

    for indicator in indicators:
        if indicator in title or indicator in html:
            print(f"[Cloudflare detected] Indicator: {indicator}")
            return True

    return False

driver = create_driver()

try:
    driver.get(f"{BASE_URL}?page=1")
    time.sleep(1)

    if is_cloudflare_page(driver):
        raise RuntimeError("Cloudflare block")

    pagination = driver.find_element(
        By.ID,
        "job-listing-paginate-text"
    )

    pagination_text = pagination.text

    total_pages = int(
        pagination_text
        .split("/")[1]
        .strip()
        .split()[0]
    )

    print("Pagination:", pagination_text)
    print("Total pages:", total_pages)

finally:
    driver.quit()

for page in range(1, total_pages + 1):
    result = []
    print()
    print("=" * 50)
    print(f"Processing page {page}/{total_pages}")
    print("=" * 50)

    driver = create_driver()

    try:
        url = set_url(page=page)
        print("URL:", url)
        driver.get(url)

        job_items = driver.find_elements(
            by=By.CSS_SELECTOR,
            value="div.job-item-search-result"
        )

        for i, job_item in enumerate(job_items):
            print(f"{page} - {i}")
            time.sleep(random.uniform(10, 20))
            result.append(processing_job_item(job_item))

        with open(f"../data/res_{page}.json", "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=4)
        time.sleep(0.5)

        print("Current URL:", driver.current_url)
        print("Title:", driver.title)

        

    finally:
        driver.quit()

        print(f"Chrome closed after page {page}")

    time.sleep(1)
print("\nDone.")