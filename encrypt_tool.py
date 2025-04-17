from main_ui import MainUI
from language import load_language

if __name__ == '__main__':
    language = load_language()
    root = MainUI(language)
    root.run()
