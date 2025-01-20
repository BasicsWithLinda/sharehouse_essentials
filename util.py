import sqlite3
from typing import Dict, List, Optional, Union
from constants import table_names

def view_database() -> None:
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

def reset_database() -> None:
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

def add_person(first_name: str, last_name: str, allergies: Optional[str] = None, misc_info: Optional[str] = None) -> None:
    """Adds a new person to the database."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO People (first_name, last_name, allergies, misc_info)
                   VALUES (?, ?, ?, ?)""", (first_name, last_name, allergies, misc_info))
    
    conn.commit()
    conn.close()

def delete_person(person_id: int) -> None:
    """Deletes a person from the database by person_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM People WHERE person_id = ?", (person_id,))
    conn.commit()
    conn.close()

def add_item(item_name: str, default_cost: float) -> None:
    """Adds a new item to the Items table."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Items (item_name, default_cost)
    VALUES (?, ?)
    """, (item_name, default_cost))

    conn.commit()
    conn.close()

def delete_item(item_id: int) -> None:
    """Deletes an item from the Items table by item_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def add_debt(person_id: int, item_id: int, owed_by: int, owed_to: int, amount: float, purchase_date: str) -> None:
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

def delete_debt(debt_id: int) -> None:
    """Deletes a debt from the DebtMapping table by debt_id."""
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM DebtMapping WHERE origin_id = ?", (debt_id,))
    conn.commit()
    conn.close()

def get_people() -> List[Dict[str, Union[int, str]]]:
    """
    Fetches all people from the database and returns a list of dictionaries with their IDs and full names.
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

def get_owed_amounts() -> List[Dict[str, Union[int, str, float]]]:
    """
    Fetches the total owed amount for each person from the database.
    Returns a list of dictionaries with person ID, name, and amount owed.
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

def get_debt_details() -> List[Dict[str, Union[int, str, float]]]:
    """
    Fetches detailed debt records, including what was owed, who owes it, and to whom.
    Returns a list of dictionaries with debt details.
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
