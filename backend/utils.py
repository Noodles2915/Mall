import uuid
import os

def avatar_path(instance, filename: str):
    ext = filename.split(".")[-1]
    fname = f"{uuid.uuid4().hex}.{ext}"

    return os.path.join("avatars", str(instance.id), fname)