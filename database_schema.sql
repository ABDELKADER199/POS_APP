-- ============================================
-- قاعدة بيانات تطبيق POS - نظام الفروع والمبيعات
-- ============================================

-- حذف قاعدة البيانات إن وجدت (اختياري)
DROP DATABASE IF EXISTS stocks;
CREATE DATABASE stocks;
USE stocks;

-- ============================================
-- 1. جدول الصلاحيات والأدوار
-- ============================================
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO roles (role_name, description) VALUES
('admin', 'مدير النظام - يمتلك جميع الصلاحيات'),
('manager', 'مدير المخزن'),
('cashier', 'كاشير'),
('call_center', 'موظف Call Center'),
('warehouse_staff', 'موظف المخزن');

-- ============================================
-- 2. جدول الفروع والمخازن
-- ============================================
CREATE TABLE stores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_name VARCHAR(100) NOT NULL,
    store_type ENUM('Main', 'Branch', 'GM', 'Warehouse') DEFAULT 'Branch',
    city VARCHAR(50),
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    manager_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO stores (store_name, store_type, city, address, phone, manager_name) VALUES
('مدير عام', 'GM', 'القاهرة', 'المقر الرئيسي', '01070276578', 'عبدالقادر طارق'),
('المخزن الرئيسي', 'Main', 'القاهرة', 'شارع النيل', '0201234567', 'أحمد محمد'),
('فرع الإسكندرية', 'Branch', 'الإسكندرية', 'شارع البحر', '0203456789', 'محمد علي'),
('فرع الجيزة', 'Branch', 'الجيزة', 'شارع الهرم', '0202345678', 'فاطمة محمود');

-- ============================================
-- 3. جدول المستخدمين
-- ============================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role_id INT NOT NULL,
    store_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ============================================
-- 4. جدول الفئات (أنواع المنتجات)
-- ============================================
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categories (category_name, description) VALUES
('إلكترونيات', 'أجهزة إلكترونية'),
('ملابس', 'ملابس وأحذية'),
('غذائيات', 'منتجات غذائية'),
('مستحضرات عناية', 'مستحضرات العناية الشخصية'),
('أدوات منزلية', 'أدوات وأجهزة منزلية');

-- ============================================
-- 5. جدول المنتجات
-- ============================================
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    buy_price DECIMAL(10, 2) NOT NULL,
    sell_price DECIMAL(10, 2) NOT NULL,
    profit_margin DECIMAL(5, 2),
    unit VARCHAR(20) DEFAULT 'piece',
    barcode VARCHAR(50) UNIQUE,
    description TEXT,
    image_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_product_code (product_code),
    INDEX idx_barcode (barcode)
);

-- ============================================
-- 6. جدول مخزون المنتجات (حسب المخزن)
-- ============================================
CREATE TABLE product_inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    store_id INT NOT NULL,
    quantity_in_stock INT NOT NULL DEFAULT 0,
    minimum_quantity INT DEFAULT 10,
    last_count_date DATETIME,
    last_counted_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (last_counted_by) REFERENCES users(id),
    UNIQUE KEY unique_product_store (product_id, store_id),
    INDEX idx_store_quantity (store_id, quantity_in_stock)
);

-- ============================================
-- 7. جدول سجل تاريخ الأسعار
-- ============================================
CREATE TABLE price_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    old_buy_price DECIMAL(10, 2),
    new_buy_price DECIMAL(10, 2),
    old_sell_price DECIMAL(10, 2),
    new_sell_price DECIMAL(10, 2),
    changed_by INT NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- ============================================
-- 8. جدول الفواتير
-- ============================================
CREATE TABLE invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    store_id INT NOT NULL,
    cashier_id INT NOT NULL,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    customer_address TEXT,
    drawer_id INT,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    paid_amount DECIMAL(12, 2),
    remaining_amount DECIMAL(12, 2),
    payment_method ENUM('Cash', 'Card', 'Check', 'Other') DEFAULT 'Cash',
    status ENUM('Completed', 'Cancelled', 'Draft') DEFAULT 'Completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (cashier_id) REFERENCES users(id),
    INDEX idx_invoice_number (invoice_number),
    INDEX idx_invoice_date (invoice_date)
);

-- ============================================
-- 9. جدول بنود الفاتورة
-- ============================================
CREATE TABLE invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    total_price DECIMAL(12, 2) NOT NULL,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================
-- 10. جدول الطلبات (من Call Center)
-- ============================================
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_address TEXT,
    customer_city VARCHAR(50),
    source_store_id INT NOT NULL,
    destination_store_id INT,
    call_center_user_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_delivery_date DATETIME,
    total_amount DECIMAL(12, 2),
    status ENUM('Pending', 'Confirmed', 'Prepared', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (source_store_id) REFERENCES stores(id),
    FOREIGN KEY (destination_store_id) REFERENCES stores(id),
    FOREIGN KEY (call_center_user_id) REFERENCES users(id),
    INDEX idx_order_number (order_number),
    INDEX idx_order_status (status)
);

