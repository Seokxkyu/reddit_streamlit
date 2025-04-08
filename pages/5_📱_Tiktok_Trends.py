# import streamlit as st
# import pandas as pd
# import os

# st.set_page_config(page_title="TikTok Trending Analysis", layout="wide")
# st.title("TikTok Trending Analysis")

# @st.cache_data
# def load_data():
#     # CSV 파일 경로 (예: data 폴더 내 tiktok.csv)
#     csv_path = os.path.join("data", "tiktok.csv")
#     df = pd.read_csv(csv_path, encoding="cp949")
    
#     # 컬럼 이름의 여분의 공백 제거
#     df.columns = df.columns.str.strip()
    
#     # 'createTimeISO' 컬럼을 datetime으로 파싱 (오류 발생 시 NaT 처리)
#     df['createTimeISO'] = pd.to_datetime(df['createTimeISO'], errors='coerce')
#     # 날짜 정보만 추출하여 'date' 컬럼 생성 (st.line_chart는 인덱스를 x축으로 사용)
#     df['date'] = pd.to_datetime(df['createTimeISO'].dt.date)
    
#     return df

# # 데이터 로드
# df = load_data()

# # -----------------------------
# # 각 날짜별 총합 집계
# # -----------------------------
# metrics = df.groupby('date').agg({
#     'diggCount': 'sum',
#     'shareCount': 'sum',
#     'commentCount': 'sum'
# }).sort_index()

# # -----------------------------
# # 각 날짜별 Posts Count 집계
# # -----------------------------
# trend = df.groupby('date').size().to_frame(name='Posts Count').sort_index()

# # ========== Posts Count 차트 ==========
# st.subheader("Posts Count Trend")
# # 최소, 최대 날짜 계산 (Posts Count용)
# min_date_posts = trend.index.min().date()
# max_date_posts = trend.index.max().date()
# # 날짜 필터(Posts Count)
# date_range_posts = st.date_input("📅 날짜 필터링", (min_date_posts, max_date_posts), key="posts_date")
# # 날짜 범위 필터 적용
# trend_filtered = trend[
#     (trend.index >= pd.to_datetime(date_range_posts[0])) &
#     (trend.index <= pd.to_datetime(date_range_posts[1]))
# ]
# st.line_chart(trend_filtered)

# # ========== Likes 차트 ==========
# st.subheader("Likes Trend")
# # 최소, 최대 날짜 계산 (metrics용)
# min_date_metrics = metrics.index.min().date()
# max_date_metrics = metrics.index.max().date()
# # 날짜 필터(Likes)
# date_range_likes = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="likes_date")
# # 날짜 범위 필터 적용
# metrics_filtered_likes = metrics[
#     (metrics.index >= pd.to_datetime(date_range_likes[0])) &
#     (metrics.index <= pd.to_datetime(date_range_likes[1]))
# ]
# # 'diggCount'는 Likes로 표시
# st.line_chart(metrics_filtered_likes[['diggCount']].rename(columns={'diggCount': 'Likes'}))

# # ========== Shares 차트 ==========
# st.subheader("Shares Trend")
# date_range_shares = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="shares_date")
# metrics_filtered_shares = metrics[
#     (metrics.index >= pd.to_datetime(date_range_shares[0])) &
#     (metrics.index <= pd.to_datetime(date_range_shares[1]))
# ]
# st.line_chart(metrics_filtered_shares[['shareCount']].rename(columns={'shareCount': 'Shares'}))

# # ========== Comments 차트 ==========
# st.subheader("Comments Trend")
# date_range_comments = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="comments_date")
# metrics_filtered_comments = metrics[
#     (metrics.index >= pd.to_datetime(date_range_comments[0])) &
#     (metrics.index <= pd.to_datetime(date_range_comments[1]))
# ]
# st.line_chart(metrics_filtered_comments[['commentCount']].rename(columns={'commentCount': 'Comments'}))

import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="📱 TikTok Trending Analysis", layout="wide")
st.title("📱 TikTok Trending Analysis")

@st.cache_data
def load_data():
    # CSV 파일 경로 (예: data 폴더 내 tiktok.csv)
    csv_path = os.path.join("data", "tiktok.csv")
    df = pd.read_csv(csv_path, encoding="cp949")
    
    # 컬럼 이름의 여분의 공백 제거
    df.columns = df.columns.str.strip()
    
    # 'createTimeISO' 컬럼을 datetime으로 파싱 (오류 발생 시 NaT 처리)
    df['createTimeISO'] = pd.to_datetime(df['createTimeISO'], errors='coerce')
    # 날짜 정보만 추출하여 'date' 컬럼 생성
    df['date'] = pd.to_datetime(df['createTimeISO'].dt.date)
    
    return df

# 데이터 로드 및 날짜를 인덱스로 설정
df = load_data()
df = df.set_index('date').sort_index()

# -----------------------------
# Weekly Aggregation
# -----------------------------
# 각 주별 총합 집계 (매주 토요일 기준)
weekly_metrics = df.resample('W-SAT').agg({
    'diggCount': 'sum',
    'shareCount': 'sum',
    'commentCount': 'sum'
}).sort_index()

# 각 주별 Posts Count 집계
weekly_trend = df.resample('W-SAT').size().to_frame(name='Posts Count').sort_index()

# ========== Posts Count 차트 ==========
st.subheader("Weekly Posts Count Trend")
min_date_posts = weekly_trend.index.min().date()
max_date_posts = weekly_trend.index.max().date()
date_range_posts = st.date_input("📅 날짜 필터링", (min_date_posts, max_date_posts), key="posts_date")
weekly_trend_filtered = weekly_trend[
    (weekly_trend.index >= pd.to_datetime(date_range_posts[0])) &
    (weekly_trend.index <= pd.to_datetime(date_range_posts[1]))
]
st.line_chart(weekly_trend_filtered)

# ========== Likes 차트 ==========
st.subheader("Weekly Likes Trend")
min_date_metrics = weekly_metrics.index.min().date()
max_date_metrics = weekly_metrics.index.max().date()
date_range_likes = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="likes_date")
weekly_metrics_filtered_likes = weekly_metrics[
    (weekly_metrics.index >= pd.to_datetime(date_range_likes[0])) &
    (weekly_metrics.index <= pd.to_datetime(date_range_likes[1]))
]
# 'diggCount'를 Likes로 표시
st.line_chart(weekly_metrics_filtered_likes[['diggCount']].rename(columns={'diggCount': 'Likes'}))

# ========== Shares 차트 ==========
st.subheader("Weekly Shares Trend")
date_range_shares = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="shares_date")
weekly_metrics_filtered_shares = weekly_metrics[
    (weekly_metrics.index >= pd.to_datetime(date_range_shares[0])) &
    (weekly_metrics.index <= pd.to_datetime(date_range_shares[1]))
]
st.line_chart(weekly_metrics_filtered_shares[['shareCount']].rename(columns={'shareCount': 'Shares'}))

# ========== Comments 차트 ==========
st.subheader("Weekly Comments Trend")
date_range_comments = st.date_input("📅 날짜 필터링", (min_date_metrics, max_date_metrics), key="comments_date")
weekly_metrics_filtered_comments = weekly_metrics[
    (weekly_metrics.index >= pd.to_datetime(date_range_comments[0])) &
    (weekly_metrics.index <= pd.to_datetime(date_range_comments[1]))
]
st.line_chart(weekly_metrics_filtered_comments[['commentCount']].rename(columns={'commentCount': 'Comments'}))
