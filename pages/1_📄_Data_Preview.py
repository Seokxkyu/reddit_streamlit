import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="📄 Data Preview",
    layout="wide" 
)

st.title("📄 Data Preview")

@st.cache_data
def load_data():
    hoka_posts = r"C:\Users\rootn\OneDrive\Desktop\Reddit\data\hoka_subreddit.csv"
    subreddit_posts = r"C:\Users\rootn\OneDrive\Desktop\Reddit\data\hoka_posts.csv"
    posts = pd.read_csv(hoka_posts)
    subreddits = pd.read_csv(subreddit_posts)
    
    posts["time"] = pd.to_datetime(posts["time"], errors="coerce")
    subreddits["time"] = pd.to_datetime(subreddits["time"], errors="coerce")
    return posts, subreddits

hoka_posts, subreddit_posts = load_data()

tab1, tab2 = st.tabs(["📄 Hoka Posts", "📄 Subreddits"])

# ✅ Hoka Posts Tab
with tab1:
    st.markdown("### r/Hoka 게시글 미리보기")

    if st.checkbox("📅 날짜 선택"):
        min_date = hoka_posts["time"].min().date()
        max_date = hoka_posts["time"].max().date()
        start_date, end_date = st.date_input("날짜 선택", (min_date, max_date), min_value=min_date, max_value=max_date, key="hoka_date")
        
        hoka_filtered = hoka_posts[
            (hoka_posts["time"].dt.date >= start_date) &
            (hoka_posts["time"].dt.date <= end_date)
        ]
    else:
        hoka_filtered = hoka_posts

    st.write(f"🔎 총 {len(hoka_filtered)}개 항목 표시 중")
    st.dataframe(hoka_filtered)


# ✅ Subreddits Tab
with tab2:
    st.markdown("### 기타 서브레딧 게시글 미리보기")

    # 서브레딧 필터
    if st.checkbox("🔍 서브레딧 필터링"):
        unique_subreddits = sorted(subreddit_posts['subreddit'].dropna().unique())
        selected_subs = st.multiselect("서브레딧 선택", unique_subreddits, default=unique_subreddits[:1])
    else:
        selected_subs = None

    # 날짜 필터
    if st.checkbox("📅 날짜 필터링"):
        min_date = subreddit_posts["time"].min().date()
        max_date = subreddit_posts["time"].max().date()
        start_date, end_date = st.date_input("날짜 선택", (min_date, max_date), min_value=min_date, max_value=max_date, key="subreddit_date")
    else:
        start_date, end_date = None, None

    filtered_df = subreddit_posts.copy()

    if selected_subs:
        filtered_df = filtered_df[filtered_df["subreddit"].isin(selected_subs)]

    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["time"].dt.date >= start_date) &
            (filtered_df["time"].dt.date <= end_date)
        ]

    st.write(f"🔎 총 {len(filtered_df)}개 항목 표시 중")
    st.dataframe(filtered_df)