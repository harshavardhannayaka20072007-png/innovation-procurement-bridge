import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY MUST be set as an environment variable in production.
    # Never use a hardcoded value — it allows session cookie forgery.
    _secret = os.environ.get('SECRET_KEY')
    if not _secret:
        # In local dev (no env file) generate a random key per process.
        # This means sessions clear on restart, which is acceptable for dev.
        _secret = secrets.token_hex(32)
    SECRET_KEY = _secret

    DATABASE = os.path.join(BASE_DIR, 'database.db')
    SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
    SEED_PATH = os.path.join(BASE_DIR, 'database', 'seed.sql')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload

