import json
import logging
from datetime import datetime
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class OfflineManager:
    """مدير العمل بوضع الأوفلاين - يستخدم MySQL المحلي للتخزين المؤقت"""
    
    def __init__(self):
        self.db = DatabaseManager()

    def add_to_sync_queue(self, table_name: str, record_id: int, action: str, data: dict):
        """إضافة عملية إلى قائمة المزامنة في MySQL"""
        try:
            query = """
            INSERT INTO sync_queue (table_name, record_id, action_type, data_json)
            VALUES (%s, %s, %s, %s)
            """
            self.db.cursor.execute(query, (
                table_name, 
                record_id, 
                action, 
                json.dumps(data, ensure_ascii=False)
            ))
            self.db.conn.commit()
            return True
        except Exception as e:
            logger.error(f"فشل إضافة عملية للمزامنة: {e}")
            return False

    def get_pending_syncs(self):
        """جلب العمليات التي لم ترفع للسحاب"""
        try:
            query = "SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY created_at ASC"
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Exception as e:
            logger.error(f"خطأ في جلب طابور المزامنة: {e}")
            return []

    def mark_as_synced(self, sync_id):
        """تحديث حالة المزامنة لنظام MySQL"""
        try:
            query = "UPDATE sync_queue SET status = 'synced', synced_at = NOW() WHERE id = %s"
            self.db.cursor.execute(query, (sync_id,))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة المزامنة: {e}")
