#!/usr/bin/env python3
"""
ローカルLINE botサーバーにテストwebhookリクエストを送信するスクリプト
"""

import requests
import json
import hmac
import hashlib
import base64
from datetime import datetime
import argparse
from dotenv import load_dotenv
import os

# 環境変数を読み込み
load_dotenv()

def generate_signature(channel_secret, body):
    """LINE webhook署名を生成"""
    hash = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode('utf-8')

def send_test_message(url, message_text, channel_secret=None):
    """テストテキストメッセージwebhookを送信"""
    
    webhook_body = {
        "destination": "U123456789abcdef0123456789abcdef0",
        "events": [
            {
                "type": "message",
                "mode": "active",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "source": {
                    "type": "user",
                    "userId": "U123456789abcdef0123456789abcdef0"
                },
                "replyToken": "test-reply-token-" + str(datetime.now().timestamp()),
                "message": {
                    "type": "text",
                    "id": str(int(datetime.now().timestamp() * 1000)),
                    "text": message_text
                }
            }
        ]
    }
    
    body_json = json.dumps(webhook_body)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "LineBotWebhook/2.0"
    }
    
    if channel_secret:
        signature = generate_signature(channel_secret, body_json)
        headers["X-Line-Signature"] = signature
    
    try:
        response = requests.post(url, data=body_json, headers=headers)
        print(f"レスポンスステータス: {response.status_code}")
        print(f"レスポンスボディ: {response.text}")
        return response
    except Exception as e:
        print(f"リクエスト送信エラー: {str(e)}")
        return None

def send_follow_event(url, channel_secret=None):
    """テストフォローイベントwebhookを送信"""
    
    webhook_body = {
        "destination": "U123456789abcdef0123456789abcdef0",
        "events": [
            {
                "type": "follow",
                "mode": "active",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "source": {
                    "type": "user",
                    "userId": "U123456789abcdef0123456789abcdef0"
                },
                "replyToken": "test-reply-token-" + str(datetime.now().timestamp())
            }
        ]
    }
    
    body_json = json.dumps(webhook_body)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "LineBotWebhook/2.0"
    }
    
    if channel_secret:
        signature = generate_signature(channel_secret, body_json)
        headers["X-Line-Signature"] = signature
    
    try:
        response = requests.post(url, data=body_json, headers=headers)
        print(f"レスポンスステータス: {response.status_code}")
        print(f"レスポンスボディ: {response.text}")
        return response
    except Exception as e:
        print(f"リクエスト送信エラー: {str(e)}")
        return None

def send_postback_event(url, data, channel_secret=None):
    """テストポストバックイベントwebhookを送信"""
    
    webhook_body = {
        "destination": "U123456789abcdef0123456789abcdef0",
        "events": [
            {
                "type": "postback",
                "mode": "active",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "source": {
                    "type": "user",
                    "userId": "U123456789abcdef0123456789abcdef0"
                },
                "replyToken": "test-reply-token-" + str(datetime.now().timestamp()),
                "postback": {
                    "data": data
                }
            }
        ]
    }
    
    body_json = json.dumps(webhook_body)
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "LineBotWebhook/2.0"
    }
    
    if channel_secret:
        signature = generate_signature(channel_secret, body_json)
        headers["X-Line-Signature"] = signature
    
    try:
        response = requests.post(url, data=body_json, headers=headers)
        print(f"レスポンスステータス: {response.status_code}")
        print(f"レスポンスボディ: {response.text}")
        return response
    except Exception as e:
        print(f"リクエスト送信エラー: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='LINE botサーバーにテストwebhookを送信')
    parser.add_argument('--url', default='http://localhost:5000/webhook', 
                        help='Webhook URL (デフォルト: http://localhost:5000/webhook)')
    parser.add_argument('--test-url', action='store_true',
                        help='/testエンドポイントを使用 (署名検証なし)')
    parser.add_argument('--type', choices=['message', 'follow', 'postback'], 
                        default='message', help='送信するイベントタイプ')
    parser.add_argument('--text', default='Hello, bot!', 
                        help='メッセージテキスト (messageタイプ用)')
    parser.add_argument('--data', default='action=test&value=123', 
                        help='ポストバックデータ (postbackタイプ用)')
    parser.add_argument('--no-signature', action='store_true',
                        help='署名生成をスキップ')
    
    args = parser.parse_args()
    
    # 環境からチャンネルシークレットを取得
    channel_secret = os.getenv('LINE_CHANNEL_SECRET') if not args.no_signature else None
    
    # テストエンドポイントを使用する場合はURLを調整
    if args.test_url:
        url = args.url.replace('/webhook', '/test')
    else:
        url = args.url
    
    print(f"{args.type}イベントを{url}に送信")
    
    if args.type == 'message':
        send_test_message(url, args.text, channel_secret)
    elif args.type == 'follow':
        send_follow_event(url, channel_secret)
    elif args.type == 'postback':
        send_postback_event(url, args.data, channel_secret)

if __name__ == "__main__":
    main()