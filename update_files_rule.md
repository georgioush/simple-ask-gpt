後述するファイルリストのみで構成される ask_aoai_files_config.json を出力してください。
ファイルリストに存在しないものは ask_aoai_files_config.json から削除してください。
ただし exclude は保持してください。
既存の ask_aoai_files_config.json に存在しない、新規に追加されるファイルリストは、 filename に パスを含まないファイル名を記載し、include_in_input を true に指定し、description はファイル名から想定される内容を考えて、filepath は適切なパスを指定してください。
ファイルリスト: