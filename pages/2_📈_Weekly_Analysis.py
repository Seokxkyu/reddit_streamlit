import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="📈 Weekly Analysis", layout="wide")

st.title("📈 Weekly Analysis")

@st.cache_data
def load_data():
    # Streamlit 앱 루트 기준 경로
    hoka_sub = os.path.join("data", "hoka_subreddit.csv")
    other_subs = os.path.join("data", "hoka_posts.csv")
    # hoka_sub = r"C:\Users\rootn\OneDrive\Desktop\Reddit\data\hoka_subreddit.csv"
    # other_subs = r"C:\Users\rootn\OneDrive\Desktop\Reddit\data\hoka_posts.csv"

    df1 = pd.read_csv(hoka_sub)
    df2 = pd.read_csv(other_subs)

    df1["time"] = pd.to_datetime(df1["time"], errors='coerce')
    df2["time"] = pd.to_datetime(df2["time"], errors='coerce')

    df1 = df1.dropna(subset=["time"])
    df2 = df2.dropna(subset=["time"])

    df1["week"] = df1["time"].dt.to_period("W-SAT").apply(lambda r: r.start_time)
    df2["week"] = df2["time"].dt.to_period("W-SAT").apply(lambda r: r.start_time)

    return df1, df2

hoka_df, subreddit_df = load_data()

tab1, tab2 = st.tabs(["📈 r/Hoka 주간 활동", "📈 기타 서브레딧 주간 활동"])

with tab1:
    st.markdown("### 📈 r/Hoka 주간 분석")

    min_date = hoka_df["time"].min().date()
    max_date = hoka_df["time"].max().date()
    default_end = min(date.today(), max_date)

    start_date, end_date = st.date_input(
        "📅 날짜 선택",
        (min_date, default_end),
        min_value=min_date,
        max_value=max_date,
        key="hoka_date"
    )

    df_filtered = hoka_df[
        (hoka_df["time"].dt.date >= start_date) &
        (hoka_df["time"].dt.date <= end_date)
    ]

    weekly = df_filtered.groupby("week").agg({
        "score": "sum",
        "num_comments": "sum"
    })
    weekly["post_count"] = df_filtered.groupby("week").size()
    weekly.index = pd.to_datetime(weekly.index)

    st.subheader("📊 Total Score and Comments Count")
    st.line_chart(weekly[["score", "num_comments"]])

    st.subheader("📝 Posts Count")
    st.line_chart(weekly["post_count"])

with tab2:
    st.markdown("### 📈 기타 서브레딧의 Hoka 관련 주간 분석")

    subreddits = sorted(subreddit_df["subreddit"].dropna().unique())
    use_filter = st.checkbox("🔍 서브레딧 필터링")

    if use_filter:
        selected_subs = st.multiselect("서브레딧 선택", subreddits, default=subreddits[:3])
    else:
        selected_subs = subreddits  # ✅ 전체 서브레딧 대상

    min_date = subreddit_df["time"].min().date()
    max_date = subreddit_df["time"].max().date()
    default_end = min(date.today(), max_date)

    start_date2, end_date2 = st.date_input(
        "📅 날짜 선택",
        (date(2025, 1, 25), default_end),
        min_value=min_date,
        max_value=max_date,
        key="subreddit_date"
    )

    filtered_df = subreddit_df[
        (subreddit_df["subreddit"].isin(selected_subs)) &
        (subreddit_df["time"].dt.date >= start_date2) &
        (subreddit_df["time"].dt.date <= end_date2)
    ]

    weekly2 = filtered_df.groupby("week").agg({
        "score": "sum",
        "num_comments": "sum"
    })
    weekly2["post_count"] = filtered_df.groupby("week").size()
    weekly2.index = pd.to_datetime(weekly2.index)

    st.subheader("📊 Total score and Comments count")
    st.line_chart(weekly2[["score", "num_comments"]])

    st.subheader("📝 Posts count")
    st.line_chart(weekly2["post_count"])