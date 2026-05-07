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
                           password BLOB NOT NULL,
                           role TEXT DEFAULT 'user'
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
        
def buy_book(connection, user_id, book_id, quantity):
    with connection:
        book = connection.execute("SELECT quantity, price, name FROM books WHERE id=?", (book_id,)
        ).fetchone()

        if not book:
            return "book_not_found"

        stock, price, name = book

        if quantity > stock:
            return "not_enough"

        total = price * quantity

        connection.execute("UPDATE books SET quantity = quantity - ? WHERE id=?", (quantity, book_id))

        connection.execute("INSERT INTO orders(user_id, total) VALUES (?, ?)", (user_id, total))

        return ("success", name)

def get_books(connection):
    with connection:
        return connection.execute("SELECT * FROM books").fetchall()
    
def delete_book(connection, book):
    with connection:
        return connection.execute("DELETE FROM books WHERE id=?", (book,))
    

#---------USER FUNCTIONS---------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def add_user(connection, name, email, password):
    hashed = hash_password(password)
    try:
        with connection:
            connection.execute("""
                              INSERT INTO users (name, email, password) VALUES (?, ?, ?);
                              """, (name, email, hashed))
            return "success"
    except sqlite3.IntegrityError:
        return "email_exists"
    
def find_user_by_id(connection, id):
    with connection:
        return connection.execute("SELECT id, name, password FROM users WHERE id=?", (id,)
        ).fetchone()
        
def login_user(connection, email, password):
    user = connection.execute("SELECT id, name, password, role FROM users WHERE email=?", (email,)
    ).fetchone()

    if user and bcrypt.checkpw(password.encode(), user[2]):
        return user
    return None

def make_admin(connection, email):
    with connection:
        connection.execute("UPDATE users SET role='admin' WHERE email=?", (email,))

def get_user_password(connection, id):
    with connection:
        return connection.execute("SELECT password from users WHERE id=?", (id,)
        ).fetchone()

def delete_user_by_id(connection, id):
    with connection:
        connection.execute("DELETE FROM users WHERE id=?", (id,))
