import os
import shutil
from datetime import datetime

def archive_file(filepath):
    # アーカイブディレクトリが存在しない場合は作成する
    if not os.path.exists('archive'):
        os.makedirs('archive')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    archive_path = f'archive/{os.path.basename(filepath)}_{timestamp}'
    shutil.move(filepath, archive_path)  # ファイルをアーカイブディレクトリに移動
    return archive_path

def save_parsed_files(files):
    for filename, code in files:
        if os.path.exists(filename):
            # ファイルが存在する場合はアーカイブする
            archive_file(filename)
        
        # ファイルを新しい内容で上書き保存
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(code)
        print(f'{filename} を更新しました。')
