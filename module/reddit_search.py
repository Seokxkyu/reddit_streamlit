# import os
# import sys
# import time
# from dotenv import load_dotenv
# import praw
# from datetime import datetime, timezone
# import pandas as pd

# load_dotenv()

# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
#     password=os.getenv("REDDIT_PASSWORD"),
#     username=os.getenv("REDDIT_USERNAME"),
#     user_agent=os.getenv("REDDIT_USER_AGENT")
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_PATH = os.path.join(BASE_DIR, 'run_log.txt')
# LIMIT = 500

# def get_new_posts(keyword, limit=LIMIT):
#     results = []

#     try:
#         for post in reddit.subreddit("all").search(keyword, sort="new", limit=limit):
#             post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
#             results.append({
#                 "id": post.id,
#                 "subreddit": post.subreddit.display_name,
#                 "title": post.title,
#                 "selftext": post.selftext,
#                 "time": post_time,
#                 "score": post.score,
#                 "num_comments": post.num_comments
#             })
#         time.sleep(2)
#     except Exception as e:
#         print(f"🔴 Error during fetching: {e}")

#     return pd.DataFrame(results)

# def load_csv(path):
#     if os.path.exists(path):
#         return pd.read_csv(path, parse_dates=["time"])
#     return pd.DataFrame()

# def update(keyword):
#     keyword_safe = keyword.lower().replace(" ", "_")
#     csv_path = os.path.join(BASE_DIR, "data", f"{keyword_safe}_posts.csv")
#     os.makedirs(os.path.dirname(csv_path), exist_ok=True)

#     old = load_csv(csv_path)
#     new = get_new_posts(keyword)

#     if not old.empty:
#         before = len(new)
#         new = new[~new['id'].isin(old['id'])]
#         duplicates = before - len(new)
#     else:
#         duplicates = 0

#     if not new.empty:
#         combined = pd.concat([old, new], ignore_index=True)
#         combined = combined.sort_values("time", ascending=False)
#         combined.to_csv(csv_path, index=False)
#         msg = f"[{datetime.now()}] [{keyword}] {len(new)}개 저장 / 중복 {duplicates}개 제거\n"
#     else:
#         old = old.sort_values("time", ascending=False)
#         old.to_csv(csv_path, index=False)
#         msg = f"[{datetime.now()}] [{keyword}] 새로운 포스트 없음 / 중복 {duplicates}개\n"

#     with open(LOG_PATH, "a", encoding="utf-8") as f:
#         f.write(msg)

#     print(msg.strip())

# # ✅ 실행 시 키워드 입력 받기
# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         update(sys.argv[1])
#     else:
#         print("❗ 키워드를 입력하세요. 예: python keyword_scraper.py hoka")

import os
import sys
import time
from dotenv import load_dotenv
import praw
from datetime import datetime, timezone
import pandas as pd

# ✅ 프로젝트 루트 기준 경로로 수정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")

# ✅ 루트에서 .env 명시적으로 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    username=os.getenv("REDDIT_USERNAME"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

LIMIT = 500

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

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])
    return pd.DataFrame()

def update(keyword):
    keyword_safe = keyword.lower().replace(" ", "_")
    csv_path = os.path.join(DATA_DIR, f"{keyword_safe}_posts.csv")
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
        msg = f"[{datetime.now()}] [{keyword}] {len(new)}개 저장 / 중복 {duplicates}개 제거\n"
    else:
        old = old.sort_values("time", ascending=False)
        old.to_csv(csv_path, index=False)
        msg = f"[{datetime.now()}] [{keyword}] 새로운 포스트 없음 / 중복 {duplicates}개\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg)

    print(msg.strip())

# ✅ 실행 시 키워드 입력 받기
if __name__ == "__main__":
    if len(sys.argv) > 1:
        update(sys.argv[1])
    else:
        print("❗ 키워드를 입력하세요. 예: python reddit_search.py hoka")
