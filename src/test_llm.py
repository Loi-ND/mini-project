from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv("../.env")
MODEL_API_KEY = os.environ.get("MODEL_API_KEY")

elements = [
    """
    <div class="box-address">
        <h3>
            Địa điểm làm việc
            <span style="font-size: 14px; font-style: italic; font-weight: 400;">
                (đã được cập nhật theo Danh mục Hành chính mới - thêm quận/huyện cũ tương ứng để dễ dàng tra cứu)
            </span>
        </h3>
        <div>
            <div style="margin-bottom: 10px">
                - <strong>Hồ Chí Minh:</strong>
                Phòng 21.03, Tầng 21, Tòa nhà MB Sunny Tower 259 Trần Hưng Đạo,
                Phường Cầu Ông Lãnh (Quận 1 cũ)
            </div>
        </div>
    </div>
    """,

    """
    <div class="box-address">
        <h3>
            Địa điểm làm việc
            <span style="font-size: 14px; font-style: italic; font-weight: 400;">
                (đã được cập nhật theo Danh mục Hành chính mới - thêm quận/huyện cũ tương ứng để dễ dàng tra cứu)
            </span>
        </h3>
        <div>
            <div style="margin-bottom: 10px">
                - <strong>Hà Nội:</strong>
                Liễu Giai, Phường Ngọc Hà (quận Ba Đình cũ)
            </div>

            <div style="margin-bottom: 10px">
                - <strong>Hồ Chí Minh:</strong>
                Cộng Hòa, Phường Tân Bình (quận Tân Bình cũ)
            </div>
        </div>
    </div>
    """
]
prompt = f"""
Bạn là hệ thống trích xuất và chuẩn hóa địa điểm làm việc từ HTML.

Đầu vào là một JSON array gồm nhiều HTML element.

Nhiệm vụ:
- Xử lý từng HTML element độc lập.
- Trích xuất địa điểm làm việc.
- Chuẩn hóa địa điểm.
- Giữ nguyên thứ tự các element.
- Mỗi element input phải tương ứng đúng một element output.
- Không được gộp các element với nhau.
- Số lượng output phải bằng số lượng input.

Quy tắc:
1. Loại bỏ địa chỉ chi tiết như số phòng, tầng, tòa nhà, số nhà, tên đường.
2. Chỉ giữ thông tin tỉnh/thành phố và phường/xã/thị trấn hoặc khu vực tương ứng.
3. Loại bỏ thông tin quận/huyện cũ trong dấu ngoặc.
4. Không lặp lại tên thành phố trong phần địa điểm.
5. Nếu một element có nhiều thành phố, giữ tất cả theo đúng thứ tự xuất hiện.
6. Nếu không có thông tin địa điểm thì trả về "Không có thông tin".

Định dạng:
- Một thành phố:
  "Hồ Chí Minh: Phường Cầu Ông Lãnh"

- Nhiều địa điểm trong cùng thành phố:
  "Hà Nội: Phường Ngọc Hà"

- Nhiều thành phố:
  "Hà Nội: Phường Ngọc Hà: Hồ Chí Minh: Phường Tân Bình"

INPUT:
{json.dumps(elements, ensure_ascii=False)}

OUTPUT:
Chỉ trả về JSON array hợp lệ.
Không Markdown.
Không code fence.
Không giải thích.
Không thêm text trước hoặc sau JSON.
"""

client = genai.Client(
    api_key=MODEL_API_KEY
)

response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents=prompt
)

print(response.text)