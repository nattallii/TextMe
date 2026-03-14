

def make_dm_key(a: str, b: str) -> str:
    x, y = sorted([a, b])
    return f"{x}:{y}"