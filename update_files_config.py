import json
import os
from datetime import datetime
from openai import AzureOpenAI

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

output_file_path = "response.md"

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 除外するディレクトリやファイルを取得
    exclude_items = set(data.get('exclude', []))

    # カレントディレクトリからファイルリストを生成
    def get_files(start_path='.'):
        files_to_include = []
        for root, dirs, files in os.walk(start_path):
            # Exclude specific directories
            dirs[:] = [d for d in dirs if d not in exclude_items]

            for file in files:
                filepath = os.path.relpath(os.path.join(root, file), start_path)
                # Exclude specific files
                if any(exclude in filepath for exclude in exclude_items):
                    continue
                files_to_include.append(filepath)
        return files_to_include

    # JSONファイルから入力データを生成する関数のインポート
    from generate_input_from_json import generate_input_from_json
    # JSONファイルから入力データを生成
    input_data = generate_input_from_json()

    # カレントディレクトリからファイルリストを生成
    files = get_files()

    # プロンプトテキストを作成
    prompt_text = (
        "以下のファイルファイルリストのうち、ask_aoai_files_config.jsonに記載のないファイルを追加した ask_aoai_files_config.json の JSON を出力してください。\n"
        "新しく追加するものは include_in_input を false に指定し、description はファイル名から想定される内容をあなたが考えてください。\n"
        "filepath は適切に指定してください。"
        "ファイルリスト:\n"
    )
    for file in files:
        prompt_text += f"- {file}\n"

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
            response_text += content

    # 質問と回答の履歴を保存する
    history_filename = 'history.md'
    with open(history_filename, 'a', encoding='utf-8') as history_file:
        history_file.write(f"Date: {datetime.now().isoformat()}\n")
        history_file.write(f"Question:\n{prompt_text}\n")
        history_file.write(f"Response:\n{response_text}\n")
        history_file.write("\n" + "="*50 + "\n\n")

# スクリプトが直接実行された場合のみ動作するようにする
if __name__ == "__main__":
    # カレントディレクトリをスクリプトの場所に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_files_config()
