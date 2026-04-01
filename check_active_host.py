from database_manager import DatabaseManager

def check():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال بأي قاعدة بيانات")
        return
    
    print(f"📡 متصل حالياً بـ: {db.host}")
    
    db.cursor.execute("SELECT * FROM drawer_logs WHERE id = 1")
    log = db.cursor.fetchone()
    if log:
        print(f"Record: ID={log['id']}, Cashier={log['cashier_id']}, Status={log['status']}")
    else:
        print("سجل ID=1 غير موجود")

    db.close()

if __name__ == "__main__":
    check()
