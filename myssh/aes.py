
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

def handleKey(key):
    # 使用 SHA-256 哈希函数将密钥单词转换为 16 字节的密钥
    return hashlib.sha256(key.encode()).digest()[:16]

def encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return ciphertext
    # cipher = AES.new(key, AES.MODE_ECB)
    # ciphertext = cipher.encrypt(plaintext)
    # return ciphertext

def decrypt(ciphertext,key):
    decipher = AES.new(key, AES.MODE_ECB)
    decrypted_text = decipher.decrypt(ciphertext)
    return decrypted_text