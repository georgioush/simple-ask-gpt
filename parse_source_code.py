import re
import os

def extract_code_blocks(text):
    """
    指定されたテキストからファイル名とコードブロックを抽出します。

    Args:
        text (str): テキストデータ

    Returns:
        list of tuple: 抽出されたファイル名とコードブロックのリスト
    """
    # 正規表現パターン
    pattern = r'source_code_created_chat-gpt\n(?P<filename>[^\n]+)\n```(?P<language>[^\n]+)\n(?P<code>.*?)\n```'
    
    # 正規表現でマッチ
    matches = re.finditer(pattern, text, re.DOTALL)
    
    # 抽出されたファイル名とコードブロックのリスト
    extracted_blocks = []

    matched = False
    
    # 各マッチから内容を抽出
    for match in matches:
        matched = True
        filename = match.group('filename').strip()
        code = match.group('code').strip()
        
        extracted_blocks.append((filename, code))
    
    if not matched:
        print("No matches found.")
        return []

    return extracted_blocks


# テキストデータ（例）
text = '''
以下に、指定されたファイルリストのうち、`ask_aoai_files_config.json` に記載のないファイルを含む新しい `ask_aoai_files_config.json` の内容を出力します。新たに追加されたファイルには `include_in_input` を `false` に指定し、`description` には適切な説明を追加しています。

source_code_created_chat-gpt
ask_aoai_files_config.json
```json
{
    "exclude": [
        ".git",
        ".vscode",
        "__pycache__",
        "README.md",
        "test_gpt.py",
        "archive"
    ],
    "files": [
        {
            "filename": "ask_gpt.py",
            "description": "以下のスクリプトは GPT に質問を行うための機能を有します。",
            "filepath": ".",
            "include_in_input": true
        }
    ]
}
```
'''

# スクリプトが直接実行された場合のみ動作するようにする
if __name__ == "__main__":
    # カレントディレクトリをスクリプトの場所に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    extracted_blocks = extract_code_blocks(text)
    for filename, code in extracted_blocks:
        print(f"Filename: {filename}\nCode:\n{code}\n")