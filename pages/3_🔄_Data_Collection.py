import streamlit as st
import os
from datetime import datetime

from module.reddit import update as update_hoka
from module.reddit_other_subreddits import update as update_subreddits
from module.reddit_search import update as keyword_search
from module.reddit_search_subreddit import update as subreddit_search 

st.set_page_config(page_title="🔄 Reddit Data Collection", layout="wide")
st.title("🔄 Reddit Data Collection")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 서브레딧 데이터 수집",
    "🔍 검색어 기반 수집",
    "🔄 r/Hoka 서브레딧 데이터 수집",
    "🔄 전체 서브레딧 수집",
])

with tab1:
    st.markdown("### 🔄 서브레딧 기반 데이터 수집")

    target_subreddit = st.text_input("서브레딧 이름", placeholder="ex. askrunningshoegeeks")
    
    collect_comments_option = st.checkbox("댓글 수집", value=False)
    
    if st.button("🔍 데이터 수집 실행"):
        if target_subreddit.strip():
            with st.spinner(f"'{target_subreddit}' 서브레딧 데이터를 수집 중입니다..."):
                subreddit_search(target_subreddit, collect_comments=collect_comments_option)
            st.success(f"✅ '{target_subreddit}' 데이터 수집 완료!")
            
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, encoding="utf-8") as f:
                    last_log = f.readlines()[-1]
                st.markdown("### 📝 최근 수집 로그")
                st.code(last_log, language="text")
        else:
            st.warning("올바른 서브레딧 이름을 입력하세요!")

with tab2:
    st.markdown("### 🔍 전체 서브레딧에서 검색")
    st.info("세 개의 항목을 입력하세요:\n"
            "1. 검색 대상 서브레딧 (입력하지 않으면 기본값 'all' 사용)\n"
            "2. 검색 대상 키워드 (입력하지 않으면 기본값 'hoka' 사용)\n"
            "3. 참조 대상 CSV 파일 이름 (선택사항: 입력하지 않으면 키워드 기반 파일 이름 사용)")

    input_subreddit = st.text_input("검색 대상 서브레딧", placeholder="ex. all, askrunningshoegeeks")
    if input_subreddit.strip() == "":
        input_subreddit = "all"

    input_keyword = st.text_input("검색 대상 키워드", placeholder="ex. nike, hoka, asics")
    if input_keyword.strip() == "":
        input_keyword = "hoka"

    input_csv = st.text_input("참조 대상 CSV 파일", placeholder="ex. hoka (선택사항)")
    if input_csv.strip() == "":
        input_csv = None

    if st.button("🔍 키워드로 수집 실행"):
        with st.spinner(f"'{input_keyword}' 키워드로 '{input_subreddit}' 서브레딧에서 수집 중입니다..."):
            keyword_search(search_subreddit=input_subreddit, keyword=input_keyword, csv_filename_base=input_csv)
        st.success(f"✅ '{input_keyword}' 키워드 수집 완료!")

        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code(logs, language="text")

with tab3:
    st.markdown("### 🔄 r/Hoka 서브레딧 데이터 수집")

    if st.button("🌍 r/Hoka 수집 실행"):
        with st.spinner("r/Hoka 데이터를 수집 중입니다..."):
            update_hoka()
        st.success("✅ r/Hoka 수집 완료!")

        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code(logs, language="text")

with tab4:
    st.markdown("### 🔄 전체 서브레딧에서 'hoka' 키워드 검색")

    if st.button("🌍 전체 서브레딧 수집 실행"):
        with st.spinner("전체 subreddit에서 데이터를 수집 중입니다..."):
            update_subreddits()
        st.success("✅ 전체 서브레딧 수집 완료!")

        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, encoding="utf-8") as f:
                logs = f.readlines()[-1]
            st.markdown("### 📝 최근 수집 로그")
            st.code(logs, language="text")