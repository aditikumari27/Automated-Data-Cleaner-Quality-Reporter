# utils.py
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXT = {'csv'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def make_unique_filename(original: str) -> str:
    base = secure_filename(original)
    unique = f"{uuid.uuid4().hex}_{base}"
    return unique

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
