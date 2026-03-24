import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kbs@2007",
    database="price_comparison"
)

cursor = db.cursor(dictionary=True)