# 📊 توثيق قاعدة البيانات - نظام POS

## 📋 الجداول الرئيسية

### 1️⃣ **جدول الأدوار (roles)**
```
- id: معرف فريد
- role_name: اسم الدور (admin, manager, cashier, call_center, warehouse_staff)
- description: وصف الدور
```

### 2️⃣ **جدول الفروع والمخازن (stores)**
```
- id: معرف فريد
- store_name: اسم الفرع
- store_type: نوع الفرع (Main/Branch/Warehouse)
- city: المدينة
- address: العنوان
- phone: الهاتف
- email: البريد
- manager_name: اسم المدير
- is_active: حالة التفعيل
```

### 3️⃣ **جدول المستخدمين (users)**
```
- id: معرف فريد
- name: الاسم الكامل
- email: البريد الإلكتروني (فريد)
- password: كلمة المرور (مشفرة بـ bcrypt)
- phone: رقم الهاتف
- role_id: معرف الدور (FK -> roles)
- store_id: معرف الفرع (FK -> stores)
- is_active: حالة التفعيل
- last_login: آخر دخول
- created_by: من أنشأ الحساب
```

### 4️⃣ **جدول الفئات (categories)**
```
- id: معرف فريد
- category_name: اسم الفئة
- description: وصف الفئة
- is_active: حالة التفعيل
```

### 5️⃣ **جدول المنتجات (products)**
```
- id: معرف فريد
- product_code: كود المنتج (فريد)
- product_name: اسم المنتج
- category_id: معرف الفئة (FK -> categories)
- buy_price: سعر الشراء
- sell_price: سعر البيع
- profit_margin: هامش الربح (يتم حسابه تلقائياً)
- unit: وحدة القياس
- barcode: الباركود
- description: الوصف
- image_path: مسار الصورة
- is_active: حالة التفعيل
```

### 6️⃣ **جدول مخزون المنتجات (product_inventory)**
```
- id: معرف فريد
- product_id: معرف المنتج (FK -> products)
- store_id: معرف الفرع (FK -> stores)
- quantity_in_stock: الكمية الحالية
- minimum_quantity: الحد الأدنى للكمية
- last_count_date: تاريخ آخر جرد
- last_counted_by: من قام بآخر جرد
- UNIQUE: product_id + store_id (كل منتج له كمية واحدة في كل فرع)
```

### 7️⃣ **جدول سجل الأسعار (price_history)**
```
- id: معرف فريد
- product_id: معرف المنتج
- old_buy_price: السعر القديم للشراء
- new_buy_price: السعر الجديد للشراء
- old_sell_price: السعر القديم للبيع
- new_sell_price: السعر الجديد للبيع
- changed_by: من قام بالتغيير
- change_date: تاريخ التغيير
- notes: ملاحظات
```

### 8️⃣ **جدول الفواتير (invoices)**
```
- id: معرف فريد
- invoice_number: رقم الفاتورة (فريد)
- store_id: معرف الفرع
- cashier_id: معرف الكاشير
- customer_name: اسم العميل
- customer_phone: هاتف العميل
- invoice_date: تاريخ الفاتورة
- total_amount: المجموع الكلي
- paid_amount: المبلغ المدفوع
- remaining_amount: المبلغ المتبقي
- payment_method: طريقة الدفع
- status: حالة الفاتورة (Completed/Cancelled/Draft)
```

### 9️⃣ **جدول بنود الفاتورة (invoice_items)**
```
- id: معرف فريد
- invoice_id: معرف الفاتورة (FK -> invoices)
- product_id: معرف المنتج (FK -> products)
- quantity: الكمية
- unit_price: سعر الوحدة
- discount: الخصم
- total_price: السعر الكلي (يتم حسابه تلقائياً)
```

### 🔟 **جدول الطلبات من Call Center (orders)**
```
- id: معرف فريد
- order_number: رقم الطلب (فريد)
- customer_name: اسم العميل
- customer_phone: هاتف العميل
- customer_address: عنوان العميل
- customer_city: مدينة العميل
- source_store_id: الفرع المصدر
- destination_store_id: الفرع المقصد
- call_center_user_id: موظف Call Center
- order_date: تاريخ الطلب
- expected_delivery_date: تاريخ التسليم المتوقع
- total_amount: المجموع الكلي
- status: حالة الطلب (Pending/Confirmed/Prepared/Delivered/Cancelled)
```

### 1️⃣1️⃣ **جدول بنود الطلب (order_items)**
```
- id: معرف فريد
- order_id: معرف الطلب (FK -> orders)
- product_id: معرف المنتج (FK -> products)
- quantity: الكمية
- unit_price: سعر الوحدة
- total_price: السعر الكلي
```

