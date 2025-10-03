"""
Generate ECDSA key pair for certificate signing.
Run once: python gen_keys.py
Outputs: private.pem and public.pem in current dir (move to keys/ manually or via build.sh)
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

# Generate private key (SECP384R1 curve for security)
private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())

# Serialize private key (PEM format, no password for simplicity)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Get public key
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Save files
with open('private.pem', 'wb') as f:
    f.write(private_pem)
with open('public.pem', 'wb') as f:
    f.write(public_pem)

print("Keys generated: private.pem and public.pem")
print("WARNING: Keep private.pem secure! Never commit to Git.")