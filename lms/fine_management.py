import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from db_config import connect_db

# ===== CALCULATE OVERDUE FINES =====
def calculate_overdue_fines(user_id):
    conn = connect_db()
    cur = conn.cursor()
    fine_per_day = 10  # fine per overdue day

    cur.execute("SELECT issue_id, book_id, due_date FROM issued_books WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()

    for issue_id, book_id, due_date in rows:
        due_date_obj = datetime.strptime(str(due_date), "%Y-%m-%d").date()
        today = datetime.today().date()
        if today > due_date_obj:
            overdue_days = (today - due_date_obj).days
            fine_amount = overdue_days * fine_per_day
            
            # Check if a fine already exists for this book and user
            cur.execute("""
                SELECT fine_id, amount FROM fines 
                WHERE user_id=%s AND book_id=%s AND fine_type='overdue' AND status='unpaid'
            """, (user_id, book_id))
            existing_fine = cur.fetchone()

            if existing_fine:
                # Update the existing fine amount
                fine_id, current_amount = existing_fine
                if fine_amount > current_amount:
                    cur.execute("UPDATE fines SET amount=%s, issued_date=%s WHERE fine_id=%s",
                                 (fine_amount, today, fine_id))
            else:
                # Insert a new fine record
                cur.execute("""
                    INSERT INTO fines (user_id, book_id, fine_type, amount, issued_date) 
                    VALUES (%s,%s,'overdue',%s,%s)
                """, (user_id, book_id, fine_amount, today))
    
    conn.commit()
    conn.close()

# ===== VIEW & PAY FINES =====
def view_fines(parent, user_id):
    win = ctk.CTkToplevel(parent)
    win.title("My Fines & Payments")
    win.geometry("700x400")
    win.grab_set()

    ctk.CTkLabel(win, text="My Fines", font=("Arial", 18, "bold")).pack(pady=15)

    # Style the Treeview to match the CustomTkinter dark theme
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#2b2b2b",
                    fieldbackground="#2b2b2b",
                    foreground="#DCE4EE",
                    font=("Arial", 12),
                    rowheight=25)
    style.map("Treeview", background=[('selected', '#5A5A5A')])
    style.configure("Treeview.Heading",
                    background="#3A3A3A",
                    foreground="#DCE4EE",
                    font=("Arial", 12, "bold"))
    
    tree = ttk.Treeview(win, columns=("ID", "Book", "Type", "Amount", "Status"), show="headings", style="Treeview")
    for col in ("ID", "Book", "Type", "Amount", "Status"):
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.fine_id, f.book_id, f.fine_type, f.amount, f.status 
        FROM fines f WHERE f.user_id=%s
    """, (user_id,))
    for row in cur.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

    # ===== PAY FINE FUNCTION =====
    def pay_fine():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Select a fine to pay!")
            return
        fine_id = tree.item(selected[0])['values'][0]

        conn = connect_db()
        cur = conn.cursor()

        # Get fine amount
        cur.execute("SELECT amount FROM fines WHERE fine_id=%s", (fine_id,))
        fine_amt = cur.fetchone()[0]

        # Get wallet balance
        cur.execute("SELECT wallet_balance FROM users WHERE user_id=%s", (user_id,))
        wallet = cur.fetchone()[0]

        if wallet < fine_amt:
            messagebox.showerror("Insufficient Balance", "Recharge your wallet first!")
        else:
            cur.execute("UPDATE users SET wallet_balance=wallet_balance-%s WHERE user_id=%s", (fine_amt, user_id))
            cur.execute("UPDATE fines SET status='paid' WHERE fine_id=%s", (fine_id,))
            conn.commit()
            messagebox.showinfo("Success", f"Fine ₹{fine_amt} paid successfully!")
            win.destroy()
            view_fines(parent, user_id)  # Refresh table
        conn.close()

    ctk.CTkButton(win, text="Pay Selected Fine", command=pay_fine, fg_color="green", hover_color="#2ecc71").pack(pady=10)

# ===== WALLET RECHARGE =====
def recharge_wallet(parent, user_id):
    win = ctk.CTkToplevel(parent)
    win.title("Recharge Wallet")
    win.geometry("400x200")
    win.grab_set()

    ctk.CTkLabel(win, text="Enter Recharge Amount:", font=("Arial", 14)).pack(pady=10)
    entry_amt = ctk.CTkEntry(win, font=("Arial", 12))
    entry_amt.pack(pady=5)

    def add_money():
        try:
            amt = float(entry_amt.get())
            if amt <= 0:
                messagebox.showwarning("Invalid", "Enter positive amount!")
                return
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("UPDATE users SET wallet_balance=wallet_balance+%s WHERE user_id=%s", (amt, user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Wallet recharged with ₹{amt}!")
            win.destroy()
        except:
            messagebox.showerror("Error", "Invalid input!")

    ctk.CTkButton(win, text="Recharge", command=add_money, fg_color="blue", hover_color="#3498db").pack(pady=10)