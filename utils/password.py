import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password, bcrypt.gensalt())


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password, hash_password)
