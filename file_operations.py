import os
import shutil
from datetime import datetime
import atexit

def archive_file(filepath):
    if not os.path.exists('archive'):
        os.makedirs('archive')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    archive_path = f'archive/{os.path.basename(filepath)}_{timestamp}'
    shutil.copy(filepath, archive_path)
    return archive_path

def save_parsed_files(files):
    for filename, code in files:
        temp_filepath = save_to_temp_file(filename, code)
        replace_file_on_exit(filename, temp_filepath)

def save_to_temp_file(original_filepath, new_content):
    temp_filepath = original_filepath + ".tmp"
    with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
        temp_file.write(new_content)
    return temp_filepath

def replace_file_on_exit(original_filepath, temp_filepath):
    def on_exit():
        try:
            if os.path.exists(original_filepath):
                archive_file(original_filepath)
                os.remove(original_filepath)
            shutil.move(temp_filepath, original_filepath)
            print(f"{original_filepath} を更新しました。")
        except Exception as e:
            print(f"Error during file replacement: {e}")
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)  # Clean up temp file if it still exists

    atexit.register(on_exit)