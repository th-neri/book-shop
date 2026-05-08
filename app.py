import database
import bcrypt

def menu():
    connection = database.connect()
    database.create_tables(connection)

    current_user = None
    is_admin = False

    while True:
        if current_user is None:
            print("\n===View options===")
            print("1. Create your account")
            print("2. Sign in")
            print("3. Exit")

            choice = input("Enter your choice number: ").strip()

            if choice == "1":
                print("\n---Create your own account now.---")
                name = input("Write your name: ")
                email = input("Write your email: ").lower()
                password  = input("Write your password: ").lower()

                if not name or not email or not password:
                    print("\nYou need to fill in all the fields.\n")
                    continue

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(f'\n---Your account has been successfully created. Welcome to our app, {name}!---')
                elif result == "email_exists":
                    print("\n---This email is already registered. Try to sign in or use a different email to create your own account.---")
            elif choice == "2":
                print("\n---Sign in---")
                email = input("Enter your email: ").lower()
                password = input("Enter your password: ").lower()

                user = database.login_user(connection, email, password)

                if user:
                    current_user = user[0]
                    name = user[1]
                    is_admin = user[3] == "admin"
                    print(f'\n---You have been logged in, {name}!---\n')
                else:
                    print("\n---Wrong email or password. Try again or create your own account.---")
            elif choice == "3":
                print("\nHave a good day and feel welcome to come back anytime!\n")
                break
            else:
                print("Invalid choice. Pick a valid number.")

        else:
            print("\n===Welcome to our shop! Pick any option you want.===")
            print("1. View the books")
            if is_admin:
                print("2. Add a book on the shop")
            print("3. Add book to the cart")
            print("4. View cart")
            print("5. Remove from cart")
            print("6. Checkout")
            print("7. Delete your account")
            print("8. Log out")

            choice = input("Enter your choice number: ").strip()

            if choice == "1":
                books = database.get_books(connection)

                if not books:
                    print("\n---No books available.---\n")

                else:
                    print("\n---Books available---")
                    for book in books:
                        print(f'ID NUMBER: {book[0]} | NAME OF THE BOOK: {book[1]} | PRICE: ${book[3]:.2f} | AUTHOR: {book[2]} | STOCK: {book[4]}')
            elif choice == "2":
                if not is_admin:
                    print("\nError :/\n")
                    continue
                
                print("\n---Write the book informations you want to add----")
                name = input("Name of the book: ")
                author = input("Name of the author: ")

                try:
                    price = float(input("Price of the book: "))
                    quantity = int(input("Quantity: "))
                except ValueError:
                    print("\nInvalid price or quantity.\n")
                    continue

                if not name or not author:
                    print("\nYou need to fill in all the fields.\n")
                    continue

                database.add_book(connection, name, author, price, quantity)
                print(f'\n---{name} added successfully!---\n')
            elif choice == "3":
                books = database.get_books(connection)

                if not books:
                    print("\n---No books available.---\n")
                    continue

                print("\n---Books available---")
                for book in books:
                    print(f'ID NUMBER: {book[0]} | NAME OF THE BOOK: {book[1]} | PRICE: ${book[3]:.2f} | AUTHOR: {book[2]} | STOCK: {book[4]}')

                try:
                    book_id = int(input("Enter the Book ID number you want: "))
                    quantity = int(input("Quantity: "))
                except ValueError:
                    print("\nInvalid number.\n")
                    continue

                result = database.add_to_the_cart(connection, current_user, book_id, quantity)

                if result[0] == "success":
                    print(f'\n---Book {result[1]} added to the cart!---')
                elif result == "book_not_found":
                    print("\nBook ID not found :(\n")
                elif result == "not_enough":
                    print("\nThere is not enough stock.\n")
                elif result == "invalid_quantity":
                    print("\nInvalid quantity.\n")
            elif choice == "4":
                cart = database.get_cart(connection, current_user)

                if not cart:
                    print("\n---No books added to the cart---\n")
                    continue

                total = 0

                print("\n---Your cart---")
                for item in cart:
                    book_id, name, author, price, quantity = item

                    subtotal = price * quantity
                    total += subtotal
                
                    print(f'ID NUMBER: {book_id} | NAME OF THE BOOK: {name} | PRICE: ${price:.2f} | AUTHOR: {author} | QUANTITY: {quantity} | SUBTOTAL: ${subtotal:.2f}')

                print(f'\nTOTAL: ${total:.2f}')
            elif choice == "5":
                books = database.get_books(connection, current_user)

                if not books:
                    print("\n---No books added to the cart---\n")
                    continue

                print("\n---Your cart---")
                for item in cart:
                    print(f'ID NUMBER: {item[9]} | NAME OF THE BOOK: {item[1]} | QUANTITY: {item[4]}')

                try:
                    book_id = int(input("Enter the Book ID number you want to remove from your cart: "))
                except ValueError:
                    print("\nInvalid number.\n")
                    continue

                database.delete_from_cart(connection, current_user, book_id)

                print("\n---Book removed from your cart.---\n")
            elif choice == "6":
                pass
            elif choice == "7":
                password = input("Enter your password to delete your account: ")

                result = database.get_user_password(connection, current_user)

                if result:
                    stored_password = result[0]

                    confirm = input("Are you sure you want to delete your account ? (Y/N): ").lower()
                    if confirm == "n":
                        print("\nCancelled.")
                        continue
                    elif confirm == "y":
                        if bcrypt.checkpw(password.encode(), stored_password):
                            database.delete_user_by_id(connection, current_user)
                            current_user = None
                            print("\n---Account has been deleted successfully!---")
                        else:
                            print("\n---Incorrect password. Try again.---")
                    else:
                        print("\nInvalid input. You have to use (Y) for yes or (N) for no.")
                else:
                    print("\nUser not found.")
            elif choice == "8":
                print("\nThanks for visiting our shop and have a good day!")
                current_user = None
                is_admin= False
                continue
            else:
                print("Invalid choice. Pick a valid number.")
                  
    connection.close()

menu()
