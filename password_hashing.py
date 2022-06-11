def create_hash(password: bytes or str) -> str:
    if isinstance(password, str):
        password = bytes(password, "utf-8")
    import hashlib  # importing haslib library for hash algorithms
    # hexdigest makes it go brrrr 0xAAAAAAAA
    return hashlib.sha224(password).hexdigest()  # returned hashed password in Base 16 (hexadecimal)


# not for reqular users
if __name__ == '__main__':
    print(create_hash(b"admin"))
