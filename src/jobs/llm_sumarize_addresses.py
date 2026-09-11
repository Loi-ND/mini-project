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
    Bạn là một hệ thống trích xuất và chuẩn hóa địa điểm làm việc từ dữ liệu tuyển dụng.

    ========================
    NGUYÊN TẮC QUAN TRỌNG NHẤT
    ==========================

    INPUT là một JSON array gồm N phần tử.

    OUTPUT BẮT BUỘC phải là một JSON array gồm CHÍNH XÁC N phần tử.

    Có quan hệ 1-1 tuyệt đối:

    INPUT[i] -> OUTPUT[i]

    Trong mọi trường hợp:

    * Không được bỏ sót bất kỳ input nào.
    * Không được tạo thêm output.
    * Không được gộp hai hoặc nhiều input thành một output.
    * Không được tách một input thành nhiều output.
    * Không được thay đổi thứ tự input.
    * Mỗi input phải tạo ra đúng một output string.
    * Nếu không tìm thấy địa điểm trong một input thì output tương ứng là "Không có thông tin".
    * KHÔNG được vì input giống nhau mà gộp chúng thành một phần tử.
    * Hai input giống hệt nhau vẫn phải tạo ra hai output riêng biệt.

    Ví dụ:

    INPUT:
    ["Hà Nội", "Hà Nội", "Đà Nẵng"]

    OUTPUT:
    ["Hà Nội", "Hà Nội", "Đà Nẵng"]

    Không được trả về:
    ["Hà Nội", "Đà Nẵng"]

    ========================
    QUY TRÌNH XỬ LÝ
    ===============

    Hãy xử lý từng input element độc lập theo index.

    Với mỗi INPUT[i]:

    1. Đọc toàn bộ chuỗi.
    2. Xác định TẤT CẢ địa điểm làm việc thực sự xuất hiện trong chuỗi.
    3. Không lấy thông tin không phải địa điểm.
    4. Chuẩn hóa từng địa điểm.
    5. Nếu có nhiều địa điểm trong cùng một input, giữ nguyên thứ tự xuất hiện.
    6. Tạo ĐÚNG MỘT output string cho INPUT[i].
    7. Sau khi xử lý toàn bộ input, kiểm tra lại số lượng output.

    ========================
    QUY TẮC TRÍCH XUẤT
    ==================

    Chỉ trích xuất địa điểm làm việc thực sự xuất hiện trong INPUT.

    Không được suy đoán địa điểm dựa trên:

    * Tên công ty.
    * Tên đường.
    * Tên dự án.
    * Tên tòa nhà.
    * Thông tin tuyển dụng.
    * Địa điểm thường gặp của công ty.
    * Kiến thức bên ngoài INPUT.

    Không được thêm tỉnh/thành phố, phường/xã hoặc khu vực nếu thông tin đó không xuất hiện hoặc không thể xác định trực tiếp từ INPUT.

    ========================
    QUY TẮC CHUẨN HÓA
    =================

    Mỗi địa điểm phải được chuẩn hóa theo cấu trúc:

    "Tỉnh/Thành phố: Phường/Xã/Khu vực"

    Ví dụ:

    "Hà Nội: Phường Ngọc Hà"

    "Hồ Chí Minh: Phường Tân Bình"

    Nếu INPUT chứa địa chỉ chi tiết:

    "Hà Nội: Số 122 đường Hoàng Quốc Việt, Phường Cầu Giấy (quận Cầu Giấy cũ)"

    OUTPUT:

    "Hà Nội: Phường Cầu Giấy"

    Loại bỏ:

    * Số nhà.
    * Số phòng.
    * Số tầng.
    * Tòa nhà.
    * Tên đường.
    * Khu dân cư.
    * Tên chung cư.
    * Địa chỉ chi tiết khác.

    Giữ lại:

    * Tỉnh/thành phố.
    * Phường.
    * Xã.
    * Thị trấn.
    * Khu vực tương ứng nếu INPUT thực sự cung cấp khu vực đó.

    ========================
    QUY TẮC NGOẶC
    =============

    Nếu thông tin trong ngoặc chỉ là tên quận/huyện cũ hoặc thông tin hành chính cũ thì loại bỏ.

    Ví dụ:

    "Phường Cầu Giấy (quận Cầu Giấy cũ)"

    -> "Phường Cầu Giấy"

    "Phường Đống Đa (quận Đống Đa cũ)"

    -> "Phường Đống Đa"

    Không được loại bỏ thông tin trong ngoặc nếu nó là một phần cần thiết để xác định địa điểm.

    ========================
    NHIỀU ĐỊA ĐIỂM TRONG MỘT INPUT
    ==============================

    Nếu một INPUT chứa nhiều địa điểm, phải giữ TẤT CẢ địa điểm theo đúng thứ tự xuất hiện.

    Ví dụ:

    INPUT:
    "- Hà Nội: Phường Ngọc Hà | - Hồ Chí Minh: Phường Tân Bình"

    OUTPUT:
    "Hà Nội: Phường Ngọc Hà: Hồ Chí Minh: Phường Tân Bình"

    Không được bỏ địa điểm thứ hai.

    Không được đổi thứ tự.

    Không được dùng ký tự "|".

    ========================
    QUY TẮC DẤU PHÂN CÁCH
    =====================

    Khi một INPUT có nhiều địa điểm:

    * Dùng ": " để phân cách giữa các địa điểm.
    * Không sử dụng "|".
    * Không sử dụng ";".
    * Không sử dụng newline.
    * Không tạo array con.
    * Tất cả các địa điểm của cùng một INPUT phải nằm trong MỘT JSON string.

    Ví dụ:

    ĐÚNG:
    "Hà Nội: Phường Ngọc Hà: Hồ Chí Minh: Phường Tân Bình"

    SAI:
    ["Hà Nội: Phường Ngọc Hà", "Hồ Chí Minh: Phường Tân Bình"]

    SAI:
    "Hà Nội: Phường Ngọc Hà | Hồ Chí Minh: Phường Tân Bình"

    ========================
    KHI KHÔNG CÓ ĐỊA ĐIỂM
    =====================

    Nếu INPUT không chứa thông tin địa điểm làm việc rõ ràng:

    OUTPUT tương ứng phải là:

    "Không có thông tin"

    Không được suy đoán.

    Ví dụ:

    INPUT:
    ["Lương thỏa thuận", "Full-time", "Hà Nội"]

    OUTPUT:
    ["Không có thông tin", "Không có thông tin", "Hà Nội"]

    ========================
    KIỂM TRA TÍNH CHÍNH XÁC
    =======================

    TRƯỚC KHI TRẢ OUTPUT, bắt buộc thực hiện kiểm tra nội bộ:

    Gọi:

    N = số phần tử INPUT
    M = số phần tử OUTPUT

    Điều kiện bắt buộc:

    M == N

    Ngoài ra phải kiểm tra:

    1. OUTPUT[i] tương ứng với INPUT[i].
    2. Không có INPUT nào bị bỏ qua.
    3. Không có OUTPUT nào được tạo thêm.
    4. Không có INPUT nào tạo ra nhiều OUTPUT.
    5. Không có nhiều INPUT bị gộp thành một OUTPUT.
    6. Thứ tự các INPUT được giữ nguyên.
    7. Mỗi OUTPUT là một JSON string.
    8. OUTPUT không chứa nested array.
    9. OUTPUT không chứa object.
    10. Không có ký tự "|" trong bất kỳ OUTPUT nào.
    11. Không có Markdown.
    12. Không có text ngoài JSON.

    Nếu phát hiện M != N, phải sửa OUTPUT trước khi trả về.

    TUYỆT ĐỐI KHÔNG được trả về kết quả nếu số lượng OUTPUT chưa bằng số lượng INPUT.

    ========================
    QUY TẮC JSON BẮT BUỘC
    =====================

    Output cuối cùng phải:

    * Là JSON array hợp lệ.
    * Có chính xác N phần tử.
    * Mỗi phần tử là một JSON string.
    * Không phải object.
    * Không phải nested array.
    * Không có Markdown.
    * Không có code fence.
    * Không có giải thích.
    * Không có text trước JSON.
    * Không có text sau JSON.
    * Bắt đầu bằng "[".
    * Kết thúc bằng "]".

    Ví dụ định dạng hợp lệ:

    ["Hà Nội: Phường Cầu Giấy", "Không có thông tin", "Đà Nẵng: Phường Hải Châu"]

    ========================
    INPUT
    =====

    {json.dumps(elements, ensure_ascii=False)}

    ========================
    OUTPUT
    ======

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