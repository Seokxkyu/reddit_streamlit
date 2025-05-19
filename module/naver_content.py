import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "debate")

def extract_body(url: str) -> str:
    if not url:
        return ""
    try:
        resp = requests.get(url, headers=HEADERS)
        resp.encoding = "euc-kr"
        soup = BeautifulSoup(resp.text, "lxml")
        body_div = soup.find("div", id="body", class_="view_se")
        if body_div:
            return body_div.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def update_bodies(code: str, delay: float = 0.7):
    csv_path = os.path.join(DATA_DIR, f"{code}_board.csv")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    if "content" not in df.columns:
        df["content"] = ""

    empty = df["content"].isnull() | (df["content"] == "")
    for idx, row in df.loc[empty].iterrows():
        url = row.get("url", "")
        df.at[idx, "content"] = extract_body(url)
        time.sleep(delay)

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")