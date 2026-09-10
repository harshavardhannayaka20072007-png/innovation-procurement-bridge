import sqlite3
import os
from flask import g
from config import Config

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            Config.DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database using schema.sql and seed.sql if database does not exist."""
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    
    # Run schema
    if os.path.exists(Config.SCHEMA_PATH):
        with open(Config.SCHEMA_PATH, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
            
    # Run seed data if database is fresh
    if os.path.exists(Config.SEED_PATH):
        with open(Config.SEED_PATH, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
            
    db.commit()
    db.close()
    print("Database initialized and seeded successfully.")

def ensure_schema_extensions():
    """Apply additive schema changes to an existing local demo database."""
    db = sqlite3.connect(Config.DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS audit_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type VARCHAR(80) NOT NULL,
        entity_type VARCHAR(80) NOT NULL,
        entity_id INTEGER NOT NULL,
        actor_id INTEGER,
        actor_name VARCHAR(150),
        actor_role VARCHAR(50),
        payload TEXT NOT NULL,
        previous_hash VARCHAR(64) NOT NULL,
        record_hash VARCHAR(64) NOT NULL UNIQUE,
        anchor_status VARCHAR(50) NOT NULL DEFAULT 'LOCAL_SEALED',
        transaction_hash VARCHAR(100),
        created_at TIMESTAMP NOT NULL
    )''')
    # Additive migrations keep existing local databases usable without a reset.
    user_columns = {row[1] for row in db.execute('PRAGMA table_info(users)')}
    if 'mobile_number' not in user_columns:
        db.execute('ALTER TABLE users ADD COLUMN mobile_number VARCHAR(20)')
    db.execute('''CREATE TABLE IF NOT EXISTS password_reset_otps (
        reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        otp_hash VARCHAR(255) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        consumed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_challenge_startup ON applications(challenge_id, startup_id)')
    # Earlier demo data pointed to a non-viewable ZIP placeholder. Keep it usable after upgrade.
    db.execute("UPDATE milestones SET evidence_file = 'dashboard_integration_proof.pdf' WHERE evidence_file = 'dashboard_integration_proof.zip'")
    db.commit()
    db.close()

def query_db(query, args=(), one=False):
    """Helper query function that converts rows into standard Python dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    # Convert Row objects to dicts
    results = [dict(row) for row in rv]
    return (results[0] if results else None) if one else results

def execute_db(query, args=()):
    """Helper function to execute INSERT/UPDATE/DELETE queries and return inserted row id."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id
