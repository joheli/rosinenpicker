import hashlib

def file_sha256(file_name: str) -> str:
    with open(file_name, "rb") as f:
        bytes = f.read()
        hex_hash = hashlib.sha256(bytes).hexdigest()
        return hex_hash
