import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_aes_key(password: str):
    """Converts a normal password into a secure 32-byte AES key."""
    salt = b"btech_project_salt" # In a production app, this should be random
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

def encrypt_text(text: str, password: str):
    """Encrypts the text using AES."""
    f = get_aes_key(password)
    # Fernet uses AES in CBC mode under the hood
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text: str, password: str):
    """Decrypts the text. Returns None if password is wrong."""
    f = get_aes_key(password)
    try:
        return f.decrypt(encrypted_text.encode()).decode()
    except:
        return None # Wrong password or corrupted data