import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont
import os

# =========================================================
# [설정] 디자인 가이드 규격 (720x432)
# =========================================================
BANNER_WIDTH = 720
BANNER_HEIGHT = 432

# 1. 좌표 및 제한선
TEXT_START_X = 36         
TEXT_START_Y = 49         

LIMIT_MAIN_X = 458        # 메인 카피 제한선 (노란선)
LIMIT_SUB_X = 348         # 서브 카피 제한선 (주황선)

# 2. 안전 영역 너비
WIDTH_LIMIT_MAIN = LIMIT_MAIN_X - TEXT_START_X
WIDTH_LIMIT_SUB = LIMIT_SUB_X - TEXT_START_X

# 3. 폰트 및 간격
FONT_SIZE_MAIN = 46       
FONT_SIZE_SUB = 26
LINE_SPACING = 16         
PARAGRAPH_SPACING = 34    

# 레이아웃 와이드 모드
st.set_page_config(page_title="배너 디자인 가이드", page_icon="🎨", layout="wide")

# =========================================================
# [기능] 폰트 로드
# =========================================================
def get_custom_font(size, is_bold=True):
    font_file = "Pretendard-Bold.otf" if is_bold else "Pretendard-Medium.otf"
    if os.path.exists(font_file):
        return ImageFont.truetype(font_file, size)
    try:
        weight_index = 1 if is_bold else 0
        return ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", size, index=weight_index)
    except:
        return ImageFont.load_default()

# =========================================================
# [기능] 미리보기 생성 (가이드 개선)
# =========================================================
def create_preview(line1, line2, sub_text):
    img = Image.new('RGB', (BANNER_WIDTH, BANNER_HEIGHT), (20, 30, 80))
    
    # 제한 영역 표시
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    # 메인 침범 구역 (붉은색)
    draw_overlay.rectangle([(LIMIT_MAIN_X, 0), (BANNER_WIDTH, BANNER_HEIGHT)], fill=(255, 0, 0, 40))
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)

    font_main = get_custom_font(FONT_SIZE_MAIN, is_bold=True)
    font_sub = get_custom_font(FONT_SIZE_SUB, is_bold=False)
    # 가이드용 작은 폰트
    font_small = get_custom_font(14, is_bold=False) 
    
    # ---------------------------------------------------------
    # [가이드라인 그리기] - 개선됨
    # ---------------------------------------------------------
    
    # 1. 텍스트 시작점 (십자가)
    draw.line([(TEXT_START_X-10, TEXT_START_Y), (TEXT_START_X+10, TEXT_START_Y)], fill="#00FF00", width=1)
    draw.line([(TEXT_START_X, TEXT_START_Y-10), (TEXT_START_X, TEXT_START_Y+10)], fill="#00FF00", width=1)
    
    # 2. 메인 제한선 (노란선) - 위쪽에 라벨 표시
    draw.line([(LIMIT_MAIN_X, 0), (LIMIT_MAIN_X, BANNER_HEIGHT)], fill="#FFFF00", width=2)
    draw.text((LIMIT_MAIN_X + 5, 20), f"◀ 메인 한계 ({LIMIT_MAIN_X}px)", fill="#FFFF00", font=font_small)

    # 3. 서브 제한선 (주황선) - 아래쪽에 라벨 표시 (겹침 방지)
    draw.line([(LIMIT_SUB_X, 0), (LIMIT_SUB_X, BANNER_HEIGHT)], fill="#FF8800", width=2)
    draw.text((LIMIT_SUB_X + 5, 320), f"◀ 서브 한계 ({LIMIT_SUB_X}px)", fill="#FF8800", font=font_small)

    # 4. 우측 하단 범례 박스 (Legend)
    legend_x = BANNER_WIDTH - 140
    legend_y = BANNER_HEIGHT - 70
    draw.rectangle([(legend_x, legend_y), (BANNER_WIDTH-10, BANNER_HEIGHT-10)], outline="white", width=1)
    draw.text((legend_x + 10, legend_y + 10), "- 노란선: 메인", fill="#FFFF00", font=font_small)
    draw.text((legend_x + 10, legend_y + 30), "- 주황선: 서브", fill="#FF8800", font=font_small)


    # ---------------------------------------------------------
    # [텍스트 배치]
    # ---------------------------------------------------------
    current_y = TEXT_START_Y
    if line1:
        draw.text((TEXT_START_X, current_y), line1, font=font_main, fill="white")
    current_y += FONT_SIZE_MAIN + LINE_SPACING

    if line2:
        draw.text((TEXT_START_X, current_y), line2, font=font_main, fill="white")
    current_y += FONT_SIZE_MAIN + PARAGRAPH_SPACING

    if sub_text:
        if not line1 and not line2:
             current_y = TEXT_START_Y + FONT_SIZE_MAIN + LINE_SPACING + FONT_SIZE_MAIN + PARAGRAPH_SPACING
        draw.text((TEXT_START_X, current_y), sub_text, font=font_sub, fill=(220, 220, 220))

    # 길이 측정
    w1 = draw.textlength(line1, font=font_main) if line1 else 0
    w2 = draw.textlength(line2, font=font_main) if line2 else 0
    w_sub = draw.textlength(sub_text, font=font_sub) if sub_text else 0

    return img, w1, w2, w_sub

