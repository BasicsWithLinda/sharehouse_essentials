# --- IMPORTS ---
import sqlite3
from datetime import datetime
from constants import table_names

# --- Database Operations ---
def initialise_database():
    """
    Initialising the SQLite database to store all sharehouse needs.
    
    Time complexity: O(n) where n is the number of tables created
    Space complexity: O(1) as there isn't really anything in the tables...yet!
    """

    conn = sqlite3.connect("sharehouse.db")  # create file
    cursor = conn.cursor()      # intermediary between python and the sqlite database

    ####### CREATING TABLES ########
    # table to identify people
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS People (
        person_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        allergies TEXT,
        misc_info TEXT
    );
    """)

    # table for total amount of money owed. this may not be necessary so temporarily keeping this here
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OwedMoney (
        person_id INTEGER NOT NULL,
        total_owed REAL DEFAULT 0,
        FOREIGN KEY (person_id) REFERENCES People(person_id)
    );
    """)

    # table of owed money where you can see transactions happening
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OriginOfOwedMoney (
        origin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        purchase_date TEXT,
        purchased_by INTEGER NOT NULL,
        FOREIGN KEY (purchased_by) REFERENCES People(person_id)
    );
    """)

    # table of items that are purchased
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        default_cost REAL
    );
    """)

    # table to directly view who owes what to who
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DebtMapping (
        origin_id INTEGER NOT NULL,
        owed_by INTEGER NOT NULL,
        owed_to INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY (origin_id) REFERENCES OriginOfOwedMoney(origin_id),
        FOREIGN KEY (owed_by) REFERENCES People(person_id),
        FOREIGN KEY (owed_to) REFERENCES People(person_id)
    );
    """)

    # table for what is needed in the household
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS HouseholdNeeds (
        need_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        budget REAL NOT NULL,
        purchased_by INTEGER,
        purchase_date TEXT,
        is_purchased INTEGER DEFAULT 0,
        FOREIGN KEY (item_id) REFERENCES Items(item_id),
        FOREIGN KEY (purchased_by) REFERENCES People(person_id)
    );
    """)

    # the passwords table...don't leak this
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Passwords (
        password_id INTEGER PRIMARY KEY AUTOINCREMENT,
        password_name TEXT NOT NULL,
        password_value TEXT NOT NULL,
        person_id INTEGER,
        FOREIGN KEY (person_id) REFERENCES People(person_id)
    );
    """)

    conn.commit()
    conn.close()

def view_database():
    """
    View the database in list format. Just in case you need to double check if all the data in the database is correct.
    Mostly used for debugging purposes.
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    # get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"\nContents of table: {table_name}")

        # through current table, go through each item
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        if rows:
            # print row if exists
            for row in rows:
                print(row)
        else:
            print("No data found.")

    conn.close()

def reset_database():
    """
    Resets the database by deleting all data in every table. 
    This does not affect the table schema, only the data inside them.
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    for table in table_names:
        cursor.execute(f"DELETE FROM {table};")
        print(f"All entries deleted from {table}.")

    conn.commit()
    conn.close()