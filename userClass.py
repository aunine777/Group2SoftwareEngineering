import sqlite3

class user:
    def __init__(self, databaseName, tableName):
        pass

    def login(self):
        pass
    
    def logout(self):
        pass
    
    def viewAccountInformation(self):
        pass
    
    def createAccount(self):
        pass
    
    def validateCreditials(self, email, password):
        pass

    def getUserIdFromDatabase(self,email):
        pass

    def getAccountInfoFromDatabase(self,userID):
        pass

    def createAccountInDatabase(self, email, password, first_name, last_name, address, city, state, zip, payment):
        pass

    def setDatabaseName(self, databaseName):
        pass

    def setTableName(self, tableName):
        pass