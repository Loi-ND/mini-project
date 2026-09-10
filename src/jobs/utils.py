import pandas as pd
from typing import List
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import time

AIRFLOW_HOME=os.environ.get("AIRFLOW_HOME")
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
                    * 1000000
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
                    * 1000000
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
                    * 1000000
                )

                filtered_df["max_salary"] = (
                    filtered_df['salary']
                    .str
                    .findall(r"\d+(?:\.\d+)*")
                    .str[1]
                    .astype("Float64")
                    * 1000000
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
    new_df = new_df[
        new_df['max_salary'].isna()
        | (
            ((new_df['salary_unit'] == "USD") & (new_df['max_salary'] < 10000))
            | ((new_df['salary_unit'] == "VND") & (new_df['max_salary'] < 100000000))
        )
    ]

    return new_df

def processing_address_columns(df: pd.DataFrame) -> pd.DataFrame:

    def split_city_address_tuple(addresses: List) -> List:
        length = len(addresses)
        res = []

        for i in range(0, length // 2):
            res.append([
                addresses[i * 2],
                addresses[i * 2 + 1]
            ])

        return res

    patterns = [
        r"^[\w\s]+$",
        r"^[\w\s]+(: [\w,\s]+)+$"
    ]

    new_df = []

    for pattern in patterns:

        mask = df["address"].str.match(pattern)
        filtered_df = df.loc[mask].copy()

        match pattern:

            case r"^[\w\s]+$":

                filtered_df = filtered_df.assign(
                    city=filtered_df["address"],
                    district=pd.Series(
                        "Unknown",
                        index=filtered_df.index,
                        dtype="string"
                    ),
                )

            case r"^[\w\s]+(: [\w,\s]+)+$":

                filtered_df = filtered_df.reset_index(names="id")

                addreses_df = filtered_df[["id", "address"]].copy()

                addreses_df["splited_addresses"] = (
                    addreses_df["address"]
                    .str.findall(r"[\w,\s]+")
                    .apply(
                        lambda x: [
                            item.strip()
                            for item in x
                        ]
                    )
                )

                addreses_df = addreses_df.drop(
                    columns=["address"]
                )

                addreses_df["splited_addresses"] = (
                    addreses_df["splited_addresses"]
                    .apply(split_city_address_tuple)
                )

                addreses_df = addreses_df.explode(
                    "splited_addresses",
                    ignore_index=True
                )

                # Tách [city, district]
                city_district = pd.DataFrame(
                    addreses_df["splited_addresses"].tolist(),
                    index=addreses_df.index,
                    columns=["city", "district"]
                )

                addreses_df = pd.concat(
                    [
                        addreses_df.drop(
                            columns=["splited_addresses"]
                        ),
                        city_district
                    ],
                    axis=1
                )

                addreses_df["district"] = (
                    addreses_df["district"]
                    .str.findall(r"[\w\s]+")
                    .apply(
                        lambda x: [
                            item.strip()
                            for item in x
                        ]
                    )
                )

                addreses_df = addreses_df.explode(
                    "district",
                    ignore_index=True
                )

                filtered_df = filtered_df.merge(
                    addreses_df[["id", "city", "district"]], on="id", how="inner"
                )

                filtered_df = filtered_df.drop(
                    columns=["id"]
                )

        new_df.append(filtered_df)

    new_df = pd.concat(
        new_df,
        ignore_index=True
    )

    return new_df

def processing_job_categories(df: pd.DataFrame) -> pd.DataFrame:
    load_dotenv(
        os.path.join(
            AIRFLOW_HOME,
            "..",
            ".env"
        )
    )

    MODEL_API_KEY = os.environ.get("MODEL_API_KEY")

    elements = df['job_title'].to_list()

    client = genai.Client(
        api_key=MODEL_API_KEY
    )

    def process_batch(elements: List[str]) -> List[str]:

        prompt = f"""
        Bạn là hệ thống phân loại chức danh công việc.

        NHIỆM VỤ:
        Phân loại TỪNG job_title trong danh sách INPUT thành ĐÚNG MỘT job_category.

        ====================
        CATEGORY HỢP LỆ
        ====================

        [
            "Sales IT Phần mềm",
            "Quảng cáo/Sáng tạo",
            "Software Engineering",
            "IT Infrastructure and Operations",
            "Product Management",
            "Thiết kế Đồ hoạ/Giao diện/Trải nghiệm",
            "Công nghệ thông tin khác",
            "Software Testing",
            "Data Science",
            "IT Project Management"
        ]

        ====================
        QUY TẮC OUTPUT — BẮT BUỘC
        ====================

        1. INPUT có N job_title thì OUTPUT phải có CHÍNH XÁC N phần tử.

        2. Mỗi job_title trong INPUT phải tương ứng với ĐÚNG MỘT category trong OUTPUT.

        3. OUTPUT[i] phải là category của INPUT[i].

        4. Giữ nguyên tuyệt đối thứ tự của INPUT.

        5. Không được bỏ qua bất kỳ job_title nào.

        6. Không được gộp nhiều job_title thành một category.

        7. Không được thêm category không tương ứng với INPUT.

        8. Nếu job_title bị trùng, vẫn phải tạo category riêng cho TỪNG phần tử.

        9. Nếu job_title khó phân loại, vẫn phải chọn category phù hợp nhất.

        10. Không được trả về null.

        11. Không được trả về chuỗi rỗng.

        12. Không được trả về job_title.

        13. Không được trả về index.

        14. Không được trả về object.

        15. Không được trả về dictionary.

        16. Không được giải thích.

        17. Không được trả về markdown.

        18. Chỉ trả về JSON array gồm các category.

        19. Mỗi phần tử của OUTPUT phải là một giá trị CHÍNH XÁC trong CATEGORY HỢP LỆ.

        ====================
        ÁNH XẠ CATEGORY
        ====================

        Sales IT Phần mềm:
        Các vị trí bán sản phẩm hoặc dịch vụ IT/phần mềm:
        IT Sales, Software Sales, Technical Sales, Sales Engineer,
        Account Executive trong IT, Business Development trong IT/software.

        Quảng cáo/Sáng tạo:
        Advertising, Content, Copywriter, Creative,
        Creative Marketing, quảng cáo, sáng tạo nội dung,
        sản xuất nội dung.

        Software Engineering:
        Software Engineer, Software Developer, Developer, Programmer,
        Backend Developer, Frontend Developer, Full-stack Developer,
        Web Developer, Mobile Developer và các vị trí phát triển phần mềm.

        IT Infrastructure and Operations:
        System Administrator, System Engineer, Network Engineer,
        Cloud Engineer, Infrastructure Engineer, IT Operations,
        DevOps, SRE, DBA và các vị trí hạ tầng/vận hành hệ thống.

        Product Management:
        Product Manager, Product Owner, Product Specialist,
        Product Operations, Product Strategy và các vị trí quản lý/phát triển sản phẩm.

        Thiết kế Đồ hoạ/Giao diện/Trải nghiệm:
        UI Designer, UX Designer, UI/UX Designer,
        Product Designer, Graphic Designer, Visual Designer,
        Interaction Designer, Web Designer và các vị trí thiết kế.

        Công nghệ thông tin khác:
        IT Support, IT Specialist, IT Consultant, Cybersecurity,
        Information Security và các vị trí CNTT khác không thuộc rõ ràng
        các nhóm còn lại.

        Software Testing:
        Tester, QA, QC, Test Engineer, Automation Tester,
        Manual Tester, Software Tester và các vị trí kiểm thử phần mềm.

        Data Science:
        Data Scientist, Data Analyst, Data Engineer,
        Machine Learning Engineer, ML Engineer, AI Engineer,
        BI, Business Intelligence, Data Analytics và các vị trí
        liên quan đến dữ liệu, AI, ML.

        IT Project Management:
        IT Project Manager, Technical Project Manager,
        IT Program Manager, Project Coordinator trong IT
        và các vị trí quản lý dự án CNTT.

        ====================
        INPUT
        ====================

        job_titles = {elements}

        ====================
        CÁCH XỬ LÝ
        ====================

        Xử lý tuần tự từ job_title đầu tiên đến job_title cuối cùng.

        Với mỗi job_title:
        - Xác định đúng một category.
        - Ghi category đó vào OUTPUT ngay tại vị trí tương ứng.

        Ví dụ:

        INPUT:
        [
            "Backend Developer",
            "QA Engineer",
            "Product Manager"
        ]

        OUTPUT:
        [
            "Software Engineering",
            "Software Testing",
            "Product Management"
        ]

        Nếu INPUT có 206 phần tử:
        OUTPUT bắt buộc phải có 206 phần tử.

        Nếu INPUT có 100 phần tử:
        OUTPUT bắt buộc phải có 100 phần tử.

        Số lượng OUTPUT phải bằng tuyệt đối số lượng INPUT.

        ====================
        FINAL CHECK
        ====================

        Trước khi trả kết quả, tự kiểm tra:

        - Số lượng OUTPUT == số lượng INPUT.
        - Không có phần tử INPUT nào bị bỏ qua.
        - Không có phần tử OUTPUT nào dư.
        - Thứ tự OUTPUT khớp với thứ tự INPUT.
        - Tất cả OUTPUT đều thuộc CATEGORY HỢP LỆ.

        Nếu chưa thỏa mãn tất cả điều kiện trên, phải sửa kết quả
        trước khi trả về.

        ====================
        OUTPUT
        ====================

        CHỈ trả về JSON array category.

        KHÔNG trả về explanation.
        KHÔNG trả về markdown.
        KHÔNG trả về code block.
        KHÔNG trả về index.
        KHÔNG trả về job_title.
        KHÔNG trả về object.

        Chỉ trả về JSON array.
        """

        response = client.models.generate_content(
            model="models/gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[str],
            ),
        )

        result = json.loads(response.text)

        if len(result) != len(elements):
            raise ValueError(
                f"Số lượng input/output không khớp: "
                f"input={len(elements)}, output={len(result)}"
            )
        return result

    total = len(elements)

    batch_size = (total + 2) // 40

    batches = [
        elements[i:i + batch_size]
        for i in range(0, total, batch_size)
    ]

    print(f"Tổng số elements: {total}")
    print(f"Số request: {len(batches)}")
    all_results = []
    for i, batch in enumerate(batches, start=1):

        print(
            f"\nRequest {i}/{len(batches)} "
            f"- {len(batch)} elements"
        )

        result = process_batch(batch)

        all_results.extend(result)

        print(
            f"Request {i} hoàn thành: "
            f"{len(result)} results"
        )



    if len(all_results) != len(df):
        raise ValueError(
            f"Tổng input/output không khớp: "
            f"input={len(df)}, output={len(all_results)}"
        )

    df['job_category'] = all_results

    return df