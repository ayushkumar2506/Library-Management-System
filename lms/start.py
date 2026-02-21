import main

if __name__ == "__main__":
    app = main.App()
    app.mainloop()

# ===== LOGIN ATTEMPT =====
def attempt_login(entry_user, entry_pass, root):
    username = entry_user.get().strip()
    password = entry_pass.get().strip()

    