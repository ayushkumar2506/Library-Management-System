import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
import db_config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===== DATABASE CONNECT =====
def connect_db():
    return db_config.connect_db()

# ===== REPORT DASHBOARD =====
def open_reports_dashboard(parent):
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    win = ctk.CTkToplevel(parent)
    win.title("📊 Reports Dashboard")
    win.geometry("1150x680")
    win.grab_set()

    # ===== Layout =====
    sidebar = ctk.CTkFrame(win, width=220, corner_radius=15)
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    main_frame = ctk.CTkFrame(win, corner_radius=15)
    main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # ===== Sidebar with Logo =====
    try:
        logo = ctk.CTkImage(light_image=Image.open("assets/report.png"), size=(180, 120))
        logo_label = ctk.CTkLabel(sidebar, image=logo, text="")
        logo_label.pack(pady=15)
    except Exception:
        ctk.CTkLabel(sidebar, text="📊 Reports", font=("Segoe UI", 20, "bold")).pack(pady=20)

    ctk.CTkLabel(sidebar, text="MIS / Analytics", font=("Segoe UI", 16, "bold")).pack(pady=10)

    # Sidebar buttons
    ctk.CTkButton(sidebar, text="📘 All Books", width=180, command=lambda: show_books_report(main_frame)).pack(pady=5)
    ctk.CTkButton(sidebar, text="📖 Issued Books", width=180, command=lambda: show_issued_books_report(main_frame)).pack(pady=5)
    ctk.CTkButton(sidebar, text="👥 Users", width=180, command=lambda: show_users_report(main_frame)).pack(pady=5)
    ctk.CTkButton(sidebar, text="💰 Fines", width=180, command=lambda: show_fines_report(main_frame)).pack(pady=5)

    # 🆕 Acquisition buttons
    ctk.CTkLabel(sidebar, text="--- Acquisition ---", font=("Segoe UI", 14, "bold")).pack(pady=10)
    ctk.CTkButton(sidebar, text="🏢 Vendors", width=180, command=lambda: show_vendors_report(main_frame)).pack(pady=5)
    ctk.CTkButton(sidebar, text="🛒 Purchase Orders", width=180, command=lambda: show_purchase_orders_report(main_frame)).pack(pady=5)

    # Analytics
    ctk.CTkButton(sidebar, text="📊 Analytics (Charts)", width=180, command=lambda: show_analytics(main_frame)).pack(pady=10)

    ctk.CTkButton(sidebar, text="❌ Close", fg_color="red", width=180, command=win.destroy).pack(pady=30)

    # Default page
    ctk.CTkLabel(main_frame, text="📊 Reports Dashboard", font=("Segoe UI", 24, "bold")).pack(pady=20)
    ctk.CTkLabel(main_frame, text="Select a report from the sidebar", font=("Segoe UI", 16)).pack(pady=10)

    win.mainloop()

# ===== Helper to Clear Frame =====
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# ===== Books Report =====
def show_books_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="📘 Books Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Author", "Category", "Status"), show="headings", height=20)
    for col in ("ID", "Name", "Author", "Category", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT book_id, book_name, author, category, status FROM books")
        for book in cur.fetchall():
            tree.insert("", "end", values=book)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Issued Books Report =====
def show_issued_books_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="📖 Issued Books Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("User ID", "Book ID", "Issue Date", "Due Date"), show="headings", height=20)
    for col in ("User ID", "Book ID", "Issue Date", "Due Date"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, book_id, issue_date, due_date FROM issued_books")
        for record in cur.fetchall():
            tree.insert("", "end", values=record)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Users Report =====
def show_users_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="👥 Users Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("User ID", "Name", "Email", "Contact", "Role", "Wallet"), show="headings", height=20)
    for col in ("User ID", "Name", "Email", "Contact", "Role", "Wallet"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, name, email, contact, role, wallet_balance FROM users")
        for record in cur.fetchall():
            tree.insert("", "end", values=record)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Fines Report =====
def show_fines_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="💰 Fines Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("User ID", "Book ID", "Fine Amount"), show="headings", height=20)
    for col in ("User ID", "Book ID", "Fine Amount"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT user_id, book_id, fine_amount FROM fines")
        for record in cur.fetchall():
            tree.insert("", "end", values=record)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Vendors Report =====
def show_vendors_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="🏢 Vendors Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Contact", "Email", "Address"), show="headings", height=20)
    for col in ("ID", "Name", "Contact", "Email", "Address"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT vendor_id, name, contact, email, address FROM vendors")
        for record in cur.fetchall():
            tree.insert("", "end", values=record)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Purchase Orders Report =====
def show_purchase_orders_report(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="🛒 Purchase Orders Report", font=("Segoe UI", 20, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("Order ID", "Vendor", "Book Title", "Qty", "Price", "Status"), show="headings", height=20)
    for col in ("Order ID", "Vendor", "Book Title", "Qty", "Price", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, padx=15, pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT po.order_id, v.name, po.book_title, po.quantity, po.price, po.status
            FROM purchase_orders po
            JOIN vendors v ON po.vendor_id = v.vendor_id
        """)
        for record in cur.fetchall():
            tree.insert("", "end", values=record)
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ===== Analytics with Charts =====
def show_analytics(frame):
    clear_frame(frame)
    ctk.CTkLabel(frame, text="📊 Analytics Dashboard", font=("Segoe UI", 20, "bold")).pack(pady=10)

    try:
        conn = connect_db()
        cur = conn.cursor()

        # Total Books vs Issued Books
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM books WHERE status='Issued'")
        issued_books = cur.fetchone()[0]
        available_books = total_books - issued_books

        # Top 5 Users by Issued Books
        cur.execute("SELECT user_id, COUNT(*) FROM issued_books GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 5")
        top_users = cur.fetchall()

        conn.close()

        # Plot Charts
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        # Pie Chart
        axes[0].pie([issued_books, available_books], labels=["Issued", "Available"], autopct="%1.1f%%", colors=["#ff9999", "#66b3ff"])
        axes[0].set_title("Books Status")

        # Bar Chart
        if top_users:
            users = [u[0] for u in top_users]
            counts = [u[1] for u in top_users]
            axes[1].bar(users, counts, color="#4CAF50")
            axes[1].set_title("Top 5 Active Users")
            axes[1].set_ylabel("Books Issued")
        else:
            axes[1].text(0.5, 0.5, "No Data", ha="center", va="center")

        # Embed chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
