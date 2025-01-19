import sqlite3
from constants import table_names

############################ VIEWING/RESETTING DATABASE #######################################
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

def show_person_options():
    people = get_people()
    print("Select a person from the following list by enterring the number next to it:")
    for person in people:
        print(f"{person['person_id']}: {person['full_name']}")

def show_item_options():
    items = get_items()
    print("Select an item from the following list by enterring the number next to it:")
    for it in items:
        print(f"{it['item_id']}: {it['item_name']} with cost ${it['default_cost']}")

############################ ADDING OR REMOVING FROM DATABASE #######################################

def add_person(first_name, last_name, allergies=None, misc_info=None):
    """Adds a new person to the database"""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO People (first_name, last_name, allergies, misc_info)
                   VALUES (?, ?, ?, ?)""", (first_name, last_name, allergies, misc_info))
    
    conn.commit()
    conn.close()

def delete_person(person_id):
    """Deletes a person from the database by person_id"""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM People WHERE person_id = ?", (person_id,))
    conn.commit()
    conn.close()

def add_item(item_name, default_cost):
    """Adds a new item to the Items table"""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Items (item_name, default_cost)
    VALUES (?, ?)
    """, (item_name, default_cost))

    conn.commit()
    conn.close()

def delete_item(item_id):
    """Deletes an item from the Items table by item_id"""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def add_debt(person_id, item_id, owed_by, owed_to, amount, purchase_date):
    """Adds a new debt to the DebtMapping table"""
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

############################ GETTING FROM DATABASE #######################################

def get_people():
    """
    Gets all people from the database and returns a list of dictionaries with their IDs and full names
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("SELECT person_id, first_name, last_name FROM People;")
    people = [
        {"person_id": row[0], "full_name": f"{row[1]} {row[2]}"}
        for row in cursor.fetchall()
    ]

    conn.close()
    return people

def get_owed_amounts():
    """"
    Gets the total owed amount for each person from the database
    Returns a list of dictionaries with person ID, name, and amount owed
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT People.person_id, first_name, last_name, SUM(amount)
    FROM DebtMapping
    JOIN People ON DebtMapping.owed_by = People.person_id
    GROUP BY People.person_id;
    """)

    owed_amounts = [
        {"person_id": row[0], "full_name": f"{row[1]} {row[2]}", "amount_owed": row[3] or 0}
        for row in cursor.fetchall()
    ]

    conn.close()
    return owed_amounts

def get_debt_details():
    """
    Gets detailed debt records, including what was owed, who owes it, and to whom
    Returns a list of dictionaries with debt details
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        DM.origin_id,
        P1.first_name || ' ' || P1.last_name AS owed_by,
        P2.first_name || ' ' || P2.last_name AS owed_to,
        Items.item_name,
        DM.amount
    FROM DebtMapping DM
    JOIN People P1 ON DM.owed_by = P1.person_id
    JOIN People P2 ON DM.owed_to = P2.person_id
    JOIN OriginOfOwedMoney OOM ON DM.origin_id = OOM.origin_id
    JOIN Items ON OOM.item_id = Items.item_id;
    """)

    debt_details = [
        {"origin_id": row[0], "owed_by": row[1], "owed_to": row[2], "item_name": row[3], "amount": row[4]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return debt_details

def get_items():
    """
    Gets all items from the database and returns a list of dictionaries with their details
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("SELECT item_id, item_name, default_cost FROM Items;")
    items = [
        {"item_id": row[0], "item_name": row[1], "default_cost": row[2] or 0.0}
        for row in cursor.fetchall()
    ]

    conn.close()
    return items

def get_item_cost(item_id):
    """
    Gets the cost of an item from the database based on its item_id
    
    Args:
        item_id (int): The ID of the item to fetch the cost for

    Returns:
        float: The cost of the item if it exists, or None
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("SELECT default_cost FROM Items WHERE item_id = ?;", (item_id,))
    result = cursor.fetchone()
    
    conn.close()

    if result:
        return result[0] or 0.0  # defaults to 0 if does not exist
    return None  # Item not found
