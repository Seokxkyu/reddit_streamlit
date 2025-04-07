import os
import pandas as pd
import praw
from datetime import datetime, timedelta, timezone

# ✅ Streamlit Cloud와 로컬 환경 모두 호환
try:
    import streamlit as st
    secrets = st.secrets
except:
    from dotenv import load_dotenv
    load_dotenv()
    secrets = os.environ

# ✅ praw 인스턴스 생성
reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    username=secrets["USERNAME"],
    password=secrets["PASSWORD"],
    user_agent=secrets["REDDIT_USER_AGENT"]
)

# ✅ 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")
CSV_PATH = os.path.join(DATA_DIR, "hoka_subreddit.csv")

SUBREDDIT_NAME = 'Hoka'
LIMIT = 1000
DAYS_BACK = 7

# ✅ 게시글 가져오기

def get_new_posts(subreddit, days=7, limit=1000):
    recent = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for post in reddit.subreddit(subreddit).new(limit=limit):
        post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        if post_time >= cutoff:
            recent.append({
                "id": post.id,
                "subreddit": post.subreddit.display_name,
                "title": post.title,
                "selftext": post.selftext,
                "time": post_time,
                "score": post.score,
                "num_comments": post.num_comments
            })
    return pd.DataFrame(recent)

# ✅ CSV 로드

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["id", "subreddit", "title", "selftext", "time", "score", "num_comments"])

# ✅ 업데이트 함수

def update():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    old = load_csv(CSV_PATH)
    new = get_new_posts(SUBREDDIT_NAME, DAYS_BACK, LIMIT)

    if not old.empty:
        new = new[~new['id'].isin(old['id'])]

    if not new.empty:
        combined = pd.concat([old, new], ignore_index=True)
        combined["time"] = pd.to_datetime(combined["time"], errors="coerce")
        combined = combined.drop_duplicates(subset="id", keep="first")
        combined = combined.sort_values(by="time", ascending=False)
        combined.to_csv(CSV_PATH, index=False)
        msg = f"[{datetime.now()}] {len(new)}개의 새로운 포스트가 저장되었습니다.\n"
    else:
        msg = f"[{datetime.now()}] 새로운 포스트가 없습니다.\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)

    print(msg.strip())

# ✅ CLI 실행용
if __name__ == "__main__":
    update()