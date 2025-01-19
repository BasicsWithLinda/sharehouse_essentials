import sqlite3

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