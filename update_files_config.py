import json
import os
import re
import shutil
from datetime import datetime
from openai import AzureOpenAI
from file_operations import save_to_temp_file, replace_file_on_exit

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
    pattern = r'^(.*?)\n```(.*?)\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    
    files = [(match[0].strip(), match[1].strip(), match[2].strip()) for match in matches]
    return files

def update_files(parsed_files):
    for filename, code in parsed_files:
        # 新しいファイル内容をテンポラリファイルに保存
        temp_filepath = save_to_temp_file(filename, code)

        # プログラム終了時にテンポラリファイルを既存ファイルに置き換える
        replace_file_on_exit(filename, temp_filepath)

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 除外するべきファイルを除いた、保持するべきリストを用意する
    exclude_items = set(data.get('exclude', []))

    def get_files(start_path='.'):
        files_to_include = []
        for root, dirs, filenames in os.walk(start_path):
            # ディレクトリの除外フィルタリング
            dirs[:] = [d for d in dirs if not any(exclude in os.path.join(root, d) for exclude in exclude_items)]

            for filename in filenames:
                filepath = os.path.relpath(os.path.join(root, filename), start_path)
                # ファイルの除外フィルタリング
                if not any(exclude in filepath for exclude in exclude_items):
                    files_to_include.append(filepath)
        return files_to_include

    some_files = get_files()

    from generate_input_from_json import generate_input_from_json
    input_data = generate_input_from_json()

    # md ファイルの内容を変数に読み込む
    with open("source_code_rule.md", 'r', encoding='utf-8') as source_code_rule:
        rule = source_code_rule.read()

    prompt_text = rule

    prompt_text += (
"""
"後述するファイルリストのみで構成される ask_aoai_files_config.json を出力してください。"
"ファイルリストに存在しないものは files から削除してください。"
"exclude は保持してください"
"既存の JSON を変更する必要がない場合は JSON を出力せず、「変更するべきものはありません」と応答してください。"
"新しく追加するファイルリストは filename は パスを含まないファイル名を記載し、include_in_input を true に指定し、description はファイル名から想定される内容を考えて、filepath は適切に指定してください。"
"ファイルリスト:"
"""
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

            if response.choices[0].message.content:
                content = response.choices[0].message.content
                print(content, end="")
                output_file.write(content)

                # ここのロジックで、ファイルのアップデートを行う
                from parse_source_code import extract_code_blocks
                parsed_files = extract_code_blocks(content)
                if not parsed_files:
                    print("一致するファイルはありませんでした")
                else:
                    update_files(parsed_files)

            else:
                raise ValueError("No response content received")
        except Exception as e:
            print(f"An error occurred: {e}")
            output_file.write(f"An error occurred: {e}")

    history_filename = 'history.md'
    with open(history_filename, 'a', encoding='utf-8') as history_file:
        history_file.write(f"Date: {datetime.now().isoformat()}\n")
        history_file.write(f"System Input:\n{input_data}\n")
        history_file.write(f"Question:\n{prompt_text}\n")
        if 'content' in locals():
            history_file.write(f"Response:\n{content}\n")
        else:
            history_file.write(f"Response: Error occurred - {e}\n")
        history_file.write("\n" + "="*50 + "\n\n")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_files_config()