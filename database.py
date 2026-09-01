import sqlite3

DATABASE = "reflex.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            address TEXT NOT NULL,
            item_description TEXT NOT NULL,
            rider TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            order_code TEXT UNIQUE NOT NULL
        )
    """)

    connection.commit()
    connection.close()
    