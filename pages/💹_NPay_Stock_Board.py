import streamlit as st
import os
from datetime import datetime, date, time
from module.naver_board import update as update_naver  # 모듈 경로에 맞게 수정하세요

st.set_page_config(page_title="💹 Naver Pay Stock Board", layout="wide")
st.title("💹 Naver Pay Stock Board")

st.markdown("### 네이버페이증권 종목 토론방 데이터 수집")
st.info("[네이버 증권: 수집할 기업의 종목 코드 입력](https://finance.naver.com/item/board.naver?code=005930)")

code_input = st.text_input("종목 코드", value="005930", placeholder="예: 005930")

selected_date = st.date_input("기준 날짜", value=date.today())
default_time = time(0, 0) 
threshold_datetime = datetime.combine(selected_date, default_time)
threshold_str = threshold_datetime.strftime("%Y.%m.%d %H:%M")  

st.markdown(f"**선택된 기준 날짜 및 시간:** {threshold_str}")

if st.button("🔄 수집 실행"):
    with st.spinner("데이터를 수집 중입니다..."):
        df = update_naver(code_input, threshold_str)
    st.success("수집 완료!")

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    LOG_PATH = os.path.join(BASE_DIR, "naver_board_log.txt")
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = f.readlines()
        if logs:
            last_log = logs[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code(last_log, language="text")
        else:
            st.info("로그가 없습니다.")