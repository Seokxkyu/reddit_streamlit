import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="📱 TikTok Trending Analysis", layout="wide")
st.title("📱 TikTok Trending Analysis")

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "tiktok.csv")
    df = pd.read_csv(csv_path, encoding="cp949")
    df.columns = df.columns.str.strip()
    df['createTimeISO'] = pd.to_datetime(df['createTimeISO'], errors='coerce')
    df['date'] = pd.to_datetime(df['createTimeISO'].dt.date)
    return df

df = load_data()
df = df.set_index('date').sort_index()

weekly_metrics = df.resample('W-SAT', label='left').agg({
    'playCount': 'sum',    
    'diggCount': 'sum',    
    'shareCount': 'sum',   
    'commentCount': 'sum'  
}).sort_index()

weekly_trend = df.resample('W-SAT', label='left').size().to_frame(name='Posts Count').sort_index()

tabs = st.tabs(["Posts", "Play", "Likes", "Shares", "Comments"])

with tabs[0]:
    st.subheader("Weekly Posts Count Trend")
    min_date_posts = weekly_trend.index.min().date()
    max_date_posts = weekly_trend.index.max().date()
    date_range_posts = st.date_input("📅 날짜 필터링", (min_date_posts, max_date_posts), key="posts_date")
    weekly_trend_filtered = weekly_trend[
        (weekly_trend.index >= pd.to_datetime(date_range_posts[0])) &
        (weekly_trend.index <= pd.to_datetime(date_range_posts[1]))
    ]
    st.line_chart(weekly_trend_filtered)

with tabs[1]:
    st.subheader("Weekly Play Count Trend")
    min_date_play = weekly_metrics.index.min().date()
    max_date_play = weekly_metrics.index.max().date()
    date_range_play = st.date_input("📅 날짜 필터링", (min_date_play, max_date_play), key="play_date")
    weekly_metrics_filtered_play = weekly_metrics[
        (weekly_metrics.index >= pd.to_datetime(date_range_play[0])) &
        (weekly_metrics.index <= pd.to_datetime(date_range_play[1]))
    ]
    st.line_chart(weekly_metrics_filtered_play[['playCount']].rename(columns={'playCount': 'Play Count'}))

with tabs[2]:
    st.subheader("Weekly Likes Trend")
    min_date_metrics = weekly_metrics.index.min().date()
    max_date_metrics = weekly_metrics.index.max().date()
    date_range_likes = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="likes_date")
    weekly_metrics_filtered_likes = weekly_metrics[
        (weekly_metrics.index >= pd.to_datetime(date_range_likes[0])) &
        (weekly_metrics.index <= pd.to_datetime(date_range_likes[1]))
    ]
    st.line_chart(weekly_metrics_filtered_likes[['diggCount']].rename(columns={'diggCount': 'Likes'}))

with tabs[3]:
    st.subheader("Weekly Shares Trend")
    date_range_shares = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="shares_date")
    weekly_metrics_filtered_shares = weekly_metrics[
        (weekly_metrics.index >= pd.to_datetime(date_range_shares[0])) &
        (weekly_metrics.index <= pd.to_datetime(date_range_shares[1]))
    ]
    st.line_chart(weekly_metrics_filtered_shares[['shareCount']].rename(columns={'shareCount': 'Shares'}))

with tabs[4]:
    st.subheader("Weekly Comments Trend")
    date_range_comments = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="comments_date")
    weekly_metrics_filtered_comments = weekly_metrics[
        (weekly_metrics.index >= pd.to_datetime(date_range_comments[0])) &
        (weekly_metrics.index <= pd.to_datetime(date_range_comments[1]))
    ]
    st.line_chart(weekly_metrics_filtered_comments[['commentCount']].rename(columns={'commentCount': 'Comments'}))