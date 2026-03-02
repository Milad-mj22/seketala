from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

fernet = Fernet(settings.PASSWORD_ENCRYPTION_KEY)

def encrypt_text(plain: str) -> str:
    if plain is None:
        return ""
    token = fernet.encrypt(plain.encode("utf-8"))
    return token.decode("utf-8")

def decrypt_text(token: str) -> str:
    if not token:
        return ""
    try:
        plain = fernet.decrypt(token.encode("utf-8"))
        return plain.decode("utf-8")
    except InvalidToken:
        return "[DECRYPTION ERROR]"
