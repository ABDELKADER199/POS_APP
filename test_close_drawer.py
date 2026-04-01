from database_manager import DatabaseManager
db = DatabaseManager()
db.connect()

details = {
    "1ج": 8350,
    "Visa": 0.0
}

result = db.close_drawer(1, 8350.0, details)
print("Result:", result)
db.close()
