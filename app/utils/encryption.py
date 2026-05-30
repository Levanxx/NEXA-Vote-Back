from cryptography.fernet import Fernet
import base64
from app.config import Config

_key = None

def _get_key():
    global _key
    if _key is None:
        raw = Config.VOTE_SECRET_KEY.ljust(32, '0')[:32]
        _key = base64.urlsafe_b64encode(raw.encode())
    return _key

def encrypt_text(plain: str) -> str:
    return Fernet(_get_key()).encrypt(plain.encode()).decode()

def decrypt_text(token: str) -> str:
    # Backward compat: si no tiene formato Fernet, es dato viejo (texto plano)
    if not token.startswith("gAAAAA"):
        return token
    return Fernet(_get_key()).decrypt(token.encode()).decode()