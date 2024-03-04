import sqlite3

class user:
    def __init__(self, databaseName, tableName):
        self.databaseName = databaseName
        self.tableName = tableName
        self.loggedIn = False
        self.userID = None

    def login(self):
        username = input("Enter your email: ")
        password = input("Enter your password: ")

        if self.validate_credentials(username, password):
            
            self.loggedIn = True
            self.userID = self.get(username)
            print("Login successful.")
          
            return True
        else:
            print("Login failed.")
            return False

    def logout(self):
        self.userID = ""
        self.loggedIn = False
        print("You have been logged out.")
        return True
    
    def viewAccountInformation(self):
        if self.loggedIn:

            account_info = self.getAccountInfoFromDatabase(self.userID)
            if account_info:
                print("Account Information:")
               
                for key, value in account_info.items():
                    print(f"{key}: {value}")
            else:
                print("Account information could not be retrieved.")
        else:
            print("You are not logged in.")
    
    def createAccount(self):
        firstName = input("Enter your first name: ")
        lastName = input("Enter your last name: ")
        email = input("Enter email: ")
        password = input("Enter a password: ")
        address = input("Enter a mailing address: ")
        state = input("Enter state: ")
        city = input("Enter city: ")
        zipCode = input("Enter zip code: ")
        paymentType = input("Enter method of payment: ")

       
        if self.createAccountInDatabase(email, password, firstName, lastName,address, city, state, zipCode, paymentType):
            print("Account created successfully.")
        else:
            print("Account creation failed.")
    

    def updateProfile(self, email, password):
        pass   
    
  
    def validateCreditials(self, email, password):
        connection = sqlite3.connect(self.databaseName)
        cursor = connection.cursor()
        # Query to check if the email and password combination exists in the database
        cursor.execute(f"SELECT UserId, Password FROM {self.tableName} WHERE Email = ?", (email,))
        result = cursor.fetchone()
        connection.close()

        return result and result[1] == password

    def getUserIdFromDatabase(self,email):
        
        connection = sqlite3.connect(self.databaseName)
        cursor = connection.cursor()
        cursor.execute(f"SELECT UserId FROM {self.tableName} WHERE Email = ?", (email,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else None


    def getAccountInfoFromDatabase(self,userID):
        connection = sqlite3.connect(self.databaseName)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {self.tableName} WHERE UserId = ?", (userID,))
        columns = [column[0] for column in cursor.description]
        account_info = cursor.fetchone()
        connection.close()
        # Return a dictionary of the account info if found, else None
        return dict(zip(columns, account_info)) if account_info else None

    def createAccountInDatabase(self, email, password, firstName, lastName, address, city, state, zipCode, paymentType):
        try:
            connection = sqlite3.connect(self.databaseName)
            cursor = connection.cursor()
            # SQL query to insert the new account data
            cursor.execute(f"INSERT INTO {self.tableName} (Email, Password, FirstName, LastName, Address, City, State, Zip, Payment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (email, password, firstName, lastName, address, city, state, zipCode, paymentType))
            connection.commit()
            connection.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def setDatabaseName(self, databaseName):
        self.databaseName = databaseName

    def setTableName(self, tableName):
         self.tableName = tableName