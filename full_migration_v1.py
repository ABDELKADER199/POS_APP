import mysql.connector
from database_manager import DatabaseManager
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migration")

def migrate():
    logger.info("🚀 بدء عملية الهجرة الكاملة من المحلي إلى السحاب...")
    
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

    # ترتيب الجداول مهم جداً بسبب القيود (Foreign Keys)
    tables = [
        'users', 'categories', 'stores', 'products', 
        'customers', 'suppliers', 'drawer_logs', 'drawer_closing_details',
        'invoices', 'invoice_items', 'purchase_invoices', 'purchase_items',
        'financial_ledger', 'treasury', 'expenses', 'sales_returns'
    ]

    for table in tables:
        try:
            logger.info(f"📦 جاري معالجة الجدول: {table}...")
            
            # جلب البيانات من المحلي
            db_local.cursor.execute(f"SELECT * FROM {table}")
            rows = db_local.cursor.fetchall()
            
            if not rows:
                logger.info(f"ℹ️ الجدول {table} فارغ محلياً، تخطي...")
                continue

            # تجهيز أمر الإدخال (REPLACE INTO) لتجنب التكرار وتحديث الموجود
            columns = rows[0].keys()
            placeholders = ", ".join(["%s"] * len(columns))
            cols_str = ", ".join(columns)
            query = f"REPLACE INTO {table} ({cols_str}) VALUES ({placeholders})"
            
            # تحويل البيانات لتناسب MySQL (التحويلات العشارية والتاريخ)
            values_to_insert = []
            for row in rows:
                values_to_insert.append(tuple(row.values()))
            
            # تنفيذ الإدخال على السحاب
            db_cloud.cursor.executemany(query, values_to_insert)
            db_cloud.conn.commit()
            
            logger.info(f"✅ تم نقل {len(rows)} سجل في جدول {table}")
            
        except Exception as e:
            logger.error(f"❌ خطأ أثناء نقل جدول {table}: {e}")
            db_cloud.conn.rollback()

    # إعادة تفعيل القيود
    db_cloud.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    db_local.close()
    db_cloud.close()
    logger.info("🏁 تمت عملية الهجرة بنجاح!")

if __name__ == "__main__":
    migrate()
