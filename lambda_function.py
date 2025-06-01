# AWS Lambdaデプロイ用のエントリーポイント
# Lambda関数のハンドラー設定: lambda_function.lambda_handler

from src.lambda_function import lambda_handler

__all__ = ['lambda_handler']