from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())
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

# Encode keys in Base64 URL-safe format (needed for Web Push)
private_raw = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_b64 = base64.urlsafe_b64encode(private_raw).decode('utf-8').rstrip('=')

public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, 'big')
y = public_numbers.y.to_bytes(32, 'big')
public_raw = b'\x04' + x + y
public_b64 = base64.urlsafe_b64encode(public_raw).decode('utf-8').rstrip('=')

print("Private key (Base64):", private_b64)
print("Public key (Base64):", public_b64)
