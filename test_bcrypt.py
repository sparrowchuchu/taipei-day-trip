import bcrypt
print(bcrypt.__version__)

password = b"test123"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print("Hashed:", hashed)

if bcrypt.checkpw(password, hashed):
    print("Password matches!")
else:
    print("Password does not match!")