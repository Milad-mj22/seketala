from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate EC private key (P-256 curve)
private_key = ec.generate_private_key(ec.SECP256R1())

# Export private key in base64 URL-safe VAPID format
priv_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
vapid_private = base64.urlsafe_b64encode(priv_bytes).rstrip(b'=').decode('ascii')

# Export public key in VAPID format
public_numbers = private_key.public_key().public_numbers()
x = public_numbers.x.to_bytes(32, 'big')
y = public_numbers.y.to_bytes(32, 'big')
public_key_bytes = b'\x04' + x + y

vapid_public = base64.urlsafe_b64encode(public_key_bytes).rstrip(b'=').decode('ascii')

print("VAPID_PRIVATE_KEY =", vapid_private)
print("VAPID_PUBLIC_KEY  =", vapid_public)
