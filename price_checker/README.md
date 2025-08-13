# Price Checker (Darts)

ダーツ関連ECサイトの価格を定期チェックし、前回との差分があれば通知するツールです。  
趣味での購入検討をきっかけに「価格の上げ下げを自動で追いたい」というニーズから作りました。  
**単一ファイル（`price_checker.py`）で動作**し、常時起動すれば8時間ごとに価格を確認します。

---

## 使える場面
- セールの値下げをすぐ知りたい
- 値段の変動を履歴として残したい
- Discordで通知を受け取りたい（任意）

---

## 主な機能
- 複数サイトの価格を取得し、**前回値と比較して変化を検出**
- HTML構造が変わっても拾えるよう、**簡易フォールバック**でテキスト全体から価格抽出
- **Webhook通知（任意）**：`.env` にURLを設定した場合のみ Discord 等へ通知
- 秘密情報は `.env` で管理、履歴は `data/` に保存

> **「任意」とは？**  
> Webhook を設定しなくてもツールは動作します（標準出力とファイル保存）。  
> Webhook URL を設定すると、価格変化や取得失敗を Discord に通知します。

---

## 動作環境
- Python **3.10以上**（3.10/3.11で動作確認）
- macOS / Windows / Linux いずれも可

---

## セットアップ
```bash
git clone https://github.com/maream1017/my-python-project
cd my-python-project
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Webhook を使う場合のみ（任意）
cp .env.example .env
# .env に以下を記入:
# DISCORD_WEBHOOK_URL=（DiscordのWebhook URL。使わない場合は空でOK）

mkdir -p data