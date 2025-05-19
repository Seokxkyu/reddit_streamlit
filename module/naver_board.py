import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_DIR = os.path.join(BASE_DIR, "data", "debate")
LOG_PATH = os.path.join(BASE_DIR, "naver_board_log.txt")

def crawl_page(page, threshold, code, existing_urls=None):
    base = "https://finance.naver.com"
    url = f"{base}/item/board.naver?code={code}&page={page}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.encoding = "euc-kr"
    soup = BeautifulSoup(r.text, "lxml")
    
    content_div = soup.find("div", id="content")
    if content_div is None:
        return [], False
    table = content_div.find("table", class_="type2")
    if table is None:
        return [], False
    
    data, stop = [], False
    for row in table.find_all("tr", attrs={"onmouseover": True}):
        cells = row.find_all("td")
        if len(cells) < 6:
            continue
        dt_str = cells[0].get_text(strip=True)
        try:
            post_dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M")
        except Exception:
            continue
        # 게시글 제목 및 URL 추출
        link_tag = cells[1].find("a")
        if link_tag:
            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "")
            full_url = base + href if href.startswith("/") else href
            
            # URL에서 오직 code와 nid 파라미터만 사용
            if full_url:
                parsed_url = urlparse(full_url)
                qs = parse_qs(parsed_url.query)
                new_qs = {}
                if 'code' in qs:
                    new_qs['code'] = qs['code'][0]
                if 'nid' in qs:
                    new_qs['nid'] = qs['nid'][0]
                new_query = urlencode(new_qs)
                full_url = urlunparse((
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    new_query,
                    parsed_url.fragment
                ))
        else:
            title = cells[1].get_text(strip=True)
            full_url = ""
        # 기준 날짜보다 이전이거나 이미 등록된 URL이면 중단
        if post_dt < threshold or (existing_urls and full_url in existing_urls):
            stop = True
            break
        data.append({
            "date": post_dt,   # datetime 객체
            "title": title,
            "url": full_url,
            "writer": cells[2].get_text(strip=True),
            "view": cells[3].get_text(strip=True),
            "like": cells[4].get_text(strip=True),
            "dislike": cells[5].get_text(strip=True)
        })
    return data, stop

def update(code, threshold_str):  # removed max_pages parameter
    threshold = datetime.strptime(threshold_str, "%Y.%m.%d %H:%M")
    csv_path = os.path.join(DATA_DIR, f"{code}_board.csv")
    
    # 기존 CSV가 존재하면 로드 후 URL 집합 생성, 아니면 빈 DataFrame
    if os.path.exists(csv_path):
        old_df = pd.read_csv(csv_path, encoding="utf-8-sig")
        old_df["date"] = pd.to_datetime(old_df["date"])
        existing_urls = set(old_df["url"])
    else:
        old_df = pd.DataFrame()
        existing_urls = set()
    
    new_posts = []
    page = 1
    while True:
        page_data, should_stop = crawl_page(page, threshold, code, existing_urls)
        new_posts.extend(page_data)
        if should_stop or not page_data:
            break
        page += 1
        time.sleep(0.7)
    
    df_new = pd.DataFrame(new_posts)
    if not old_df.empty:
        df_combined = pd.concat([df_new, old_df], ignore_index=True)
        df_combined.drop_duplicates(subset=["url"], inplace=True)
    else:
        df_combined = df_new

    os.makedirs(DATA_DIR, exist_ok=True)
    df_combined.sort_values("date", ascending=False, inplace=True)
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    log_msg = (f"[{datetime.now()}] [종목코드: {code}] {len(df_new)}개 신규 게시글 추가 수집됨, "
               f"누적 데이터 {len(df_combined)}개\n")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_msg)
    print(log_msg.strip())
    return df_combined

if __name__ == "__main__":
    if len(sys.argv) > 2:
        code = sys.argv[1]
        threshold_date = sys.argv[2]
        update(code, threshold_date)
    else:
        print("사용법: python naver_board.py 종목코드 'YYYY.MM.DD HH:MM'")