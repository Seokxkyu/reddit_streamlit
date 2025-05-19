import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

st.set_page_config(page_title="📈 Reddit Weekly Analysis", layout="wide")
st.title("📈 Reddit Weekly Analysis")

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(base_dir)
data_dir = os.path.join(project_root, "data")  

@st.cache_data
def load_csv(file_name):
    csv_path = os.path.join(data_dir, file_name)
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])
    df["week"] = df["time"].dt.to_period("W-SAT").apply(lambda r: r.start_time)
    return df

def get_csv_list(suffix):
    return sorted([f for f in os.listdir(data_dir) if f.endswith(suffix)])

csv_files_subreddit = get_csv_list("_subreddit.csv")
if not csv_files_subreddit:
    st.error("데이터 폴더 내에 _subreddit.csv 파일이 없습니다.")
    st.stop()

csv_files_posts = get_csv_list("_posts.csv")
if not csv_files_posts:
    st.error("데이터 폴더 내에 _posts.csv 파일이 없습니다.")
    st.stop()

tab1, tab2 = st.tabs(["📈 단일 서브레딧 주간 분석", "📈 기타 서브레딧 주간 분석"])

# ========= Tab1: r/Hoka 주간 활동 =========
with tab1:
    st.markdown("### 📈 단일 서브레딧 주간 분석")
    default_idx = csv_files_subreddit.index("hoka_subreddit.csv") if "hoka_subreddit.csv" in csv_files_subreddit else 0
    selected_file = st.selectbox("파일 선택", csv_files_subreddit, index=default_idx, key="weekly_tab1")
    df = load_csv(selected_file)
    
    min_date = df["time"].min().date()
    max_date = df["time"].max().date()
    default_end = min(date.today(), max_date)
    
    default_start_date = max_date - timedelta(days=365)
    if default_start_date < min_date:
        default_start_date = min_date

    start_date, end_date = st.date_input(
        "📅 날짜 선택",
        (default_start_date, default_end),
        min_value=min_date,
        max_value=max_date,
        key="hoka_date"
    )
    
    df_filtered = df[(df["time"].dt.date >= start_date) & (df["time"].dt.date <= end_date)]
    
    if (end_date - start_date).days <= 90:
        df_filtered["day"] = df_filtered["time"].dt.to_period("D").apply(lambda r: r.start_time)
        grouped = df_filtered.groupby("day").agg({
            "score": "sum",
            "num_comments": "sum"
        })
        grouped["post_count"] = df_filtered.groupby("day").size()
        grouped.index = pd.to_datetime(grouped.index)
        
        st.subheader("📊 Daily Total Score and Comments Count")
        st.line_chart(grouped[["score", "num_comments"]])
        
        st.subheader("📝 Daily Posts Count")
        st.line_chart(grouped["post_count"])
    else:
        grouped = df_filtered.groupby("week").agg({
            "score": "sum",
            "num_comments": "sum"
        })
        grouped["post_count"] = df_filtered.groupby("week").size()
        grouped.index = pd.to_datetime(grouped.index)
        
        st.subheader("📊 Weekly Total Score and Comments Count")
        st.line_chart(grouped[["score", "num_comments"]])
        
        st.subheader("📝 Weekly Posts Count")
        st.line_chart(grouped["post_count"])

# ========= Tab2: 기타 서브레딧 주간 활동 =========
with tab2:
    st.markdown("### 📈 기타 서브레딧 주간 분석")
    default_idx_posts = csv_files_posts.index("hoka_posts.csv") if "hoka_posts.csv" in csv_files_posts else 0
    selected_file = st.selectbox("파일 선택", csv_files_posts, index=default_idx_posts, key="weekly_tab2")
    df = load_csv(selected_file)
    
    subreddits = sorted(df["subreddit"].dropna().unique()) if "subreddit" in df.columns else []
    use_filter = st.checkbox("🔍 서브레딧 필터링", key="subreddit_filter")
    if use_filter and subreddits:
        selected_subs = st.multiselect("서브레딧 선택", subreddits, default=subreddits[:3])
    else:
        selected_subs = subreddits  
    
    # 전체 날짜 범위
    min_date = df["time"].min().date()
    max_date = df["time"].max().date()
    default_end = min(date.today(), max_date)

    default_start_date = max_date - timedelta(days=365)
    if default_start_date < min_date:
        default_start_date = min_date

    start_date, end_date = st.date_input(
        "📅 날짜 선택",
        (default_start_date, default_end),
        min_value=min_date,
        max_value=max_date,
        key="subreddit_date"
    )
    
    df_filtered = df.copy()
    if selected_subs:
        df_filtered = df_filtered[df_filtered["subreddit"].isin(selected_subs)]
    df_filtered = df_filtered[(df_filtered["time"].dt.date >= start_date) & (df_filtered["time"].dt.date <= end_date)]
    
    if (end_date - start_date).days <= 180:
        df_filtered["day"] = df_filtered["time"].dt.to_period("D").apply(lambda r: r.start_time)
        grouped = df_filtered.groupby("day").agg({
            "score": "sum",
            "num_comments": "sum"
        })
        grouped["post_count"] = df_filtered.groupby("day").size()
        grouped.index = pd.to_datetime(grouped.index)
        
        st.subheader("📊 Daily Total Score and Comments Count")
        st.line_chart(grouped[["score", "num_comments"]])
        
        st.subheader("📝 Daily Posts Count")
        st.line_chart(grouped["post_count"])
    else:
        grouped = df_filtered.groupby("week").agg({
            "score": "sum",
            "num_comments": "sum"
        })
        grouped["post_count"] = df_filtered.groupby("week").size()
        grouped.index = pd.to_datetime(grouped.index)
        
        st.subheader("📊 Weekly Total Score and Comments Count")
        st.line_chart(grouped[["score", "num_comments"]])
        
        st.subheader("📝 Weekly Posts Count")
        st.line_chart(grouped["post_count"])