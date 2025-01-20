# --- EXPORTS ---
from actions import initialise_database, input_debt, input_sharehouse_needs, confirm_debt_payment, confirm_houseneed_payment, visualise_household_data
import util

# the big boss function
if __name__ == "__main__":
    initialise_database()
    while True:
        print("\nWhat would you like? Type the number associated with the option:")
        print("1. Input debt")
        print("2. Input sharehouse needs")
        print("3. Confirm debt payment")
        print("4. Confirm sharehouse needs payment")
        print("5. Visualize")
        print("e. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            input_debt()
        elif choice == "2":
            input_sharehouse_needs()
        elif choice == "3":
            confirm_debt_payment()
        elif choice == "4":
            confirm_houseneed_payment()
        elif choice == "5":
            visualise_household_data()
        elif choice.lower() == "e":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")