# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LINE Bot application that runs on AWS Lambda and integrates with Claude AI (Anthropic) to provide intelligent responses to LINE messages. The bot receives webhooks from LINE, processes messages using Claude API, and sends replies back to users.

## Project Structure

```
├── src/                    # Main application code
│   └── lambda_function.py  # Lambda handler implementation
├── tests/                  # Test code
│   └── test_lambda_handler.py
├── scripts/                # Utility scripts
│   ├── local_server.py     # Flask server for local testing
│   └── test_webhook_sender.py
└── lambda_function.py      # Lambda deployment entry point (imports from src/)
```

## Essential Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.template .env
# Edit .env and add: LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, ANTHROPIC_API_KEY
```

### Testing Commands
```bash
# Direct Lambda function testing (unit tests) - run from project root
python tests/test_lambda_handler.py

# Local server testing (integration tests) - run from project root
python scripts/local_server.py                                    # Terminal 1: Start server
python scripts/test_webhook_sender.py --type message --text "テスト"  # Terminal 2: Send test

# End-to-end testing with ngrok
python scripts/local_server.py    # Terminal 1
ngrok http 5000                  # Terminal 2
# Then update LINE Developers webhook URL with ngrok URL
```

### Linting and Formatting
```bash
# Format code
black *.py

# Lint code
flake8 *.py
```

## Architecture

### Lambda Event Flow
```
LINE Platform → API Gateway → lambda_handler() → Claude API
                                    ↓
                              LINE Reply API
```

### Key Integration Points

1. **LINE Webhook Handling**: The Lambda function validates webhook signatures and processes events. The main handler is in `src/lambda_function.py:lambda_handler()`.

2. **Claude API Integration**: Messages are sent to Claude using the Anthropic Python SDK in `src/lambda_function.py:get_claude_response()`. The model is set to `claude-3-sonnet-20240229`.

3. **Local Development**: The Flask server in `scripts/local_server.py` simulates API Gateway by converting HTTP requests to Lambda event format.

4. **Deployment Structure**: The root `lambda_function.py` serves as the entry point for Lambda, importing the actual handler from `src/lambda_function.py`.

### Error Handling Strategy

The bot implements multiple levels of error handling:
- LINE signature validation errors (400)
- Claude API rate limits and errors (specific messages in Japanese)
- General exceptions (500 with error logging)

### Testing Architecture

- **Unit Tests**: Mock Lambda events created by `tests/test_lambda_handler.py`
- **Integration Tests**: HTTP requests via `scripts/test_webhook_sender.py` 
- **Signature Verification**: Can be tested with/without signatures using different endpoints
- **Import Paths**: All test scripts are designed to be run from the project root

## Important Considerations

1. **Lambda Deployment**: When deploying, package all dependencies with the function:
   ```bash
   pip install -r requirements.txt -t .
   zip -r function.zip .
   ```

2. **Environment Variables**: The Lambda function expects these environment variables:
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `ANTHROPIC_API_KEY`

3. **Message Length**: Responses are automatically truncated to 5000 characters to comply with LINE's limits.

4. **Japanese Language**: All user-facing error messages and logs are in Japanese.