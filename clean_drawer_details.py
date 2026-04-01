from database_manager import DatabaseManager

def clean_duplicates(db, name):
    print(f"جاري تنظيف قاعدة البيانات: {name} ...")
    try:
        db.cursor.execute("SELECT id, drawer_log_id, denomination FROM drawer_closing_details")
        rows = db.cursor.fetchall()
        
        # Keep track of latest id for each (drawer_log_id, denomination)
        unique_map = {}
        for row in rows:
            key = (row['drawer_log_id'], row['denomination'])
            if key not in unique_map or row['id'] > unique_map[key]:
                unique_map[key] = row['id']
                
        keep_ids = list(unique_map.values())
        
        if len(keep_ids) > 0:
            format_strings = ','.join(['%s'] * len(keep_ids))
            db.cursor.execute(f"DELETE FROM drawer_closing_details WHERE id NOT IN ({format_strings})", tuple(keep_ids))
            deleted = db.cursor.rowcount
            db.conn.commit()
            print(f"✅ تم حذف {deleted} سجل مكرر من {name}.")
        else:
            print(f"لا توجد بيانات تحتاج للحذف في {name}.")
            
    except Exception as e:
        print(f"❌ حدث خطأ في {name}: {e}")

def run():
    # 1. تنظيف السحابة
    cloud_db = DatabaseManager()
    if hasattr(cloud_db, 'cloud_config') and cloud_db.cloud_config:
        cloud_db._apply_config(cloud_db.cloud_config)
    if cloud_db._do_connect():
        clean_duplicates(cloud_db, "السحابة (TiDB)")
        cloud_db.close()
    
    # 2. تنظيف المحلية
    local_db = DatabaseManager()
    local_db.connect()
    clean_duplicates(local_db, "المحلية (Localhost)")
    local_db.close()

if __name__ == "__main__":
    run()
