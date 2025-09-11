import base64
import math

# ---- Oracle helpers (ground truth using Python stdlib) ----

def int_to_le_bytes(n: int) -> bytes:
    if n < 0:
        raise ValueError("negative not supported in oracle")
    if n == 0:
        return b"\x00"
    length = math.ceil(n.bit_length() / 8)
    return n.to_bytes(length, "little")

def le_b64_from_int(n: int) -> str:
    return base64.b64encode(int_to_le_bytes(n)).decode("ascii")

def int_from_le_b64(s: str) -> int:
    raw = base64.b64decode(s, validate=True)
    return int.from_bytes(raw, "little") if raw else 0

def render(value: int, kind: str) -> str:
    if kind == "decimal":
        return str(value)
    if kind == "binary":
        return format(value, "b")
    if kind == "octal":
        return format(value, "o")
    if kind == "hexadecimal":
        return format(value, "x")
    if kind == "base64":
        return le_b64_from_int(value)
    raise AssertionError(f"unknown kind {kind}")

def parse(text: str, kind: str) -> int:
    s = text.strip()
    if kind == "decimal":
        return int(s)
    if kind == "binary":
        return int(s, 2)
    if kind == "octal":
        return int(s, 8)
    if kind == "hexadecimal":
        return int(s, 16)
    if kind == "base64":
        return int_from_le_b64(s)
    raise AssertionError(f"unknown kind {kind}")