#!/usr/bin/env python3
"""
LINE botのwebhookをテストするためのローカルFlaskサーバー
Lambda関数をローカルでシミュレートします
"""

import os
import json
import hmac
import hashlib
import base64
from flask import Flask, request, abort
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)

# 設定
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
PORT = int(os.getenv('LOCAL_SERVER_PORT', 5000))

def verify_signature(body, signature):
    """LINE webhookの署名を検証"""
    if not LINE_CHANNEL_SECRET:
        print("警告: LINE_CHANNEL_SECRETが設定されていません。署名検証をスキップします")
        return True
    
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    
    return signature == base64.b64encode(hash).decode('utf-8')

def create_lambda_event(request):
    """FlaskリクエストをLambdaイベント形式に変換"""
    
    # リクエストボディを取得
    body = request.get_data(as_text=True)
    
    # ヘッダー辞書を構築
    headers = {}
    for key, value in request.headers:
        headers[key] = value
    
    # Lambdaイベントを作成
    lambda_event = {
        "resource": request.path,
        "path": request.path,
        "httpMethod": request.method,
        "headers": headers,
        "multiValueHeaders": {},
        "queryStringParameters": dict(request.args) if request.args else None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "local",
            "resourcePath": request.path,
            "httpMethod": request.method,
            "extendedRequestId": f"local-{datetime.now().timestamp()}",
            "requestTime": datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000"),
            "path": request.path,
            "accountId": "local",
            "protocol": "HTTP/1.1",
            "stage": "local",
            "domainPrefix": "localhost",
            "requestTimeEpoch": int(datetime.now().timestamp() * 1000),
            "requestId": f"local-{datetime.now().timestamp()}",
            "identity": {
                "sourceIp": request.remote_addr,
                "userAgent": request.headers.get('User-Agent', '')
            },
            "domainName": f"localhost:{PORT}",
            "apiId": "local"
        },
        "body": body,
        "isBase64Encoded": False
    }
    
    return lambda_event

@app.route('/', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "ok",
        "message": "LINE Botローカルサーバーが実行中です",
        "timestamp": datetime.now().isoformat()
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE webhookエンドポイント"""
    
    # X-Line-Signatureヘッダー値を取得
    signature = request.headers.get('X-Line-Signature', '')
    
    # リクエストボディをバイナリとして取得
    body = request.get_data()
    
    # webhook署名を検証
    if not verify_signature(body, signature):
        print("無効な署名")
        abort(400)
    
    # webhookボディを解析
    try:
        events = json.loads(body)
    except json.JSONDecodeError:
        print("無効なJSONボディ")
        abort(400)
    
    # 受信したイベントをログ出力
    print(f"\nWebhookを受信しました: {datetime.now().isoformat()}")
    print(f"イベント: {json.dumps(events, indent=2, ensure_ascii=False)}")
    
    # Lambdaイベントを作成
    lambda_event = create_lambda_event(request)
    
    # ここでLambdaハンドラーをインポートして呼び出します
    try:
        from src.lambda_function import lambda_handler
        response = lambda_handler(lambda_event, {})
        
        # Lambdaレスポンスを返却
        return response.get('body', ''), response.get('statusCode', 200), {
            'Content-Type': 'application/json'
        }
    except ImportError:
        print("lambda_function.pyが見つかりません。コメントアウトされたコードを有効にしてください")
        return {"status": "ok"}, 200
    except Exception as e:
        print(f"Lambdaハンドラーでエラーが発生: {str(e)}")
        return {"error": str(e)}, 500
    return {"status": "ok"}, 200

@app.route('/test', methods=['POST'])
def test_webhook():
    """任意のJSONを受け入れてLINE webhookとして処理するテストエンドポイント"""
    
    # テストエンドポイントでは署名検証をスキップ
    body = request.get_data()
    
    try:
        events = json.loads(body)
    except json.JSONDecodeError:
        return {"error": "無効なJSON"}, 400
    
    # 受信したイベントをログ出力
    print(f"\nテストwebhookを受信しました: {datetime.now().isoformat()}")
    print(f"イベント: {json.dumps(events, indent=2, ensure_ascii=False)}")
    
    # Lambdaイベントを作成
    lambda_event = create_lambda_event(request)
    print(f"\nLambdaイベント: {json.dumps(lambda_event, indent=2, ensure_ascii=False)}")
    
    # ここでLambdaハンドラーをインポートして呼び出します
    try:
        from src.lambda_function import lambda_handler
        response = lambda_handler(lambda_event, {})
        return response
    except ImportError:
        print("lambda_function.pyが見つかりません")
        return {"status": "ok", "received": events}, 200
    except Exception as e:
        print(f"Lambdaハンドラーでエラーが発生: {str(e)}")
        return {"error": str(e)}, 500

@app.errorhandler(Exception)
def handle_error(error):
    """グローバルエラーハンドラー"""
    print(f"エラー: {str(error)}")
    return {"error": str(error)}, 500

if __name__ == '__main__':
    print(f"""
    LINE Bot ローカルサーバー
    ====================
    http://localhost:{PORT} で実行中
    
    エンドポイント:
    - GET  /           : ヘルスチェック
    - POST /webhook    : LINE webhookエンドポイント（署名検証あり）
    - POST /test       : テストエンドポイント（署名検証なし）
    
    環境変数:
    - LINE_CHANNEL_SECRET: {'設定済み' if LINE_CHANNEL_SECRET else '未設定'}
    - LINE_CHANNEL_ACCESS_TOKEN: {'設定済み' if LINE_CHANNEL_ACCESS_TOKEN else '未設定'}
    """)
    
    app.run(host='0.0.0.0', port=PORT, debug=True)