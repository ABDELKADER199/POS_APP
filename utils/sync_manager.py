import logging
import time
import threading
import json
from typing import List, Dict
from database_manager import DatabaseManager
from utils.offline_manager import OfflineManager

logger = logging.getLogger(__name__)

class SyncManager:
    """مدير المزامنة بين قاعدة البيانات المحلية و TiDB Cloud"""
    
    def __init__(self):
        self.db_local = DatabaseManager()
        self.offline = OfflineManager()
        self._sync_thread = None
        self._stop_event = threading.Event()

    def start_background_sync(self, interval=300):
        """بدء المزامنة في الخلفية كل فترة زمنية (بالثواني)"""
        if self._sync_thread and self._sync_thread.is_alive():
            return
            
        self._stop_event.clear()
        self._sync_thread = threading.Thread(target=self._sync_loop, args=(interval,), daemon=True)
        self._sync_thread.start()
        logger.info(f"بدأت المزامنة التلقائية كل {interval} ثانية")

    def stop_background_sync(self):
        """إيقاف المزامنة في الخلفية"""
        self._stop_event.set()
        if self._sync_thread:
            self._sync_thread.join(timeout=2)

    def _sync_loop(self, interval):
        while not self._stop_event.is_set():
            logger.info("بدء جولة المزامنة التلقائية...")
            self.sync_to_cloud() # المزامنة من طابور MySQL إلى السحاب
            
            if self._stop_event.wait(interval):
                break

    def sync_to_cloud(self, progress_callback=None):
        """مزامنة كافة العمليات المعلقة من القاعدة المحلية إلى السحاب (TiDB Cloud)"""
        pending = self.offline.get_pending_syncs()
        if not pending:
            if progress_callback: progress_callback(100, "لا توجد بيانات للمزامنة")
            return True
            
        total = len(pending)
        logger.info(f"بدء مزامنة {total} عملية إلى السحاب...")
        
        # 1. الاتصال بالسحاب خصيصاً للمزامنة
        cloud_db = DatabaseManager()
        # نطلب منه الاتصال بالسحاب حصراً باستخدام الإعدادات الداخلية
        if hasattr(cloud_db, 'cloud_config') and cloud_db.cloud_config:
            cloud_db._apply_config(cloud_db.cloud_config)
            
        if not cloud_db.host or cloud_db.host == 'localhost' or cloud_db.host == '127.0.0.1' or cloud_db.host == 'HIDDEN':
            error_msg = "إعدادات السحابة غير متوفرة أو خاطئة. تم إيقاف المزامنة لحماية البيانات المحلية."
            logger.error(error_msg)
            if progress_callback: progress_callback(0, error_msg)
            return False
            
        if not cloud_db._do_connect():
            error_msg = "فشل الاتصال بالسحاب للمزامنة"
            logger.error(error_msg)
            if progress_callback: progress_callback(0, error_msg)
            return False
        
        try:
            for i, item in enumerate(pending):
                sync_id = item['id']
                table = item['table_name']
                action = item['action_type']
                data = json.loads(item['data_json'])
                
                status_text = f"مزامنة {table} ({i+1}/{total})..."
                if progress_callback:
                    progress_callback(int((i / total) * 100), status_text)
                
                success = False
                try:
                    if table == 'expenses' and action == 'INSERT':
                        success = cloud_db.add_expense(
                            store_id=data['store_id'], user_id=data['user_id'],
                            expense_type=data['expense_type'], amount=data['amount'],
                            description=data['description'], is_personal=data['is_personal']
                        )
                    elif table == 'purchase_invoices' and action == 'INSERT':
                        success = cloud_db.create_purchase_invoice(
                            supplier_id=data['supplier_id'], total_amount=data['total_amount'],
                            items=data['items'], user_id=data['created_by'],
                            notes=data['notes'], ref_number=data['ref_number'],
                            payment_method=data['payment_method'], paid_amount=data['paid_amount'],
                            subtotal=data['subtotal'], tax_amount=data['tax_amount'],
                            discount_amount=data['discount_amount']
                        )
                    elif table == 'purchase_invoices_payment' and action == 'UPDATE_PAYMENT':
                        success = cloud_db.update_purchase_invoice_payment(
                            invoice_id=item['record_id'], amount=data['amount'],
                            payment_method=data['payment_method']
                        )
                    elif table == 'invoices_finalize' and action == 'FINALIZE':
                        success = cloud_db.finalize_invoice(
                            invoice_number=data['invoice_number'], user_id=data['user_id']
                        )
                    elif table == 'invoices' and action == 'INSERT':
                        # إنشاء الفاتورة على السحاب
                        success = cloud_db.create_invoice(
                            store_id=data['store_id'], cashier_id=data['cashier_id'],
                            customer_name=data.get('customer_name'),
                            customer_phone=data.get('customer_phone'),
                            customer_address=data.get('customer_address'),
                            drawer_id=data.get('drawer_id'), 
                            payment_method=data['payment_method'],
                            cash_amount=data['cash_amount'],
                            card_amount=data['card_amount']
                        )
                    elif table == 'invoice_items' and action == 'INSERT':
                        success = cloud_db.add_invoice_item(
                            invoice_number=data['invoice_number'],
                            product_id=data['product_id'],
                            quantity=data['quantity'],
                            unit_price=data['unit_price'],
                            discount=data.get('discount', 0)
                        )
                    elif table == 'drawer_logs' and action == 'OPEN':
                        success = cloud_db.open_drawer(
                            store_id=data['store_id'],
                            cashier_id=data['cashier_id'],
                            opening_balance=data['opening_balance']
                        )
                    elif table == 'drawer_logs' and action == 'CLOSE':
                        # محاولة إيجاد الدرج المفتوح حالياً على السحاب لهذا المستخدم
                        cashier_id = data.get('cashier_id')
                        target_drawer_id = None
                        
                        if cashier_id:
                            cloud_db.cursor.execute(
                                "SELECT id FROM drawer_logs WHERE status = 'Open' AND cashier_id = %s",
                                (cashier_id,)
                            )
                            res = cloud_db.cursor.fetchone()
                            if res: target_drawer_id = res['id']
                        
                        if not target_drawer_id:
                            target_drawer_id = item['record_id'] # Fallback
                            
                        success = cloud_db.close_drawer(
                            drawer_id=target_drawer_id,
                            closing_balance=data['closing_balance'],
                            denomination_details=data['denomination_details']
                        )
                    elif table == 'settlements' and action == 'INSERT':
                        success = cloud_db.record_settlement(
                            account_type=data['account_type'], account_id=data['account_id'],
                            amount=data['amount'], desc=data['description'], user_id=data['user_id']
                        )
                    
                    if success:
                        self.offline.mark_as_synced(sync_id)
                    else:
                        logger.error(f"فشل تنفيذ العملية {sync_id} على السحاب")
                        
                except Exception as e:
                    logger.error(f"خطأ أثناء معالجة العملية {sync_id}: {e}")
            
            if total > 0:
                logger.info(f"✅ تم الانتهاء من مزامنة {total} عملية بنجاح للسحاب")
            
            if progress_callback: progress_callback(100, "تمت المزامنة بنجاح")
            return True
        finally:
            cloud_db.close()
