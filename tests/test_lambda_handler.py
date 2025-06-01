#!/usr/bin/env python3
"""
LINE bot Lambdaハンドラーのテストスクリプト
ローカルテスト用のLambdaイベントをシミュレート
"""

import json
import sys
import os
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Lambdaハンドラーをインポート
try:
    from src.lambda_function import lambda_handler
except ImportError:
    print("エラー: src/lambda_function.pyが見つかりません")
    print("プロジェクトルートからスクリプトを実行してください")
    sys.exit(1)

def create_line_webhook_event(event_type="message", message_text="Hello"):
    """テスト用のLINE webhookイベントを作成"""
    
    timestamp = int(datetime.now().timestamp() * 1000)
    
    if event_type == "message":
        event = {
            "type": "message",
            "mode": "active",
            "timestamp": timestamp,
            "source": {
                "type": "user",
                "userId": "U123456789abcdef0123456789abcdef0"
            },
            "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
            "message": {
                "type": "text",
                "id": "1234567890",
                "text": message_text
            }
        }
    elif event_type == "follow":
        event = {
            "type": "follow",
            "mode": "active",
            "timestamp": timestamp,
            "source": {
                "type": "user",
                "userId": "U123456789abcdef0123456789abcdef0"
            },
            "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA"
        }
    elif event_type == "unfollow":
        event = {
            "type": "unfollow",
            "mode": "active",
            "timestamp": timestamp,
            "source": {
                "type": "user",
                "userId": "U123456789abcdef0123456789abcdef0"
            }
        }
    elif event_type == "postback":
        event = {
            "type": "postback",
            "mode": "active",
            "timestamp": timestamp,
            "source": {
                "type": "user",
                "userId": "U123456789abcdef0123456789abcdef0"
            },
            "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
            "postback": {
                "data": "action=buy&itemid=123"
            }
        }
    else:
        raise ValueError(f"Unknown event type: {event_type}")
    
    return event

def create_lambda_event(line_events):
    """LINE webhookイベントを含むLambdaイベントを作成"""
    
    body = {
        "destination": "U123456789abcdef0123456789abcdef0",
        "events": line_events
    }
    
    lambda_event = {
        "resource": "/",
        "path": "/",
        "httpMethod": "POST",
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "LineBotWebhook/2.0",
            "X-Line-Signature": "test_signature"
        },
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "123456",
            "resourcePath": "/",
            "httpMethod": "POST",
            "extendedRequestId": "test-request-id",
            "requestTime": "01/Jan/2024:00:00:00 +0000",
            "path": "/",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "prod",
            "domainPrefix": "test",
            "requestTimeEpoch": int(datetime.now().timestamp() * 1000),
            "requestId": "test-request-id",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": "1.2.3.4",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "LineBotWebhook/2.0",
                "user": None
            },
            "domainName": "test.execute-api.us-east-1.amazonaws.com",
            "apiId": "test123"
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }
    
    return lambda_event

def test_handler():
    """様々なLINEイベントでLambdaハンドラーをテスト"""
    
    print("LINE Bot Lambdaハンドラーのテスト")
    print("=" * 50)
    
    # テスト1: テキストメッセージイベント
    print("\n1. テキストメッセージイベントのテスト")
    message_event = create_line_webhook_event("message", "Hello, bot!")
    lambda_event = create_lambda_event([message_event])
    
    print(f"イベント: {json.dumps(lambda_event, indent=2)}")
    
    # Lambdaハンドラーを実行
    try:
        response = lambda_handler(lambda_event, {})
        print(f"レスポンス: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    # テスト2: フォローイベント
    print("\n2. フォローイベントのテスト")
    follow_event = create_line_webhook_event("follow")
    lambda_event = create_lambda_event([follow_event])
    
    # Lambdaハンドラーを実行
    try:
        response = lambda_handler(lambda_event, {})
        print(f"レスポンス: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    # テスト3: 複数のイベント
    print("\n3. 複数イベントのテスト")
    events = [
        create_line_webhook_event("message", "最初のメッセージ"),
        create_line_webhook_event("message", "2番目のメッセージ")
    ]
    lambda_event = create_lambda_event(events)
    
    # Lambdaハンドラーを実行
    try:
        response = lambda_handler(lambda_event, {})
        print(f"レスポンス: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    # テスト4: ポストバックイベント
    print("\n4. ポストバックイベントのテスト")
    postback_event = create_line_webhook_event("postback")
    lambda_event = create_lambda_event([postback_event])
    
    # Lambdaハンドラーを実行
    try:
        response = lambda_handler(lambda_event, {})
        print(f"レスポンス: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"エラー: {str(e)}")

if __name__ == "__main__":
    test_handler()