import re

def extract_code_blocks(text):
    pattern = r'source_code_created_chat-gpt\n(?P<path>[^\n]+)\n(?P<filename>[^\n]+)\n```(?P<language>[^\n]+)\n(?P<code>.*?)\n```'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    extracted_blocks = []
    matched = False
    
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