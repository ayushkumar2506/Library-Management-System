import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta, date
import db_config
import reports

# ===== DATABASE FUNCTIONS =====
def connect_db():
    return db_config.connect_db()

# ===== ADMIN DASHBOARD CLASS =====
class AdminDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id, admin_name):
        super().__init__(parent, corner_radius=15)
        self.parent = parent
        self.user_id = user_id
        self.admin_name = admin_name
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)

        # ===== Header Frame =====
        header_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        ctk.CTkLabel(header_frame, text="  Library Management System", font=("Arial", 24, "bold"), compound="left").pack(side="left", padx=20, pady=10)

        # Main content area
        main_content_frame = ctk.CTkFrame(self, corner_radius=15)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content_frame.grid_columnconfigure((0, 1), weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(main_content_frame, text=f"Welcome Admin {self.admin_name}", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # ===== Left Panel: Library Management =====
        library_frame = ctk.CTkFrame(main_content_frame, corner_radius=15)
        library_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(library_frame, text="--- Library Management ---", font=("Arial", 12, "bold")).pack(pady=10)
        
        ctk.CTkButton(library_frame, text="Add Book", width=30, command=self.add_book).pack(pady=5)
        ctk.CTkButton(library_frame, text="View All Books", width=30, command=self.view_books).pack(pady=5)
        ctk.CTkButton(library_frame, text="Update Book", width=30, command=self.update_book).pack(pady=5)
        ctk.CTkButton(library_frame, text="Delete Book", width=30, command=self.delete_book).pack(pady=5)
        ctk.CTkButton(library_frame, text="Issue Book", width=30, command=self.issue_book).pack(pady=5)
        ctk.CTkButton(library_frame, text="Return Book", width=30, command=self.return_book).pack(pady=5)
        ctk.CTkButton(library_frame, text="View Issued Books", width=30, command=self.view_issued_books).pack(pady=5)

        # ===== Right Panel: Acquisition & Reports =====
        acquisition_frame = ctk.CTkFrame(main_content_frame, corner_radius=15)
        acquisition_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(acquisition_frame, text="--- Acquisition & Reports ---", font=("Arial", 12, "bold")).pack(pady=10)
        
        ctk.CTkButton(acquisition_frame, text="Add Vendor", width=30, command=self.add_vendor).pack(pady=5)
        ctk.CTkButton(acquisition_frame, text="View Vendors", width=30, command=self.view_vendors).pack(pady=5)
        ctk.CTkButton(acquisition_frame, text="Create Purchase Order", width=30, command=self.create_purchase_order).pack(pady=5)
        ctk.CTkButton(acquisition_frame, text="View Purchase Orders", width=30, command=self.view_purchase_orders).pack(pady=5)
        ctk.CTkButton(acquisition_frame, text="Open Reports Dashboard", width=30, command=lambda: reports.open_reports_dashboard(self.parent)).pack(pady=5)

        # Logout button
        ctk.CTkButton(self, text="Logout", width=30, command=self.parent.logout, fg_color="red", hover_color="#c0392b").grid(row=2, column=0, pady=20)

    # ===== Methods for the dashboard, updated to work within the class =====
    def connect_db(self):
        return db_config.connect_db()

    def add_book(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Add New Book")
        win.geometry("400x300")
        win.grab_set()

        ctk.CTkLabel(win, text="Add Book", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(win, text="Book ID:").pack()
        entry_id = ctk.CTkEntry(win); entry_id.pack(pady=5)
        ctk.CTkLabel(win, text="Book Name:").pack()
        entry_name = ctk.CTkEntry(win); entry_name.pack(pady=5)
        ctk.CTkLabel(win, text="Author:").pack()
        entry_author = ctk.CTkEntry(win); entry_author.pack(pady=5)
        ctk.CTkLabel(win, text="Category:").pack()
        entry_cat = ctk.CTkEntry(win); entry_cat.pack(pady=5)

        def save_book():
            book_id = entry_id.get()
            name = entry_name.get()
            author = entry_author.get()
            category = entry_cat.get()
            if not book_id or not name or not author or not category:
                messagebox.showwarning("Input Error", "Fill all fields!")
                return
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
                if cur.fetchone():
                    messagebox.showwarning("Duplicate ID", "A book with this ID already exists.")
                    conn.close()
                    return
                cur.execute(
                    "INSERT INTO books (book_id, book_name, author, category, status) VALUES (%s, %s, %s, %s, 'Available')",
                    (book_id, name, author, category)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Book added successfully!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        ctk.CTkButton(win, text="Save Book", command=save_book).pack(pady=15)

    def view_books(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("All Books")
        win.geometry("600x400")
        win.grab_set()

        ctk.CTkLabel(win, text="Books List", font=("Arial", 14, "bold")).pack(pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="#DCE4EE", font=("Arial", 12), rowheight=25)
        style.map("Treeview", background=[('selected', '#5A5A5A')])
        style.configure("Treeview.Heading", background="#3A3A3A", foreground="#DCE4EE", font=("Arial", 12, "bold"))

        tree = ttk.Treeview(win, columns=("ID", "Name", "Author", "Category", "Status"), show="headings", style="Treeview")
        for col in ("ID", "Name", "Author", "Category", "Status"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        try:
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT book_id, book_name, author, category, status FROM books")
            for book in cur.fetchall():
                tree.insert("", "end", values=book)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def update_book(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Update Book")
        win.geometry("400x300")
        win.grab_set()
        
        ctk.CTkLabel(win, text="Enter Book ID to Update:").pack()
        entry_id = ctk.CTkEntry(win); entry_id.pack(pady=5)
        ctk.CTkLabel(win, text="New Book Name:").pack()
        entry_name = ctk.CTkEntry(win); entry_name.pack(pady=5)
        ctk.CTkLabel(win, text="New Author:").pack()
        entry_author = ctk.CTkEntry(win); entry_author.pack(pady=5)
        ctk.CTkLabel(win, text="New Category:").pack()
        entry_cat = ctk.CTkEntry(win); entry_cat.pack(pady=5)
        
        def save_update():
            book_id = entry_id.get()
            new_name = entry_name.get()
            new_author = entry_author.get()
            new_cat = entry_cat.get()
            if not book_id or not new_name or not new_author or not new_cat:
                messagebox.showwarning("Input Error", "Fill all fields!")
                return
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE books SET book_name=%s, author=%s, category=%s WHERE book_id=%s",
                    (new_name, new_author, new_cat, book_id)
                )
                if cur.rowcount == 0:
                    messagebox.showwarning("Not Found", "Book ID not found!")
                else:
                    conn.commit()
                    messagebox.showinfo("Success", "Book updated successfully!")
                conn.close()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        ctk.CTkButton(win, text="Update Book", command=save_update).pack(pady=15)
        
    def delete_book(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Delete Book")
        win.geometry("400x200")
        win.grab_set()

        ctk.CTkLabel(win, text="Enter Book ID to Delete:").pack()
        entry_id = ctk.CTkEntry(win); entry_id.pack(pady=5)

        def remove_book():
            book_id = entry_id.get()
            if not book_id:
                messagebox.showwarning("Input Error", "Enter Book ID!")
                return
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
                if cur.rowcount == 0:
                    messagebox.showwarning("Not Found", "Book ID not found!")
                else:
                    conn.commit()
                    messagebox.showinfo("Success", "Book deleted successfully!")
                conn.close()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        ctk.CTkButton(win, text="Delete Book", command=remove_book).pack(pady=15)

    def issue_book(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Issue Book")
        win.geometry("400x300")
        win.grab_set()

        ctk.CTkLabel(win, text="User ID:").pack()
        entry_user = ctk.CTkEntry(win); entry_user.pack(pady=5)
        ctk.CTkLabel(win, text="Book ID:").pack()
        entry_book = ctk.CTkEntry(win); entry_book.pack(pady=5)

        issue_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        ctk.CTkLabel(win, text=f"Issue Date: {issue_date}").pack()
        ctk.CTkLabel(win, text=f"Due Date: {due_date}").pack()
        
        def save_issue():
            user_id = entry_user.get()
            book_id = entry_book.get()
            if not user_id or not book_id:
                messagebox.showwarning("Input Error", "Fill all fields!")
                return
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
                user_exists = cur.fetchone()
                if not user_exists:
                    messagebox.showwarning("User Not Found", "User ID does not exist.")
                    conn.close()
                    return
                cur.execute("SELECT status FROM books WHERE book_id=%s", (book_id,))
                book_status = cur.fetchone()
                if not book_status:
                    messagebox.showwarning("Not Found", "Book ID not found!")
                    conn.close()
                    return
                if book_status[0] != 'Available':
                    messagebox.showwarning("Not Available", "This book is currently not available.")
                    conn.close()
                    return
                cur.execute("SELECT COUNT(*) FROM issued_books WHERE user_id = %s AND book_id = %s", (user_id, book_id))
                is_issued = cur.fetchone()[0]
                if is_issued > 0:
                    messagebox.showwarning("Already Issued", "This book is already issued to this user.")
                    conn.close()
                    return
                max_books = 3
                cur.execute("SELECT COUNT(*) FROM issued_books WHERE user_id = %s", (user_id,))
                issued_count = cur.fetchone()[0]
                if issued_count >= max_books:
                    messagebox.showwarning("Limit Reached", f"User {user_id} has already issued the maximum limit of {max_books} books.")
                    conn.close()
                    return
                cur.execute(
                    "INSERT INTO issued_books (user_id, book_id, issue_date, due_date) VALUES (%s,%s,%s,%s)",
                    (user_id, book_id, issue_date, due_date)
                )
                cur.execute("UPDATE books SET status='Issued' WHERE book_id=%s", (book_id,))
                conn.commit()
                messagebox.showinfo("Success", "Book issued successfully!")
                win.destroy()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        ctk.CTkButton(win, text="Issue Book", command=save_issue).pack(pady=15)

    def return_book(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Return Book")
        win.geometry("400x250")
        win.grab_set()

        ctk.CTkLabel(win, text="User ID:").pack()
        entry_user = ctk.CTkEntry(win); entry_user.pack(pady=5)
        ctk.CTkLabel(win, text="Book ID:").pack()
        entry_book = ctk.CTkEntry(win); entry_book.pack(pady=5)

        def process_return():
            user_id = entry_user.get()
            book_id = entry_book.get()
            if not user_id or not book_id:
                messagebox.showwarning("Input Error", "Fill all fields!")
                return
            try:
                conn = self.connect_db()
                cur = conn.cursor()
                cur.execute("DELETE FROM issued_books WHERE user_id=%s AND book_id=%s", (user_id, book_id))
                if cur.rowcount == 0:
                    messagebox.showwarning("Not Found", "No such issued book found!")
                else:
                    cur.execute("UPDATE books SET status='Available' WHERE book_id=%s", (book_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Book returned successfully!")
                conn.close()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        ctk.CTkButton(win, text="Return Book", command=process_return).pack(pady=15)

    def view_issued_books(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Issued Books")
        win.geometry("600x400")
        win.grab_set()

        ctk.CTkLabel(win, text="Issued Books List", font=("Arial", 14, "bold")).pack(pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="#DCE4EE", font=("Arial", 12), rowheight=25)
        style.map("Treeview", background=[('selected', '#5A5A5A')])
        style.configure("Treeview.Heading", background="#3A3A3A", foreground="#DCE4EE", font=("Arial", 12, "bold"))
        
        tree = ttk.Treeview(win, columns=("User ID", "Book ID", "Issue Date", "Due Date"), show="headings", style="Treeview")
        for col in ("User ID", "Book ID", "Issue Date", "Due Date"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM issued_books")
            for record in cur.fetchall():
                tree.insert("", "end", values=record)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_vendor(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Add Vendor")
        win.geometry("400x300")
        win.grab_set()
        
        ctk.CTkLabel(win, text="Vendor Name:").pack()
        entry_name = ctk.CTkEntry(win); entry_name.pack(pady=5)
        ctk.CTkLabel(win, text="Contact:").pack()
        entry_contact = ctk.CTkEntry(win); entry_contact.pack(pady=5)
        ctk.CTkLabel(win, text="Email:").pack()
        entry_email = ctk.CTkEntry(win); entry_email.pack(pady=5)
        ctk.CTkLabel(win, text="Address:").pack()
        entry_address = ctk.CTkEntry(win); entry_address.pack(pady=5)
        
        def save_vendor():
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO vendors (name, contact, email, address) VALUES (%s,%s,%s,%s)",
                (entry_name.get(), entry_contact.get(), entry_email.get(), entry_address.get())
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Vendor added successfully!")
            win.destroy()
        ctk.CTkButton(win, text="Save Vendor", command=save_vendor).pack(pady=10)

    def view_vendors(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Vendors")
        win.geometry("600x400")
        win.grab_set()

        ctk.CTkLabel(win, text="Vendors List", font=("Arial", 14, "bold")).pack(pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="#DCE4EE", font=("Arial", 12), rowheight=25)
        style.map("Treeview", background=[('selected', '#5A5A5A')])
        style.configure("Treeview.Heading", background="#3A3A3A", foreground="#DCE4EE", font=("Arial", 12, "bold"))

        tree = ttk.Treeview(win, columns=("ID", "Name", "Contact", "Email", "Address"), show="headings", style="Treeview")
        for col in ("ID", "Name", "Contact", "Email", "Address"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM vendors")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def create_purchase_order(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Create Purchase Order")
        win.geometry("500x500")
        win.grab_set()

        ctk.CTkLabel(win, text="Book Title:").pack()
        entry_title = ctk.CTkEntry(win); entry_title.pack(pady=5)
        ctk.CTkLabel(win, text="Author:").pack()
        entry_author = ctk.CTkEntry(win); entry_author.pack(pady=5)
        ctk.CTkLabel(win, text="ISBN:").pack()
        entry_isbn = ctk.CTkEntry(win); entry_isbn.pack(pady=5)
        ctk.CTkLabel(win, text="Category:").pack()
        entry_cat = ctk.CTkEntry(win); entry_cat.pack(pady=5)
        ctk.CTkLabel(win, text="Quantity:").pack()
        entry_qty = ctk.CTkEntry(win); entry_qty.pack(pady=5)
        ctk.CTkLabel(win, text="Price per unit:").pack()
        entry_price = ctk.CTkEntry(win); entry_price.pack(pady=5)
        ctk.CTkLabel(win, text="Vendor:").pack()
        vendor_box = ttk.Combobox(win); vendor_box.pack(pady=5)

        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT vendor_id, name FROM vendors")
        vendors = cur.fetchall()
        conn.close()
        vendor_box["values"] = [f"{v[0]} - {v[1]}" for v in vendors]
        
        def save_order():
            if not vendor_box.get():
                messagebox.showwarning("Error", "Select a vendor!")
                return
            vendor_id = vendor_box.get().split(" - ")[0]
            conn = self.connect_db()
            cur = conn.cursor()
            cur.execute("""INSERT INTO purchase_orders (vendor_id, book_title, author, isbn, category, quantity, price, order_date, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'Pending')""", (vendor_id, entry_title.get(), entry_author.get(), entry_isbn.get(), entry_cat.get(), entry_qty.get(), entry_price.get(), date.today()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Purchase Order created!")
            win.destroy()
        ctk.CTkButton(win, text="Save Order", command=save_order).pack(pady=10)

    def view_purchase_orders(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("Purchase Orders")
        win.geometry("700x400")
        win.grab_set()

        ctk.CTkLabel(win, text="Purchase Orders List", font=("Arial", 14, "bold")).pack(pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="#DCE4EE", font=("Arial", 12), rowheight=25)
        style.map("Treeview", background=[('selected', '#5A5A5A')])
        style.configure("Treeview.Heading", background="#3A3A3A", foreground="#DCE4EE", font=("Arial", 12, "bold"))

        tree = ttk.Treeview(win, columns=("Order ID", "Vendor", "Book", "Qty", "Price", "Status"), show="headings", style="Treeview")
        for col in ("Order ID", "Vendor", "Book", "Qty", "Price", "Status"):
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT po.order_id, v.name, po.book_title, po.quantity, po.price, po.status
            FROM purchase_orders po
            JOIN vendors v ON po.vendor_id = v.vendor_id
        """)
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()