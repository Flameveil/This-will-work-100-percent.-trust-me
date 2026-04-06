import tkinter as tk
from tkinter import messagebox

def calculate_tip():
    try:
        bill = float(entry_bill.get())
        people = int(entry_people.get())

        if bill < 0 or people <= 0:
            raise ValueError

        tip_percent = tip_var.get()

        tip_amount = bill * tip_percent
        total = bill + tip_amount
        per_person = total / people

        label_tip_result.config(text=f"Tip: ${tip_amount:.2f}")
        label_total_result.config(text=f"Total: ${total:.2f}")
        label_per_person_result.config(text=f"Per Person: ${per_person:.2f}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers!")

# Create main window
root = tk.Tk()
root.title("Tip Calculator")
root.geometry("350x300")

# Bill input
tk.Label(root, text="Bill Amount ($):").pack()
entry_bill = tk.Entry(root)
entry_bill.pack()

# Number of people
tk.Label(root, text="Number of People:").pack()
entry_people = tk.Entry(root)
entry_people.pack()

# Tip selection
tk.Label(root, text="Select Tip Percentage:").pack()

tip_var = tk.DoubleVar(value=0.15)

tk.Radiobutton(root, text="10%", variable=tip_var, value=0.10).pack()
tk.Radiobutton(root, text="15%", variable=tip_var, value=0.15).pack()
tk.Radiobutton(root, text="20%", variable=tip_var, value=0.20).pack()

# Calculate button
tk.Button(root, text="Calculate", command=calculate_tip).pack(pady=10)

# Results
label_tip_result = tk.Label(root, text="Tip: $0.00")
label_tip_result.pack()

label_total_result = tk.Label(root, text="Total: $0.00")
label_total_result.pack()

label_per_person_result = tk.Label(root, text="Per Person: $0.00")
label_per_person_result.pack()

# Run app
root.mainloop()