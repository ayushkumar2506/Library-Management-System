import tkinter as tk
from tkinter import messagebox
import db_config
import start  # Ye import karna zaroori hai taaki signup ke baad login page khule

# ====== FUNCTION TO SIGNUP USER ======
def signup_user(root, entry_id, entry_name, entry_contact, entry_email, entry_pass):
    user_id = entry_id.get()
    name = entry_name.get()
    contact = entry_contact.get()
    email = entry_email.get()
    password = entry_pass.get()

    if not user_id or not name or not contact or not email or not password:
        messagebox.showwarning("Input Error", "Please fill all fields!")
        return

    try:
        conn = db_config.connect_db()
        cur = conn.cursor()
        # role ko default 'user' set kar diya
        cur.execute(
            "INSERT INTO users (user_id, name, contact, email, password, role) VALUES (%s,%s,%s,%s,%s,'user')",
            (user_id, name, contact, email, password)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account created successfully!")
        root.destroy()  # Signup window close
        start.open_login_page()  # Login page open

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ====== FUNCTION TO OPEN SIGNUP PAGE ======
def open_signup_page():
    root = tk.Tk()
    root.title("Signup - Library Management System")
    root.geometry("400x400")

    tk.Label(root, text="Signup Page", font=("Arial", 18, "bold")).pack(pady=20)

    # User ID
    tk.Label(root, text="User ID:", font=("Arial", 12)).pack(pady=5)
    entry_id = tk.Entry(root, font=("Arial", 12))
    entry_id.pack(pady=5)

    # Name
    tk.Label(root, text="Name:", font=("Arial", 12)).pack(pady=5)
    entry_name = tk.Entry(root, font=("Arial", 12))
    entry_name.pack(pady=5)

    # Contact
    tk.Label(root, text="Contact:", font=("Arial", 12)).pack(pady=5)
    entry_contact = tk.Entry(root, font=("Arial", 12))
    entry_contact.pack(pady=5)

    # Email
    tk.Label(root, text="Email:", font=("Arial", 12)).pack(pady=5)
    entry_email = tk.Entry(root, font=("Arial", 12))
    entry_email.pack(pady=5)

    # Password
    tk.Label(root, text="Password:", font=("Arial", 12)).pack(pady=5)
    entry_pass = tk.Entry(root, font=("Arial", 12), show="*")
    entry_pass.pack(pady=5)

    # Signup Button
    tk.Button(
        root, text="Signup", font=("Arial", 12), width=12,
        command=lambda: signup_user(root, entry_id, entry_name, entry_contact, entry_email, entry_pass)
    ).pack(pady=20)

    root.mainloop()

# Agar file directly run ho toh
if __name__ == "__main__":
    open_signup_page()
