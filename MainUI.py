import os
import threading
import time
import glob
import tkinter as tk
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from tkinter import filedialog
from tkinter import messagebox
from SlideShow import EncryptedSlideShow
from VideoPlayer import VideoPlayer
from Decryptor import Decryptor

class MainUI:
    def __init__(self):
        self.root = None
        self.output_text = None
        self.encrypt_button = None
        self.decrypt_button = None
        self.slideshow_button = None
        self.video_button  = None
        self.buttons = []
        self.key_path = 'key.bin'
        self.create_root()

    def on_close(self):
        if messagebox.askyesno("確認關閉", "你確定要關閉這個視窗嗎？"):
            self.root.destroy()

    def create_root(self):
        self.root = tk.Tk()
        self.root.title("加解密工具")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.create_text()
        self.create_buttons()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_text(self):
        self.output_text = tk.Text(self.root, height=20, width=80, wrap=tk.WORD, state=tk.NORMAL)
        self.output_text.place(x=20, y=100, width=760, height=400)

    def create_buttons(self):
        self.encrypt_button = tk.Button(self.root, text="加密文件", command=self.start_encrypt_thread)
        self.decrypt_button = tk.Button(self.root, text="解密文件", command=self.start_decrypt_thread)
        self.slideshow_button = tk.Button(self.root, text="幻燈片", command=self.select_directory_and_slideshow)
        self.video_button = tk.Button(self.root, text="影片", command=self.start_select_video_thread)
        self.buttons = [self.encrypt_button, self.decrypt_button, self.slideshow_button, self.video_button]
        self.place_buttons()


    def place_buttons(self):
        placements = [(self.encrypt_button, 20, 20), (self.decrypt_button, 200, 20),
                      (self.slideshow_button, 400, 20), (self.video_button, 600, 20)]
        for button, x, y in placements:
            button.place(x=x, y=y, width=160, height=40)

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
        key = None
        if os.path.exists(self.key_path):
            self.after_insert_message('已找到key.bin\n')
            with open(self.key_path, "rb") as f:
                key = f.read()
        return key

    def generate_key(self):
        key = os.urandom(32)
        with open(self.key_path, "wb") as f:
            f.write(key)
        self.after_insert_message('已生成key.bin\n')

    def start_encrypt_thread(self):
        thread = threading.Thread(target=self.select_directory_and_encrypt, daemon=True)
        thread.start()

    def select_directory_and_encrypt(self):
        directory = filedialog.askdirectory(title="選擇資料夾")
        if not directory:
            self.after_insert_message('未選擇資料夾\n')
            return
        self.after_insert_message(f'正在加密{directory}下的文件...\n')
        file_paths = self.get_directory_files(directory)
        if len(file_paths) == 0:
            self.after_insert_message('沒有任何檔案\n')
            return
        self.set_buttons_config('disabled')
        key = self.load_key()
        if not key:
            self.generate_key()
            key = self.load_key()
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            if file_path.endswith('.enc'):
                self.after_insert_message(f'檔案{file_name}已經被加密過\n')
                continue
            if file_name == 'desktop.ini':
                continue
            encrypted_path = file_path + ".enc"
            self.encrypt_file(file_path, encrypted_path, key)
            self.after_insert_message(f'檔案{file_name}已加密並保存為{file_name + ".enc"}\n')
            # 要不要刪除原始檔案視情況
            #try:
            #    os.remove(file_path)
            #except Exception as e:
            #    pass
        self.after_insert_message('所有文件加密完成！\n')
        self.set_buttons_config('normal')

    def encrypt_file(self, file_path, encrypted_path, key):
        chunk_size = 64 * 1024
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        try:
            with open(file_path, 'rb') as f:
                with open(encrypted_path, 'wb') as out_f:
                    out_f.write(iv)
                    while chunk := f.read(chunk_size):
                        padded_chunk = padder.update(chunk)
                        encrypted_chunk = encryptor.update(padded_chunk)
                        out_f.write(encrypted_chunk)
                    final_chunk = encryptor.update(padder.finalize())
                    out_f.write(final_chunk)
        except Exception as e:
            self.after_insert_message(f'加密{file_path}時出現錯誤\n')

    def start_decrypt_thread(self):
        thread = threading.Thread(target=self.select_directory_and_decrypt, daemon=True)
        thread.start()

    def select_directory_and_decrypt(self):
        directory = filedialog.askdirectory(title="選擇資料夾")
        if not directory:
            self.after_insert_message('未選擇資料夾\n')
            return
        self.after_insert_message(f'正在解密{directory}下的文件...\n')
        file_paths = self.get_directory_files(directory)
        if len(file_paths) == 0:
            self.after_insert_message('沒有任何檔案\n')
            return
        key = self.load_key()
        if not key:
            self.after_insert_message('key.bin不存在\n')
            return
        self.set_buttons_config('disabled')
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            if file_path.endswith('.enc'):
                decrypted_path = file_path[:-4]
                decrypted_file_name = os.path.basename(decrypted_path)
                decryptor = Decryptor(key)
                decryptor.decrypt_file(file_path, decrypted_path)
                self.after_insert_message(f'檔案{file_name}已解密並保存為{decrypted_file_name}\n')
                time.sleep(1)
        self.after_insert_message('所有文件解密完成！\n')
        self.set_buttons_config('normal')

    def start_slideshow_thread(self):
        thread = threading.Thread(target=self.select_directory_and_slideshow, daemon=True)
        thread.start()

    def select_directory_and_slideshow(self):
        directory = filedialog.askdirectory(title="選擇圖片資料夾")
        if not directory:
            self.after_insert_message('未選擇資料夾\n')
            return
        image_files = glob.glob(os.path.join(directory, "*.enc"))
        if not image_files:
            self.after_insert_message('沒有任何enc檔案\n')
            return
        key = self.load_key()
        if not key:
            self.after_insert_message('key.bin不存在\n')
            return
        slideshow = EncryptedSlideShow(image_files, key, delay=3000)
        slideshow.run()

    def start_select_video_thread(self):
        thread = threading.Thread(target=self.select_video_and_play, daemon=True)
        thread.start()

    def select_video_and_play(self):
        encrypted_file_path = filedialog.askopenfilename(title="選擇影片", filetypes=[("Encrypted Files", "*.enc")])
        if not encrypted_file_path:
            self.after_insert_message('未選擇檔案\n')
            return
        key = self.load_key()
        if not key:
            self.after_insert_message('key.bin不存在\n')
            return
        decrypted_file_path = encrypted_file_path.replace('.enc', '')
        decryptor = Decryptor(key)
        decryptor.decrypt_file(encrypted_file_path, decrypted_file_path)
        self.after_insert_message(f'文件解密完成，保存至 {decrypted_file_path}\n')
        self.set_buttons_config('disabled')
        player = VideoPlayer(decrypted_file_path, self.after_insert_message)
        player.play()
        while player.is_play:
            time.sleep(1)
        self.set_buttons_config('normal')
