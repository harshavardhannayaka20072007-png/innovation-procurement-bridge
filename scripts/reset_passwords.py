"""One-time script: update all demo account passwords in the live database.db."""
import sqlite3
from werkzeug.security import generate_password_hash

PASSWORDS = {
    'gov_admin':      'nrm20142029',
    'evaluator_tech': 'rlg2026IPB',
    'sys_admin':      'admin@Bridge2026!',
    'techsolve':      'techsolve@2026',
    'greenwater':     'greenwater@2026',
}

db = sqlite3.connect('database.db')
db.row_factory = sqlite3.Row
for username, password in PASSWORDS.items():
    new_hash = generate_password_hash(password)
    db.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, username))
    print(f'Updated: {username}')

db.commit()

# Verify
print('\nVerification:')
from werkzeug.security import check_password_hash
rows = db.execute('SELECT username, password_hash, role FROM users').fetchall()
for row in rows:
    row = dict(row)
    expected = PASSWORDS.get(row['username'])
    if expected:
        ok = check_password_hash(row['password_hash'], expected)
        print(f"  {row['username']} ({row['role']}): {'PASS' if ok else 'FAIL'}")
    else:
        print(f"  {row['username']} ({row['role']}): (user-registered, not updated)")

db.close()
print('\nDone.')
