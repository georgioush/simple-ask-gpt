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
    rel_path = os.path.relpath(path)
    for pattern in include_patterns:
        if rel_path.startswith(os.path.relpath(pattern)) or pattern in rel_path:
            return True
    return False

def should_include_file_in_folders(file_path, include_folders):
    """
    ファイルが指定されたフォルダに含まれるかどうかを確認
    """
    for folder in include_folders:
        if file_path.startswith(os.path.relpath(folder)):
            return True
    return False

def get_files(start_path, exclude_folders, exclude_files, include_files, include_folders):
    """
    指定されたstart_pathからファイルを再帰的に取得します
    """
    files_to_include = []
    include_files_relative = {os.path.relpath(file) for file in include_files}

    for root, dirs, filenames in os.walk(start_path):
        # 除外パターンに一致するディレクトリをフィルタリング
        filtered_dirs = []
        for d in dirs:
            dir_path = os.path.relpath(os.path.join(root, d))
            if (not any(dir_path.startswith(os.path.relpath(pattern)) for pattern in exclude_folders) or 
                should_include(dir_path, include_files)):
                filtered_dirs.append(d)
        dirs[:] = filtered_dirs

        # 含むべきファイルを探索
        for filename in filenames:
            filepath = os.path.relpath(os.path.join(root, filename))
            if (should_include(filepath, include_files_relative) or 
                not any(filepath.startswith(os.path.relpath(pattern)) for pattern in exclude_files) or
                should_include_file_in_folders(filepath, include_folders)):
                files_to_include.append(filepath)
    
    # 明示的に指定されたファイルをリストに追加
    for pattern in include_files:
        if os.path.exists(pattern):
            rel_pattern = os.path.relpath(pattern)
            if rel_pattern not in files_to_include:
                files_to_include.append(rel_pattern)
        
    return files_to_include

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    exclude_folders = set(data.get('exclude_folder', []))
    exclude_files = set(data.get('exclude_files', []))
    include_files = set(data.get('include_files', []))
    include_folders = set(data.get('include_folder', []))

    all_files = get_files(".", exclude_folders, exclude_files, include_files, include_folders)

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