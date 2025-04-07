# import os
# from dotenv import load_dotenv
# import praw
# from datetime import datetime, timedelta, timezone
# import pandas as pd

# # Load environment variables
# load_dotenv()

# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
#     password=os.getenv("REDDIT_PASSWORD"),
#     username=os.getenv("REDDIT_USERNAME"),
#     user_agent=os.getenv("REDDIT_USER_AGENT")
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV_PATH = os.path.join(BASE_DIR, 'data', 'hoka_subreddit.csv')
# SUBREDDIT_NAME = 'Hoka'
# LIMIT = 1000
# DAYS_BACK = 7

# def get_new_posts(subreddit, days=7, limit=1000):
#     recent = []
#     cutoff = datetime.now(timezone.utc) - timedelta(days=days)

#     for post in reddit.subreddit(subreddit).new(limit=limit):
#         post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
#         if post_time >= cutoff:
#             recent.append({
#                 "id": post.id,
#                 "subreddit": post.subreddit.display_name,
#                 "title": post.title,
#                 "selftext": post.selftext,
#                 "time": post_time,
#                 "score": post.score,
#                 "num_comments": post.num_comments
#             })
#     return pd.DataFrame(recent)

# def load_csv(path):
#     if os.path.exists(path):
#         return pd.read_csv(path)
#     return pd.DataFrame(columns=["id", "subreddit", "title", "selftext", "time", "score", "num_comments"])

# def update():
#     os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

#     old = load_csv(CSV_PATH)
#     new = get_new_posts(SUBREDDIT_NAME, DAYS_BACK, LIMIT)

#     if not old.empty:
#         new = new[~new['id'].isin(old['id'])]

#     if not new.empty:
#         combined = pd.concat([old, new], ignore_index=True)
#         combined["time"] = pd.to_datetime(combined["time"], errors="coerce")
#         combined = combined.drop_duplicates(subset="id", keep="first")
#         combined = combined.sort_values(by="time", ascending=False)
#         combined.to_csv(CSV_PATH, index=False)
#         msg = f"[{datetime.now()}] {len(new)}개의 새로운 포스트가 저장되었습니다.\n"
#     else:
#         msg = f"[{datetime.now()}] 새로운 포스트가 없습니다.\n"

#     with open(os.path.join(BASE_DIR, "run_log.txt"), "a", encoding="utf-8") as f:
#         f.write(msg)

#     print(msg.strip())

# if __name__ == "__main__":
#     update()

import os
from dotenv import load_dotenv
import praw
from datetime import datetime, timedelta, timezone
import pandas as pd

# ✅ 프로젝트 루트 기준 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")
CSV_PATH = os.path.join(DATA_DIR, "hoka_subreddit.csv")

# ✅ 환경변수 로드 (루트에 .env가 있는 경우)
load_dotenv(os.path.join(BASE_DIR, ".env"))

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    username=os.getenv("REDDIT_USERNAME"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

SUBREDDIT_NAME = 'Hoka'
LIMIT = 1000
DAYS_BACK = 7

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

def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["id", "subreddit", "title", "selftext", "time", "score", "num_comments"])

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

if __name__ == "__main__":
    update()