import bcrypt

def hash_password(password: str) -> str:
    # bcrypt recibe bytes
    password_bytes = password.encode('utf-8')

    # generar salt
    salt = bcrypt.gensalt()

    # generar hash
    hashed = bcrypt.hashpw(password_bytes, salt)

    # convertimos bytes → str para guardarlo en la BD
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    # convertimos ambos a bytes
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)
