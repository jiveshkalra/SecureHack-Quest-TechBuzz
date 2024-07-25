
import mysql.connector

# Connect to the database
mydb = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    user="sql12722127",
    password="kKVN6xFhI9",
    database="sql12722127"
)

def get_db():
    return mydb
