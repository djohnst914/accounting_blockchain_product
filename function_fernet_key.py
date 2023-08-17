from cryptography.fernet import Fernet



# This function generates a new Fernet key and saves it to a file named "secret.key" in binary mode. The generated key 
# is written directly to the file using the write() method.
def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# This function reads the previously generated Fernet key from the "secret.key" file in binary mode and returns the key 
# as raw bytes.
def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

# This function takes a message in the form of bytes and encrypts it using the Fernet encryption scheme. It loads the 
# Fernet key using the load_key() function, initializes a Fernet object with the key, and then encrypts the input message
# bytes using the encrypt() method of the Fernet object. The encrypted message is returned.
def encrypt_message(message_bytes):
    """
    Encrypts a message
    """
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message_bytes)
    return encrypted_message

# This function takes an encrypted message (presumably obtained by using the encrypt_message() function) and decrypts it 
# using the Fernet decryption scheme. It loads the Fernet key using the load_key() function, initializes a Fernet object 
# with the key, and then decrypts the encrypted message using the decrypt() method of the Fernet object. The decrypted 
# message (in bytes) is returned.
def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message  # don't decode