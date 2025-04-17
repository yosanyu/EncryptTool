import io
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class Decrypter:
    def __init__(self, key):
        self.key = key

    def decrypt_file(self, encrypted_path, decrypted_path):
        chunk_size = 64 * 1024
        with open(encrypted_path, 'rb') as f:
            iv = f.read(16)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            with open(decrypted_path, 'wb') as out_f:
                prev_data = b''
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    decrypted = decryptor.update(chunk)
                    if prev_data:
                        out_f.write(prev_data)
                    prev_data = decrypted
                final_decrypted = decryptor.finalize()
                full_data = prev_data + final_decrypted
                unpadded = unpadder.update(full_data) + unpadder.finalize()
                out_f.write(unpadded)

    def decrypt_image_memory(self, encrypted_path):
        with open(encrypted_path, 'rb') as f:
            iv = f.read(16)
            encrypted_data = f.read()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        original_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return io.BytesIO(original_data)