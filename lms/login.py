import db_config

# ===== Login and role check function =====
def check_login(username, password):
    """
    Check login credentials and return user data.

    Returns:
        tuple: (user_id, name, role) if login successful
        None: if login fails
    """
    try:
        conn = db_config.connect_db()
        cur = conn.cursor()

        # Sirf necessary columns uthao: user_id, name, role
        cur.execute(
            "SELECT user_id, name, role FROM users WHERE user_id=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            # Return tuple (user_id, name, role)
            return user
        else:
            return None
    except Exception as e:
        print("Login Error:", e)  # Debugging ke liye
        return None 