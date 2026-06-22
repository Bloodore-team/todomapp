"""
Utility script to generate VAPID key pair (P-256) for Web Push.
Writes keys to stdout and optionally to .env if provided.
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64
import os

def generate_vapid_keys():
    # generate private key
    private_key = ec.generate_private_key(ec.SECP256R1())
    # private key in PEM (we will export raw private numbers as base64 urlsafe)
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # public key (uncompressed point) as bytes
    public_key = private_key.public_key()
    pub_numbers = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # base64url encode
    priv_b64 = base64.urlsafe_b64encode(priv_bytes).rstrip(b"=").decode('utf-8')
    pub_b64 = base64.urlsafe_b64encode(pub_numbers).rstrip(b"=").decode('utf-8')
    return pub_b64, priv_b64

if __name__ == '__main__':
    pub, priv = generate_vapid_keys()
    print('VAPID_PUBLIC_KEY=' + pub)
    print('VAPID_PRIVATE_KEY=' + priv)
    # optionally write to .env
    if os.path.exists('.env'):
        with open('.env','a') as f:
            f.write('\nVAPID_PUBLIC_KEY=' + pub + '\n')
            f.write('VAPID_PRIVATE_KEY=' + priv + '\n')
        print('Keys appended to .env')
