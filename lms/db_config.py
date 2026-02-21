import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",      # apna MySQL password
        database="library_db"
    )
