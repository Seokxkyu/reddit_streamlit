# ✅ CLI 실행 예시:
#   기본 실행 (기본 서브레딧 "hoka"):
#       python reddit_search_subreddit.py hoka
#   서브레딧 이름을 변경하여 실행:
#       python reddit_search_subreddit.py askreddit
#   댓글까지 함께 수집:
#       python reddit_search_subreddit.py hoka --with-comments

import os
import sys
import time
import pandas as pd
import praw
from datetime import datetime, timezone, timedelta   

try:
    import streamlit as st
    if hasattr(st, "secrets") and "REDDIT_CLIENT_ID" in st.secrets:
        secrets = st.secrets
        IS_STREAMLIT = True
    else:
        raise ImportError
except ImportError:
    from dotenv import load_dotenv
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    secrets = os.environ

reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    username=secrets["USERNAME"],
    password=secrets["PASSWORD"],
    user_agent=secrets["REDDIT_USER_AGENT"]
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(BASE_DIR, "run_log.txt")

LIMIT        = 1000   # 최대 게시글 수 
DAYS_WINDOW  = 7      # 최근 일수 

def get_new_posts(subreddit: str, days_window: int = DAYS_WINDOW, limit: int = LIMIT) -> pd.DataFrame:
    """
    지정한 서브레딧에서 최근 `days_window`일 이내의 게시글을
    최대 `limit`개까지 가져와 DataFrame으로 반환.
    """
    cutoff  = datetime.now(timezone.utc) - timedelta(days=days_window)
    results = []
    
    try:
        for post in reddit.subreddit(subreddit).new(limit=None):
            post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
            if post_time < cutoff:
                break                     
            results.append({
                "id": post.id,
                "subreddit": post.subreddit.display_name,
                "title": post.title,
                "selftext": post.selftext,
                "time": post_time,
                "score": post.score,
                "num_comments": post.num_comments
            })
            if len(results) >= limit:    
                break
        time.sleep(1.5)                      
    except Exception as e:
        print(f"🔴 Error during fetching posts: {e}")

    return pd.DataFrame(results)

def get_comments_for_posts(posts_df: pd.DataFrame, existing_comment_ids=None) -> pd.DataFrame:
    if existing_comment_ids is None:
        existing_comment_ids = set()

    comments = []
    for _, row in posts_df.iterrows():
        post_id = row["id"]
        try:
            submission = reddit.submission(id=post_id)
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                if comment.id in existing_comment_ids:
                    continue  
                comment_time = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                comments.append({
                    "post_id": post_id,
                    "comment_id": comment.id,
                    "comment_author": str(comment.author),
                    "comment_body": comment.body,
                    "comment_time": comment_time,
                    "comment_score": comment.score
                })
            time.sleep(1.5)
        except Exception as e:
            print(f"Error getting comments for post {post_id}: {e}")

    return pd.DataFrame(comments)

def update(subreddit: str, collect_comments: bool = False):
    """
    서브레딧 데이터를 CSV로 저장하고 로그를 기록.
    댓글 수집 여부는 collect_comments 플래그로 제어.
    """
    subreddit_safe = subreddit.lower().replace(" ", "_")
    posts_csv_path = os.path.join(DATA_DIR, f"{subreddit_safe}_subreddit.csv")
    comments_csv_path = os.path.join(DATA_DIR, f"{subreddit_safe}_comments.csv")
    os.makedirs(DATA_DIR, exist_ok=True)

    new_posts = get_new_posts(subreddit)
    new_posts_count = len(new_posts)

    if os.path.exists(posts_csv_path):
        old_posts = pd.read_csv(posts_csv_path, encoding="utf-8-sig")
        old_posts["time"] = pd.to_datetime(old_posts["time"])
        old_posts_count = len(old_posts)

        combined_posts = (
            pd.concat([old_posts, new_posts], ignore_index=True).drop_duplicates(subset=["id"]).sort_values("time", ascending=False)
        )
        new_posts_added = len(combined_posts) - old_posts_count
    else:
        combined_posts = new_posts
        new_posts_added = new_posts_count

    combined_posts.to_csv(posts_csv_path, index=False, encoding="utf-8-sig")

    if collect_comments:
        if os.path.exists(comments_csv_path):
            old_comments = pd.read_csv(comments_csv_path, encoding="utf-8-sig")
            old_comments["comment_time"] = pd.to_datetime(old_comments["comment_time"])
            existing_ids = set(old_comments["comment_id"])
            old_count = len(old_comments)
        else:
            old_comments = pd.DataFrame()
            existing_ids = set()
            old_count = 0

        new_comments = get_comments_for_posts(new_posts, existing_comment_ids=existing_ids)

        if not old_comments.empty:
            combined_comments = (pd.concat([old_comments, new_comments], ignore_index=True).drop_duplicates(subset=["comment_id"]))
            new_comments_added = len(combined_comments) - old_count
        else:
            combined_comments  = new_comments
            new_comments_added = len(new_comments)

        combined_comments.to_csv(comments_csv_path, index=False, encoding="utf-8-sig")
    else:
        new_comments_added = 0

    log_msg = (f"[{datetime.now()}] [{subreddit}] "
               f"게시글 {new_posts_added}개 추가(총 {len(combined_posts)}개), "
               f"댓글 {new_comments_added}개 추가.\n")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_msg)
    print(log_msg.strip())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        subreddit_name  = sys.argv[1]
        collect_comments = "--with-comments" in sys.argv[2:]
        update(subreddit_name, collect_comments)
    else:
        print("❗ 서브레딧 이름을 입력하세요. 예: python reddit_search_subreddit.py hoka [--with-comments]")
