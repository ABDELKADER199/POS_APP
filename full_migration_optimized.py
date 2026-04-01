import mysql.connector
from database_manager import DatabaseManager
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migration")

def migrate():
    logger.info("🚀 بدء عملية الهجرة المحسنة (للبيانات الضخمة) من المحلي إلى السحاب...")
    
    # 1. الاتصال بالمحلي
    db_local = DatabaseManager()
    if not db_local.connect():
        logger.error("❌ فشل الاتصال بالقاعدة المحلية")
        return
    
    # 2. الاتصال بالسحابي
    db_cloud = DatabaseManager()
    db_cloud._load_config_values_from_env()
    if not db_cloud._do_connect():
        logger.error("❌ فشل الاتصال بالقاعدة السحابية")
        return

    # تعطيل القيود مؤقتاً لتسهيل عملية الهجرة الشاملة
    db_cloud.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables = [
        'users', 'categories', 'stores', 'products', 
        'customers', 'suppliers', 'drawer_logs', 'drawer_closing_details',
        'invoices', 'invoice_items', 'purchase_invoices', 'purchase_items',
        'financial_ledger', 'treasury', 'expenses', 'sales_returns'
    ]

    chunk_size = 500 # حجم الدفعة الواحدة للإرسال للسحاب

    for table in tables:
        try:
            logger.info(f"📦 جاري معالجة الجدول: {table}...")
            
            # جلب العدد الإجمالي
            db_local.cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
            total_rows = db_local.cursor.fetchone()['total']
            
            if total_rows == 0:
                logger.info(f"ℹ️ الجدول {table} فارغ محلياً، تخطي...")
                continue
            
            logger.info(f"📊 إجمالي السجلات في {table}: {total_rows}")

            # جلب البيانات من المحلي بنظام "الشرائح" (Pagination) لتوفير الذاكرة
            offset = 0
            while offset < total_rows:
                db_local.cursor.execute(f"SELECT * FROM {table} LIMIT %s OFFSET %s", (chunk_size, offset))
                rows = db_local.cursor.fetchall()
                
                if not rows:
                    break

                # تجهيز أمر الإدخال (REPLACE INTO)
                columns = rows[0].keys()
                placeholders = ", ".join(["%s"] * len(columns))
                cols_str = ", ".join(columns)
                query = f"REPLACE INTO {table} ({cols_str}) VALUES ({placeholders})"
                
                values_to_insert = [tuple(row.values()) for row in rows]
                
                # تنفيذ الإدخال على السحاب
                db_cloud.cursor.executemany(query, values_to_insert)
                db_cloud.conn.commit()
                
                offset += len(rows)
                progress = (offset / total_rows) * 100
                logger.info(f"   ⬆️ تم رفع {offset}/{total_rows} سجل ({progress:.1f}%) من جدول {table}")

            logger.info(f"✅ اكتمل نقل جدول {table}")
            
        except Exception as e:
            logger.error(f"❌ خطأ أثناء نقل جدول {table}: {e}")
            db_cloud.conn.rollback()

    # إعادة تفعيل القيود
    db_cloud.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    db_local.close()
    db_cloud.close()
    logger.info("🏁 تمت عملية الهجرة الشاملة بنجاح!")

if __name__ == "__main__":
    migrate()
