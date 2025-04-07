import streamlit as st
import sys
import os
from datetime import datetime

# ✅ 외부 모듈 경로 추가
sys.path.append(r"C:\Users\rootn\OneDrive\Desktop\Reddit")

# ✅ 두 모듈에서 update 함수 불러오기
from reddit import update as update_hoka
from reddit_other_subreddits import update as update_subreddits
from reddit_search import update as keyword_search

st.set_page_config(page_title="🔄 Data Collection", layout="wide")
st.title("🔄 Data Collection")

# tab1, tab2 = st.tabs(["🔄 r/Hoka 수집", "🔄 전체 서브레딧 수집"])
tab1, tab2, tab3 = st.tabs([
    "🔄 r/Hoka 수집",
    "🔄 전체 서브레딧 수집",
    "🔍 검색어 기반 수집"
])

# ✅ r/Hoka 수집 탭
with tab1:
    st.markdown("### 🔄 r/Hoka 서브레딧 데이터 수집")

    if st.button("🌍 r/Hoka 수집 실행"):
        with st.spinner("r/Hoka 데이터를 수집 중입니다..."):
            update_hoka()
        st.success("✅ r/Hoka 수집 완료!")

        log_path = r"C:\Users\rootn\OneDrive\Desktop\Reddit\run_log.txt"
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code("".join(logs), language="text")

# ✅ 전체 서브레딧 수집 탭
with tab2:
    st.markdown("### 🔄 전체 서브레딧에서 'hoka' 키워드 검색")

    if st.button("🌍 전체 서브레딧 수집 실행"):
        with st.spinner("전체 subreddit에서 데이터를 수집 중입니다..."):
            update_subreddits()
        st.success("✅ 전체 서브레딧 수집 완료!")

        log_path = r"C:\Users\rootn\OneDrive\Desktop\Reddit\run_log.txt"
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code("".join(logs), language="text")

with tab3:
    st.markdown("### 🔍 전체 서브레딧에서 검색")

    keyword = st.text_input("키워드 입력", placeholder="예: nike, hoka, running shoes")

    if st.button("🔍 키워드로 수집 실행") and keyword.strip():
        with st.spinner(f"'{keyword}' 키워드로 수집 중입니다..."):
            keyword_search(keyword)
        st.success(f"✅ '{keyword}' 수집 완료!")

        log_path = r"C:\Users\rootn\OneDrive\Desktop\Reddit\run_log.txt"
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code(logs, language="text")
