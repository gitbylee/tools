import streamlit as st

st.set_page_config(
    page_title="디자인 자동화 지원 툴",
    page_icon="🥩",
    layout="centered"
)

st.title("디자인 자동화 지원 툴")
st.write("기획자와 마케터의 빠른 업무 처리를 위해 디자인팀에서 제공하는 자동화 프로그램입니다.")

st.divider()

st.markdown("### 👈 좌측 메뉴를 선택해 업무를 시작하세요.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("**1. 옵션 배너 만들기**\n\n가이드에 맞춰 다중 옵션 배너 이미지를 생성합니다.")

with col2:
    st.info("**2. 공지용 배너 만들기**\n\n부분 색상 강조가 가능한 안내용 텍스트 배너를 생성합니다.")

with col3:
    st.success("**3. HTML 자동 생성기**\n\n(test)상세페이지 및 배너 등록을 위한 HTML 코드를 생성합니다.")

with col4:
    st.success("**4.배너 문안 가이드**\n\n메인배너 요청 전 문안 길이를 검수합니다.")

st.divider()
st.caption("툴 사용 중 오류 발생 및 가이드 관련 문의: 디자인팀")