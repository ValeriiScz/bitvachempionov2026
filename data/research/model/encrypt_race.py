#!/usr/bin/env python3
"""encrypt_race.py — v1.0 · 17.09.2026
Назначение: шифрует data/race2026.js (выход build_race.py) в vault/race.json
для закрытого раздела «Гонка за дюжину» на dovod-mafia.com.
Формат тот же, что у Лаборатории (lab.html / vault/*.json):
  {"v":1,"it":250000,"s":<b64 salt 16>,"i":<b64 iv 12>,"c":<b64 ciphertext+tag>}
Ключ: PBKDF2-HMAC-SHA256(пароль, salt, it) → AES-256-GCM.
Использование:
  python3 encrypt_race.py <race2026.js> <vault/race.json> [--pass DOVOD26]
Пароль по умолчанию берётся из переменной окружения RACE_PASS.
"""
import sys, os, json, base64, argparse
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

IT = 250000

def encrypt(plaintext: bytes, password: str) -> dict:
    salt = os.urandom(16); iv = os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=IT).derive(password.encode())
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "it": IT, "s": b(salt), "i": b(iv), "c": b(ct)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--pass", dest="pw", default=os.environ.get("RACE_PASS"))
    a = ap.parse_args()
    if not a.pw: sys.exit("нет пароля: --pass или RACE_PASS")
    data = open(a.src, "rb").read()
    obj = encrypt(data, a.pw)
    os.makedirs(os.path.dirname(a.dst) or ".", exist_ok=True)
    json.dump(obj, open(a.dst, "w"), separators=(",", ":"))
    print(f"ok: {a.src} ({len(data)} B) → {a.dst} ({os.path.getsize(a.dst)} B)")

if __name__ == "__main__":
    main()
