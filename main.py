# --- EXPORTS ---
from actions import initialise_database, view_database

# the big boss function
if __name__ == "__main__":
    initialise_database()
    view_database()