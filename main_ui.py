import os
import threading
import time
import glob
import tkinter as tk
import ctypes
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from slide_show import EncryptedSlideShow
from video_player import VideoPlayer
from decrypter import Decrypter
from encrypter import Encryptor
from translation import translations

def is_hidden(filepath):
    attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
    return attrs != -1 and (attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 0x2

class MainUI:
    def __init__(self, language):
        self.root = None
        self.output_text = None
        self.encrypt_button = None
        self.decrypt_button = None
        self.slideshow_button = None
        self.video_button  = None
        self.progress_bar = None
        self.progress_label = None
        self.buttons = []
        self.language = language
        self.key_path = 'key.bin'
        self.key = None
        self.create_root()

    def on_close(self):
        if messagebox.askyesno(translations[self.language]['close'], translations[self.language]['close_message']):
            self.root.destroy()

    def create_root(self):
        self.root = tk.Tk()
        self.root.title(translations[self.language]['title'])
        self.root.geometry('800x600')
        self.root.resizable(False, False)
        self.create_text()
        self.create_buttons()
        self.create_progress_bar()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

    def create_text(self):
        self.output_text = tk.Text(self.root, height=20, width=80, wrap=tk.WORD, state=tk.NORMAL)
        self.output_text.place(x=20, y=150, width=760, height=400)

    def create_buttons(self):
        self.encrypt_button = tk.Button(self.root, text=translations[self.language]['encrypt_button'], command=self.start_encrypt_thread)
        self.decrypt_button = tk.Button(self.root, text=translations[self.language]['decrypt_button'], command=self.start_decrypt_thread)
        self.slideshow_button = tk.Button(self.root, text=translations[self.language]['slideshow_button'], command=self.select_directory_and_slideshow)
        self.video_button = tk.Button(self.root, text=translations[self.language]['video_button'], command=self.start_select_video_thread)
        self.buttons = [self.encrypt_button, self.decrypt_button, self.slideshow_button, self.video_button]
        self.place_buttons()

    def place_buttons(self):
        placements = [(self.encrypt_button, 20, 20), (self.decrypt_button, 200, 20),
                      (self.slideshow_button, 400, 20), (self.video_button, 600, 20)]
        for button, x, y in placements:
            button.place(x=x, y=y, width=160, height=40)

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=400, mode='determinate')
        self.progress_label = tk.Label(self.root, text='', font=('Arial', 25))
        self.place_progress_bar(False)

    def place_progress_bar(self, b_show:bool):
        if b_show is True:
            self.progress_bar.place(x=200, y=100, width=400, height=40)
            self.progress_label.place(x=620, y=100, width=100, height=40)
            return
        self.progress_bar['value'] = 0
        self.progress_label.config(text='')
        self.progress_bar.place_forget()
        self.progress_label.place_forget()

    def update_progress_bar(self, index:int, length:int):
        self.progress_bar['value'] = float(index) / float(length) * 100
        self.progress_label.config(text=f'{index}/{length}')

    def run(self):
        self.root.mainloop()

    def set_buttons_config(self, config):
        for button in self.buttons:
            button.config(state=config)

    def after_insert_message(self, message):
        self.root.after(0, self.insert_message, message)

    def insert_message(self, message):
        self.output_text.insert(tk.END, message)
        self.output_text.yview(tk.END)

    def get_directory_files(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths

    def load_key(self):
        if self.key:
            return
        if os.path.exists(self.key_path):
            self.after_insert_message(translations[self.language]['found_key'])
            with open(self.key_path, 'rb') as f:
                self.key = f.read()

    def generate_key(self):
        self.key = os.urandom(32)
        with open(self.key_path, "wb") as f:
            f.write(self.key)
        self.after_insert_message(translations[self.language]['generated_key'])

    def start_encrypt_thread(self):
        thread = threading.Thread(target=self.select_directory_and_encrypt, daemon=True)
        thread.start()

    def select_directory_and_encrypt(self):
        directory = filedialog.askdirectory(title=translations[self.language]['select_dir'])
        if not directory:
            self.after_insert_message(translations[self.language]['no_select_dir'])
            return
        self.after_insert_message(translations[self.language]['encrypting'].format(directory=directory))
        file_paths = self.get_directory_files(directory)
        if len(file_paths) == 0:
            self.after_insert_message(translations[self.language]['no_file'])
            return
        self.set_buttons_config('disabled')
        self.load_key()
        if not self.key:
            self.generate_key()
        index = 0
        file_length = len(file_paths)
        self.place_progress_bar(True)
        wrote_file_size = 0
        for file_path in file_paths:
            wrote_file_size += self.encrypt(file_path)
            index += 1
            self.update_progress_bar(index, file_length)
            if wrote_file_size >= 1 * 1024 * 1024 * 1024:
                wrote_file_size = 0
                self.after_insert_message('累計寫入超過1gb休息10秒\n')
                time.sleep(10)

        self.after_insert_message(translations[self.language]['encrypted'])
        self.set_buttons_config('normal')
        messagebox.showinfo(translations[self.language]['hint'], translations[self.language]['hint_encrypted'])
        self.place_progress_bar(False)

    def encrypt(self, file_path):
        file_name = os.path.basename(file_path)
        file_size = 0
        if file_path.endswith('.enc'):
            self.after_insert_message(translations[self.language]['already_encrypted'].format(file_name=file_name))
        elif is_hidden(file_path):
            self.after_insert_message(translations[self.language]['system_file'].format(file_name=file_name))
        else:
            encrypted_path = file_path + '.enc'
            start_time = time.time()
            encryptor = Encryptor(self.key)
            encryptor.encrypt_file(file_path, encrypted_path)
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.after_insert_message(translations[self.language]['encrypt_message'].format
                                      (file_name=file_name, elapsed_time=elapsed_time))
            file_size = os.path.getsize(file_path)
        return file_size


    def start_decrypt_thread(self):
        thread = threading.Thread(target=self.select_directory_and_decrypt, daemon=True)
        thread.start()

    def select_directory_and_decrypt(self):
        directory = filedialog.askdirectory(title=translations[self.language]['select_dir'])
        if not directory:
            self.after_insert_message(translations[self.language]['no_select_dir'])
            return
        self.after_insert_message(translations[self.language]['decrypting'].format(directory=directory))
        file_paths = self.get_directory_files(directory)
        if len(file_paths) == 0:
            self.after_insert_message(translations[self.language]['no_file'])
            return
        self.load_key()
        if not self.key:
            self.after_insert_message(translations[self.language]['no_key'])
            return
        self.set_buttons_config('disabled')
        index = 0
        file_length = len(file_paths)
        self.place_progress_bar(True)
        for file_path in file_paths:
            self.decrypt(file_path)
            index += 1
            self.update_progress_bar(index, file_length)
            time.sleep(0.1)
        self.after_insert_message(translations[self.language]['decrypted'])
        self.set_buttons_config('normal')
        messagebox.showinfo(translations[self.language]['hint'], translations[self.language]['hint_decrypted'])
        self.place_progress_bar(False)

    def decrypt(self, file_path):
        file_name = os.path.basename(file_path)
        if file_path.endswith('.enc'):
            decrypted_path = file_path[:-4]
            decrypted_file_name = os.path.basename(decrypted_path)
            start_time = time.time()
            decrypter = Decrypter(self.key)
            decrypter.decrypt_file(file_path, decrypted_path)
            end_time = time.time()
            elapsed_time = end_time - start_time
            self.after_insert_message(translations[self.language]['decrypt_message'].format
                                      (file_name=file_name,
                                       decrypted_file_name=decrypted_file_name,
                                       elapsed_time=elapsed_time))

    def start_slideshow_thread(self):
        thread = threading.Thread(target=self.select_directory_and_slideshow, daemon=True)
        thread.start()

    def select_directory_and_slideshow(self):
        directory = filedialog.askdirectory(title=translations[self.language]['select_dir'])
        if not directory:
            self.after_insert_message(translations[self.language]['no_select_dir'])
            return
        image_files = glob.glob(os.path.join(directory, '*.enc'))
        if not image_files:
            self.after_insert_message(translations[self.language]['no_enc_file'])
            return
        self.load_key()
        if not self.key:
            self.after_insert_message(translations[self.language]['no_key'])
            return
        slideshow = EncryptedSlideShow(image_files, self.key, 3000, self.language)
        slideshow.run()

    def start_select_video_thread(self):
        thread = threading.Thread(target=self.select_video_and_play, daemon=True)
        thread.start()

    def select_video_and_play(self):
        encrypted_file_path = filedialog.askopenfilename(title=translations[self.language]['select_video'], filetypes=[('Encrypted Files', '*.enc')])
        if not encrypted_file_path:
            self.after_insert_message(translations[self.language]['no_select_video'])
            return
        self.load_key()
        if not self.key:
            self.after_insert_message(translations[self.language]['no_key'])
            return
        decrypted_file_path = encrypted_file_path.replace('.enc', '')
        self.set_buttons_config('disabled')
        start_time = time.time()
        decrypter = Decrypter(self.key)
        decrypter.decrypt_file(encrypted_file_path, decrypted_file_path)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.after_insert_message(translations[self.language]['decrypt_video_message'].format
                                  (decrypted_file_path=decrypted_file_path, elapsed_time=elapsed_time))
        player = VideoPlayer(decrypted_file_path, self.language, self.after_insert_message)
        player.play()
        while player.is_play:
            time.sleep(1)
        self.set_buttons_config('normal')
