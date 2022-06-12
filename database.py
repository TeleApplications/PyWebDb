import sqlite3

__author__ = "SchemeXY"
__licence__ = "Copyright © 2022 SchemeXY"
__version__ = "0.1.0"


class Database:
    sql_cmd = """SELECT vulk.FirstName, vulk.LastName, c.City, a.Street, a.PostalCode, b.Birthdate, g.Gender FROM vulkanolog as vulk
        INNER JOIN birthdate as b ON vulk.BirthdateID=b.BirthdateID
        INNER JOIN gender as g ON vulk.GenderID=g.GenderID
        INNER JOIN address as a ON vulk.AddressID=a.AddressID
        INNER JOIN city as c ON a.CityID=c.CityID"""

    def __init__(self, database: str):
        self.database = database

    def connection(self) -> sqlite3.connect:
        with sqlite3.connect(self.check_database(self.database)) as con:
            return con

    def query(self, sql_command: str) -> list:
        connect = self.connection()
        try:
            cursor = connect.cursor()
            cursor.execute(sql_command)
            connect.commit()
            return cursor.fetchall()
        except Exception:
            connect.rollback()

    @staticmethod
    def check_database(database: str) -> str:
        import os
        assert os.path.exists(database) and database.endswith(".db"), "Invalid Databse File"
        return database
