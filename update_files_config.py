import json
import os
from datetime import datetime
from openai import AzureOpenAI
from utils.file_operations import save_to_temp_file, replace_file_on_exit
from utils.code_parser import extract_code_blocks
from utils.input_generator import generate_input_from_json

# 環境変数から設定を取得
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint)

def update_files(parsed_files):
    for path, filename, code in parsed_files:
        full_filepath = os.path.join(path, filename)
        temp_filepath = save_to_temp_file(full_filepath, code)
        replace_file_on_exit(full_filepath, temp_filepath)

def should_include(path, include_patterns):
    """
    明示的に含めるべきパターンと一致するか確認
    """
    return any(os.path.abspath(path).startswith(os.path.abspath(pattern)) for pattern in include_patterns)

def get_files(start_path, exclude_patterns, include_patterns):
    """
    指定されたstart_pathからファイルを再帰的に取得します
    """
    files_to_include = []
    include_patterns_absolute = {os.path.abspath(pattern) for pattern in include_patterns}

    for root, dirs, filenames in os.walk(start_path):
        # 除外パターンに一致するディレクトリは探索しない。明示的に含まれている場合を除く。
        dirs[:] = [d for d in dirs if not any(os.path.abspath(os.path.join(root, d)).startswith(os.path.abspath(pattern)) for pattern in exclude_patterns) or should_include(os.path.join(root, d), include_patterns)]

        for filename in filenames:
            filepath = os.path.join(root, filename)
            if should_include(filepath, include_patterns_absolute) or not any(os.path.abspath(filepath).startswith(os.path.abspath(pattern)) for pattern in exclude_patterns):
                files_to_include.append(filepath)

    # include_files に指定されたファイルを追加
    for pattern in include_patterns:
        if os.path.exists(pattern):
            abs_pattern = os.path.abspath(pattern)
            if abs_pattern not in files_to_include:
                files_to_include.append(pattern)

    return files_to_include

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    exclude_patterns = set(data.get('exclude', []))
    include_patterns = set(data.get('include_files', []))

    all_files = get_files(".", exclude_patterns, include_patterns)

    # System Input の設定
    input_data = generate_input_from_json()

    # Prompt の設定
    prompt_text = ""
    with open("source_code_rule.md", 'r', encoding='utf-8') as source_code_rule:
        code_rule = source_code_rule.read()

    with open("update_files_rule.md", 'r', encoding='utf-8') as update_rule:
        update_rule = update_rule.read()

    prompt_text += code_rule + update_rule

    for file in all_files:
        prompt_text += f"{file}\n"

    with open("response.md", 'w', encoding='utf-8') as output_file:
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "system", "content": input_data}, {"role": "user", "content": prompt_text}],
            )

            content = response.choices[0].message.content
            if content:
                output_file.write(content)
                parsed_files = extract_code_blocks(content)
                if parsed_files:
                    update_files(parsed_files)
            else:
                raise ValueError("No response content received")
        except Exception as e:
            output_file.write(f"An error occurred: {e}")

    with open('history.md', 'a', encoding='utf-8') as history_file:
        history_file.write(f"Date: {datetime.now().isoformat()}\n")
        history_file.write(f"System Input:\n{input_data}\n")
        history_file.write(f"Question:\n{prompt_text}\n")
        history_file.write(f"Response:{content if 'content' in locals() else 'Error occurred - {e}'}\n")
        history_file.write("\n" + "="*50 + "\n\n")

if __name__ == "__main__":
    update_files_config()