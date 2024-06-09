import json
import os
import re
import shutil
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

def parse_output(content):
    # ファイル名とその内容を抽出するためのパターン
    pattern = r'^(.*?)\n```(.*?)\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    
    # パースした内容を返す
    files = []
    for match in matches:
        filename = match[0].strip()
        language = match[1].strip()
        code = match[2].strip()
        files.append((filename, language, code))

    return files

def archive_file(filepath):
    # アーカイブディレクトリが存在しない場合は作成する
    if not os.path.exists('archive'):
        os.makedirs('archive')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    archive_path = f'archive/{os.path.basename(filepath)}_{timestamp}'
    shutil.copy(filepath, archive_path)
    return archive_path

def save_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def update_files(content):
    files = parse_output(content)
    
    for filename, language, code in files:
        if os.path.exists(filename):
            # ファイルが存在する場合はアーカイブする
            archive_file(filename)
        
        # ファイルを新しい内容で上書き保存
        save_file(filename, code)
        print(f'{filename} を更新しました。')

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 除外するディレクトリやファイルを取得
    exclude_items = set(data.get('exclude', []))

    # カレントディレクトリからファイルリストを生成
    def get_files(start_path='.'):
        files_to_include = []
        for root, dirs, filenames in os.walk(start_path):
            # Exclude specific directories
            dirs[:] = [d for d in dirs if d not in exclude_items]

            for filename in filenames:
                filepath = os.path.relpath(os.path.join(root, filename), start_path)
                # Exclude specific files
                if any(exclude in filepath for exclude in exclude_items):
                    continue
                files_to_include.append(filepath)
        return files_to_include

    # カレントディレクトリからファイルリストを生成
    some_files = get_files()

    # JSONファイルから入力データを生成する関数のインポート
    from generate_input_from_json import generate_input_from_json
    # JSONファイルから入力データを生成
    input_data = generate_input_from_json()

    # プロンプトテキストを作成
    prompt_text = (
        "以下のファイルリストを含めた JSON ファイルである ask_aoai_files_config.json を出力してください。\n"
        "追加するべきものが無い場合はその旨を述べてください。\n"
        "新しく追加するものは include_in_input を true に指定し、description はファイル名から想定される内容を考えてください。\n"
        "filepath は適切に指定してください。\n"
        "ファイルリスト:\n"
    )
    for file in some_files:
        prompt_text += file + "\n"

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        try:
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
                # 解析してファイル保存
                from parse_source_code import extract_code_blocks
                from file_operations import save_parsed_files
                parsed_files = extract_code_blocks(content)
                if not parsed_files:
                    print("There is no matched files")
                save_parsed_files(parsed_files)
            else:
                raise ValueError("No response content received")
        except Exception as e:
            print(f"An error occurred: {e}")
            output_file.write(f"An error occurred: {e}")

    # 質問と回答の履歴を保存する
    history_filename = 'history.md'
    with open(history_filename, 'a', encoding='utf-8') as history_file:
        history_file.write(f"Date: {datetime.now().isoformat()}\n")
        history_file.write(f"Question:\n{prompt_text}\n")
        if 'content' in locals():
            history_file.write(f"Response:\n{content}\n")
        else:
            history_file.write(f"Response: Error occurred - {e}\n")
        history_file.write("\n" + "="*50 + "\n\n")

# スクリプトが直接実行された場合のみ動作するようにする
if __name__ == "__main__":
    # カレントディレクトリをスクリプトの場所に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_files_config()