# =========================================================
# [UI] 화면 구성
# =========================================================
st.title("🎨 배너 디자인 가이드 (720x432)")

col_left, col_right = st.columns([1.5, 1])

# [좌측] 입력 & 미리보기
with col_left:
    st.subheader("1. 문안 입력 & 미리보기")
    
    main_line1 = st.text_input("메인 카피 (1줄) *필수", placeholder="예: 토스페이 결제하면")
    main_line2 = st.text_input("메인 카피 (2줄) *필수", placeholder="예: 최대 1만원 적립")
    sub_text = st.text_input("서브 카피 (선택)", placeholder="예: 기간 한정 혜택을 놓치지 마세요")

    st.markdown("---")
    
    preview_img, w1, w2, w_sub = create_preview(main_line1, main_line2, sub_text)
    st.image(preview_img, caption="노란선: 메인 한계 / 주황선: 서브 한계", use_container_width=True)

# [우측] 검수 & 복사 버튼
with col_right:
    st.subheader("2. 검수 결과")
    
    err_msgs = []
    total_main_len = len(main_line1) + len(main_line2)

    # 검수 로직
    if not main_line1: err_msgs.append("❌ [메인 1줄] 필수 입력입니다.")
    if not main_line2: err_msgs.append("❌ [메인 2줄] 필수 입력입니다.")
    if total_main_len > 22: err_msgs.append(f"❌ [메인] 글자 수 초과 ({total_main_len}/22자)")
    if len(sub_text) > 18: err_msgs.append(f"❌ [서브] 글자 수 초과 ({len(sub_text)}/18자)")
    if w1 > WIDTH_LIMIT_MAIN: err_msgs.append(f"❌ [메인 1줄] 노란선 초과")
    if w2 > WIDTH_LIMIT_MAIN: err_msgs.append(f"❌ [메인 2줄] 노란선 초과")
    if w_sub > WIDTH_LIMIT_SUB: err_msgs.append(f"❌ [서브] 주황선 초과")

    if err_msgs:
        st.error("🚨 규격 미달 / 필수 입력 누락")
        for msg in err_msgs: st.write(msg)
        
    else:
        # ✅ 검수 통과
        st.success("✅ 규격 통과! 추가 옵션을 선택하세요.")
        
        st.markdown("##### ➕ 추가 요청 사항")
        
        # [옵션]
        use_badge = st.checkbox("딱지(Badge) 활용")
        badge_text = ""
        if use_badge:
            badge_text = st.text_input("딱지 문구 입력 (최대 8자)", max_chars=8, placeholder="예: 단독특가")
            
        make_gif = st.checkbox("GIF 제작 요청")
        
        st.divider()

        # [요청서 생성]
        req_text = f"""[디자인 요청서]
- 규격: 720x432
- 메인1: {main_line1}
- 메인2: {main_line2}
- 서브: {sub_text}"""

        if use_badge:
            badge_val = badge_text if badge_text else "(문구 미입력)"
            req_text += f"\n- 딱지: {badge_val}"
            
        if make_gif:
            req_text += "\n- GIF: 제작 요청 (시안 확정 후 gif 제작됩니다.)"

        req_text += f"\n-----------------------\n* 규격 검수 완료 (메인 {total_main_len}자)"
        
        st.markdown("##### 📋 최종 요청서 미리보기")
        st.text_area("요청서 내용", req_text, height=200, label_visibility="collapsed")
        
        # 복사 버튼 (줄바꿈 오류 수정 및 UX 개선)
        html_button = f"""
        <div style="margin-top: 10px;">
            <textarea id="copyTarget" style="opacity: 0; position: absolute; z-index: -1;">{req_text}</textarea>
            <button id="copyBtn" onclick="copyToClipboard()" style="
                background-color: #007AFF; 
                color: white; 
                border: none; 
                padding: 15px 0px; 
                border-radius: 8px; 
                font-size: 16px; 
                font-weight: bold; 
                cursor: pointer; 
                width: 100%; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: background-color 0.3s;
            ">
                📋 최종 요청서 복사하기
            </button>
            <script>
            function copyToClipboard() {{
                var copyText = document.getElementById("copyTarget");
                copyText.select();
                copyText.setSelectionRange(0, 99999); 
                document.execCommand("copy");
                
                var btn = document.getElementById("copyBtn");
                btn.innerText = "✅ 복사 완료!";
                btn.style.backgroundColor = "#34C759";
                
                setTimeout(function() {{
                    btn.innerText = "📋 최종 요청서 복사하기";
                    btn.style.backgroundColor = "#007AFF";
                }}, 2000);
            }}
            </script>
        </div>
        """
        components.html(html_button, height=80)