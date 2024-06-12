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

def update_files_config(input_json='ask_aoai_files_config.json'):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    exclude_items = set(data.get('exclude', []))

    def get_files(start_path='.'):
        files_to_include = []
        for root, dirs, filenames in os.walk(start_path):
            dirs[:] = [d for d in dirs if not any(exclude in os.path.join(root, d) for exclude in exclude_items)]
            for filename in filenames:
                filepath = os.path.relpath(os.path.join(root, filename), start_path)
                if not any(exclude in filepath for exclude in exclude_items):
                    files_to_include.append(filepath)
        return files_to_include

    some_files = get_files()

    # Sytem Input の設定
    input_data = generate_input_from_json()

    # Prompt の設定
    prompt_text = ""
    with open("source_code_rule.md", 'r', encoding='utf-8') as source_code_rule:
        code_rule = source_code_rule.read()

    with open("update_files_rule.md", 'r', encoding='utf-8') as update_rule:
        update_rule = update_rule.read()

    prompt_text += code_rule + update_rule

    for file in some_files:
        prompt_text += file + "\n"

    with open("response.md", 'w', encoding='utf-8') as output_file:
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "system", "content": input_data}, {"role": "user", "content": prompt_text}],
            )

            if response.choices[0].message.content:
                content = response.choices[0].message.content
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