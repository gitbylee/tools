import streamlit as st
import unicodedata
import re
import streamlit.components.v1 as components

def clean_path(path_str):
    return path_str.strip(" \"'")

def win_to_mac(path_str):
    p = clean_path(path_str)
    p = re.sub(r'^\\\\192\.168\.0\.249\\([^\\]+)\\', r'/Volumes/\1/', p)
    p = p.replace('\\', '/')
    return unicodedata.normalize('NFD', p)

def mac_to_win(path_str):
    p = clean_path(path_str)
    p = re.sub(r'^/Volumes/([^/]+)/', r'\\\\192.168.0.249\\\1\\', p)
    p = p.replace('/', '\\')
    return unicodedata.normalize('NFC', p)

st.set_page_config(page_title="경로 변환기", layout="centered")

with st.sidebar:
    st.title("📌 사용 방법")
    st.write("1. 변환할 윈도우 또는 맥 형식의 경로를 붙여넣습니다.")
    st.write("2. [🍎 맥] 또는 [🪟 윈도우] 변환 버튼을 누릅니다.")
    st.write("3. 결과창 우측의 **'📋 복사하기'** 버튼을 눌러 경로를 복사합니다.")

st.title("윈도우 ↔ 맥 경로 변환기")

input_path = st.text_area("변환할 경로 입력", placeholder="여기에 복사한 경로를 붙여넣으세요.", height=100)

if 'output_path' not in st.session_state:
    st.session_state.output_path = ""
if 'status_msg' not in st.session_state:
    st.session_state.status_msg = ""

col1, col2 = st.columns(2)

with col1:
    if st.button("🍎 맥(Mac) 경로로 변환", use_container_width=True):
        if input_path:
            st.session_state.output_path = win_to_mac(input_path)
            st.session_state.status_msg = "맥(NFD) 형식에 맞게 변환했습니다."
        else:
            st.warning("경로를 입력해주세요.")

with col2:
    if st.button("🪟 윈도우(Win) 경로로 변환", use_container_width=True):
        if input_path:
            st.session_state.output_path = mac_to_win(input_path)
            st.session_state.status_msg = "윈도우(NFC) 형식에 맞게 변환했습니다."
        else:
            st.warning("경로를 입력해주세요.")

if st.session_state.output_path:
    st.divider()
    
    st.success(f"✅ {st.session_state.status_msg}")
    
    # 타이틀과 복사 버튼을 가로로 배치
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("<h4 style='margin-top:0px;'>변환 결과</h4>", unsafe_allow_html=True)
    with col_btn:
        # 경로 안의 따옴표 충돌을 막기 위한 이스케이프 처리
        safe_path = st.session_state.output_path.replace("'", "\\'")
        
        # HTML/JS로 클립보드 복사 버튼 구현
        copy_script = f"""
        <script>
        function copyText() {{
            navigator.clipboard.writeText('{safe_path}').then(function() {{
                const btn = document.getElementById("copybtn");
                btn.innerText = "복사 완료!";
                btn.style.backgroundColor = "#e8f5e9";
                btn.style.borderColor = "#4caf50";
                btn.style.color = "#2e7d32";
                setTimeout(()=>{{ 
                    btn.innerText = "📋 복사하기"; 
                    btn.style.backgroundColor = "#fff";
                    btn.style.borderColor = "#ccc";
                    btn.style.color = "#333";
                }}, 2000);
            }});
        }}
        </script>
        <button id="copybtn" onclick="copyText()" style="cursor:pointer; padding:6px 12px; font-size:14px; border-radius:6px; border:1px solid #ccc; background-color:#fff; color:#333; font-family:sans-serif; width:100%; transition: 0.2s;">📋 복사하기</button>
        """
        components.html(copy_script, height=45)
    
    # 코드는 그대로 노출하되 버튼으로 복사 가능
    st.code(st.session_state.output_path, language="text")