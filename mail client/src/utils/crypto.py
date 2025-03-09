from cryptography.fernet import Fernet
import os
import base64
from pathlib import Path

def get_or_create_key():
    """Get existing key or create a new one"""
    key_path = Path.home() / '.config' / 'hood-mail' / 'crypto.key'
    
    # Create directory if it doesn't exist
    key_path.parent.mkdir(parents=True, exist_ok=True)
    
    if key_path.exists():
        with open(key_path, 'rb') as f:
            return f.read()
    else:
        # Generate new key
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        return key

def encrypt_password(password: str) -> str:
    """Encrypt password using Fernet symmetric encryption"""
    if not password:
        return ''
        
    try:
        key = get_or_create_key()
        f = Fernet(key)
        return base64.b64encode(f.encrypt(password.encode())).decode()
    except Exception as e:
        raise Exception(f"Error encrypting password: {str(e)}")

def decrypt_password(encrypted: str) -> str:
    """Decrypt password using Fernet symmetric encryption"""
    if not encrypted:
        return ''
        
    try:
        key = get_or_create_key()
        f = Fernet(key)
        return f.decrypt(base64.b64decode(encrypted)).decode()
    except Exception as e:
        raise Exception(f"Error decrypting password: {str(e)}")
