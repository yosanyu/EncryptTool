import os

language_path = 'language.txt'
languages = ['zh_TW', 'zh_CN', 'en_US', 'ja_JP']

def load_language():
    if not os.path.exists(language_path):
        return 'en_US'
    with open(language_path, 'r') as f:
        language = f.read()
        if language in languages:
            return language
    return 'en_US'