"""Rotate one account password without storing credentials in source."""
import os
import sqlite3
import sys
from werkzeug.security import generate_password_hash

email = os.environ.get('ACCOUNT_EMAIL', '').strip().lower()
password = os.environ.get('NEW_PASSWORD', '')
if not email or not password:
    sys.exit('Set ACCOUNT_EMAIL and NEW_PASSWORD before running this script.')
if len(password) < 12 or len(password) > 128:
    sys.exit('NEW_PASSWORD must contain 12 to 128 characters.')

db = sqlite3.connect('database.db')
try:
    result = db.execute('UPDATE users SET password_hash = ? WHERE email = ?',
                        (generate_password_hash(password), email))
    if result.rowcount != 1:
        sys.exit('No account exists for ACCOUNT_EMAIL; create it through the approved provisioning process.')
    db.commit()
finally:
    db.close()
print('Password rotated successfully.')
