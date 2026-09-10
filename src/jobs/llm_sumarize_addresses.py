# datetime.today().date().strftime("%Y-%m-%d")
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import pandas as pd
import time

AIRFLOW_HOME=os.environ.get("AIRFLOW_HOME")
def merge_json_files(folder_path):
    folder = Path(folder_path)
    all_data = []

    for file_path in folder.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            all_data.extend(data)
        else:
            print(f"Bỏ qua {file_path.name}: JSON không phải list")

    return all_data

data: List[Dict] = merge_json_files(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        f"data/{datetime.today().date().strftime("%Y-%m-%d")}"
    )
)

load_dotenv(os.path.join(AIRFLOW_HOME, "..",".env"))

MODEL_API_KEY = os.environ.get("MODEL_API_KEY")

elements = [item.get("address") for item in data]

client = genai.Client(
    api_key=MODEL_API_KEY
)

def process_batch(elements):

    prompt = f"""
Bạn là hệ thống trích xuất và chuẩn hóa địa điểm làm việc.

ĐẦU VÀO:
Là một JSON array gồm nhiều chuỗi địa điểm làm việc.

NHIỆM VỤ:
- Xử lý từng element input độc lập.
- Trích xuất tất cả địa điểm làm việc xuất hiện trong từng element.
- Chuẩn hóa địa điểm theo các quy tắc bên dưới.
- Giữ nguyên thứ tự các element input.
- Mỗi element input phải tương ứng với đúng một element output.
- Không được gộp các element input với nhau.
- Số lượng phần tử output phải bằng chính xác số lượng phần tử input.

QUY TẮC CHUẨN HÓA:

1. Loại bỏ các thông tin địa chỉ chi tiết:
   - Số nhà
   - Số phòng
   - Tầng
   - Tòa nhà
   - Tên đường
   - Khu dân cư
   - Các thông tin địa chỉ chi tiết khác.

2. Chỉ giữ:
   - Tên tỉnh/thành phố.
   - Tên phường/xã/thị trấn hoặc khu vực tương ứng.

3. Loại bỏ thông tin quận/huyện cũ trong dấu ngoặc.

4. Không tự suy đoán hoặc thêm địa điểm không xuất hiện trong input.

5. Nếu một element chỉ có một địa điểm:
   "Thành phố: Phường/Xã/Khu vực"

6. Nếu một element có nhiều địa điểm:
   Nối các địa điểm bằng dấu ":".

   Ví dụ:
   Input:
   "- Hà Nội: Phường Ngọc Hà | - Hồ Chí Minh: Phường Tân Bình"

   Output:
   "Hà Nội: Phường Ngọc Hà: Hồ Chí Minh: Phường Tân Bình"

7. Không sử dụng ký tự "|" trong output.

8. Mỗi thành phố phải đi kèm với phường/xã/khu vực tương ứng.

9. Nếu không có thông tin địa điểm:
   "Không có thông tin"

10. Không được thay đổi thứ tự địa điểm xuất hiện trong input.

QUY TẮC JSON BẮT BUỘC:

- Output phải là một JSON array hợp lệ.
- Mỗi phần tử của array phải là một JSON string.
- Số lượng phần tử output phải bằng chính xác số lượng phần tử input.
- Không được trả về object.
- Không được trả về nested array.
- Không được thêm Markdown.
- Không được dùng code fence.
- Không được thêm giải thích.
- Không được thêm text trước JSON.
- Không được thêm text sau JSON.
- Output phải bắt đầu bằng "[" và kết thúc bằng "]".
- Phải đảm bảo số lượng phần tử của output

INPUT:
{json.dumps(elements, ensure_ascii=False)}

OUTPUT:
"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[str],
        ),
    )

    result = json.loads(response.text)

    # Kiểm tra số lượng
    if len(result) != len(elements):
        raise ValueError(
            f"Số lượng input/output không khớp: "
            f"input={len(elements)}, output={len(result)}"
        )

    return result

total = len(elements)

batch_size = (total + 2) // 10

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

    time.sleep(4)


if len(all_results) != len(data):
    raise ValueError(
        f"Tổng input/output không khớp: "
        f"input={len(data)}, output={len(all_results)}"
    )


for item, address in zip(data, all_results):
    item["address"] = address


data_df = pd.DataFrame(data)

data_df.to_csv(
    os.path.join(
        AIRFLOW_HOME,
        "..",
        "data/data.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)