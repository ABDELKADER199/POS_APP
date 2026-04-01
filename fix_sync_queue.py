from database_manager import DatabaseManager

def fix_queue():
    db = DatabaseManager()
    db.connect()
    try:
        # إرجاع حالة المزامنة للبيانات التي لم ترفع فعلياً للسحابة
        db.cursor.execute("UPDATE sync_queue SET status = 'pending' WHERE status = 'synced'")
        db.conn.commit()
        print("✅ تم إعادة تعيين طابور المزامنة بنجاح ليرفع البيانات المتأخرة إلى السحابة.")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_queue()
