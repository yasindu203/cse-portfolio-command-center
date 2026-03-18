import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        # This will create the file portfolio.db if it doesn't exist
        conn = sqlite3.connect(db_file)
        # FIXED: Changed sqlite3.version to sqlite3.sqlite_version for Python 3.14 compatibility
        print(f"Successfully connected to SQLite version: {sqlite3.sqlite_version}")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    
    return conn

def create_table(conn, create_table_sql):
    """Execute a CREATE TABLE statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Error creating table: {e}")

def setup_database():
    database = r"portfolio.db"

    # SQL statement for the transactions table
    # Using AUTOINCREMENT for the id so each trade gets a unique identifier
    sql_create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        ticker TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('buy', 'sell')),
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        fees REAL NOT NULL
    );
    """

    # SQL statement for the current_holdings table
    # Ticker is the PRIMARY KEY since we only want one row per company (e.g., SAMP.CM)
    sql_create_holdings_table = """
    CREATE TABLE IF NOT EXISTS current_holdings (
        ticker TEXT PRIMARY KEY,
        total_quantity REAL NOT NULL,
        average_cost REAL NOT NULL
    );
    """

    # Create a database connection
    conn = create_connection(database)

    # Create tables
    if conn is not None:
        print("Creating 'transactions' table...")
        create_table(conn, sql_create_transactions_table)
        
        print("Creating 'current_holdings' table...")
        create_table(conn, sql_create_holdings_table)
        
        print("Database setup complete.")
        
        # Close the connection when done
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    setup_database()