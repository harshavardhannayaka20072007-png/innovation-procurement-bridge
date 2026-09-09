import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sih2026-maharashtra-innovation-bridge-secret'
    DATABASE = os.path.join(BASE_DIR, 'database.db')
    SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
    SEED_PATH = os.path.join(BASE_DIR, 'database', 'seed.sql')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
