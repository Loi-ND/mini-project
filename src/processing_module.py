from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from datetime import date
import os


BASE_URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?sort=new&type_keyword=1&disable_auto_detect_type_keyword=1&page=1&category_family=r257&saturday_status=0"

def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)
driver = create_driver()
driver.get(BASE_URL)
time.sleep(2)

job_items = driver.find_elements(
    by=By.CSS_SELECTOR,
    value="div.job-item-search-result"
)
job_item = job_items[0]

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

driver_detail = create_driver()
driver_detail.get(link_description_txt)

box_header_job = driver_detail.find_element(
    by=By.CSS_SELECTOR,
    value="div.box-header-job"
)
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


print(job_title_txt)
print(salary_txt)
print(time_txt)
print(created_date_txt)
print(link_description_txt)
print(company_txt)
print(address_text)

time.sleep(2)
driver.close()
driver_detail.close()