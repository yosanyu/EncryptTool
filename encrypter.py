import os
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class Encryptor:
    def __init__(self, key):
        self.key = key

    def encrypt_file(self, file_path, encrypted_path):
        chunk_size = 64 * 1024
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        with open(file_path, 'rb') as f:
            with open(encrypted_path, 'wb') as out_f:
                out_f.write(iv)
                while chunk := f.read(chunk_size):
                    padded_chunk = padder.update(chunk)
                    encrypted_chunk = encryptor.update(padded_chunk)
                    out_f.write(encrypted_chunk)
                final_chunk = encryptor.update(padder.finalize())
                out_f.write(final_chunk)
