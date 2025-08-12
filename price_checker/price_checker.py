# src/price_checker.py
import os, re, json, time, logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # 実値は.envに
DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "PriceChecker/1.0 (+https://github.com/<yourname>; purpose=portfolio)"
}

SITES = [
    {
        "name": "ダーツハイブ",
        "url": "https://www.dartshive.jp/shopdetail/000000030962/",
        "find_tag": "strong",
        "find_attrs": {"id": "btocOnly"},
    },
    {
        "name": "TiTO",
        "url": "https://www.tito-shop.com/product/detail/st-tit-004-",
        "find_tag": "span",
        "find_attrs": {"class": "discount_value"},
    },
]

def extract_price(text: str) -> str:
    t = text.replace(",", "").replace("\n", "")
    m = re.search(r"\d{3,}", t)  # 3桁以上の数値を価格候補として抽出
    return m.group(0) if m else "価格取得失敗"

def get_price(url, find_tag, find_attrs, timeout=10):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)  # verify=True (デフォルト)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find(find_tag, find_attrs)
        if tag:
            return extract_price(tag.get_text())
        return "価格取得失敗"
    except Exception as e:
        logging.warning("Error fetching %s: %s", url, e)
        return "価格取得失敗"

def load_prev(site_name: str) -> str:
    f = DATA_DIR / f"price_{site_name}.txt"
    return f.read_text(encoding="utf-8") if f.exists() else ""

def save_curr(site_name: str, price: str):
    (DATA_DIR / f"price_{site_name}.txt").write_text(price, encoding="utf-8")

def main(sites=SITES, sleep_sec=1):
    for s in sites:
        name, url = s["name"], s["url"]
        curr = get_price(url, s["find_tag"], s["find_attrs"])
        prev = load_prev(name)
        print(f"[{name}] 現在: {curr} / 前回: {prev or '(なし)'}")
        if prev and curr not in ("価格取得失敗", prev) and curr != "":
            msg = {
                "site": name, "url": url,
                "previous": prev, "current": curr,
                "event": "price_changed"
            }
            print("価格変更:", json.dumps(msg, ensure_ascii=False))
            # ここでWebhook送信（環境変数がある時だけ）
            # if DISCORD_WEBHOOK_URL: requests.post(DISCORD_WEBHOOK_URL, json={"content": str(msg)}, timeout=10)
        save_curr(name, curr)
        time.sleep(sleep_sec)

if __name__ == "__main__":
    main()
