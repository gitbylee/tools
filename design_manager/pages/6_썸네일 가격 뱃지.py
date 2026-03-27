import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import zipfile

st.set_page_config(page_title="썸네일 가격 딱지 생성기", layout="centered")

# =========================
# 고정값
# =========================
BADGE_BG = (255, 84, 42, 217)
TEXT_COLOR = (255, 255, 255, 255)
RADIUS = 6
GAP = 6

SQ_SIZE = (600, 600)
SQ_TOP = 20
SQ_RIGHT = 22
SQ_BADGE_HEIGHT = 48
SQ_PADDING_X = 15
SQ_FONT_SIZE = 28

HR_SIZE = (640, 338)
HR_TOP = 12
HR_RIGHT = 12
HR_BADGE_HEIGHT = 38
HR_PADDING_X = 15
HR_FONT_SIZE = 22


# =========================
# 폰트
# =========================
def load_font(size):
    font_path_candidates = [
        "Pretendard-SemiBold.ttf",
        "./Pretendard-SemiBold.ttf",
        "./fonts/Pretendard-SemiBold.ttf",
    ]

    for path in font_path_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    raise FileNotFoundError(
        "Pretendard-SemiBold.ttf 파일을 app.py와 같은 폴더 또는 fonts 폴더에 넣어주세요."
    )


# =========================
# 틸드 이미지 로드
# =========================
def load_tilde(thumb_type):
    tilde_path_candidates = [
        "tilde.png",
        "./tilde.png",
        "./assets/tilde.png",
    ]

    tilde_path = None
    for path in tilde_path_candidates:
        if os.path.exists(path):
            tilde_path = path
            break

    if tilde_path is None:
        raise FileNotFoundError(
            "tilde.png 파일을 app.py와 같은 폴더 또는 assets 폴더에 넣어주세요."
        )

    img = Image.open(tilde_path).convert("RGBA")

    if thumb_type == "square":
        return img.resize((12, 5), Image.LANCZOS)
    else:
        return img.resize((9, 4), Image.LANCZOS)


# =========================
# 유틸
# =========================
def format_price(price):
    return f"{price:,}"


def measure_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def save_jpg(img):
    buffer = io.BytesIO()

    img.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=100,
        subsampling=0,
        optimize=True
    )

    buffer.seek(0)
    return buffer.getvalue()


def detect_type(img):
    if img.size == SQ_SIZE:
        return "square"

    if img.size == HR_SIZE:
        return "horizontal"

    return None


# =========================
# 딱지 생성
# =========================
def add_badge(base, price, thumb_type):
    base = base.convert("RGBA")
    w, h = base.size

    if thumb_type == "square":
        top = SQ_TOP
        right = SQ_RIGHT
        badge_height = SQ_BADGE_HEIGHT
        padding_x = SQ_PADDING_X
        font_size = SQ_FONT_SIZE
    else:
        top = HR_TOP
        right = HR_RIGHT
        badge_height = HR_BADGE_HEIGHT
        padding_x = HR_PADDING_X
        font_size = HR_FONT_SIZE

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = load_font(font_size)
    tilde = load_tilde(thumb_type)

    part1 = "1팩"
    part2 = f"{format_price(price)}원"

    w1, h1 = measure_text(draw, part1, font)
    w2, h2 = measure_text(draw, part2, font)
    w3, h3 = tilde.size

    badge_w = w1 + GAP + w2 + GAP + w3 + padding_x * 2

    x = w - badge_w - right
    y = top

    draw.rounded_rectangle(
        [x, y, x + badge_w, y + badge_height],
        radius=RADIUS,
        fill=BADGE_BG
    )

    current_x = x + padding_x

    y1 = y + (badge_height - h1) / 2 - 2
    y2 = y + (badge_height - h2) / 2 - 2
    y3 = int(y + (badge_height - h3) / 2)

    draw.text((current_x, y1), part1, font=font, fill=TEXT_COLOR)
    current_x += w1 + GAP

    draw.text((current_x, y2), part2, font=font, fill=TEXT_COLOR)
    current_x += w2 + GAP

    overlay.alpha_composite(tilde, (int(current_x), y3))

    return Image.alpha_composite(base, overlay)


# =========================
# ZIP 생성
# =========================
def make_zip(results):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for filename, img in results:
            z.writestr(filename, save_jpg(img))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# =========================
# 사이드바 가이드
# =========================
with st.sidebar:
    st.markdown("### home")
    st.markdown("**썸네일 가격 배지**")

    st.divider()

    st.markdown("## 📌 툴 사용 방법")
    st.markdown("### 썸네일 가격 배지")

    st.markdown(
        """
1. **썸네일 이미지를 업로드**합니다.  
   - 600×600 → 정사각형  
   - 640×338 → 가로형  

2. **가격을 입력**합니다.  
   - 예: `1520`

3. **딱지 생성** 버튼을 누릅니다.

4. 업로드한 이미지 크기를 자동으로 인식해서  
   **가격 딱지**를 붙입니다.

5. 결과물을 **ZIP 파일로 한 번에 다운로드**합니다.
"""
    )

    st.divider()

    st.markdown("### 안내")
    st.markdown(
        """
- 지원 파일 형식: **png, jpg, jpeg, webp**
- 지원 크기가 아니면 자동 제외됩니다.
- 결과물은 **JPG**로 저장됩니다.
"""
    )

    st.divider()
    st.caption("문제 발생 시 디자인팀에 문의 바랍니다.")



# =========================
# UI
# =========================
st.title("썸네일 가격 딱지 생성기")

files = st.file_uploader(
    "썸네일 업로드 (600×600 / 640×338)",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

price_input = st.text_input(
    "가격 입력",
    placeholder="가격을 입력하세요 (숫자만 입력)"
)

if price_input.isdigit():
    price = int(price_input)
else:
    price = 0

if st.button("딱지 생성"):
    try:
        if not files:
            st.warning("썸네일 파일을 업로드해주세요.")
        elif price <= 0:
            st.warning("가격을 입력해주세요.")
        else:
            results = []
            invalid = []

            for f in files:
                img = Image.open(f)
                thumb_type = detect_type(img)

                if not thumb_type:
                    invalid.append(f"{f.name} ({img.size[0]}×{img.size[1]})")
                    continue

                result = add_badge(img, price, thumb_type)

                base_name = os.path.splitext(f.name)[0]

                if thumb_type == "square":
                    filename = f"pc(600x600)_{base_name}.jpg"
                else:
                    filename = f"mo(640x338)_{base_name}.jpg"

                results.append((filename, result))

            if invalid:
                st.warning(
                    "지원하지 않는 사이즈의 파일이 있어 제외했어요:\n\n- " + "\n- ".join(invalid)
                )

            if results:
                for name, img in results:
                    st.image(img, caption=name)

                zip_data = make_zip(results)

                st.download_button(
                    "ZIP 다운로드",
                    zip_data,
                    "thumbnails.zip",
                    mime="application/zip"
                )
            else:
                st.error("처리 가능한 이미지가 없습니다. 600×600 또는 640×338 파일만 업로드해주세요.")

    except FileNotFoundError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")