import sqlite3

class user:
    def __init__(self, databaseName, tableName):
        self.databaseName = databaseName
        self.tableName = tableName

    def login(self):
        pass
    
    def logout(self):
        pass
    
    def viewAccountInformation(self):
        pass
    
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
    
    def viewOrderHistory(self):
        pass
    
    def validateCreditials(self, email, password):
        pass

    def getUserIdFromDatabase(self,email):
        pass

    def getAccountInfoFromDatabase(self,userID):
        pass

    def createAccountInDatabase(self, email, password, firstName, lastName, address, city, state, zipCode, paymentType):
        pass

    def setDatabaseName(self, databaseName):
        pass

    def setTableName(self, tableName):
        pass