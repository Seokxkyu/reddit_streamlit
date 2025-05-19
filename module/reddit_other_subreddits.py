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
CSV_PATH = os.path.join(DATA_DIR, "hoka_posts.csv")  # 기본 CSV 파일 경로
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")

# 기본값 설정
KEYWORD = "hoka"
DAYS_BACK = 7
LIMIT = 250

# ✅ PRAW 인스턴스 생성
reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    password=secrets["PASSWORD"],
    username=secrets["USERNAME"],
    user_agent=secrets["REDDIT_USER_AGENT"]
)

def get_new_posts(keyword=KEYWORD, days=DAYS_BACK, limit=LIMIT):
    """
    입력받은 키워드로 reddit의 모든 서브레딧에서 최신 게시글을 검색하여 DataFrame으로 반환
    """
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
    except Exception as e:
        print(f"🔴 Error during fetching: {e}")
    
    return pd.DataFrame(results)

def load_csv(path):
    """
    지정 경로의 CSV 파일을 DataFrame으로 로드 (시간 컬럼은 datetime으로 파싱)
    """
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])
    return pd.DataFrame()

def update(csv_filename=None, keyword=KEYWORD):
    """
    CSV 파일명과 검색 키워드를 받아,
    해당 CSV 파일에 새로운 포스트를 업데이트하고 로그에 기록합니다.
    
    - csv_filename 인수가 제공되지 않으면 기본 CSV_PATH (즉, "hoka_posts.csv")를 사용합니다.
    - 검색 키워드 기본값은 'hoka'입니다.
    """
    # csv_filename 이 없으면 CSV_PATH 를 사용
    if csv_filename is None:
        csv_path = CSV_PATH
        display_csv_name = os.path.basename(CSV_PATH).replace("_posts.csv", "")
    else:
        csv_path = os.path.join(DATA_DIR, f"{csv_filename.lower()}_posts.csv")
        display_csv_name = csv_filename.lower()
        
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
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
        msg = f"[{datetime.now()}] [{display_csv_name}] - 키워드 '{keyword}'로 {len(new)}개의 새로운 포스트 저장. / 중복 {duplicates}개 제거.\n"
    else:
        if not old.empty:
            old = old.sort_values("time", ascending=False)
            old.to_csv(csv_path, index=False)
        msg = f"[{datetime.now()}] [{display_csv_name}] - 키워드 '{keyword}'로 새로운 포스트 없음. / 중복 {duplicates}개.\n"
    
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)
    
    print(msg.strip())

if __name__ == "__main__":
    import sys
    # 첫 번째 인수: CSV 파일명, 두 번째 인수: 검색 키워드.
    # 둘 다 제공하지 않으면 기본값으로 CSV_PATH ("hoka_posts.csv")와 검색 키워드 "hoka"를 사용합니다.
    csv_name = sys.argv[1] if len(sys.argv) > 1 else None
    search_keyword = sys.argv[2] if len(sys.argv) > 2 else KEYWORD
    update(csv_filename=csv_name, keyword=search_keyword)