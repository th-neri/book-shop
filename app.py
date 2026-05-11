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
            
#---CREATE ACCOUNT OPTION----
            if choice == "1":
                print("\n---Create your own account now.---")
                name = input("Write your name: ")
                email = input("Write your email: ")
                password = input("Write your password: ")

                if not name or not email or not password:
                    print("\nYou need to fill in all the fields.\n")
                    continue

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(
                        f'\n---Your account has been successfully created. Welcome to our app, {name}!---')
                elif result == "email_exists":
                    print(
                        "\n---This email is already registered. Try to sign in or use a different email to create your own account.---")
                    
#---LOGIN ACCOUNT OPTION----        
            elif choice == "2":
                print("\n---Sign in---")
                email = input("Enter your email: ")
                password = input("Enter your password: ")

                user = database.login_user(connection, email, password)

                if user:
                    current_user = user[0]
                    name = user[1]
                    is_admin = user[3] == "admin"
                    print(f'\n---You have been logged in, {name}!---')
                else:
                    print(
                        "\n---Wrong email or password. Try again or create your own account.---")
                    
#---EXIT----      
            elif choice == "3":
                print("\nHave a good day and feel welcome to come back anytime!\n")
                break
            else:
                print("Invalid choice. Pick a valid number.")

#---OPTIONS FOR WHEN THE LOGIN IS SUCCEEDED----
        else:
            print("\n===Options of our shop===")
            print("1. View the books")
            print("2. Buy your book here")
            print("3. Delete your account")
            print("4. Log out")
            if is_admin:
#ONLY FOR ADMINS
                print("5. Add a book on the shop")
                print("6. Remove book from the shop")

            choice = input("Enter your choice number: ").strip()

#---OPTION ONE: VIEW THE BOOKS AVAILABLE----
            if choice == "1":
                books = database.get_books(connection)

                if not books:
                    print("\n---No books available.---\n")

                else:
                    print("\n---Books available---")
                    for book in books:
                        print(
                            f'ID NUMBER: {book[0]} | NAME OF THE BOOK: {book[1]} | PRICE: ${book[3]:.2f} | AUTHOR: {book[2]} | STOCK: {book[4]}')
                        
#---OPTION THREE: BUY A BOOK(WHICH WILL TAKE THE USER TO ANOTHER PAGE WHERE THERE ARE MORE OPTIONS RELATED TO THE PURCHASE----
            elif choice == "2":
               while True:
                    print("\n===Options===")
                    print("1. Add book to the cart")
                    print("2. View cart")
                    print("3. Remove from the cart")
                    print("4. Checkout")
                    print("5. Go back to the main page")

                    option = input("\nEnter the option number: ").strip()

#---OPTION ONE OF THE BUY BOOK OPTION: ADD THE BOOK TO THE CART----
                    if option == "1":
                        books = database.get_books(connection)

                        if not books:
                            print("\n---No books available.---")
                            continue

                        print("\n---Books available---")
                        for book in books:
                            print(f'ID NUMBER: {book[0]} | NAME OF THE BOOK: {book[1]} | PRICE: ${book[3]:.2f} | AUTHOR: {book[2]} | STOCK: {book[4]}')

                        try:
                            book_id = int(input("Enter the Book ID number you want: "))
                            quantity = int(input("Quantity: "))
                        except ValueError:
                            print("\nInvalid number.")
                            continue

                        result = database.add_to_the_cart(connection, current_user, book_id, quantity)

                        if result[0] == "success":
                            print(f'\n---Book {result[1]} added to the cart!---')
                        elif result == "book_not_found":
                            print("\nBook ID not found :(")
                        elif result == "not_enough":
                            print("\nThere is not enough stock.")
                        elif result == "invalid_quantity":
                            print("\nInvalid quantity.")

#---OPTION TWO OF THE BUY BOOK OPTION: VIEW CART----
                    elif option == "2":
                        cart = database.get_cart(connection, current_user)

                        if not cart:
                            print("\n---No books added to the cart---")
                            continue

                        total = 0

                        print("\n---Your cart---")
                        for item in cart:
                            book_id, name, author, price, quantity = item

                            subtotal = price * quantity
                            total += subtotal

                            print(f'ID NUMBER: {book_id} | NAME OF THE BOOK: {name} | PRICE: ${price:.2f} | AUTHOR: {author} | QUANTITY: {quantity} | SUBTOTAL: ${subtotal:.2f}')

                        print(f'\nTOTAL: ${total:.2f}')

#---OPTION THREE OF THE BUY BOOK OPTION: REMOVE BOOK FROM THE CART----
                    elif option == "3":
                        cart = database.get_cart(connection, current_user)

                        if not cart:
                            print("\n---No books added to the cart---")
                            continue

                        print("\n---Your cart---")
                        for item in cart:
                            print(f'ID NUMBER: {item[0]} | NAME OF THE BOOK: {item[1]} | QUANTITY: {item[4]}')

                        try:
                            book_id = int(input("Enter the Book ID number you want to remove from your cart: "))
                        except ValueError:
                            print("\nInvalid number.")
                            continue

                        database.delete_from_cart(connection, current_user, book_id)
                        print("\n---Book removed from your cart.---")

#---OPTION FOUR OF THE BUY BOOK OPTION: CHECKOUT----
                    elif option == "4":
                        pass

#---OPTION FIVE OF THE BUY BOOK OPTION: TAKE THE USER TO THE MAIN PAGE----
                    elif option == "5":
                        break

#---OPTION FOUR: DELETE THE USER ACCOUNT----
            elif choice == "3":
                password = input(
                    "Enter your password to delete your account: ")

                result = database.get_user_password(connection, current_user)

                if result:
                    stored_password = result[0]

                    confirm = input(
                        "Are you sure you want to delete your account ? (Y/N): ").lower()
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
                        print(
                            "\nInvalid input. You have to use (Y) for yes or (N) for no.")
                else:
                    print("\nUser not found.")

#---OPTION FIVE: LOGOUT----
            elif choice == "4":
                print("\nThanks for visiting our shop and have a good day!")
                current_user = None
                is_admin = False
                continue

#---OPTION TWO: ADD BOOK(ONLY FOR ADMINS)----
            elif choice == "5":
                if not is_admin:
                    print("\nError :/")
                    continue

                print("\n---Write the book informations you want to add----")
                name = input("Name of the book: ")
                author = input("Name of the author: ")

                try:
                    price = float(input("Price of the book: "))
                    quantity = int(input("Quantity: "))
                except ValueError:
                    print("\nInvalid price or quantity.")
                    continue

                if not name or not author:
                    print("\nYou need to fill in all the fields.")
                    continue

                database.add_book(connection, name, author, price, quantity)
                print(f'\n---{name} added successfully!---')

#---OPTION THREE: REMOVE BOOK FROM THE SHOP(ONLY FOR ADMINS)----
            elif choice == "6":
                if not is_admin:
                    print("\nError :/")
                    continue

                try:
                    book_id = int(input("Enter the book ID number you want to remove from the shop: "))
                except ValueError:
                    print("\nInvalid number.")
                    continue

                database.delete_book(connection, book_id)
                print("\n---Book removed from the shop.---")            
            else:
                print("Invalid choice. Pick a valid number.")

    connection.close()

menu()
