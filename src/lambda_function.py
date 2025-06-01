import json
import os
import logging
from typing import Dict, Any
import anthropic
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent, TextSendMessage

logger = logging.getLogger()
logger.setLevel(logging.INFO)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
claude_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    LINE Botのwebhook用AWS Lambdaハンドラー
    """
    try:
        signature = event['headers'].get('x-line-signature', event['headers'].get('X-Line-Signature'))
        body = event['body']
        
        logger.info(f"Received event: {json.dumps(event)}")
        
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("無効な署名")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid signature'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'result': 'OK'})
        }
        
    except Exception as e:
        logger.error(f"lambda_handlerでエラーが発生: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent) -> None:
    """
    LINEユーザーからのテキストメッセージを処理
    """
    user_message = event.message.text
    user_id = event.source.user_id
    
    logger.info(f"{user_id}からメッセージを受信: {user_message}")
    
    try:
        response = get_claude_response(user_message)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        
    except Exception as e:
        logger.error(f"メッセージ処理中にエラーが発生: {str(e)}")
        
        error_message = "申し訳ございません。エラーが発生しました。しばらくしてから再度お試しください。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=error_message)
        )


def get_claude_response(user_message: str) -> str:
    """
    Claude APIからレスポンスを取得
    """
    try:
        message = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        response_text = message.content[0].text
        
        if len(response_text) > 5000:
            response_text = response_text[:4997] + "..."
        
        return response_text
        
    except anthropic.RateLimitError:
        logger.error("Claude APIのレート制限を超過")
        return "現在リクエストが多いため、しばらくしてから再度お試しください。"
        
    except anthropic.APIError as e:
        logger.error(f"Claude APIエラー: {str(e)}")
        return "APIエラーが発生しました。しばらくしてから再度お試しください。"
        
    except Exception as e:
        logger.error(f"Claude API呼び出し中に予期しないエラーが発生: {str(e)}")
        return "予期しないエラーが発生しました。"