# license_core.py
import hmac
import hashlib
import base64
import uuid
import platform
import os

SECRET_KEY = "CHANGE_THIS_SECRET_MFLOW5247_LIC_2026!!"  # 절대 공개 X (긴 문자열로 변경 추천)
PREFIX = "MFLOW"

def normalize_email(email: str) -> str:
    return email.strip().lower()

def get_device_id() -> str:
    mac = uuid.getnode()
    node = f"{mac:012x}"
    host = platform.node()
    user = os.environ.get("USERNAME", "")

    raw = f"{node}-{host}-{user}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return digest[:16].upper()

def _hmac_digest(email: str, device_id: str) -> bytes:
    message = f"{normalize_email(email)}|{device_id}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).digest()

def generate_license(email: str, device_id: str) -> str:
    digest = _hmac_digest(email, device_id)
    code = base64.b32encode(digest[:9]).decode().rstrip("=")
    return f"{PREFIX}-{code[0:4]}-{code[4:8]}-{code[8:12]}"

def verify_license(email: str, license_key: str, device_id: str) -> bool:
    expected = generate_license(email, device_id)
    return expected.upper() == license_key.strip().upper()