-- ============================================
-- 11. جدول بنود الطلب
-- ============================================
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(12, 2),
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================
-- 12. جدول الفواتير المؤقتة (درج الكاشير)
-- ============================================
CREATE TABLE temporary_invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    temp_invoice_code VARCHAR(50) NOT NULL UNIQUE,
    store_id INT NOT NULL,
    cashier_id INT NOT NULL,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    total_amount DECIMAL(12, 2),
    saved_by INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (cashier_id) REFERENCES users(id),
    FOREIGN KEY (saved_by) REFERENCES users(id)
);

-- ============================================
-- 13. جدول بنود الفواتير المؤقتة
-- ============================================
CREATE TABLE temporary_invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    temp_invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    total_price DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (temp_invoice_id) REFERENCES temporary_invoices(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================
-- 14. جدول تحويلات المخزن (بين الفروع)
-- ============================================
CREATE TABLE warehouse_transfers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transfer_number VARCHAR(50) NOT NULL UNIQUE,
    from_store_id INT NOT NULL,
    to_store_id INT NOT NULL,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    received_date DATETIME,
    created_by INT NOT NULL,
    received_by INT,
    status ENUM('Pending', 'In Transit', 'Received', 'Cancelled') DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (from_store_id) REFERENCES stores(id),
    FOREIGN KEY (to_store_id) REFERENCES stores(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (received_by) REFERENCES users(id),
    INDEX idx_transfer_status (status)
);

-- ============================================
-- 15. جدول بنود التحويل
-- ============================================
CREATE TABLE transfer_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transfer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity_sent INT NOT NULL,
    quantity_received INT,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transfer_id) REFERENCES warehouse_transfers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ============================================
-- 16. جدول سجل الدرج (الرصيد والإغلاق)
-- ============================================
CREATE TABLE drawer_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    store_id INT NOT NULL,
    cashier_id INT NOT NULL,
    opening_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    opening_balance DECIMAL(12, 2) DEFAULT 0,
    closing_date DATETIME,
    closing_balance DECIMAL(12, 2),
    status ENUM('Open', 'Closed') DEFAULT 'Open',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (cashier_id) REFERENCES users(id),
    INDEX idx_drawer_status (status)
);

-- ============================================
-- 17. جدول تفاصيل إغلاق الدرج (فئات النقود)
-- ============================================
CREATE TABLE drawer_closing_details (
    id INT PRIMARY KEY AUTO_INCREMENT,
    drawer_log_id INT NOT NULL,
    denomination VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drawer_log_id) REFERENCES drawer_logs(id) ON DELETE CASCADE
);

-- ============================================
-- 18. جدول سجل العمليات (Audit Log)
-- ============================================
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    table_name VARCHAR(100),
    record_id INT,
    old_values JSON,
    new_values JSON,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_action_date (action_date)
);

-- ============================================
-- المؤشرات المهمة للأداء
-- ============================================
CREATE INDEX idx_product_inventory_store ON product_inventory(store_id);
CREATE INDEX idx_product_inventory_product ON product_inventory(product_id);
CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_transfer_items_transfer ON transfer_items(transfer_id);

-- ============================================
-- Triggers لتحديث الأسعار تلقائياً
-- ============================================
DELIMITER $$

CREATE TRIGGER update_product_profit_margin
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
    SET NEW.profit_margin = ((NEW.sell_price - NEW.buy_price) / NEW.buy_price) * 100;
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

-- ============================================
-- Views مفيدة
-- ============================================

-- عرض المخزون الحالي
CREATE VIEW view_current_inventory AS
SELECT 
    pi.id,
    p.product_code,
    p.product_name,
    c.category_name,
    s.store_name,
    pi.quantity_in_stock,
    pi.minimum_quantity,
    p.sell_price,
    (pi.quantity_in_stock * p.sell_price) AS inventory_value,
    CASE 
        WHEN pi.quantity_in_stock <= pi.minimum_quantity THEN 'Low Stock'
        ELSE 'OK'
    END AS stock_status
FROM product_inventory pi
JOIN products p ON pi.product_id = p.id
JOIN stores s ON pi.store_id = s.id
JOIN categories c ON p.category_id = c.id
WHERE p.is_active = TRUE AND s.is_active = TRUE;

-- عرض المبيعات اليومية
CREATE VIEW view_daily_sales AS
SELECT 
    DATE(i.invoice_date) AS sale_date,
    s.store_name,
    COUNT(i.id) AS total_invoices,
    SUM(i.total_amount) AS total_sales,
    COUNT(DISTINCT i.cashier_id) AS cashiers
FROM invoices i
JOIN stores s ON i.store_id = s.id
WHERE i.status = 'Completed'
GROUP BY DATE(i.invoice_date), s.store_id
ORDER BY sale_date DESC;

-- عرض الطلبات المعلقة
CREATE VIEW view_pending_orders AS
SELECT 
    o.order_number,
    o.customer_name,
    o.customer_phone,
    s.store_name AS source_store,
    COUNT(oi.id) AS items_count,
    o.total_amount,
    o.order_date,
    o.status
FROM orders o
JOIN stores s ON o.source_store_id = s.id
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.status IN ('Pending', 'Confirmed')
GROUP BY o.id
ORDER BY o.order_date;

-- ============================================
-- تنويه: الخطوات التالية
-- ============================================
-- 1. أضف مستخدم إداري (admin) باستخدام bcrypt
-- 2. تأكد من تثبيت mysql-connector-python و bcrypt
-- 3. استخدم هذه البيانات في التطبيق PyQt6
