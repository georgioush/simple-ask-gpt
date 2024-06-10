import json
import os

def generate_input_from_json(config_file='ask_aoai_files_config.json'):
    # JSONデータを読み込む
    with open(config_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 入力用の変数を初期化
    result = ""

    # 各ファイルについて処理
    for file_info in data['files']:
        if file_info['include_in_input']:
            filepath = file_info['filepath']
            filename = file_info['filename']
            full_path = os.path.join(filepath, filename)

            # ファイルが存在するか確認
            if not os.path.exists(full_path):
                print(f"File not found: {full_path}")
                continue
            
            description = "\n\n===================================="
            description += file_info['description']
            description += f" ファイル名は {filename} です。"
            
            # ファイルの内容を読み込む
            try:
                with open(full_path, 'r', encoding='utf-8') as file:
                    script_content = file.read()
                
                # 変数に追加
                result += f"{description}\n{script_content}\n"
            except Exception as e:
                print(f"An error occurred while reading {full_path}: {e}")
    
    return result

# スクリプトが直接実行された場合のみ動作するようにする
if __name__ == "__main__":
    # カレントディレクトリをスクリプトの場所に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    input_data = generate_input_from_json()
    print(input_data)