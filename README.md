# simple-ask-gpt

## init.py

You need to execute init.py first. It will generate question.md and some files. 

## How to use

- Write a question on question.md.
- Change the JSON file to manage what source code will be input in ask_aoai_files_config.json by changing "true" or "false" status.
- Then just run use ask-gpt.py

## update_files_config.py
You can automatically  update the JSON file by executing update_files_config.py

What the code does is this file will search the directory and find a new file except files which written in ask_aoai_files_config.json as "exclude".
Then let the gpt to generate the JSON script and parse the response, then replace the ask_aoai_files_config.json. 

