import requests
from bs4 import BeautifulSoup
import os
import json
import time

def send_discord_webhook(webhook_url, message):
    """DiscordのWebhookにメッセージを送信する関数"""
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status() # HTTPエラーが発生した場合に例外を発生
        print("Discordへの通知に成功しました。")
    except requests.exceptions.RequestException as e:
        print(f"Discordへの通知でエラーが発生しました: {e}")

def get_price(url, find_tag, find_attrs):
    """汎用的な価格取得関数"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(find_tag, find_attrs)
        
        if not price_tag:
            print(f"価格タグが見つかりませんでした: {find_tag}, {find_attrs}")
            return "価格取得失敗"

        # 価格文字列のクリーニング
        price_text = price_tag.text.replace(",", "").replace("\n", "").replace("円（税込）","").replace("税込:","").replace("円(税抜:"," ").split()[0].strip()
        
        # 取得した価格が数字として扱えるか確認
        if price_text.isdigit():
            return price_text
        else:
            print(f"取得した価格が不正な形式です: {price_text}")
            return "価格取得失敗"

    except requests.exceptions.RequestException as e:
        print(f"{url} の価格取得でリクエストエラー: {e}")
    except Exception as e:
        print(f"{url} の価格取得で予期せぬエラー: {e}")
        
    return "価格取得失敗"

def main():
    """メインの実行関数"""
    # 設定ファイルからサイト情報を読み込む
    try:
        with open('sites.json', 'r', encoding='utf-8') as f:
            sites_to_check = json.load(f)
    except FileNotFoundError:
        print("sites.json が見つかりませんでした。ファイルを作成してください。")
        return
    except json.JSONDecodeError:
        print("sites.json の形式が不正です。JSON形式で記述してください。")
        return

    # ディレクトリの準備
    DATA_DIR = "price_data"
    os.makedirs(DATA_DIR, exist_ok=True)

    # Discord Webhook URLの設定
    DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', 'YOUR_WEBHOOK_URL_HERE')
    if DISCORD_WEBHOOK_URL == 'YOUR_WEBHOOK_URL_HERE':
        print("警告: Discord Webhook URLが設定されていません。環境変数 'DISCORD_WEBHOOK_URL' を設定するか、コード内のプレースホルダーを置き換えてください。")
    
    for site in sites_to_check:
        site_name = site["name"]
        print(f"--- {site_name} の価格チェック開始 ---")
        
        current_price = get_price(site["url"], site["find_tag"], site["find_attrs"])
        price_file = os.path.join(DATA_DIR, f"price_{site_name}.txt")
        
        previous_price = ""
        if os.path.exists(price_file):
            with open(price_file, "r") as f:
                previous_price = f.read()

        print(f"現在の価格: {current_price}")
        print(f"前回の価格: {previous_price}")

        if previous_price and current_price != "価格取得失敗" and current_price != previous_price:
            message = f"【価格変更通知】\nサイト: {site_name}\n\n前回の価格: {previous_price}\n現在の価格: {current_price}\n商品ページ: {site['url']}"
            print(message)
            send_discord_webhook(DISCORD_WEBHOOK_URL, message)
        else:
            print("価格の変更はありません。")

        with open(price_file, "w") as f:
            f.write(current_price)
        
        print("-" * 25)
        time.sleep(1)

if __name__ == "__main__":
    main()