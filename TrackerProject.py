import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Configuration
FILE_NAME = "expenses.csv"

def initialize_df():
    """Ensures a CSV exists with the correct columns."""
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        columns = ["Date", "Category", "Description", "Amount"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(FILE_NAME, index=False)
        return df

def add_expense(category, description, amount):
    """Appends a new expense to the CSV."""
    df = pd.read_csv(FILE_NAME)

    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Description": description,
        "Amount": float(amount)
    }

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    print("\n✅ Expense added successfully!")

def view_summary():
    """Displays data and basic stats using Pandas."""
    df = pd.read_csv(FILE_NAME)

    if df.empty:
        print("\n📭 No expenses recorded yet.")
        return

    print("\n--- Current Expenses ---")
    print(df)

    total = df["Amount"].sum()
    average = df["Amount"].mean()

    print(f"\n💰 Total Spent: ${total:.2f}")
    print(f"📊 Average Expense: ${average:.2f}")

    print("\n--- Spending by Category ---")
    print(df.groupby("Category")["Amount"].sum())

def delete_expense():
    df = pd.read_csv(FILE_NAME)

    if df.empty:
        print("\n📭 No expenses to delete.")
        return

    print("\n--- Current Expenses ---")
    print(df)

    try:
        loc = int(input("Enter index to delete: "))
        if loc not in df.index:
            print("❌ Invalid index.")
            return

        df = df.drop(index=loc)

        # Reset index so it stays clean
        df = df.reset_index(drop=True)

        df.to_csv(FILE_NAME, index=False)
        print("\n🗑️ Expense deleted successfully!")

        view_summary()

    except ValueError:
        print("❌ Invalid input.")

def edit_expense():
    df = pd.read_csv(FILE_NAME)

    if df.empty:
        print("\n📭 No expenses to edit.")
        return

    print("\n--- Current Expenses ---")
    print(df)

    try:
        loc = int(input("Enter index to edit: "))
        if loc not in df.index:
            print("❌ Invalid index.")
            return

        print("\nLeave blank to keep current value.")

        new_cat = input(f"New Category ({df.at[loc, 'Category']}): ")
        new_desc = input(f"New Description ({df.at[loc, 'Description']}): ")
        new_amt = input(f"New Amount ({df.at[loc, 'Amount']}): ")

        if new_cat:
            df.at[loc, 'Category'] = new_cat
        if new_desc:
            df.at[loc, 'Description'] = new_desc
        if new_amt:
            df.at[loc, 'Amount'] = float(new_amt)

        df.to_csv(FILE_NAME, index=False)
        print("\n✅ Expense updated successfully!")

    except ValueError:
        print("❌ Invalid input.")

def plot_expense():
    df = pd.read_csv(FILE_NAME)

    if df.empty:
        print("\n📭 No data to plot.")
        return

    category_totals = df.groupby('Category')['Amount'].sum()

    plt.figure(figsize=(8, 8))
    plt.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%')
    plt.title('Total Expense by Category')
    plt.axis('equal')
    plt.show()

def main():
    initialize_df()

    while True:
        print("\n--- 📈 Expense Tracker CLI ---")
        print("1. Add Expense")
        print("2. View Summary")
        print("3. Delete Expense")
        print("4. Edit Expense")
        print("5. Plot")
        print("6. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            cat = input("Enter Category (e.g., Food, Rent, Fun): ")
            desc = input("Short Description: ")
            amt = input("Amount: ")
            add_expense(cat, desc, amt)

        elif choice == "2":
            view_summary()

        elif choice == "3":
            delete_expense()

        elif choice == "4":
            edit_expense()

        elif choice == "5":
            plot_expense()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()