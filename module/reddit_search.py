# 핵심 기능:
#   지정된 서브레딧에서 주어진 키워드를 기반으로 게시글을 검색하고,
#   새로운 게시글을 CSV 파일에 업데이트한 후 로그를 기록합니다.
#
# 주요 파라미터:
#   get_new_posts(keyword, subreddit, limit): 서브레딧에서 게시글을 검색 후 DataFrame 반환.
#   update(search_subreddit, keyword, csv_filename_base): CSV 업데이트 및 로그 기록.

import os
import sys
import time
import pandas as pd
import praw
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    import streamlit as st
    if hasattr(st, "secrets") and "REDDIT_CLIENT_ID" in st.secrets:
        secrets = st.secrets
        IS_STREAMLIT = True
    else:
        raise ImportError("Streamlit secrets not configured properly.")
except:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    secrets = os.environ

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")
LIMIT = 500

reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    username=secrets["USERNAME"],
    password=secrets["PASSWORD"],
    user_agent=secrets["REDDIT_USER_AGENT"]
)

def load_csv(path):
    """
    주어진 경로의 CSV 파일을 DataFrame으로 로드합니다.
    (시간 컬럼은 datetime으로 파싱)
    """
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])
    return pd.DataFrame()

def get_new_posts(keyword, subreddit="all", limit=LIMIT):
    """
    지정된 subreddit(기본: "all")에서, 입력받은 keyword를 기준으로 최신 게시글을 검색하여
    DataFrame으로 반환합니다.
    """
    results = []
    try:
        for post in reddit.subreddit(subreddit).search(keyword, sort="new", limit=limit):
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

def update(search_subreddit="all", keyword="hoka", csv_filename_base=None):
    """
    [매개변수]
      - search_subreddit: 검색 대상 서브레딧 (기본: "all")
      - keyword: 검색어 (기본: "hoka")
      - csv_filename_base: CSV 파일명 기본이름; 미지정 시 keyword 기반 파일("hoka_posts.csv") 사용,
                            지정 시 data/{csv_filename_base}_posts.csv 형식으로 저장.

    CSV 파일에 새로운 포스트를 추가하고, 작업 결과를 로그에 기록합니다.
    """

    if csv_filename_base is None:
        csv_path = os.path.join(DATA_DIR, f"{keyword.lower().replace(' ', '_')}_posts.csv")
        display_name = keyword.lower().replace(" ", "_")
    else:
        csv_path = os.path.join(DATA_DIR, f"{csv_filename_base.lower()}_posts.csv")
        display_name = csv_filename_base.lower()

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    old = load_csv(csv_path)
    new = get_new_posts(keyword, subreddit=search_subreddit)

    if not old.empty:
        before = len(new)
        new = new[~new['id'].isin(old['id'])]
        duplicates = before - len(new)
    else:
        duplicates = 0

    if not new.empty:
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.sort_values("time", ascending=False)
        combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
        msg = f"[{datetime.now()}] [Subreddit: {search_subreddit}] [{display_name}] {len(new)}개 저장 / 중복 {duplicates}개 제거\n"
    else:
        if not old.empty:
            old = old.sort_values("time", ascending=False)
            old.to_csv(csv_path, index=False, encoding="utf-8-sig")
        msg = f"[{datetime.now()}] [Subreddit: {search_subreddit}] [{display_name}] 새로운 포스트 없음 / 중복 {duplicates}개\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)

    print(msg.strip())

# CLI 실행용 예시:
#   기본 실행 (기본 서브레딧 "all", 기본 검색어 "hoka"):
#       python reddit_search.py
#   서브레딧, 검색어, 그리고 CSV 파일 기본이름 지정:
#       python reddit_search.py sports baseball sports_posts

if __name__ == "__main__":
    # CLI 인수:
    #   1번째 인수 (optional): 검색 대상 subreddit (기본: "all")
    #   2번째 인수 (optional): 검색 대상 keyword (기본: "hoka")
    #   3번째 인수 (optional): CSV 파일명 기본이름 (미지정 시 keyword 기반 파일 사용)
    args = sys.argv[1:]
    search_subreddit = args[0] if len(args) > 0 else "all"
    keyword = args[1] if len(args) > 1 else "hoka"
    csv_filename_base = args[2] if len(args) > 2 else None
    update(search_subreddit=search_subreddit, keyword=keyword, csv_filename_base=csv_filename_base)