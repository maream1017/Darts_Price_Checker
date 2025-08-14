#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, json, time, logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "PriceChecker/1.0 (+https://github.com/maream1017; purpose=portfolio)"
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

def _sanitize(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", name)

def extract_price(text: str) -> str:
    t = text.replace(",", "").replace("\n", "")
    t = t.replace("円（税込）", "").replace("税込:", "").replace("円(税抜:", " ")
    m = re.search(r"\d{3,}", t)
    if m:
        return m.group(0)
    else:
        raise ValueError("価格抽出失敗")

def get_price(url: str, find_tag: str, find_attrs: dict) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find(find_tag, find_attrs)
        if tag:
            return extract_price(tag.get_text())
    except ValueError as e:
        raise e
    
def send_webhook(message: dict) -> None:
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": json.dumps(message, ensure_ascii=False)}, timeout=10)
    except Exception as e:
        logging.warning("Webhook送信失敗: %s", e)

def load_prev(site_name: str) -> str:
    f = DATA_DIR / f"price_{_sanitize(site_name)}.txt"
    return f.read_text(encoding="utf-8") if f.exists() else ""

def save_curr(site_name: str, price: str) -> None:
    (DATA_DIR / f"price_{_sanitize(site_name)}.txt").write_text(price, encoding="utf-8")

def check_prices(sites=SITES):
    for s in sites:
        name, url = s["name"], s["url"]
        try:
            curr = get_price(url, s["find_tag"], s["find_attrs"])
        except ValueError as e:
            logging.warning("%s の価格取得でエラー: %s", name, e)
            msg = {"event":"price_failed","site":name,"url":url,"previous":prev,"current":curr}
            print("価格取得失敗:", json.dumps(msg, ensure_ascii=False))
            send_webhook(msg)
            continue
        
        prev = load_prev(name)
        print(f"[{name}] 現在: {curr} / 前回: {prev or '(なし)'}")

        if prev and curr not in (prev, ""):
            msg = {"event":"price_changed","site":name,"url":url,"previous":prev,"current":curr}
            print("価格変更:", json.dumps(msg, ensure_ascii=False))
            send_webhook(msg)

        save_curr(name, curr)

if __name__ == "__main__":
    while True:
        check_prices()
        print("=== 次のチェックまで8時間待機 ===")
        time.sleep(8 * 60 * 60)