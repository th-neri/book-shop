import sqlite3
import bcrypt

def connect():
    return sqlite3.connect("shop_book.db")

def create_tables(connection):
    with connection:
        connection.execute("""
                           CREATE TABLE IF NOT EXISTS books (
                           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                           name TEXT NOT NULL,
                           author TEXT NOT NULL,
                           price REAL NOT NULL,
                           quantity INTEGER NOT NULL
                           )
                           """)
              
        connection.execute("""
                           CREATE TABLE IF NOT EXISTS users (
                           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                           name TEXT NOT NULL,
                           email TEXT UNIQUE NOT NULL,
                           password TEXT NOT NULL
                           )
                           """)
        
        connection.execute("""
                           CREATE TABLE IF NOT EXISTS cart (
                           user_id INTEGER,
                           book_id INTEGER,
                           quantity INTEGER,
                           PRIMARY KEY(user_id, book_id),
                           FOREIGN KEY(user_id) REFERENCES users(id),
                           FOREIGN KEY(book_id) REFERENCES books(id)
                           )
                           """)
        
        connection.execute("""
                           CREATE TABLE IF NOT EXISTS orders (
                           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                           user_id INTEGER,
                           total REAL,
                           FOREIGN KEY(user_id) REFERENCES users(id)
                           )
                           """)

def add_book(connection, name, author, price, quantity):
    with connection:
        connection.execute("""
                          INSERT INTO books (name, author, price, quantity) VALUES (?, ?, ?, ?);
                           """, (name, author, price, quantity))

def get_books(connection):
    with connection:
        return connection.execute("SELECT * FROM books").fetchall()
    
def delete_book(connection, book_id):
    with connection:
        return connection.execute("DELETE FROM books WHERE id=?", (book_id,))

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def add_user(connection, name, email, password):
    hashed = hash_password(password)
    try:
        with connection:
            connection.execute("""
                              INSERT INTO users (name, email, password) VALUES (?, ?, ?);
                              """, (name, email, password))
            return "success"
    except sqlite3.IntegrityError:
        return "email_exists"
        
def login_user(connection, email, password):
    user = connection.execute(
        "SELECT id, password FROM users WHERE email=?", (email,)
    ).fetchone()

    if user and bcrypt.checkpw(password.encode(), user[1]):
        return user[0]
    return None

