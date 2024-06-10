import os

def create_file_if_not_exists(filename, content):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{filename} ファイルを作成しました。")
    else:
        print(f"{filename} ファイルは既に存在します。")

def main():
    create_file_if_not_exists("question.md", "このファイルには質問内容を記述します。\n")
    create_file_if_not_exists("response.md", "このファイルには回答内容を記述します。\n")
    create_file_if_not_exists("history.md", "このファイルは、私が聞いた質問とあなたが過去に答えた回答を記録します。\n")
    print("初期化が完了しました。")

if __name__ == "__main__":
    main()
    input("Press Enter to continue...")
