import database
import bcrypt

def menu():
    connection = database.connect()
    database.create_tables(connection)

    current_user = None

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
                email = input("Write your email: ")
                password  = input("Write your password: ")

                if not name or not email or not password:
                    print("You need to fill in all the fields.")
                    continue

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(f'\n---Your account has been successfully created. Welcome to our app, {name}!---')
                elif result == "email_exists":
                    print("\n---This email is already registered. Try to sign in or use a different email to create your own account.---")
            elif choice == "2":
                print("\n---Sign in---")
                email = input("Enter your email: ")
                password = input("Enter your password: ")

                user = database.login_user(connection, email, password)

                if user:
                    current_user = user[0]
                    name = user[1]
                    is_admin = user[3] == "admin"
                    print(f'\n---You have been logged in successfully, {name}!---\n')
                else:
                    print("\n---Wrong email or password. Try again or create your own account.---")
            elif choice == "3":
                print("\nHave a good day and feel welcome to come back anytime!\n")
                break
            else:
                print("Invalid choice. Pick a valid number.")

        else:
            print("===Welcome to our shop! Pick any option you want.===")
            print("1. View the books")
            if is_admin:
                print("2. Add a book")
            print("3. Buy a book")
            print("4. Delete your account")
            print("5. Log out")

            choice = input("Enter your choice number: ").strip()

            if choice == "1":
                books = database.get_books(connection)

                if not books:
                    print("\n---No books available.---\n")

                else:
                    print("\n---Books available---")
                    for book in books:
                        print(f'ID Number: {book[0]} | Name of the book: {book[1]} | Price: {book[3]} | Author: {book[2]} | Quantity: {book[4]}')
            elif choice == "2":
                if not is_admin:
                    print("Error :/")
                    continue
            elif choice == "3":
                pass
            elif choice == "4":
                password = input("Enter your password to delete your account: ")

                result = database.get_user_password(connection, current_user)

                if result:
                    stored_password = result[0]

                    if bcrypt.checkpw(password.encode(), stored_password):
                        database.delete_user_by_id(connection, current_user)
                        current_user = None
                        print("\n---Account has been deleted successfully!---")
                    else:
                        print("\n---Incorrect password. Try again.---")
                else:
                    print("\n---User not found.---")
            elif choice == "5":
                print("\nThanks for visiting our shop and have a good day!")
                current_user = None
                continue
            else:
                print("Invalid choice. Pick a valid number.")
                  
    connection.close()

menu()
