import os
import json
import subprocess

def create_file_if_not_exists(filename, content):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{filename} ファイルを作成しました。")
    else:
        print(f"{filename} ファイルは既に存在します。")

def run_git_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"コマンド実行: {command}")
    except subprocess.CalledProcessError as e:
        print(f"コマンド失敗: {command}, エラー: {e}")

def update_files_config(mode):
    config_file = 'ask_aoai_files_config.json'
    
    with open(config_file, 'r', encoding='utf-8') as file:
        config_data = json.load(file)

    if mode == "dev":
        for file_info in config_data['files']:
            if file_info['filename'] == 'ask_aoai_files_config.json' or file_info['filepath'].startswith('dev'):
                file_info['include_in_input'] = True
            else:
                file_info['include_in_input'] = False
    elif mode == "all":
        for file_info in config_data['files']:
            file_info['include_in_input'] = (file_info['filename'] != 'history.md')
    elif mode == "history":
        for file_info in config_data['files']:
            if file_info['filename'] == 'history.md':
                file_info['include_in_input'] = True
    elif mode == "nohistory":
        for file_info in config_data['files']:
            if file_info['filename'] == 'history.md':
                file_info['include_in_input'] = False
    elif mode == "ignore":
        run_git_command("git update-index --assume-unchanged ask_aoai_files_config.json")
    elif mode == "ack" or mode == "noignore":
        run_git_command("git update-index --no-assume-unchanged ask_aoai_files_config.json")
    else:
        print(f"無効なモード: {mode}")
        return
    
    if mode not in ["ignore", "ack", "noignore"]:
        with open(config_file, 'w', encoding='utf-8') as file:
            json.dump(config_data, file, ensure_ascii=False, indent=4)
        print(f"{config_file} が {mode} モードで更新されました。")

def main():
    create_file_if_not_exists("question.md", "このファイルには質問内容を記述します。\n")
    create_file_if_not_exists("response.md", "このファイルには回答内容を記述します。\n")
    create_file_if_not_exists("history.md", "このファイルは、私が聞いた質問とあなたが過去に答えた回答を記録します。\n")
    run_git_command("git update-index --assume-unchanged ask_aoai_files_config.json")
    print("初期化が完了しました。")

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "config":
        if len(os.sys.argv) > 2:
            mode = os.sys.argv[2]
            update_files_config(mode)
        else:
            print("モードが指定されていません。'dev', 'all', 'history', 'nohistory', 'ignore', 'ack', 'noignore' のいずれかを指定してください。")
    else:
        main()
        input("Press Enter to continue...")