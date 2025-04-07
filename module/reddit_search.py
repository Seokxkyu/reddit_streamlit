import os
import sys
import time
import pandas as pd
import praw
from datetime import datetime, timezone

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
LIMIT = 500

# ✅ 게시글 가져오기

def get_new_posts(keyword, limit=LIMIT):
    results = []
    try:
        for post in reddit.subreddit("all").search(keyword, sort="new", limit=limit):
            post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
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
    except Exception as e:
        print(f"🔴 Error during fetching: {e}")
    return pd.DataFrame(results)

# ✅ CSV 로드

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])
    return pd.DataFrame()

# ✅ 업데이트 함수

def update(keyword):
    keyword_safe = keyword.lower().replace(" ", "_")
    csv_path = os.path.join(DATA_DIR, f"{keyword_safe}_posts.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    print(f"📁 [DEBUG] CSV 저장 경로: {csv_path}")

    old = load_csv(csv_path)
    new = get_new_posts(keyword)

    if not old.empty:
        before = len(new)
        new = new[~new['id'].isin(old['id'])]
        duplicates = before - len(new)
    else:
        duplicates = 0

    if not new.empty:
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.sort_values("time", ascending=False)
        combined.to_csv(csv_path, index=False)
        print(f"✅ [DEBUG] 파일 저장 완료. row 수: {len(combined)}")
        msg = f"[{datetime.now()}] [{keyword}] {len(new)}개 저장 / 중복 {duplicates}개 제거\n"
    else:
        old = old.sort_values("time", ascending=False)
        old.to_csv(csv_path, index=False)
        print("⚠️ [DEBUG] 새로운 포스트 없음")
        msg = f"[{datetime.now()}] [{keyword}] 새로운 포스트 없음 / 중복 {duplicates}개\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)

    print("📝 " + msg.strip())

# ✅ CLI 실행용
if __name__ == "__main__":
    if len(sys.argv) > 1:
        update(sys.argv[1])
    else:
        print("❗ 키워드를 입력하세요. 예: python reddit_search.py hoka")