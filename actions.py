# --- IMPORTS ---
import sqlite3
from datetime import datetime
from constants import table_names
from util import get_people, add_debt, get_items, add_item, show_person_options, show_item_options, add_household_need


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

    # table of items that are purchased_state
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

def input_debt():
    """Prompts user to input debt details. Adds new item to the items database if the debt is over an item not been entered before."""

    show_person_options()
    person_id = int(input("Enter the person ID who owes money: "))
    amount = float(input("How much do they owe? "))
    show_item_options()
    item_try = input("If none, type a random number not in the list. ")
    item_id = add_new_item(int(item_try))
    show_person_options()
    owed_to_id = int(input("Who do they owe it to (enter person ID)? "))
    date = input("What is the date (YYYY-MM-DD)? ")

    add_debt(item_id, person_id, owed_to_id, amount, date)

def input_sharehouse_needs():
    """Prompts user to input what the sharehouse requires with the item and the cost, and stores that into the database for later referral."""
    
    print("\nInput Sharehouse Needs")
    show_item_options()
    item_try = input("What is the item? Enter the associated number. ")
    item_id = add_new_item(int(item_try))
    budget = float(input("What is the approximate cost/budget for the household item? "))
    assigned_try = input("Are you assigning it to anyone? Enter 'N' if not. ")
    assigned_person_id = assigned_try if assigned_try.upper() != "N" else 0
    purchase_date = input("What is the desired purchase date (YYYY-MM-DD)? ")
    purchased_state = int(input("Has it been purchased yet? Enter 0 for no, and 1 for yes. "))

    add_household_need(int(item_id), float(budget), int(assigned_person_id), purchase_date, int(purchased_state))    

def add_new_item(item_try: int):
    """Adds new item to the item list if it does not exist and returns the new item's id. Otherwise, returns current item id choice"""
    items = get_items()
    item = item_try
    print(items[-1]['item_id'])
    if item > int(items[-1]['item_id']):
        item_name = input("What is the name of the item? ")
        item_cost = input("What is the cost of the item? ")
        add_item(item_name, item_cost)
        item = items[-1]['item_id'] + 1 # due to auto incrementing, the latest item added will just be the last item's id + 1
    return item