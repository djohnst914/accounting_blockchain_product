from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding



# New class for User with cryptographic capabilities
class User:

    # This is the constructor method that initializes a new User object. It takes a parameter name to 
    # assign a name to the user. Inside the constructor, the following actions are performed:
    # - A private key is generated using the generate_private_key function from the 
    # cryptography.hazmat.primitives.asymmetric module.
    # - The private key is used to derive a corresponding public key.
    # - The private_key and public_key attributes are assigned to the user object.
    def __init__(self, name):
        self.name = name
        self.private_key = generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    # This method takes a transaction parameter, which is presumably an object representing a transaction. The method 
    # converts the transaction data to bytes, signs it using the private key, and returns the resulting signature. 
    # The signature is generated using the PSS (Probabilistic Signature Scheme) padding scheme with the SHA-256 hash 
    # algorithm.
    def sign_transaction(self, transaction):
        transaction_data = str(transaction).encode()
        signature = self.private_key.sign(
            transaction_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    # This method returns the public key associated with the user in PEM (Privacy Enhanced Mail) format. The public key 
    # is encoded using the serialization.Encoding.PEM format and serialization.PublicFormat.SubjectPublicKeyInfo.
    def get_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )