import os
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path

# ファイルを開いて内容を読み取る
prompt_file_path = "question.md"
output_file_path = "response.md"

# 環境変数から設定を取得
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv("AZURE_OPENAI_MODEL_NAME")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint,
)

# JSONファイルから入力データを生成する関数のインポート
from generate_input_from_json import generate_input_from_json
# ファイルから抽出したコードブロックを保存する関数のインポート
from parse_source_code import extract_code_blocks
from file_operations import save_parsed_files

# JSONファイルから入力データを生成
input_data = generate_input_from_json()


# md ファイルの内容を変数に読み込む
with open("source_code_rule.md", 'r', encoding='utf-8') as source_code_rule:
    rule = source_code_rule.read()

prompt_text = rule

with open(prompt_file_path, 'r', encoding='utf-8') as file:
    prompt_text += file.read()

# Azure OpenAIに質問を送信する
response_text = ""

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": input_data},
            {"role": "user", "content": prompt_text},
        ],
    )

    if response.choices[0].message.content is not None:
        content = response.choices[0].message.content
        print(content, end="")
        output_file.write(content)
        
        # 要求されたファイルのパースと保存を行う
        from parse_source_code import extract_code_blocks
        parsed_files = extract_code_blocks(content)
        if parsed_files:
            save_parsed_files(parsed_files)
        response_text += content
    else:
        raise ValueError("No response content received")

# 質問と回答の履歴を保存する
history_filename = 'history.md'
with open(history_filename, 'a', encoding='utf-8') as history_file:
    history_file.write(f"Date: {datetime.now().isoformat()}\n")
    history_file.write(f"Question:\n{prompt_text}\n")
    history_file.write(f"Response:\n{response_text}\n")
    history_file.write("\n" + "="*50 + "\n\n")