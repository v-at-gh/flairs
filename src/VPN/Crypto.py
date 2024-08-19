import subprocess, base64, random


try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    X25519_Provider = 'python'
except ImportError:
    X25519_Provider = 'system'

if X25519_Provider == 'python':

    class X25519:
        @staticmethod
        def gen_private_key() -> str:
            return base64.b64encode(
                X25519PrivateKey.generate().private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            ).decode()

        @staticmethod
        def gen_public_key(privkey: str) -> str:
            return base64.b64encode(
                X25519PrivateKey.from_private_bytes(base64.b64decode(privkey.encode()))
                .public_key()
                .public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            ).decode()

        @staticmethod
        def gen_preshared_key() -> str:
            return X25519.gen_private_key()

elif X25519_Provider == 'system':

    #TODO: implement binary selection
    WG_BIN_PATH = '/opt/homebrew/bin/wg'
    OPENSSL_BIN_PATH = '/opt/homebrew/bin/openssl'

    class X25519:
        @staticmethod
        def gen_private_key() -> str:
            private_key = subprocess.run(
                [WG_BIN_PATH, 'genkey'], capture_output=True, encoding='utf-8', text=True
            ).stdout.strip()
            return private_key

        @staticmethod
        def gen_public_key(private_key: str) -> str:
            public_key = subprocess.run(
                [WG_BIN_PATH, 'pubkey'], input=private_key, capture_output=True, encoding='utf-8', text=True
            ).stdout.strip()
            return public_key

        @staticmethod
        def gen_preshared_key() -> str:
            return X25519.gen_private_key()

# class OpenVPN:
#     @staticmethod
#     def gen_certificate():
#         return base64.b64encode(random.randbytes(128)).decode()

#     @staticmethod
#     def gen_private_key():
#         return base64.b64encode(random.randbytes(128)).decode()

# class IPsec(OpenVPN): pass
