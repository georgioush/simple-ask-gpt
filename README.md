# simple-ask-gpt

## 初期設定

`init.py`を最初に実行してください。このスクリプトは、`question.md`、`response.md`、`history.md`や他のいくつかのファイルを生成します。

```sh
python init.py
```

`init.py`実行後に生成されるファイルは次の通りです：
- `question.md`: このファイルには質問内容を記述します。
- `response.md`: このファイルには回答内容を記述します。
- `history.md`: このファイルは、私が聞いた質問とあなたが過去に答えた回答を記録します。


### 補足

初期設定として ask_aoai_files_config.json は git で追えないようにしています。

4. `init.py`スクリプトを使って Git のインデックスを管理することもできます。

    改めて JSON も Git に追わせたい場合は以下。
   * `git update-index --assume-unchanged  ask_aoai_files_config.json` を設定:
     ```sh
     python init.py config ignore
     ```

    改めて JSON も Git に追わせたくない場合は以下。
   * `git update-index --no-assume-unchanged  ask_aoai_files_config.json` を設定:
     ```sh
     python init.py config ack
     ```

## 使用方法

1. `question.md`に質問を記述します。
2. `ask_aoai_files_config.json`内で、`"include_in_input"` フィールドを変更することで、入力として使用するソースコードを管理します。特定のファイルを入力に含めた い場合は `true` に、含めたくない場合は `false` に設定します。

   例:
   ```json
   {
       "filename": "ask_gpt.py",
       "description": "以下のスクリプトは GPT に質問を行うための機能を有します。",
       "filepath": ".",
       "include_in_input": true
   },
   {
       "filename": "file_operations.py",
       "description": "以下のスクリプトは、ファイルのアーカイブおよび保存に関連する機能を有します。",
       "filepath": ".",
       "include_in_input": false
   }
   ```

3. 次に、`ask_gpt.py`を実行します。

```sh
python ask_gpt.py
```

## 現状のデザイン

現状のデザインとして、開発したいプロジェクトを`dev`フォルダに入れることで、その中で開発を進めながら、`ask_gpt.py`などのスクリプトを利用してコードを自動生成できるようになっています。`dev`フォルダには、あなたのプロジェクトファイルを配置し、以下の主要なクラスデザインに基づいて拡張や修正を行うことができます：

## 自動更新

`update_files_config.py`を実行することで、JSONファイルを自動的に更新できます。このスクリプトはディレクトリを検索し、`ask_aoai_files_config.json`の"exclude"に記載されていない新しいファイルを見つけます。その後、GPTにJSONスクリプトの生成を依頼し、応答を解析して、`ask_aoai_files_config.json`を置き換えます。

```sh
python update_files_config.py
```

## ファイル説明

- `ask_gpt.py`: GPTに質問を行うための機能を有したスクリプト。
- `file_operations.py`: ファイルのアーカイブおよび保存に関連する機能を持つスクリプト。
- `generate_input_from_json.py`: JSONデータを読み出し、入力用の変数を生成するスクリプト。
- `history.md`: 過去の質問と回答を記録するファイル。
- `parse_source_code.py`: ソースコードを解析するためのスクリプト。
- `update_files_config.py`: `ask_aoai_files_config.json`を更新するためのスクリプト。
- `ask_aoai_files_config.json`: AOAIに入力するファイルの設定を記述するファイル。
- `source_code_rule.md`: ソースコードを出力する際のフォーマットを規定するファイル。
- `README.md`: プロジェクトの概要と使用方法について説明するファイル。

開発したいプロジェクトを`dev`フォルダに入れて、`ask_gpt.py`などのスクリプトを利用して、コードの生成を自動化することができます。これにより、プロジェクト開発の迅速化と効率化が図れます。