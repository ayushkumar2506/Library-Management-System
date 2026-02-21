import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import db_config
import admin_dashboard
import user_dashboard
import os

# Set a cohesive color theme and appearance mode for the entire application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """
    Main application class that manages the login and dashboard views.
    Uses a single-window, frame-swapping approach for a modern feel.
    """
    def __init__(self):
        super().__init__()
        self.title("📚 Library Management System")
        self.geometry("900x580")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Load a default banner image from the assets folder.
        self.logo_image = self.load_image("assets/login_banner.png", (350, 200))
        
        self.current_frame = None
        self.show_login_frame()

    def load_image(self, path, size):
        """Helper to load and resize images, handling potential errors."""
        try:
            image_path = os.path.join(os.path.dirname(__file__), path)
            img = Image.open(image_path)
            return ctk.CTkImage(light_image=img, size=size)
        except Exception as e:
            print(f"Image load error: {e}. Falling back to text.")
            return None

    def show_login_frame(self):
        """Displays the login frame and hides any existing frame."""
        self.clear_frame()
        self.current_frame = LoginFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    def on_login_success(self, user_data):
        """Called upon successful login to transition to the appropriate dashboard."""
        self.clear_frame()
        user_id, uname, role = user_data
        
        if role == "admin":
            # Pass the main App instance to the dashboard for logout functionality
            self.current_frame = admin_dashboard.AdminDashboardFrame(self, user_id, uname)
        elif role == "user":
            self.current_frame = user_dashboard.UserDashboardFrame(self, user_id, uname)
            
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        """Resets the application to the login screen."""
        self.show_login_frame()
        
    def clear_frame(self):
        """Destroys the current frame to prepare for a new one."""
        if self.current_frame:
            self.current_frame.destroy()

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=15)
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=0)

        # Use the image loaded by the parent App class
        if self.parent.logo_image:
            ctk.CTkLabel(self, text="", image=self.parent.logo_image).pack(pady=20)
        else:
            ctk.CTkLabel(self, text="📚 Library", font=("Segoe UI", 36, "bold")).pack(pady=20)

        ctk.CTkLabel(self, text="Library Management System", font=("Segoe UI", 24, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(self, text="Login to your account", font=("Segoe UI", 16)).pack(pady=5)

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username", width=300)
        self.entry_user.pack(pady=10)
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=300)
        self.entry_pass.pack(pady=10)
        
        self.login_button = ctk.CTkButton(self, text="Login", command=self.attempt_login, width=300, fg_color="blue", hover_color="#3498db")
        self.login_button.pack(pady=(15, 5))

        self.signup_button = ctk.CTkButton(self, text="Create an Account", command=self.open_signup_page, width=300, fg_color="gray", hover_color="#7f8c8d")
        self.signup_button.pack(pady=5)

    def attempt_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return

        try:
            conn = db_config.connect_db()
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, role FROM users WHERE user_id=%s AND password=%s", (username, password))
            user_data = cur.fetchone()
            conn.close()

            if user_data:
                self.parent.on_login_success(user_data)
            else:
                messagebox.showerror("Login Failed", "Invalid Username or Password!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def open_signup_page(self):
        signup_win = ctk.CTkToplevel(self.parent)
        signup_win.title("Create New Account")
        signup_win.geometry("400x450")
        signup_win.grab_set()  # This makes it a modal window

        signup_frame = ctk.CTkFrame(signup_win, corner_radius=15)
        signup_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(signup_frame, text="Create Account", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        entry_id = ctk.CTkEntry(signup_frame, placeholder_text="User ID", width=300); entry_id.pack(pady=5)
        entry_name = ctk.CTkEntry(signup_frame, placeholder_text="Full Name", width=300); entry_name.pack(pady=5)
        entry_contact = ctk.CTkEntry(signup_frame, placeholder_text="Contact Number", width=300); entry_contact.pack(pady=5)
        entry_email = ctk.CTkEntry(signup_frame, placeholder_text="Email", width=300); entry_email.pack(pady=5)
        entry_pass = ctk.CTkEntry(signup_frame, placeholder_text="Password", show="*", width=300); entry_pass.pack(pady=5)

        def signup_user():
            user_id, name, contact, email, password = entry_id.get(), entry_name.get(), entry_contact.get(), entry_email.get(), entry_pass.get()
            if not all([user_id, name, contact, email, password]):
                messagebox.showwarning("Input Error", "Please fill all fields!")
                return
            try:
                conn = db_config.connect_db()
                cur = conn.cursor()
                cur.execute("INSERT INTO users (user_id, name, contact, email, password, role) VALUES (%s,%s,%s,%s,%s,'user')", (user_id, name, contact, email, password))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Account created successfully!")
                signup_win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
        
        ctk.CTkButton(signup_frame, text="Signup", command=signup_user, fg_color="green", hover_color="#2ecc71").pack(pady=15)

if __name__ == "__main__":
    app = App()
    app.mainloop()