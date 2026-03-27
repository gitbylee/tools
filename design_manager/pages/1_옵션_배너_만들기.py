import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- [1] 디자인 시스템 고정값 설정 ---
CANVAS_WIDTH = 860
PADDING_X = 50
BADGE_COLOR = "#ff7b00"
DIVIDER_COLOR = "#e6e6e6"
TEXT_COLOR = "#000000"
MAX_TEXT_WIDTH = 690 

def draw_badge_aa(img, x, y, w, h, radius, color, text, font):
    scale = 3 
    hr_w, hr_h = w * scale, h * scale
    
    badge_hr = Image.new('RGBA', (hr_w, hr_h), (255, 255, 255, 0))
    draw_hr = ImageDraw.Draw(badge_hr)
    draw_hr.rounded_rectangle([(0, 0), (hr_w, hr_h)], radius=radius * scale, fill=color)
    
    badge_resized = badge_hr.resize((w, h), resample=Image.Resampling.LANCZOS)
    img.paste(badge_resized, (int(x), int(y)), badge_resized)
    
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    tx = x + (w - text_w) / 2 - bbox[0]
    ty = y + (h - text_h) / 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill="white")

def wrap_text(text, font, max_width, dummy_draw):
    # 1. 기획자가 직접 친 엔터(\n)를 기준으로 먼저 문단을 나눔
    manual_lines = text.split('\n')
    final_lines = []
    
    for m_line in manual_lines:
        # 2. 나뉜 문단별로 가로 픽셀 길이를 계산해 자동 줄바꿈 적용
        words = m_line.split(" ")
        current_line = ""
        
        for word in words:
            if not word:
                continue
            test_line = current_line + " " + word if current_line else word
            bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    final_lines.append(current_line)
                current_line = word
                
        if current_line:
            final_lines.append(current_line)
        elif not m_line: 
            # 엔터만 여러 번 쳤을 때 빈 줄(여백)로 인식하게 유지
            final_lines.append("")
            
    return final_lines

def generate_banner(options_data):
    try:
        font_main = ImageFont.truetype("Pretendard-Bold.ttf", 32)
        font_sub = ImageFont.truetype("Pretendard-Medium.ttf", 24)
        font_badge = ImageFont.truetype("Pretendard-Bold.ttf", 22)
    except IOError:
        st.error("폰트 파일(.ttf)을 찾을 수 없습니다. 실행 폴더 내 파일명을 확인해주세요.")
        return None

    dummy_img = Image.new('RGB', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    options_draw_data = []
    total_height = 30 + 30 
    
    for data in options_data:
        main_text_raw = data['main_text'].strip()
        sub_text_raw = data['sub_text'].strip()
        
        if not main_text_raw and not sub_text_raw:
            continue

        sub_lines = wrap_text(sub_text_raw, font_sub, MAX_TEXT_WIDTH, dummy_draw)
        
        opt_height = 32 + 38 + 12 + (29 * max(len(sub_lines), 1)) + 32
        options_draw_data.append({
            'main': main_text_raw,
            'sub_lines': sub_lines,
            'height': opt_height
        })
        total_height += opt_height

    if not options_draw_data:
        return None

    img = Image.new('RGB', (CANVAS_WIDTH, total_height), color='white')
    draw = ImageDraw.Draw(img)
    current_y = 30 
    
    for i, opt in enumerate(options_draw_data):
        content_y = current_y + 32 
        
        badge_w, badge_h = 50, 34
        badge_y = content_y + 2 
        badge_text = f"{i+1:02d}"
        draw_badge_aa(img, PADDING_X, badge_y, badge_w, badge_h, 6, BADGE_COLOR, badge_text, font_badge)
        
        text_x = PADDING_X + badge_w + 20
        draw.text((text_x, content_y - 4), opt['main'], font=font_main, fill=TEXT_COLOR) 
        
        sub_y = content_y + 38 + 12
        for line in opt['sub_lines']:
            if line: # 빈 줄이 아닐 때만 렌더링
                draw.text((text_x, sub_y - 3), line, font=font_sub, fill=TEXT_COLOR) 
            sub_y += 29 
            
        current_y += opt['height']
        
        if i < len(options_draw_data) - 1:
            draw.line([(PADDING_X, current_y), (CANVAS_WIDTH - PADDING_X, current_y)], fill=DIVIDER_COLOR, width=1)

    return img

# --- [3] 기획자용 웹 UI (Streamlit) ---
st.set_page_config(page_title="배너 자동 생성기", layout="wide")

# --- [좌측 사이드바 가이드 영역] ---
with st.sidebar:
    st.title("📌 배너 제작 가이드")
    st.markdown("### 📝 자동 생성기 사용 방법")
    st.write("1. 생성하고자 하는 옵션 갯수를 선택합니다.")
    st.write("2. 옵션명을 입력합니다.")
    st.write("3. 상세 설명에 세부 옵션을 기입합니다.")
    st.write("4. 배너 생성하기 버튼 클릭")
    st.write("5. 배너 다운로드 클릭")
    st.divider()
    
    st.caption("가이드 문제 발생 시 디자인팀에 문의 바랍니다.")

# --- [메인 화면 영역] ---
st.title("옵션 배너 자동 생성기")

col_opt_input, col_empty = st.columns([1.5, 3.5])
with col_opt_input:
    # 생성 개수 제한 무제한(None)으로 풀림
    num_options = st.number_input("⚙️ 생성할 옵션 개수", min_value=2, max_value=None, value=3)

options_data = []

with st.form("banner_form"):
    col_no, col_main, col_sub = st.columns([0.5, 2, 3])
    col_no.write("**번호**")
    col_main.write("**옵션명 (Main)**")
    col_sub.write("**상세 설명 (Sub)**")
    st.divider() 

    for i in range(int(num_options)):
        c1, c2, c3 = st.columns([0.5, 2, 3])
        c1.write(f"{i+1:02d}")
        
        main_text = c2.text_input(
            f"main_{i}", 
            placeholder="예 : 혼합 4종 + 인기제품 증정", 
            label_visibility="collapsed"
        )
        
        sub_text = c3.text_area(
            f"sub_{i}", 
            placeholder="예 : 오리지널 2\n갈릭 2", 
            label_visibility="collapsed",
            height=68 
        )
        
        options_data.append({"main_text": main_text, "sub_text": sub_text})
    
    st.write("") 
    submitted = st.form_submit_button("배너 생성하기", use_container_width=True)

if submitted:
    result_img = generate_banner(options_data)
    
    if result_img:
        st.subheader("미리보기")
        st.image(result_img, use_container_width=False)
        
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="배너 다운로드",
            data=byte_im,
            file_name="option_banner.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.warning("입력된 데이터가 없습니다. 텍스트를 입력해주세요.")