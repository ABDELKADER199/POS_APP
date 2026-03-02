-- ============================================
-- Migration: إضافة جداول نظام التحكم في الوصول
-- ============================================

USE stocks;

-- ============================================
-- 1. جدول الأجهزة المصرح بها
-- ============================================
CREATE TABLE IF NOT EXISTS authorized_devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(255) NOT NULL UNIQUE,
    device_name VARCHAR(100),
    mac_address VARCHAR(50),
    store_id INT,
    user_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    registered_by INT,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (registered_by) REFERENCES users(id),
    INDEX idx_device_id (device_id),
    INDEX idx_store_user (store_id, user_id),
    INDEX idx_active (is_active)
);

-- ============================================
-- 2. إضافة حقول نطاق IP لجدول الفروع
-- ============================================
ALTER TABLE stores 
ADD COLUMN IF NOT EXISTS ip_range_start VARCHAR(15),
ADD COLUMN IF NOT EXISTS ip_range_end VARCHAR(15),
ADD COLUMN IF NOT EXISTS require_ip_check BOOLEAN DEFAULT TRUE;

-- ============================================
-- 3. جدول سجل محاولات تسجيل الدخول
-- ============================================
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_email VARCHAR(100),
    user_id INT,
    device_id VARCHAR(255),
    device_name VARCHAR(100),
    ip_address VARCHAR(45),
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    failure_reason VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_time (user_email, attempt_time),
    INDEX idx_success (success),
    INDEX idx_device (device_id)
);

-- ============================================
-- 4. تحديث بيانات الفروع الموجودة
-- ============================================

-- فرع الإسكندرية - نطاق IP: 192.168.1.x
UPDATE stores 
SET ip_range_start = '192.168.1.0', 
    ip_range_end = '192.168.1.255',
    require_ip_check = TRUE
WHERE store_name = 'فرع الإسكندرية';

-- فرع الجيزة - نطاق IP: 192.168.2.x
UPDATE stores 
SET ip_range_start = '192.168.2.0', 
    ip_range_end = '192.168.2.255',
    require_ip_check = TRUE
WHERE store_name = 'فرع الجيزة';

-- المخزن الرئيسي - نطاق IP: 192.168.3.x
UPDATE stores 
SET ip_range_start = '192.168.3.0', 
    ip_range_end = '192.168.3.255',
    require_ip_check = TRUE
WHERE store_name = 'المخزن الرئيسي';

-- مدير عام - لا يحتاج فحص IP
UPDATE stores 
SET require_ip_check = FALSE
WHERE store_name = 'مدير عام' OR store_type = 'GM';

-- ============================================
-- ملاحظات:
-- ============================================
-- 1. يمكن تعديل نطاقات IP حسب شبكة كل فرع
-- 2. المدير العام معفي من فحص IP
-- 3. يمكن تفعيل/تعطيل فحص IP لكل فرع
