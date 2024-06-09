import os
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path

# 環境変数から設定を取得
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv("AZURE_OPENAI_MODEL_NAME")

# Azure OpenAIクライアントの設定
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint,
)

# クライアントが正常にインスタンス化されたか確認するためのテストリクエスト
try:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": "This is a test message."}]
    )
    print("Test request successful. Client is working correctly.")
    print("Response from test request:", response.choices[0].message.content )
except Exception as e:
    print("An error occurred while testing the client:", e)
