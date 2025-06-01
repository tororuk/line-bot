# Claude API LINE Bot on AWS Lambda

このプロジェクトは、Claude APIを使用したLINE BotをAWS Lambda上で動作させるためのPythonアプリケーションです。

## プロジェクト構造

```
├── src/                    # メインアプリケーションコード
│   └── lambda_function.py  # Lambdaハンドラー
├── tests/                  # テストコード
│   └── test_lambda_handler.py
├── scripts/                # ユーティリティスクリプト
│   ├── local_server.py     # ローカルFlaskサーバー
│   └── test_webhook_sender.py # Webhookテスト送信
├── lambda_function.py      # Lambdaデプロイ用エントリーポイント
├── requirements.txt        # Python依存関係
├── .env.template          # 環境変数テンプレート
├── .gitignore
├── CLAUDE.md              # Claude Code向けガイド
└── README.md              # このファイル
```

## セットアップ手順

### 1. 必要な環境変数

Lambda関数に以下の環境変数を設定してください：

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのチャンネルアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Messaging APIのチャンネルシークレット
- `ANTHROPIC_API_KEY`: Claude APIのAPIキー

### 2. デプロイ手順

1. `lambda_function.py`と`requirements.txt`をzipファイルに圧縮
```bash
pip install -r requirements.txt -t .
zip -r function.zip .
```

2. AWS Lambdaで新しい関数を作成
   - ランタイム: Python 3.11
   - ハンドラー: `lambda_function.lambda_handler`
   - タイムアウト: 30秒（推奨）

3. 作成したzipファイルをアップロード
   - **重要**: `lambda_function.py`がルートにあることを確認（Lambdaエントリーポイント）

4. API Gatewayを設定してLambda関数と連携

5. LINE DevelopersコンソールでWebhook URLを設定

## ローカルテスト手順

### 1. 環境設定
```bash
# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.template .env
# .envファイルを編集して必要な認証情報を設定
```

### 2. テスト方法

#### 方法1: 直接テスト（単体テスト）
```bash
# 直接Lambda関数をテスト（プロジェクトルートから実行）
python tests/test_lambda_handler.py
```

#### 方法2: ローカルサーバーテスト（統合テスト）
```bash
# ローカルサーバーを起動（プロジェクトルートから実行）
python scripts/local_server.py

# 別ターミナルでテストメッセージを送信（プロジェクトルートから実行）
python scripts/test_webhook_sender.py --type message --text "Hello!"
```

#### 方法3: ngrokでのエンドツーエンドテスト
```bash
# ngrokを使用してローカルサーバーを公開
python scripts/local_server.py
# 別ターミナルで:
ngrok http 5000

# LINE DevelopersでWebhook URLをngrokのURLに設定
# 例: https://xxxxx.ngrok.io/webhook
```

## 機能

- LINEユーザーからのテキストメッセージを受信
- Claude API（Sonnet 3）を使用して応答を生成
- エラーハンドリング（レート制限、APIエラー等）
- 5000文字を超える応答の自動切り詰め

## 注意事項

- Lambda関数のメモリは512MB以上を推奨
- リージョンは東京（ap-northeast-1）を推奨
- Claude APIの利用料金に注意してください

## トラブルシューティング

### 署名検証エラー
- `.env`の`LINE_CHANNEL_SECRET`が正しいか確認
- Webhookボディが変更されていないか確認

### ハンドラーインポートエラー
- プロジェクトルートからスクリプトを実行しているか確認
- `src/lambda_function.py`が存在するか確認

### 接続拒否エラー
- ローカルサーバーが起動しているか確認
- ポート番号（デフォルト: 5000）が正しいか確認