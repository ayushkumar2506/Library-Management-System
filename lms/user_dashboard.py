import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import db_config
from fine_management import calculate_overdue_fines, view_fines, recharge_wallet
from PIL import Image
import os

# ===== DATABASE FUNCTIONS =====
def connect_db():
    return db_config.connect_db()

# ===== USER DASHBOARD CLASS =====
class UserDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id, username):
        super().__init__(parent, corner_radius=15)
        self.parent = parent
        self.user_id = user_id
        self.username = username
        self.pack(fill="both", expand=True)

        # Configure grid for main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(1, weight=1)

        # Load Icons
        self.icon_profile = self.load_icon("profile_icon.png")
        self.icon_books = self.load_icon("books_icon.png")
        self.icon_fines = self.load_icon("fines_icon.png")
        self.icon_wallet = self.load_icon("wallet_icon.png")
        self.icon_logout = self.load_icon("logout_icon.png")
        self.icon_logo = self.load_icon("library_logo.png", size=(40, 40))

        # ===== Header Frame =====
        header_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=15)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        # Header with Logo
        logo_label = ctk.CTkLabel(header_frame, text="  Library Management System", font=("Arial", 24, "bold"), image=self.icon_logo, compound="left")
        logo_label.pack(side="left", padx=20, pady=10)

        # ===== Sidebar for Actions =====
        sidebar = ctk.CTkFrame(self, corner_radius=15, fg_color="#2c3e50")
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        sidebar.grid_columnconfigure(0, weight=1)

        # Sidebar Title
        ctk.CTkLabel(sidebar, text=f"Welcome {self.username.capitalize()}", font=("Arial", 16, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(sidebar, text=f"User ID: {self.user_id}", font=("Arial", 12)).pack(pady=(0, 20))

        # Sidebar Buttons with Icons
        ctk.CTkButton(sidebar, text="  Show Profile", image=self.icon_profile, compound="left", command=self.show_profile).pack(pady=10, fill="x", padx=15)
        ctk.CTkButton(sidebar, text="  My Issued Books", image=self.icon_books, compound="left", command=self.view_my_books).pack(pady=10, fill="x", padx=15)
        ctk.CTkButton(sidebar, text="  My Fines & Payments", image=self.icon_fines, compound="left", command=self.view_fines).pack(pady=10, fill="x", padx=15)
        ctk.CTkButton(sidebar, text="  Recharge Wallet", image=self.icon_wallet, compound="left", command=self.recharge_wallet).pack(pady=10, fill="x", padx=15)

        # Logout button
        ctk.CTkButton(sidebar, text="  Logout", image=self.icon_logout, compound="left", command=self.parent.logout, fg_color="red", hover_color="#c0392b").pack(pady=(50, 20), fill="x", padx=15)

        # ===== Main Content Area =====
        main_content = ctk.CTkFrame(self, corner_radius=15)
        main_content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(1, weight=1)

        # Search Section
        search_frame = ctk.CTkFrame(main_content, corner_radius=15)
        search_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(search_frame, text="🔎 Search Books:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Enter Book Name, Author, or ID...", width=400)
        self.entry_search.grid(row=1, column=0, padx=(15, 5), pady=(0, 15), sticky="ew")
        ctk.CTkButton(search_frame, text="Search", command=self.search_books_bar).grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        # Call the styling function before creating the treeview
        self.style_treeview()

        # Treeview for results
        self.tree = ttk.Treeview(main_content, columns=("ID", "Name", "Author", "Category"), show="headings", style="Custom.Treeview")
        self.tree.heading("ID", text="Book ID")
        self.tree.heading("Name", text="Book Name")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Category", text="Category")
        self.tree.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # Initial data load
        self.search_books_bar()

    def style_treeview(self):
        style = ttk.Style()
        # Set the theme for the treeview to match the CustomTkinter dark theme
        style.theme_use("clam")  
        style.configure("Treeview",
                        background="#2b2b2b",
                        fieldbackground="#2b2b2b",
                        foreground="#DCE4EE",
                        font=("Arial", 12),
                        rowheight=25)
        style.map("Treeview", background=[('selected', '#5A5A5A')])

        # Style the Treeview heading
        style.configure("Treeview.Heading",
                        background="#3A3A3A",
                        foreground="#DCE4EE",
                        font=("Arial", 12, "bold"))

    def load_icon(self, filename, size=(20, 20)):
        """Helper function to load and resize images, gracefully handling errors."""
        try:
            image_path = os.path.join(os.path.dirname(__file__), "assets", filename)
            img = Image.open(image_path)
            return ctk.CTkImage(light_image=img, size=size)
        except Exception as e:
            print(f"Error loading icon: {filename}, {e}")
            return None

    # ===== Search Books Method (same as before) =====
    def search_books_bar(self):
        keyword = "%" + self.entry_search.get() + "%"
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "SELECT book_id, book_name, author, category FROM books WHERE book_id LIKE %s OR book_name LIKE %s OR author LIKE %s OR category LIKE %s",
                (keyword, keyword, keyword, keyword),
            )
            rows = cur.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ===== VIEW ISSUED BOOKS (same as before) =====
    def view_my_books(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("My Issued Books")
        win.geometry("750x400")
        win.grab_set()  # This makes the window modal and keeps it in front

        ctk.CTkLabel(win, text=f"My Issued Books (User ID: {self.user_id})", font=("Arial", 14, "bold")).pack(pady=10)
        tree = ttk.Treeview(win, columns=("Book ID", "Issue Date", "Due Date"), show="headings")
        tree.heading("Book ID", text="Book ID")
        tree.heading("Issue Date", text="Issue Date")
        tree.heading("Due Date", text="Due Date")
        tree.pack(fill="both", expand=True, padx=15, pady=10)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT book_id, issue_date, due_date FROM issued_books WHERE user_id=%s", (self.user_id,))
            for record in cur.fetchall():
                tree.insert("", "end", values=record)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ===== Show Profile (same as before) =====
    def show_profile(self):
        win = ctk.CTkToplevel(self.parent)
        win.title("My Profile")
        win.geometry("400x600")
        win.grab_set() 
        
        tk_profile = self.create_profile_widgets(win)
        tk_profile.pack(fill="both", expand=True, padx=15, pady=15)
    
    def create_profile_widgets(self, parent_window):
        frame = ctk.CTkFrame(parent_window, corner_radius=15)
        ctk.CTkLabel(frame, text="👤 My Profile", font=("Arial", 16, "bold")).pack(pady=15)
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, email, contact, wallet_balance, password FROM users WHERE user_id=%s", (self.user_id,))
            user = cur.fetchone()
            conn.close()
            if user:
                ctk.CTkLabel(frame, text=f"User ID: {user[0]}", font=("Arial", 12)).pack(pady=5)
                ctk.CTkLabel(frame, text=f"Wallet Balance: ₹{user[4]}", font=("Arial", 12, "bold")).pack(pady=5)
                ctk.CTkLabel(frame, text="Name:", font=("Arial", 12)).pack(pady=2)
                name_entry = ctk.CTkEntry(frame, font=("Arial", 12))
                name_entry.insert(0, user[1])
                name_entry.pack(pady=2, fill="x")
                ctk.CTkLabel(frame, text="Email:", font=("Arial", 12)).pack(pady=2)
                email_entry = ctk.CTkEntry(frame, font=("Arial", 12))
                email_entry.insert(0, user[2])
                email_entry.pack(pady=2, fill="x")
                ctk.CTkLabel(frame, text="Contact:", font=("Arial", 12)).pack(pady=2)
                contact_entry = ctk.CTkEntry(frame, font=("Arial", 12))
                contact_entry.insert(0, user[3])
                contact_entry.pack(pady=2, fill="x")
                def update_profile():
                    new_name = name_entry.get()
                    new_email = email_entry.get()
                    new_contact = contact_entry.get()
                    try:
                        conn = connect_db()
                        cur = conn.cursor()
                        cur.execute("""UPDATE users SET name=%s, email=%s, contact=%s WHERE user_id=%s""", (new_name, new_email, new_contact, self.user_id))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Success", "Profile updated successfully!")
                        parent_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
                ctk.CTkButton(frame, text="💾 Save Changes", command=update_profile, fg_color="green", hover_color="#2ecc71").pack(pady=15)
            else:
                ctk.CTkLabel(frame, text="User not found!", fg="red", font=("Arial", 12)).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        return frame

    # ===== View Fines (same as before) =====
    def view_fines(self):
        # The view_fines function in fine_management.py needs to be updated.
        view_fines(self.parent, self.user_id)
        

    # ===== Recharge Wallet (same as before) =====
    def recharge_wallet(self):
        # The recharge_wallet function in fine_management.py needs to be updated.
        recharge_wallet(self.parent, self.user_id)