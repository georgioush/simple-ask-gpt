import re
import os

def extract_code_blocks(text):
    """
    指定されたテキストからファイル名、パス、そしてコードブロックを抽出します。

    Args:
        text (str): テキストデータ

    Returns:
        list of tuple: 抽出されたファイル名、パス、コードブロックのリスト
    """
    # 正規表現パターン
    pattern = r'source_code_created_chat-gpt\n(?P<path>[^\n]+)\n(?P<filename>[^\n]+)\n```(?P<language>[^\n]+)\n(?P<code>.*?)\n```'
    
    # 正規表現でマッチ
    matches = re.finditer(pattern, text, re.DOTALL)
    
    # 抽出されたファイル名、パス、コードブロックのリスト
    extracted_blocks = []

    matched = False
    
    # 各マッチから内容を抽出
    for match in matches:
        matched = True
        path = match.group('path').strip()
        filename = match.group('filename').strip()
        code = match.group('code').strip()
        
        extracted_blocks.append((path, filename, code))
    
    if not matched:
        print("No matches found.")
        return []

    return extracted_blocks
