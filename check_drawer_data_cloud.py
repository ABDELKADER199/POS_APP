from database_manager import DatabaseManager

def check():
    db = DatabaseManager()
    if hasattr(db, 'cloud_config') and db.cloud_config:
        db._apply_config(db.cloud_config)
    if not db._do_connect():
        print("❌ فشل الاتصال بالقاعدة السحابية")
        return
    
    db.cursor.execute("SELECT COUNT(*) as cnt FROM drawer_logs")
    logs_cnt = db.cursor.fetchone()['cnt']
    
    db.cursor.execute("SELECT COUNT(*) as cnt FROM drawer_closing_details")
    details_cnt = db.cursor.fetchone()['cnt']
    
    print(f"Cloud drawer_logs: {logs_cnt}")
    print(f"Cloud drawer_closing_details: {details_cnt}")
    
    if logs_cnt > 0:
        db.cursor.execute("SELECT * FROM drawer_logs ORDER BY id DESC LIMIT 5")
        logs = db.cursor.fetchall()
        for log in logs:
            print(f"سجل سحابي: ID={log['id']}, Cashier={log['cashier_id']}, Status={log['status']}")

    db.close()

if __name__ == "__main__":
    check()
