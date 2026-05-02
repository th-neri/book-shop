import database

def menu():
    connection = database.connect()
    database.create_tables(connection)

    current_user = None

    while True:
        if current_user is None:
            print("\n---View options---")
            print("1. Create your account")
            print("2. Sign in")
            print("3. Exit")

            choice = input("Enter your choice number: ").strip()

            if choice == "1":
                print("\n---Create your own account now.---\n")
                name = input("Write your name: ")
                email = input("Write your email: ")
                password  = input("Write your password: ")

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(f'\n---Your account has been successfully created. Welcome to our app, {name}!---')
                elif result == "email_exists":
                    print("\n---This email is already registered. Try to sign in or use a different email to create your account.---")
            elif choice == "2":
                print("\n---Sign in---\n")
                email = input("Enter your email: ").split()
                password = input("Enter your password: ").split()
            elif choice == "3":
                print("\n---Have a good day and feel welcome to come back anytime!---\n")
                break
            else:
                print("Invalid choice. Pick a valid number.")
menu()