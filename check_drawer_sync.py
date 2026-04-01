from database_manager import DatabaseManager
import json

def check_drawer_sync():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال")
        return
    
    db.cursor.execute("SELECT * FROM sync_queue WHERE table_name LIKE '%drawer%' OR table_name = 'drawer_closing_details'")
    records = db.cursor.fetchall()
    
    if not records:
        print("ℹ️ لا توجد سجلات درج في طابور المزامنة.")
    else:
        print(f"📋 وجدنا {len(records)} سجل في طابور المزامنة:")
        for rec in records:
            print(f"- ID: {rec['id']}, Table: {rec['table_name']}, Action: {rec['action_type']}, Status: {rec['status']}, Created: {rec['created_at']}")
            if rec['status'] == 'failed':
                print(f"  ❌ Error: {rec['error_message']}")

    db.close()

if __name__ == "__main__":
    check_drawer_sync()
