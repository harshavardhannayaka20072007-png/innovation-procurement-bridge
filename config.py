import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load local, untracked development configuration before validating required
# environment values. Production hosts should supply the same values directly.
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    # Fail closed: a predictable or process-generated key permits forged sessions.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY must be set before starting the application.')

    DATABASE = os.path.join(BASE_DIR, 'database.db')
    SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
    SEED_PATH = os.path.join(BASE_DIR, 'database', 'seed.sql')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    MAX_EVIDENCE_FILE_SIZE = 10 * 1024 * 1024
    OTP_TTL_SECONDS = 10 * 60
    OTP_MAX_ATTEMPTS = 5
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Keep this true in production. Set SESSION_COOKIE_SECURE=false only for a
    # short-lived HTTP LAN demo; HTTPS is required to protect session cookies.
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'

    # Password reset delivery is deliberately disabled until an operator configures
    # a real SMTP service. Never expose an OTP in a browser response or log.
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_FROM = os.environ.get('SMTP_FROM')

    # LinkedIn OpenID Connect is opt-in. These credentials are supplied by the
    # operator, not committed to source control.
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET')

