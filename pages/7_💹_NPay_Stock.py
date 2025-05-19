import os
import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from module.naver_board import update as update_naver
from module.naver_content import update_bodies

st.set_page_config(page_title="💹 Naver Pay Stock Board", layout="wide")
st.title("💹 Naver Pay Stock Board")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "debate")

tab1, tab2 = st.tabs(["데이터 수집", "본문 수집"])

with tab1:
    st.markdown("### 네이버페이증권 종목 토론방 데이터 수집")
    st.info("[네이버 증권: 수집할 기업의 종목 코드 입력](https://finance.naver.com/item/board.naver?code=005930)")

    code_input = st.text_input("종목 코드", value="005930", placeholder="예: 005930")
    # 기본 날짜를 어제로 설정
    default_date = date.today() - timedelta(days=1)
    selected_date = st.date_input("기준 날짜", value=default_date)
    
    default_time = time(0, 0)
    threshold_str = datetime.combine(selected_date, default_time).strftime("%Y.%m.%d %H:%M")
    st.markdown(f"**선택한 기준 날짜 및 시간:** {threshold_str}")

    if st.button("🔄 수집 실행"):
        with st.spinner("데이터 수집 중..."):
            df = update_naver(code_input, threshold_str)
        st.success("수집 완료!")
        log_path = os.path.join(BASE_DIR, "naver_board_log.txt")
        if os.path.exists(log_path):
            logs = open(log_path, encoding="utf-8").read().splitlines()
            if logs:
                st.markdown("### 📝 최근 수집 로그")
                st.code(logs[-1], language="text")

        csv_path = os.path.join(DATA_DIR, f"{code_input}_board.csv")
        if os.path.exists(csv_path):
            df_updated = pd.read_csv(csv_path, encoding="utf-8-sig")
            st.markdown("### 📊 업데이트된 데이터 미리보기")
            st.dataframe(df_updated.head())

with tab2:
    st.markdown("### 네이버페이증권 본문 업데이트")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith("_board.csv")]
    codes = [os.path.splitext(f)[0].replace("_board", "") for f in files]
    selected_code = st.selectbox("종목 코드 선택", codes)

    if st.button("🔄 본문 업데이트 실행"):
        with st.spinner(f"{selected_code} 본문 업데이트 중..."):
            update_bodies(selected_code)
        st.success("본문 업데이트 완료!")
        csv_path = os.path.join(DATA_DIR, f"{selected_code}_board.csv")
        df_preview = pd.read_csv(csv_path, encoding="utf-8-sig")
        st.markdown("### 📄 본문 포함 데이터 미리보기")
        st.dataframe(df_preview.head())
