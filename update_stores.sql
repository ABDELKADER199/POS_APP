-- تعديل جدول الفروع وإضافة فرع مدير عام
-- نفذ هذا الملف في MySQL Workbench أو phpMyAdmin

USE stocks;

-- الخطوة 1: تغيير نوع حقل store_type من ENUM إلى VARCHAR
ALTER TABLE stores MODIFY store_type VARCHAR(20) NOT NULL;

-- الخطوة 2: إدراج فرع مدير عام (إذا لم يكن موجوداً)
INSERT INTO stores (store_name, store_type, city, address, phone, manager_name) 
VALUES ('مدير عام', 'GM', 'القاهرة', 'المقر الرئيسي', '01070276578', 'عبدالقادر طارق')
ON DUPLICATE KEY UPDATE store_name = store_name;

-- الخطوة 3: التحقق من النتيجة
SELECT * FROM stores WHERE store_type = 'GM';
