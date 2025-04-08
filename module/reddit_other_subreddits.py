import os
import time
from datetime import datetime, timedelta, timezone
import pandas as pd
import praw
from dotenv import load_dotenv

# ✅ 루트 기준 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ 환경 변수 로드: Streamlit 우선, 없으면 .env 처리
try:
    import streamlit as st
    required_keys = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "PASSWORD", "USERNAME", "REDDIT_USER_AGENT"]
    if hasattr(st, "secrets") and all(key in st.secrets for key in required_keys):
        secrets = st.secrets
    else:
        raise ImportError("Streamlit secrets not configured properly.")
except Exception as e:
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    secrets = {}
    missing = []
    for key in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "PASSWORD", "USERNAME", "REDDIT_USER_AGENT"]:
        value = os.environ.get(key)
        if not value:
            missing.append(key)
        secrets[key] = value
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

# ✅ 경로 설정
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "hoka_posts.csv")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")

# ✅ PRAW 인스턴스 생성
reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    password=secrets["PASSWORD"],
    username=secrets["USERNAME"],
    user_agent=secrets["REDDIT_USER_AGENT"]
)

KEYWORD = "hoka"
DAYS_BACK = 7
LIMIT = 250

def get_new_posts(keyword=KEYWORD, days=DAYS_BACK, limit=LIMIT):
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    try:
        for post in reddit.subreddit("all").search(keyword, sort="new", limit=limit):
            post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            if post_time >= cutoff:
                results.append({
                    "id": post.id,
                    "subreddit": post.subreddit.display_name,
                    "title": post.title,
                    "selftext": post.selftext,
                    "time": post_time,
                    "score": post.score,
                    "num_comments": post.num_comments
                })
        time.sleep(2)
    except:
        pass

    return pd.DataFrame(results)

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])
    return pd.DataFrame()

def update():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    old = load_csv(CSV_PATH)
    new = get_new_posts()

    if not old.empty:
        before = len(new)
        new = new[~new['id'].isin(old['id'])]
        duplicates = before - len(new)
    else:
        duplicates = 0

    if not new.empty:
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.sort_values("time", ascending=False)
        combined.to_csv(CSV_PATH, index=False)
        msg = f"[{datetime.now()}] {len(new)}개의 새로운 포스트가 저장되었습니다. / 중복 {duplicates}개 제거.\n"
    else:
        old = old.sort_values("time", ascending=False)
        old.to_csv(CSV_PATH, index=False)
        msg = f"[{datetime.now()}] 새로운 포스트가 없습니다. 중복 {duplicates}개.\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)

    print(msg.strip())

if __name__ == "__main__":
    update()