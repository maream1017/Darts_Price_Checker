# Price Checker (Darts)

ダーツ関連ECの価格を定期チェックし、前回から変化があれば通知します。  
ポートフォリオ向けの最小実装で、サイトの構成変化に強い価格抽出と、Webhook通知（任意）を備えています。

## 特徴
- 複数サイトの価格を取得して前回値と比較
- 取得失敗/セレクタ変更を検知してログ出力
- Webhook（Discordなど）での通知に対応（任意）
- `.env` で秘密情報を管理、`data/` に履歴保存

## セットアップ
```bash
git clone <YOUR_REPO_URL>
cd my-python-project
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # 必要ならWebhook URLを設定
mkdir -p data
```

## 使い方
```bash
python src/price_checker.py
```
出力例：
```
[ダーツハイブ] 現在: 12800 / 前回: 12600
価格変更: {"site":"ダーツハイブ","previous":"12600","current":"12800","event":"price_changed"}
```

## 環境変数（任意）
`.env`
```
DISCORD_WEBHOOK_URL= # 空のままでOK。使うときだけ設定
```

## 設定（監視対象の追加）
`src/price_checker.py` の `SITES` に辞書を追加してください。
```python
SITES = [
  {"name": "ダーツハイブ", "url": "...", "find_tag": "strong", "find_attrs": {"id": "btocOnly"}},
  {"name": "TiTO", "url": "...", "find_tag": "span", "find_attrs": {"class": "discount_value"}},
]
```

## 注意事項（必読）
- 対象サイトの **利用規約 / robots.txt** に従ってください。
- リクエストの間隔を空け、過度なアクセスはしないでください。
- 本ツールは学習・検証目的のサンプルです。利用は自己責任でお願いします。

## ライセンス
MIT
