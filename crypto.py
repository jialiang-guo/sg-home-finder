"""Versioned interoperable AES-256-GCM / PBKDF2-SHA256 envelope."""
import base64, hashlib, json, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ITERATIONS = 600000
AAD = b'sg-home-finder-v1'
def key(password, salt, iterations=ITERATIONS):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, 32)
def encrypt(data, password):
    if len(password) < 20:
        raise ValueError('SITE_PASSWORD must contain at least 20 characters')
    salt, iv = os.urandom(16), os.urandom(12)
    ciphertext = AESGCM(key(password, salt)).encrypt(iv, json.dumps(data, ensure_ascii=False).encode(), AAD)
    enc = lambda b: base64.b64encode(b).decode()
    return dict(version=1, iterations=ITERATIONS, salt=enc(salt), iv=enc(iv), ciphertext=enc(ciphertext))
def decrypt(envelope, password):
    if envelope['version'] != 1 or envelope['iterations'] != ITERATIONS:
        raise ValueError('Unsupported encryption format')
    dec = lambda s: base64.b64decode(s, validate=True)
    return json.loads(AESGCM(key(password, dec(envelope['salt']))).decrypt(dec(envelope['iv']), dec(envelope['ciphertext']), AAD))
