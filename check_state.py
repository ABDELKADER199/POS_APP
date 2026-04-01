from database_manager import DatabaseManager
import os

db = DatabaseManager()
print("Methods in DatabaseManager:")
for method in dir(DatabaseManager):
    if not method.startswith("__"):
        print(f"- {method}")

print("\nChecking database tables:")
if db.cursor:
    db.cursor.execute("SHOW TABLES")
    tables = db.cursor.fetchall()
    for table in tables:
        print(f"- {list(table.values())[0]}")
else:
    print("Database cursor is None!")
