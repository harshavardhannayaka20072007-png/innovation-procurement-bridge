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
