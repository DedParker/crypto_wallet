import os
import hashlib
import pyotp
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from functions import Wallet, Transaction
from words import wordlist

#генерирует bip39 мнемонику
def generate_bip39_mnemonic(strength=256):
    if strength not in [128, 160, 192, 224, 256]:
        raise ValueError("Invalid strength value")

    entropy = os.urandom(strength // 8)
    entropy_hash = hashlib.sha256(entropy).digest()
    checksum_bits = bin(int.from_bytes(entropy_hash, 'big'))[2:].zfill(256)[:strength // 32]
    entropy_bits = bin(int.from_bytes(entropy, 'big'))[2:].zfill(strength)
    combined_bits = entropy_bits + checksum_bits

    mnemonic = []
    for i in range(0, len(combined_bits), 11):
        idx = int(combined_bits[i:i + 11], 2)
        mnemonic.append(wordlist[idx])

    return " ".join(mnemonic)

#создает seed на основе мнемоники и необязательного пароля
def derive_seed(mnemonic, passphrase=""):
    salt = "mnemonic" + passphrase
    return hashlib.pbkdf2_hmac(
        "sha512",
        mnemonic.encode("utf-8"),
        salt.encode("utf-8"),
        2048,
        64
    )

#класс для работы с totp-кодами
class MFAHandler:
    def __init__(self, secret=None):
        self.secret = secret or pyotp.random_base32()

    def generate_totp(self):
        totp = pyotp.TOTP(self.secret, interval=300)
        return totp.now()

    def verify_totp(self, code):
        totp = pyotp.TOTP(self.secret, interval=300)
        return totp.verify(code)

    def get_provisioning_uri(self, account_name):
        return pyotp.totp.TOTP(self.secret).provisioning_uri(
            account_name,
            issuer_name="CryptoWallet"
        )

#имитирует работу с hsm-устройством
class HSMClient:
    def __init__(self, hsm_lib_path):
        self.session = None

    def generate_key(self, key_id):
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def sign(self, private_key, data):
        return private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )

#работа с ключами в офлайн-режиме
class ColdStorage:
    @staticmethod
    def generate_offline_key():
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    @staticmethod
    def export_key(private_key):
        return private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )

    @staticmethod
    def sign_offline(private_key, transaction_data):
        return private_key.sign(
            transaction_data,
            ec.ECDSA(hashes.SHA256())
        )

#проверка подписи с использованием открытого ключа
def verify_signature(public_key, signature, data):
    try:
        public_key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
