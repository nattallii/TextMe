import secrets

def generate_verification_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"