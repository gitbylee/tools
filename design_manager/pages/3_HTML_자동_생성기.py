import streamlit as st
import zipfile
import io
import re
from PIL import Image

st.set_page_config(page_title="HTML 자동 생성기", layout="wide")

with st.sidebar:
    st.title("📌 사용 가이드")
    st.write("1. 브랜드 코드와 ERP 코드를 입력합니다.")
    st.write("2. 수급받은 NB 상세 이미지를 모두 드래그하여 업로드합니다.(zip파일 불가)")
    st.write("3. '태그 및 이미지 자동 변환하기' 버튼을 클릭합니다.")
    st.write("4. 상단에 생성된 다운로드 버튼을 통해 ZIP 파일과 TXT 파일을 저장합니다.")
    st.write("5. 하단 텍스트를 복사하여 어드민에 등록할 수도 있습니다.")
    st.write("※ 다운로드되는 압축 파일에는 860x1px 투명 공지 이미지(notice_all.png)가 항상 포함되어 있습니다.")

st.title("HTML 자동 생성 및 이미지 변환기")

st.caption("[🔗 브랜드코드 관리 list](https://docs.google.com/spreadsheets/d/1_REBQ79_ZLCSx7V3oThb2sywuUPuFJ_QJCr5YtufVL4/edit?gid=0#gid=0)")

col1, col2 = st.columns(2)

with col1:
    brand_code = st.text_input("브랜드 코드", placeholder="예: hdd").lower()

with col2:
    erp_code = st.text_input("ERP 코드", placeholder="예: hdd3131347m").lower()

uploaded_files = st.file_uploader(
    "NB 이미지 파일 업로드 (JPG, PNG, GIF)", 
    accept_multiple_files=True, 
    type=['jpg', 'jpeg', 'png', 'gif']
)

if 'processed' not in st.session_state:
    st.session_state.processed = False

def natural_sort_key(file):
    # 파일 이름에서 숫자를 인식하여 사람이 읽는 방식(1, 2, 3... 10)으로 정렬 기준을 만듭니다.
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', file.name)]

if st.button("태그 및 이미지 자동 변환하기", use_container_width=True):
    if not brand_code or not erp_code:
        st.error("브랜드 코드와 ERP 코드를 입력해주세요.")
        st.session_state.processed = False
    elif not uploaded_files:
        st.error("이미지를 업로드해주세요.")
        st.session_state.processed = False
    else:
        # 스트림릿 객체 충돌 방지를 위해 새로운 리스트로 안전하게 정렬
        sorted_files = sorted(uploaded_files, key=natural_sort_key)
        
        zip_buffer = io.BytesIO()
        gif_warnings = []
        html_lines = []
        
        html_lines.append('<div style="margin: 0px auto; width: 100%; text-align: center; max-width: 860px;">')
        html_lines.append('')
        html_lines.append(f'    <img style="width: 100%;" alt="전체공지" src="https://file.rankingdak.com/store/store/notice/notice_all.png"><br>')
        html_lines.append(f'    <img style="width: 100%;" alt="브랜드공지" src="https://file.rankingdak.com/store/{brand_code}/banner/notice_all.png"><br>')
        html_lines.append(f'    <img style="width: 100%;" alt="상품공지" src="https://file.rankingdak.com/store/{brand_code}/item/{erp_code}/notice_all.png"><br>')
        html_lines.append('')

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            trans_img = Image.new('RGBA', (860, 1), (255, 255, 255, 0))
            trans_byte_arr = io.BytesIO()
            trans_img.save(trans_byte_arr, format='PNG')
            zip_file.writestr('notice_all.png', trans_byte_arr.getvalue())

            for i, file in enumerate(sorted_files):
                idx = i + 1
                ext = file.name.split('.')[-1].lower()
                
                file.seek(0, 2)
                file_size_mb = file.tell() / (1024 * 1024)
                file.seek(0)
                
                if ext == 'gif':
                    new_filename = f"{erp_code}_{idx:02d}.gif"
                    if file_size_mb > 7.0:
                        gif_warnings.append(f"용량 초과 오류: {file.name} -> {new_filename} ({file_size_mb:.1f}MB)")
                    elif file_size_mb > 5.0:
                        gif_warnings.append(f"용량 초과 경고: {file.name} -> {new_filename} ({file_size_mb:.1f}MB)")
                    
                    zip_file.writestr(new_filename, file.read())
                else:
                    new_filename = f"{erp_code}_{idx:02d}.jpg"
                    img = Image.open(file)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=90)
                    zip_file.writestr(new_filename, img_byte_arr.getvalue())
                
                html_lines.append(f'    <img style="width: 100%;" alt="상세" src="https://file.rankingdak.com/store/{brand_code}/item/{erp_code}/{new_filename}"><br>')
                
        html_lines.append('')
        html_lines.append('</div>')
        html_result = '\n'.join(html_lines)
        
        st.session_state.zip_data = zip_buffer.getvalue()
        st.session_state.html_result = html_result
        st.session_state.gif_warnings = gif_warnings
        st.session_state.file_name_base = erp_code
        st.session_state.processed = True

if st.session_state.processed:
    st.success("작업이 완료되었습니다. 아래 버튼을 눌러 파일을 다운로드하세요.")
    
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        st.download_button(
            label="변환된 이미지 다운로드 (.zip)",
            data=st.session_state.zip_data,
            file_name=f"{st.session_state.file_name_base}_images.zip",
            mime="application/zip",
            use_container_width=True
        )
        
    with btn_col2:
        st.download_button(
            label="HTML 다운로드 (.txt)",
            data=st.session_state.html_result,
            file_name=f"{st.session_state.file_name_base}_tag.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.text_area("복사 영역", st.session_state.html_result, height=300)
    
    for w in st.session_state.gif_warnings:
        st.warning(w)