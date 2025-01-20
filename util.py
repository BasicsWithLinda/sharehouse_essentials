import sqlite3
from typing import Dict, List, Optional, Tuple, Union
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
    """
    Shows all the possible people you can select from with their associated id!

    Returns:
        Nones
    """
    people = get_people()
    print("Select a person from the following list by enterring the number next to it:")
    for person in people:
        print(f"{person['person_id']}: {person['full_name']}")

def show_item_options():
    """
    Shows all possible items you can select from!

    Returns:
        Nones
    """
    items = get_items()
    print("Select an item from the following list by enterring the number next to it:")
    for it in items:
        print(f"{it['item_id']}: {it['item_name']}")

def show_unresolved_debts():
    """
    Shows unresolved debts!

    Returns:
        Nones
    """
    unresolved_debts = get_unresolved_debts_with_details()
    
    if not unresolved_debts:
        print("No unresolved debts found.")
        return

    for debt in unresolved_debts:
        debt_id, owed_by_name, owed_to_name, item_name, amount = debt
        print(f"{debt_id}: {owed_by_name} owes {owed_to_name} for {item_name} which costs ${amount}.")

def show_needs_to_be_purchased():
    """
    Shows what needs to be purchased!

    Returns:
        None
    """
    needs = get_needs_to_be_purchased()

    if needs:
        for need_id, item_name, budget in needs:
            print(f"{need_id}: {item_name} with the budget ${budget}")
    else:
        print("All household needs have been purchased!")

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

def add_debt(item_id, owed_by, owed_to, amount, purchase_date):
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

def add_household_need(item_id: int, budget: float, purchased_by: Optional[int] = None, purchase_date: Optional[str] = None, is_purchased: int = 0) -> None:
    """
    Adds a new entry to the HouseholdNeeds table.

    Args:
        item_id (int): The ID of the item.
        budget (float): The budget for the item.
        purchased_by (int, optional): The person ID of the purchaser. Default is None.
        purchase_date (str, optional): The date of purchase in YYYY-MM-DD format. Default is None.
        is_purchased (int, optional): Whether the item has been purchased (0 for No, 1 for Yes). Default is 0.

    Returns:
        None
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    # insert the new household need
    cursor.execute("""
        INSERT INTO HouseholdNeeds (item_id, budget, purchased_by, purchase_date, is_purchased)
        VALUES (?, ?, ?, ?, ?);
    """, (item_id, budget, purchased_by, purchase_date, is_purchased))

    conn.commit()
    conn.close()
    print("Household need added successfully.")


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

def get_debt_details() -> List[Dict[str, Union[int, str, float]]]:
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

def get_items() -> List[Dict[str, Union[int, str, float]]]:
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

def get_item_cost(item_id: int) -> Optional[float]:
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

def get_unresolved_debts_with_details() -> List[Tuple[int, str, str, str, float]]:
    """
    Retrieves all unresolved debts with full details from the database.

    Returns:
        List[Tuple[int, str, str, str, float]]: A list of tuples where each tuple represents:
            - origin_id (int): the id of the debt origin
            - owed_by_name (str): full name of debtor
            - owed_to_name (str): full name of person who is owed money
            - item_name (str): name of the item associated with the debt
            - amount (float): the amount owed
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    # finds the full name of people, the item the debt is over, the actual debt, and the id of the debt.
    cursor.execute("""
        SELECT 
            dm.origin_id,
            owed_by.first_name || ' ' || owed_by.last_name AS owed_by_name,
            owed_to.first_name || ' ' || owed_to.last_name AS owed_to_name,
            it.item_name,
            dm.amount
        FROM DebtMapping dm
        JOIN People owed_by ON dm.owed_by = owed_by.person_id
        JOIN People owed_to ON dm.owed_to = owed_to.person_id
        JOIN OriginOfOwedMoney oom ON dm.origin_id = oom.origin_id
        JOIN Items it ON oom.item_id = it.item_id
        WHERE dm.amount > 0;  -- Assuming unresolved debts have an amount greater than 0
    """)
    unresolved_debts = cursor.fetchall()

    conn.close()
    return unresolved_debts

def get_needs_to_be_purchased() -> list[tuple[int, str, float]]:
    """
    Gets the household needs that need to be purchased.
    
    Args: None

    Returns:
        list[tuple[int, str, float]]: A list of tuples containing:
            - need_id (int): id associated with the household needed item
            - item_name (str): the item needed
            - budget (float): the approximate budget of the item
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            HouseholdNeeds.need_id, 
            Items.item_name, 
            HouseholdNeeds.budget
        FROM HouseholdNeeds
        JOIN Items ON HouseholdNeeds.item_id = Items.item_id
        WHERE HouseholdNeeds.is_purchased = 0;
    """)

    needs = cursor.fetchall()
    conn.close()
    return needs

def get_total_owed_per_person() -> list[tuple[str, float]]:
    """
    Retrieves the total amount owed by each person.

    Returns:
        list[tuple[str, float]]: A list of tuples containing:
            - Person's full name.
            - Total amount owed.
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.first_name || ' ' || p.last_name AS full_name,
            SUM(dm.amount) AS total_owed
        FROM DebtMapping dm
        JOIN People p ON dm.owed_by = p.person_id
        GROUP BY dm.owed_by;
    """)

    total_owed = cursor.fetchall()
    conn.close()
    return total_owed

def get_household_needs(is_purchased: int) -> list[tuple[str, float]]:
    """
    Retrieves household needs based on purchase status.

    Args:
        is_purchased (int): The purchase status (0 for not purchased, 1 for purchased).

    Returns:
        list[tuple[str, float]]: A list of tuples containing:
            - Item name.
            - Budget for the item.
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.item_name,
            hn.budget
        FROM HouseholdNeeds hn
        JOIN Items i ON hn.item_id = i.item_id
        WHERE hn.is_purchased = ?;
    """, (is_purchased,))

    needs = cursor.fetchall()
    conn.close()
    return needs


############################### SETTERS FOR DATABASE ##########################

def set_need_as_purchased(need_id: int) -> None:
    """
    Sets a household need as purchased by updating its is_purchased state to 1.

    Args:
        need_id (int): id associated with the household needed item

    Returns:
        None
    """
    conn = sqlite3.connect("sharehouse.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE HouseholdNeeds
        SET is_purchased = 1
        WHERE need_id = ?;
    """, (need_id,))

    conn.commit()
    conn.close()