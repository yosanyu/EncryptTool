import random
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from Decryptor import Decryptor

class EncryptedSlideShow:
    def __init__(self, image_paths, key, delay=2000):
        self.root = None
        self.photo = None
        self.image_paths = image_paths
        self.key = key
        self.delay = delay
        self.shown_indices = []
        self.create_root()

    def create_root(self):
        self.root = tk.Toplevel()
        self.root.title("幻燈片")
        self.root.geometry("800x600")
        self.label = tk.Label(self.root)
        self.label.pack()

    def run(self):
        self.show_image()
        self.root.mainloop()

    def show_image(self):
        if len(self.shown_indices) == len(self.image_paths):
            self.shown_indices = []
        remaining_indices = [i for i in range(len(self.image_paths)) if i not in self.shown_indices]
        random_index = random.choice(remaining_indices)
        image_path = self.image_paths[random_index]
        decryptor = Decryptor(self.key)
        decrypted_image = decryptor.decrypt_image_memory(image_path)
        img = Image.open(decrypted_image)
        img = img.resize((800, 600))
        self.photo = ImageTk.PhotoImage(img)
        self.label.config(image=self.photo)
        self.label.image = self.photo
        self.shown_indices.append(random_index)
        self.root.after(self.delay, self.show_image)