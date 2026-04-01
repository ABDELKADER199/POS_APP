from database_manager import DatabaseManager
import json

def check_synced():
    db = DatabaseManager()
    if not db.connect():
        print("❌ فشل الاتصال بقاعدة البيانات")
        return
    
    try:
        # Check sync_queue for synced items
        db.cursor.execute("""
            SELECT table_name, action_type, COUNT(*) as count 
            FROM sync_queue 
            WHERE status = 'synced' 
            GROUP BY table_name, action_type
            ORDER BY count DESC
        """)
        synced_summary = db.cursor.fetchall()
        
        if not synced_summary:
            print("ℹ️ لا توجد سجلات تمت مزامنتها بعد في (sync_queue).")
        else:
            print("✅ البيانات التي تمت مزامنتها بنجاح:")
            for item in synced_summary:
                print(f"- الجدول: {item['table_name']}, العملية: {item['action_type']}, العدد: {item['count']}")
            
            # Show the last 5 synced items for context
            print("\n🕒 آخر 5 عمليات مزامنة:")
            db.cursor.execute("""
                SELECT table_name, action_type, synced_at, data_json 
                FROM sync_queue 
                WHERE status = 'synced' 
                ORDER BY synced_at DESC 
                LIMIT 5
            """)
            last_synced = db.cursor.fetchall()
            for rec in last_synced:
                data_preview = ""
                try:
                    data = json.loads(rec['data_json'])
                    if 'invoice_number' in data: data_preview = f"(فاتورة {data['invoice_number']})"
                    elif 'name' in data: data_preview = f"({data['name']})"
                except: pass
                print(f"- {rec['synced_at']} | {rec['table_name']} | {rec['action_type']} {data_preview}")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_synced()
