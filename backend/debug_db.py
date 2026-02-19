import sqlite3

def check_schema():
    try:
        conn = sqlite3.connect('production.db')
        cursor = conn.cursor()
        
        print("--- Users Table Schema ---")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        print("\n--- Rows in Users Table ---")
        cursor.execute("SELECT * FROM users LIMIT 1")
        print(cursor.fetchall())
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
