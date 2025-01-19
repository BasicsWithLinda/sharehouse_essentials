import sqlite3
from constants import table_names

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

def add_person(first_name, last_name, allergies=None, misc_info=None):
    """Adds a new person to the database."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO People (first_name, last_name, allergies, misc_info)
                   VALUES (?, ?, ?, ?)""", (first_name, last_name, allergies, misc_info))
    
    conn.commit()
    conn.close()

def delete_person(person_id):
    """Deletes a person from the database by person_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM People WHERE person_id = ?", (person_id,))
    conn.commit()
    conn.close()

def add_item(item_name, default_cost):
    """Adds a new item to the Items table."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Items (item_name, default_cost)
    VALUES (?, ?)
    """, (item_name, default_cost))

    conn.commit()
    conn.close()

def delete_item(item_id):
    """Deletes an item from the Items table by item_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def add_debt(person_id, item_id, owed_by, owed_to, amount, purchase_date):
    """Adds a new debt to the DebtMapping table."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO OriginOfOwedMoney (item_id, purchase_date, purchased_by)
    VALUES (?, ?, ?)
    """, (item_id, purchase_date, owed_by))

    origin_id = cursor.lastrowid  # getting id of inserted row to add to debt mapping

    cursor.execute("""
    INSERT INTO DebtMapping (origin_id, owed_by, owed_to, amount)
    VALUES (?, ?, ?, ?)
    """, (origin_id, owed_by, owed_to, amount))

    conn.commit()
    conn.close()

def delete_debt(debt_id):
    """Deletes a debt from the DebtMapping table by debt_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM DebtMapping WHERE origin_id = ?", (debt_id,))
    conn.commit()
    conn.close()