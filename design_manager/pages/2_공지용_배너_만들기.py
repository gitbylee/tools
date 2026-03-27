import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- [1] 디자인 시스템 고정값 설정 ---
CANVAS_WIDTH = 860
BG_COLOR = "#F7F7F7"
TEXT_DEFAULT_COLOR = "#000000"
TEXT_HIGHLIGHT_COLOR = "#DD3C2F"

def parse_and_draw_centered(draw, y_pos, text_line, font, is_title=False):
    """$ 기호를 파싱하여 다중 색상 텍스트를 중앙 정렬로 그리는 함수"""
    if not text_line.strip():
        return
        
    # $ 기호 기준으로 텍스트 분할
    parts = text_line.split('$')
    segments = []
    total_width = 0
    
    # 텍스트 조각별 속성 할당 및 전체 길이 계산
    for i, part in enumerate(parts):
        if not part:
            continue
        # $로 감싸진 부분(인덱스가 홀수인 경우)은 강조 컬러 적용
        color = TEXT_HIGHLIGHT_COLOR if i % 2 == 1 else TEXT_DEFAULT_COLOR
        
        # Pillow 10.0 이상에서는 getlength 활용 (구버전 호환을 위해 textbbox 사용)
        bbox = draw.textbbox((0, 0), part, font=font)
        part_width = bbox[2] - bbox[0]
        
        segments.append({'text': part, 'color': color, 'width': part_width})
        total_width += part_width

    # 중앙 정렬을 위한 시작 X 좌표 계산
    current_x = (CANVAS_WIDTH - total_width) / 2
    
    # 텍스트 조각들을 순서대로 렌더링
    for seg in segments:
        # 타이틀(Bold)과 본문(Medium)의 폰트 상하 여백 차이를 보정하기 위한 미세 조정
        y_offset = -4 if is_title else -2
        draw.text((current_x, y_pos + y_offset), seg['text'], font=font, fill=seg['color'])
        current_x += seg['width']

def generate_notice_banner(title_text, body_text):
    try:
        font_title = ImageFont.truetype("Pretendard-Bold.ttf", 32)
        font_body = ImageFont.truetype("Pretendard-Medium.ttf", 28)
    except IOError:
        st.error("폰트 파일(.ttf)을 찾을 수 없습니다.")
        return None

    # 수동 줄바꿈(Enter) 기준 텍스트 리스트화
    title_lines = [line for line in title_text.split('\n') if line.strip()] if title_text else []
    body_lines = [line for line in body_text.split('\n') if line.strip()] if body_text else []

    if not title_lines and not body_lines:
        return None

    # 높이 고정값
    TITLE_LINE_HEIGHT = 46 
    BODY_LINE_HEIGHT = 38  # 피그마 가이드 수치 적용
    GAP = 18               # 타이틀과 본문 사이 간격

    # 전체 캔버스 높이 동적 계산
    total_height = 30 # 상단 여백
    if title_lines:
        total_height += len(title_lines) * TITLE_LINE_HEIGHT
    if title_lines and body_lines:
        total_height += GAP
    if body_lines:
        total_height += len(body_lines) * BODY_LINE_HEIGHT
    total_height += 30 # 하단 여백

    # 캔버스 생성
    img = Image.new('RGB', (CANVAS_WIDTH, total_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    current_y = 30
    
    # 타이틀 렌더링
    if title_lines:
        for line in title_lines:
            parse_and_draw_centered(draw, current_y, line, font_title, is_title=True)
            current_y += TITLE_LINE_HEIGHT
            
    # 타이틀과 본문 사이 간격 추가
    if title_lines and body_lines:
        current_y += GAP
        
    # 본문 렌더링
    if body_lines:
        for line in body_lines:
            parse_and_draw_centered(draw, current_y, line, font_body, is_title=False)
            current_y += BODY_LINE_HEIGHT

    return img

# --- [3] 기획자용 웹 UI ---
st.set_page_config(page_title="공지용 배너 만들기", layout="wide")

with st.sidebar:
    st.title("📌 공지 배너 가이드")
    
    st.markdown("### 🎨 색상 강조 방법")
    st.write("텍스트 입력 시 강조하고 싶은 붉은색 글씨 양옆에 **`$`** 기호를 붙여주세요.")
    st.info("**입력 예시**\n\n재고 상황에 따라 `$기존 제품과 리뉴얼 제품이 함께 출고$`될 수 있으니")
    
    st.markdown("### ⌨️ 줄바꿈 규칙")
    st.write("가독성을 위해 **Enter 키**를 눌러 직접 원하는 위치에서 줄을 바꿔주세요.")
    st.divider()
    
    st.caption("가이드 문제 발생 시 디자인팀에 문의 바랍니다.")

st.title("공지용 배너 자동 생성기")

with st.form("notice_banner_form"):
    st.markdown("**타이틀 (선택형)**")
    title_input = st.text_area(
        "title",
        placeholder="예:\n[ 케이준 & 버터갈릭 맛 리뉴얼 안내 ]",
        label_visibility="collapsed",
        height=68
    )
    
    st.markdown("**본문 (선택형)**")
    body_input = st.text_area(
        "body",
        placeholder="예:\n더 맛있는 제품 제공을 위해 제품이 리뉴얼되었습니다.\n재고 상황에 따라 $기존 제품과 리뉴얼 제품이 함께 출고$될 수 있으니\n주문 전 참고 부탁드립니다.",
        label_visibility="collapsed",
        height=150
    )
    
    st.write("")
    submitted = st.form_submit_button("배너 생성하기", use_container_width=True)

if submitted:
    if not title_input.strip() and not body_input.strip():
        st.warning("타이틀이나 본문 중 하나 이상을 입력해주세요.")
    else:
        result_img = generate_notice_banner(title_input, body_input)
        
        if result_img:
            st.subheader("미리보기")
            st.image(result_img, use_container_width=False)
            
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="배너 다운로드",
                data=byte_im,
                file_name="notice_banner.png",
                mime="image/png",
                use_container_width=True
            )