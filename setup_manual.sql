-- ============================================
-- برنامج تشغيل قاعدة البيانات في phpMyAdmin
-- ============================================

-- 1. نسخ جميع محتويات ملف database_schema.sql وشغلها

-- 2. إذا حدثت مشاكل مع Triggers، قم بتشغيل هذا:

-- حذف الـ Triggers القديمة (إذا وجدت):
DROP TRIGGER IF EXISTS update_product_profit_margin;
DROP TRIGGER IF EXISTS calculate_invoice_item_total;
DROP TRIGGER IF EXISTS calculate_invoice_total;

-- إعادة إنشاء الـ Triggers:
DELIMITER $$

CREATE TRIGGER update_product_profit_margin
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.buy_price > 0 THEN
        SET NEW.profit_margin = ((NEW.sell_price - NEW.buy_price) / NEW.buy_price) * 100;
    END IF;
END$$

CREATE TRIGGER calculate_invoice_item_total
BEFORE INSERT ON invoice_items
FOR EACH ROW
BEGIN
    SET NEW.total_price = (NEW.quantity * NEW.unit_price) - COALESCE(NEW.discount, 0);
END$$

CREATE TRIGGER calculate_invoice_total
AFTER INSERT ON invoice_items
FOR EACH ROW
BEGIN
    UPDATE invoices 
    SET total_amount = (SELECT SUM(total_price) FROM invoice_items WHERE invoice_id = NEW.invoice_id)
    WHERE id = NEW.invoice_id;
END$$

DELIMITER ;

-- 3. التحقق من الجداول:
USE stocks;
SHOW TABLES;

-- 4. عرض محتويات الجداول الأساسية:
SELECT * FROM roles;
SELECT * FROM stores;
SELECT * FROM categories;

-- ============================================
-- أوامر مفيدة للصيانة
-- ============================================

-- لحذف جميع البيانات مع الاحتفاظ بالجداول:
-- TRUNCATE TABLE audit_logs;
-- TRUNCATE TABLE invoices;
-- TRUNCATE TABLE orders;

-- لحذف قاعدة البيانات كاملة:
-- DROP DATABASE stocks;

-- لإصلاح الأخطاء:
-- CHECK TABLE products;
-- OPTIMIZE TABLE products;

-- إحصائيات الجداول:
SELECT 
    TABLE_NAME,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS Size_MB
FROM information_schema.TABLES 
WHERE table_schema = 'stocks'
ORDER BY (data_length + index_length) DESC;
