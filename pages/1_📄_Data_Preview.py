import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="📄 Reddit Data Preview",
    layout="wide" 
)

st.title("📄 Reddit Data Preview")

@st.cache_data
def load_csv(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    data_dir = os.path.join(base_dir, "..", "data")      
    csv_path = os.path.join(data_dir, file_name)
    df = pd.read_csv(csv_path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "..", "data")

csv_files_subreddit = sorted([f for f in os.listdir(data_dir) if f.endswith("_subreddit.csv")])
if not csv_files_subreddit:
    st.error("데이터 폴더 내에 _subreddit.csv 파일이 없습니다.")
    st.stop()

csv_files_posts = sorted([f for f in os.listdir(data_dir) if f.endswith("_posts.csv")])
if not csv_files_posts:
    st.error("데이터 폴더 내에 _posts.csv 파일이 없습니다.")
    st.stop()

tab1, tab2 = st.tabs(["📄 단일 서브레딧 게시글", "📄 여러 서브레딧 게시글"])

# ======== Tab1: 단일 서브레딧 게시글 (날짜 필터링만) ========
with tab1:
    st.markdown("### 단일 서브레딧 게시글 미리보기")
    selected_file = st.selectbox("CSV 파일 선택 (_subreddit.csv)", csv_files_subreddit)
    data = load_csv(selected_file)
    
    if st.checkbox("📅 날짜 선택", key="tab1_date_filter"):
        min_date = data["time"].min().date()
        max_date = data["time"].max().date()
        start_date, end_date = st.date_input(
            "날짜 선택", 
            (min_date, max_date), 
            min_value=min_date, 
            max_value=max_date, 
            key="tab1_date"
        )
        filtered_data = data[(data["time"].dt.date >= start_date) & (data["time"].dt.date <= end_date)]
    else:
        filtered_data = data

    st.write(f"🔎 총 {len(filtered_data)}개 항목 표시 중")
    st.dataframe(filtered_data)

# ======== Tab2: 여러 서브레딧 게시글 (서브레딧 & 날짜 필터링) ========
with tab2:
    st.markdown("### 여러 서브레딧 게시글 미리보기")
    selected_file = st.selectbox("CSV 파일 선택 (_posts.csv)", csv_files_posts, key="tab2_csv")
    data = load_csv(selected_file)

    if st.checkbox("🔍 서브레딧 필터링", key="tab2_subreddit_filter"):
        if "subreddit" in data.columns:
            unique_subs = sorted(data["subreddit"].dropna().unique())
            selected_subs = st.multiselect("서브레딧 선택", unique_subs, default=unique_subs[:1])
        else:
            st.warning("선택한 파일에 'subreddit' 컬럼이 없습니다.")
            selected_subs = None
    else:
        selected_subs = None

    if st.checkbox("📅 날짜 필터링", key="tab2_date_filter"):
        min_date = data["time"].min().date()
        max_date = data["time"].max().date()
        start_date, end_date = st.date_input(
            "날짜 선택", 
            (min_date, max_date), 
            min_value=min_date, 
            max_value=max_date, 
            key="tab2_date"
        )
    else:
        start_date, end_date = None, None

    filtered_data = data.copy()
    if selected_subs:
        filtered_data = filtered_data[filtered_data["subreddit"].isin(selected_subs)]
    if start_date and end_date:
        filtered_data = filtered_data[(filtered_data["time"].dt.date >= start_date) & (filtered_data["time"].dt.date <= end_date)]
        
    st.write(f"🔎 총 {len(filtered_data)}개 항목 표시 중")
    st.dataframe(filtered_data)