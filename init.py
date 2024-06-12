import os
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

def main():
    create_file_if_not_exists("question.md", "このファイルには質問内容を記述します。\n")
    create_file_if_not_exists("response.md", "このファイルには回答内容を記述します。\n")
    create_file_if_not_exists("history.md", "このファイルは、私が聞いた質問とあなたが過去に答えた回答を記録します。\n")
    run_git_command("git update-index --assume-unchanged ask_aoai_files_config.json")
    print("初期化が完了しました。")

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "config":
        if len(os.sys.argv) > 2 and os.sys.argv[2] == "ack":
            run_git_command("git update-index --no-assume-unchanged ask_aoai_files_config.json")
        elif len(os.sys.argv) > 2 and os.sys.argv[2] == "ignore":
            run_git_command("git update-index --assume-unchanged ask_aoai_files_config.json")
        else:
            print("無効なコマンドオプションです。'ack' または 'ignore' を指定してください。")
    else:
        main()
        input("Press Enter to continue...")