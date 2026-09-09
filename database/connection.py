import sys
import os

# Ensures Python can locate 'config.py' regardless of execution path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Establishes and returns a MySQL database connection using DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)