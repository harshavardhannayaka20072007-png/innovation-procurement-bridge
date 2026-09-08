from database.connection import get_db_connection

try:
    conn = get_db_connection()
    print("DATABASE CONNECTION SUCCESSFUL")
    conn.close()
except Exception as e:
    print("DATABASE CONNECTION FAILED")
    print(e)