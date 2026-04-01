from database_manager import DatabaseManager
db = DatabaseManager()
if db.connect():
    db.cursor.execute("SELECT COUNT(*) as cnt FROM sync_queue WHERE status = 'failed'")
    print(db.cursor.fetchone()['cnt'])
    db.close()
