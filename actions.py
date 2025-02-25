# --- IMPORTS ---
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
from constants import table_names
from util import get_people, add_debt, get_items, add_item, show_person_options, show_item_options, add_household_need, show_unresolved_debts, delete_debt, show_needs_to_be_purchased, set_need_as_purchased, get_total_owed_per_person, get_household_needs


# --- Database Operations ---
def initialise_database() -> None:
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

######################### FUNCTIONS THE USER CALLS UPON ##############################

def input_debt() -> None:
    """
    Prompts user to input debt details. Adds new item to the items database if the debt is over an item not been entered before.
    
    Time complexity: O(n+m) where n is the number of people and m is the number of items
        This is because show_person_options iterates through the number of people (n) to show
        and show_item_options iterates through the number of items (m) to show the user.
    """

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
    print("Debt has been successfully logged.")

def input_sharehouse_needs() -> None:
    """
    Prompts user to input what the sharehouse requires with the item and the cost, and stores that into the database for later referral.
    
    Time complexity: O(m) where m is the number of items
        This is due to show_item_options being called.
    """
    
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

    print("Sharehouse need has been successfully added.")

def confirm_debt_payment() -> None:
    """
    Handles debt payment confirmation.
    
    Time complexity: O(d) where d is the number of unresolved debts
        This is due to show_unresolved_debts being called
    """
    print("\nConfirm Debt Payment")
    show_unresolved_debts()
    debt_id = input("Input the associated number to the debt. ")

    delete_debt(int(debt_id))

    print("Debt payment confirmed.")

def confirm_houseneed_payment() -> None:
    """
    Handles confirmation of sharehouse needs payment.
    
    Time complexity: O(h) where h is the number of unpurchased household needs.
        This is due to show_needs_to_be_purchased being called.
    """
    print("\nConfirm Sharehouse Needs Payment")
    show_needs_to_be_purchased()
    needs_id = input("What is the number of the associated need that has been purchased? ")

    set_need_as_purchased(needs_id)

    print("Sharehouse need payment confirmed.")

def visualise_household_data() -> None:
    """
    Visualises household needs data to keep it easier to track. Will output:
        - A bar chart for the total amount owed by each person.
        - A table for unpurchased household needs.
        - A table for purchased household needs.

    Time complexity: O(n+h) where n is the total number of people and h is the total number of household needs items

    """
    # total owed per person graph (bar graph)
    total_owed = get_total_owed_per_person()
    plot_total_owed(total_owed)

    # unpurchased needs table with total budget cost at the bottom
    unpurchased_needs = get_household_needs(is_purchased=0)
    display_needs_table(unpurchased_needs, "Unpurchased Household Needs")

    # purchased needs table with total budget used at the bottom
    purchased_needs = get_household_needs(is_purchased=1)
    display_needs_table(purchased_needs, "Purchased Household Needs")


######################## HELPER FUNCTIONS ##############################

def add_new_item(item_try: int) -> int:
    """
    Adds new item to the item list if it does not exist and returns the new item's id. Otherwise, returns current item id choice

    Args: 
        item_try (int): the initial input of the item id that the user submitted

    Time complexity: O(m) where m is the number of items in the database.
    """
    items = get_items()
    item = item_try
    print(items[-1]['item_id'])
    if item > int(items[-1]['item_id']):
        item_name = input("What is the name of the item? ")
        item_cost = input("What is the cost of the item? ")
        add_item(item_name, item_cost)
        item = int(items[-1]['item_id']) + 1 # due to auto incrementing, the latest item added will just be the last item's id + 1
    return item

def plot_total_owed(total_owed: list[tuple[str, float]]) -> None:
    """
    A bar chart for the total amount owed by each person in the sharehouse

    Args:
        total_owed (list[tuple[str, float]]): A list of tuples containing person's full name and amount owed.
    
    Time complexity: O(n) where n is the number of total people in the sharehouse
    """
    names = [entry[0] for entry in total_owed]
    amounts = [entry[1] for entry in total_owed]

    plt.figure(figsize=(8, 6))
    plt.bar(names, amounts, color='skyblue')
    plt.title('Total Amount Owed by Each Person')
    plt.xlabel('Person')
    plt.ylabel('Total Owed ($)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def display_needs_table(needs: list[tuple[str, float]], title: str) -> None:
    """
    Displays a table for household needs and specifically household needs.

    Args:
        needs (list[tuple[str, float]]): A list of tuples containing item names and their budgets.
        title (str): Title for the table.
    
    Time complexity: O(h) where h is the total number of household needs
    """
    # collecting data
    headers = ["Item Name", "Budget ($)"]
    table_data = [[entry[0], f"${entry[1]:.2f}"] for entry in needs]
    total_budget = sum(entry[1] for entry in needs)

    # creating table
    plt.figure(figsize=(6, len(table_data) + 2))
    plt.axis("off")  # Remove axes
    plt.title(title, fontsize=14, weight='bold')

    # adding data to table
    table = plt.table(
        cellText=table_data + [["Total", f"${total_budget:.2f}"]],
        colLabels=headers,
        loc="center",
        cellLoc="center",
        colLoc="center"
    )

    # formatting 
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(headers))))

    plt.show()