from database_manager import DatabaseManager

def check():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال بالقاعدة المحلية")
        return
    
    db.cursor.execute("SELECT COUNT(*) as cnt FROM drawer_logs")
    logs_cnt = db.cursor.fetchone()['cnt']
    
    db.cursor.execute("SELECT COUNT(*) as cnt FROM drawer_closing_details")
    details_cnt = db.cursor.fetchone()['cnt']
    
    print(f"Local drawer_logs: {logs_cnt}")
    print(f"Local drawer_closing_details: {details_cnt}")
    
    if logs_cnt > 0:
        db.cursor.execute("SELECT * FROM drawer_logs ORDER BY id DESC LIMIT 1")
        last_log = db.cursor.fetchone()
        print(f"أخر سجل في drawer_logs: ID={last_log['id']}, Status={last_log['status']}, Closing={last_log['closing_balance']}")

    db.close()

if __name__ == "__main__":
    check()
