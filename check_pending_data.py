from database_manager import DatabaseManager
import json

def check_pending():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    try:
        # Check sync_queue
        db.cursor.execute("SELECT table_name, action_type, COUNT(*) as count FROM sync_queue WHERE status = 'pending' GROUP BY table_name, action_type")
        pending_items = db.cursor.fetchall()
        
        if not pending_items:
            print("✅ لا توجد بيانات تنتظر المزامنة في طابور المزامنة (sync_queue).")
        else:
            print("📋 البيانات التي تنتظر المزامنة في (sync_queue):")
            for item in pending_items:
                print(f"- الجدول: {item['table_name']}, العملية: {item['action_type']}, العدد: {item['count']}")
        
        # Check other potential tables for unsynced markers if they exist
        # For example, if some tables have 'is_synced' column
        db.cursor.execute("SHOW TABLES")
        tables = [list(t.values())[0] for t in db.cursor.fetchall()]
        
        for table in tables:
            db.cursor.execute(f"DESCRIBE {table}")
            columns = [c['Field'] for c in db.cursor.fetchall()]
            if 'is_synced' in columns:
                db.cursor.execute(f"SELECT COUNT(*) as count FROM {table} WHERE is_synced = 0")
                count = db.cursor.fetchone()['count']
                if count > 0:
                    print(f"- الجدول: {table}, بيانات غير مزامنة (is_synced=0): {count}")
            elif 'synced' in columns:
                db.cursor.execute(f"SELECT COUNT(*) as count FROM {table} WHERE synced = 0")
                count = db.cursor.fetchone()['count']
                if count > 0:
                    print(f"- الجدول: {table}, بيانات غير مزامنة (synced=0): {count}")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء فحص البيانات: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_pending()
