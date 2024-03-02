import sqlite3

class Inventory:
    def __init__(self, database_name="", table_name=""):
        # Initialize the Inventory object with a database and table name
        self.database_name = database_name
        self.table_name = table_name

    def view_inventory(self):
        # Display all the items in the inventory
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            result = cursor.fetchall()
            print("Current Inventory:\n\nISBN\t\tTitle\t\tAuthor\t\tGenre\t\tPages\t\tRelease Date\t\tStock\n")
            for item in result:
                print(f"{item[0]}\t\t{item[1]}\t\t{item[2]}\t\t{item[3]}\t\t{item[4]}\t\t{item[5]}\t\t\t{item[6]}")

    def search_inventory(self):
        # Search for books in the inventory by title
        title = input("\nPlease enter the title of the book you want: ")
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE Title LIKE ?", (f"%{title}%",))
            result = cursor.fetchall()
            if result:
                print("\nSearch Results:\n\nISBN\t\tTitle\t\tAuthor\t\tGenre\t\tPages\t\tRelease Date\t\tStock\n")
                for item in result:
                    print(f"{item[0]}\t\t{item[1]}\t\t{item[2]}\t\t{item[3]}\t\t{item[4]}\t\t{item[5]}\t\t\t{item[6]}")
            else:
                print("No results found!\n\n")

    def decrease_stock(self, isbn):
        # Decrease the stock of a book by 1
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT stock FROM {self.table_name} WHERE ISBN=?", (isbn,))
            result = cursor.fetchone()
            if result:
                stock = result[0]
                if stock > 0:
                    cursor.execute(f"UPDATE {self.table_name} SET stock=? WHERE ISBN=?", (stock - 1, isbn))
                else:
                    print("Stock is already at 0, cannot decrease further.")
            else:
                print("No book found with the given ISBN.")

    def add_book(self, isbn, title, author, genre, pages, release_date, stock):
        # Add a new book to the inventory
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} (ISBN, Title, Author, Genre, Pages, Release_Date, Stock) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (isbn, title, author, genre, pages, release_date, stock))
            connection.commit()
