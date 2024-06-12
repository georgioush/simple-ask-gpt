import json
import os

def generate_input_from_json(config_file='ask_aoai_files_config.json'):
    with open(config_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    result = ""

    for file_info in data['files']:
        if file_info['include_in_input']:
            filepath = file_info['filepath']
            filename = file_info['filename']
            full_path = os.path.join(filepath, filename)

            if not os.path.exists(full_path):
                print(f"File not found: {full_path}")
                continue
            
            description = "\n\n===================================="
            description += f"{file_info['description']} ファイル名は {filename} です。"
            
            try:
                with open(full_path, 'r', encoding='utf-8') as file:
                    script_content = file.read()
                result += f"{description}\n{script_content}\n"
            except Exception as e:
                print(f"An error occurred while reading {full_path}: {e}")
    
    return result