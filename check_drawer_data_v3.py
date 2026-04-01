from database_manager import DatabaseManager

def check():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال بالقاعدة المحلية")
        return
    
    db.cursor.execute("SELECT * FROM drawer_logs WHERE id = 1")
    log = db.cursor.fetchone()
    if log:
        print(f"Local Record: ID={log['id']}, Cashier={log['cashier_id']}, Status={log['status']}, Store={log['store_id']}")
    else:
        print("Sجل ID=1 غير موجود محلياً")

    db.close()

if __name__ == "__main__":
    check()