### 1️⃣2️⃣ **جدول الفواتير المؤقتة (temporary_invoices)**
```
- id: معرف فريد
- temp_invoice_code: كود الفاتورة المؤقتة
- store_id: معرف الفرع
- cashier_id: معرف الكاشير
- customer_name: اسم العميل
- total_amount: المجموع الكلي
- saved_by: من قام بالحفظ
- notes: ملاحظات
```

### 1️⃣3️⃣ **جدول تحويلات المخزن (warehouse_transfers)**
```
- id: معرف فريد
- transfer_number: رقم التحويل
- from_store_id: الفرع المصدر
- to_store_id: الفرع المقصد
- transfer_date: تاريخ التحويل
- received_date: تاريخ الاستقبال
- created_by: من أنشأ التحويل
- received_by: من استقبل التحويل
- status: حالة التحويل (Pending/In Transit/Received/Cancelled)
```

### 1️⃣4️⃣ **جدول سجل الدرج (drawer_logs)**
```
- id: معرف فريد
- store_id: معرف الفرع
- cashier_id: معرف الكاشير
- opening_date: تاريخ فتح الدرج
- opening_balance: الرصيد الأول
- closing_date: تاريخ إغلاق الدرج
- closing_balance: الرصيد النهائي
- status: حالة الدرج (Open/Closed)
```

### 1️⃣5️⃣ **جدول تفاصيل إغلاق الدرج (drawer_closing_details)**
```
- id: معرف فريد
- drawer_log_id: معرف سجل الدرج
- denomination: فئة النقد (200ج, 100ج, 50ج, 20ج, 10ج, 5ج, 1ج, 0.5ج)
- quantity: عدد العملات/الأوراق
- total_amount: المجموع (الكمية × الفئة)
```

---

## 🔄 العلاقات بين الجداول

```
┌─────────────┐
│   roles     │
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────────┐
│     users       │ (كل مستخدم له دور واحد)
└─────────────────┘
       │ N:1
       └──────┬──────────────┐
              │              │
         ┌────▼────┐    ┌───▼────┐
         │ invoices │    │ orders │
         └──────────┘    └────────┘

┌──────────────┐
│   products   │
└──────┬───────┘
       │ 1:N
       │
┌──────▼────────────────┐
│ product_inventory     │
└──────┬────────────────┘
       │ 1:N
       └──── stores (M:N relationship)

```

---

## 📊 Views (الآراء) المفيدة

### 1. **view_current_inventory**
عرض شامل للمخزون الحالي مع حالة الكمية

### 2. **view_daily_sales**
عرض المبيعات اليومية حسب الفرع

### 3. **view_pending_orders**
عرض الطلبات المعلقة والمؤكدة

---

## ⚙️ Triggers (المشغلات) التلقائية

### 1. **update_product_profit_margin**
يحسب هامش الربح تلقائياً عند تحديث أسعار المنتج

### 2. **calculate_invoice_item_total**
يحسب إجمالي بند الفاتورة تلقائياً

### 3. **calculate_invoice_total**
يحسب إجمالي الفاتورة تلقائياً عند إضافة بند

---

## 🔐 الأمان

- جميع كلمات المرور مشفرة بـ **bcrypt**
- كل جدول به **timestamps** للمراجعة
- وجود **audit_logs** لتتبع جميع العمليات
- استخدام **Foreign Keys** لضمان تكامل البيانات
- **Indexes** على الحقول المهمة للأداء السريع

---

## 🚀 كيفية التشغيل

### الخطوة 1: تشغيل برنامج الإعداد
```bash
python setup_database.py
```

### الخطوة 2: سيطلب منك:
- اسم المدير
- البريد الإلكتروني
- كلمة المرور
- رقم الهاتف

### الخطوة 3: ستجد:
✅ جميع الجداول تم إنشاؤها  
✅ البيانات الأساسية تم إدراجها  
✅ أول مدير تم إنشاؤه  
✅ قاعدة البيانات جاهزة للعمل

---

## 📝 ملاحظات مهمة

1. **الباركود**: اختياري لكل منتج، يمكن استخدام QR code أو barcode
2. **الفئات الافتراضية**: تم إدراج 5 فئات أساسية (يمكن إضافة المزيد)
3. **الفروع الافتراضية**: المخزن الرئيسي + فرعين (يمكن تعديلها)
4. **الدور الافتراضي**: تم إنشاء 5 أدوار أساسية
5. **فئات النقود**: 200, 100, 50, 20, 10, 5, 1, 0.5 جنيه

---

## 🔗 الخطوة التالية

الآن يمكنك:
1. إنشاء واجهة إضافة المنتجات من Excel
2. بناء صفحة الكاشير
3. بناء نظام Call Center
4. وغيرها...

جميع الجداول جاهزة والعلاقات محددة ✅
