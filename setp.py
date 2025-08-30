import bcrypt

password = b"missanka123"  # Use b"" for bytes
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())
