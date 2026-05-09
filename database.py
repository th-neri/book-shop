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
        
def get_books(connection):
    with connection:
        return connection.execute("SELECT * FROM books"
                                  ).fetchall()
    
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


#---------CART FUNCTIONS---------

def add_to_the_cart(connection, user_id, book_id, quantity):
    with connection:
        book = connection.execute("SELECT quantity, name from books where id=?", (book_id,)
                                  ).fetchone()

        if not book:
            return("book_not_found",)
    
        stock, name = book

        if quantity <= 0:
            return("invalid_quantity",)
    
        if quantity > stock:
            return("not_enough",)
    
        existing = connection.execute("SELECT quantity from cart WHERE user_id=? AND book_id=?", (user_id, book_id)
                                      ).fetchone()

        if existing:
            connection.execute("""
                              UPDATE cart SET quantity = quantity + ? WHERE user_id=? AND book_id=?""", 
                              (quantity, user_id, book_id))
        else:
            connection.execute("""
                              INSERT INTO cart (user_id, book_id, quantity) VALUES (?, ?, ?)""", (user_id, book_id, quantity))
            
        return("success", name)
    
def get_cart(connection, user_id):
    with connection:
        return connection.execute("""
                          SELECT books.id, books.name, books.author, books.price, cart.quantity FROM cart
                            JOIN books ON cart.book_id = books.id
                            WHERE cart.user_id=?""", (user_id,)
                            ).fetchall()
        
def delete_from_cart(connection, user_id, book_id):
    with connection:
        connection.execute("DELETE FROM cart WHERE user_id=? AND book_id=?", (user_id, book_id))

def checkout_cart(connection, user_id):
    with connection:
        cart_items = connection.execute("""
                                       SELECT books.id, books.name, books.price, books.quantity, cart.quantity FROM cart
                                        JOIN books ON cart.book_id = books.id
                                        WHERE cart.user_id=?""", (user_id,)
                                        ).fetchall()
        if not cart_items:
            return("empty_cart",)
        
        total = 0

        for item in cart_items:
            book_id, name, price, stock, cart_quantity = item

            if cart_quantity > stock:
                return("not_enough", name) 
            
            total += price * cart_quantity

        for item in cart_items:
            book_id, name, price, stock, cart_quantity = item

            connection.execute("UPDATE books SET quantity = quantity - ? WHERE id=?", (cart_quantity, book_id))

        connection.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))

        connection.execute("DELETE from cart WHERE user_id=?", (user_id))

        return("success", total)
