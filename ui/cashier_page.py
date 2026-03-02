"""
صفحة الكاشير (POS - Point of Sale)
Cashier Page - Invoice Creation and Management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QHeaderView, QGroupBox, QDialog, QScrollArea, QAbstractItemView, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QShortcut, QKeySequence
from database_manager import DatabaseManager
from datetime import datetime
from ui.styles import GLOBAL_STYLE, BUTTON_STYLES, get_button_style, COLORS, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER, LABEL_STYLE_TITLE, TAB_STYLE, PANEL_STYLE, TOTAL_DISPLAY_STYLE, ACTION_BUTTON_STYLE
from ui.call_center_orders_dialog import CallCenterOrdersDialog
from ui.held_bills_dialog import HeldBillsDialog
from ui.invoices_history_dialog import InvoicesHistoryDialog
from ui.product_inquiry_dialog import ProductInquiryDialog
from utils.printer_service import PrinterService

class CashierPage(QWidget):
    """صفحة الكاشير - إنشاء الفواتير"""
    sale_completed = pyqtSignal() # Signal for global refresh
    
    def __init__(self, user_info=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.db = DatabaseManager()
        self.user_info = user_info or {}
        self.invoice_items = []
        self.current_order_id = None # Track the order being fulfilled
        
        # إعداد منطقة التمرير
        self.main_scroll = QScrollArea()
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.main_scroll.setWidget(self.content_widget)
        
        # وضع منطقة التمرير في الليوت الأساسي
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_scroll)
        
        self.init_ui()
    
    def set_user(self, user_info):
        """تعيين بيانات المستخدم"""
        self.user_info = user_info or {}
    
    def init_ui(self):
        """إنشاء واجهة الصفحة بتصميم جديد (Split Layout)"""
        # Main Horizontal Layout
        main_layout = QHBoxLayout(self.content_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Left Panel (Products & Cart) ---
        self.create_left_panel()
        main_layout.addWidget(self.left_panel, 65) # 65% width
        
        # --- Right Panel (Controls & Payment) ---
        self.create_right_panel()
        main_layout.addWidget(self.right_panel, 35) # 35% width
        
        # Set focus to scan input initially
        self.scan_input.setFocus()
        
        # إعداد الاختصارات
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح لصفحة الكاشير"""
        # 1. التركيز على حقل البحث (Ctrl + F)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.scan_input.setFocus)
        
        # 2. إتمام البيع (F12)
        QShortcut(QKeySequence(Qt.Key.Key_F12), self).activated.connect(self.checkout)
        
        # 3. تعليق الفاتورة (Ctrl + S)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.hold_invoice)
        
        # 4. فتح الفواتير المعلقة (Ctrl + H)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.open_held_bills_dialog)
        
        # 5. فتح الطلبات (Ctrl + O)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_orders_dialog)
        
        # 6. استعلام عن صنف (Ctrl + I)
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(self.open_product_inquiry)
        
        # 7. حذف الصنف المحدد (Delete)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(self.remove_selected_item)

    def remove_selected_item(self):
        """حذف السطر المختار من جدول الفاتورة عبر اختصار الكيبورد"""
        current_row = self.invoice_table.currentRow()
        if current_row >= 0:
            self.remove_from_invoice(current_row)

    def create_left_panel(self):
        """إنشاء القسم الأيسر: شريط البحث وجدول الفاتورة"""
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        self.left_panel.setStyleSheet(PANEL_STYLE)
        
        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. Header Toolbar (Orders, History, etc.)
        toolbar_layout = QHBoxLayout()
        
        title = QLabel("📦 المنتجات")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()
        
        # Toolbar Buttons (Compact)
        btn_style = get_button_style('info') + "QPushButton { padding: 5px 15px; min-height: 35px; }"
        
        btns = [
            ("📦 الطلبات", self.open_orders_dialog, BUTTON_STYLES['warning']),
            ("⏸️ المعلقة", self.open_held_bills_dialog, BUTTON_STYLES['primary']),
            ("📜 السجل", self.open_history_dialog, BUTTON_STYLES['outline']),
            ("🔍 استعلام", self.open_product_inquiry, BUTTON_STYLES['info']),
        ]
        
        for text, slot, style_key in btns:
            btn = QPushButton(text)
            btn.setStyleSheet(style_key + "QPushButton { padding: 5px 15px; min-height: 35px; font-size: 13px; }")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            toolbar_layout.addWidget(btn)
            
        layout.addLayout(toolbar_layout)
        layout.addSpacing(10)
        
        # 2. Search/Scan Input
        scan_layout = QHBoxLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("🔍 باركود أو اسم المنتج (Enter)")
        self.scan_input.setFont(QFont("Arial", 14))
        self.scan_input.setStyleSheet(INPUT_STYLE + "min-height: 50px;")
        self.scan_input.returnPressed.connect(self.process_scan)
        scan_layout.addWidget(self.scan_input)
        
        scan_btn = QPushButton("إضافة")
        scan_btn.setStyleSheet(get_button_style("primary") + "min-height: 50px;")
        scan_btn.clicked.connect(self.process_scan)
        scan_layout.addWidget(scan_btn)
        
        layout.addLayout(scan_layout)
        layout.addSpacing(10)
        
        # 3. Invoice Table
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(6)
        self.invoice_table.setHorizontalHeaderLabels(["Code", "المنتج", "السعر", "الكمية", "الإجمالي", "حذف"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.invoice_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.invoice_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.invoice_table.setStyleSheet(TABLE_STYLE + "QTableWidget { border: none; }")
        self.invoice_table.verticalHeader().setDefaultSectionSize(60) # Taller rows for touch
        self.invoice_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.invoice_table)
        
        # 4. Item Count Footer
        self.items_count_label = QLabel("عدد الأصناف: 0")
        self.items_count_label.setStyleSheet("color: #94A3B8; font-weight: bold;")
        layout.addWidget(self.items_count_label, alignment=Qt.AlignmentFlag.AlignRight)

    def create_right_panel(self):
        """إنشاء القسم الأيمن: العميل، الدفع، والإجمالي"""
        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        self.right_panel.setStyleSheet(PANEL_STYLE)
        
        layout = QVBoxLayout(self.right_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 1. Customer Section (Top)
        customer_title = QLabel("👤 بيانات العميل")
        customer_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(customer_title)
        
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("📱 رقم الهاتف")
        self.customer_phone.setStyleSheet(INPUT_STYLE)
        self.customer_phone.textChanged.connect(self.on_phone_changed)
        layout.addWidget(self.customer_phone)
        
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("👤 اسم العميل")
        self.customer_name.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.customer_name)
        
        self.customer_address = QLineEdit()
        self.customer_address.setPlaceholderText("📍 العنوان")
        self.customer_address.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.customer_address)
        
        layout.addSpacing(10)
        
        # 2. Payment Section (Middle)
        pay_title = QLabel("💳 تفاصيل الدفع")
        pay_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(pay_title)
        
        # Discount
        disc_layout = QHBoxLayout()
        disc_layout.addWidget(QLabel("الخصم:"))
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(10000)
        self.discount_input.setStyleSheet(INPUT_STYLE)
        self.discount_input.valueChanged.connect(self.calculate_total)
        disc_layout.addWidget(self.discount_input)
        layout.addLayout(disc_layout)
        
        # Method
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash (كاش)", "Visa (فيزا)", "Credit (آجل)", "Mixed (دفع مختلط)"])
        self.payment_combo.setStyleSheet(INPUT_STYLE + "min-height: 45px;")
        self.payment_combo.currentIndexChanged.connect(self.toggle_payment_inputs)
        layout.addWidget(self.payment_combo)
        
        # Split inputs (Hidden)
        self.split_payment_widget = QWidget()
        split_layout = QVBoxLayout(self.split_payment_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        self.cash_amount_input = QDoubleSpinBox()
        self.cash_amount_input.setPrefix("نقدًا: ")
        self.cash_amount_input.setMaximum(1000000)
        self.cash_amount_input.setStyleSheet(INPUT_STYLE)
        self.card_amount_input = QDoubleSpinBox()
        self.card_amount_input.setPrefix("فيزا: ")
        self.card_amount_input.setMaximum(1000000)
        self.card_amount_input.setStyleSheet(INPUT_STYLE)
        split_layout.addWidget(self.cash_amount_input)
        split_layout.addWidget(self.card_amount_input)
        self.split_payment_widget.hide()
        layout.addWidget(self.split_payment_widget)
        
        layout.addStretch()
        
        # 3. Totals (Huge)
        self.total_label = QLabel("0.00 ج.م")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.total_label.setStyleSheet(TOTAL_DISPLAY_STYLE)
        layout.addWidget(self.total_label)
        
        # 3.5 Paid Amount & Change
        paid_layout = QHBoxLayout()
        paid_layout.addWidget(QLabel("💵 المبلغ المدفوع:"))
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setMaximum(1000000)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setStyleSheet(INPUT_STYLE + "min-height: 40px; font-size: 14px;")
        self.paid_amount_input.valueChanged.connect(self.calculate_change)
        paid_layout.addWidget(self.paid_amount_input)
        layout.addLayout(paid_layout)
        
        self.change_label = QLabel("الباقي: 0.00 ج.م")
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.change_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.change_label.setStyleSheet("color: #10B981; padding: 5px; background-color: #1E293B; border-radius: 8px;")
        layout.addWidget(self.change_label)
        
        # 4. Action Buttons (Bottom)
        btns_layout = QVBoxLayout()
        btns_layout.setSpacing(10)
        
        checkout_btn = QPushButton("✅ دفع وطباعة (F12)")
        checkout_btn.setMinimumHeight(60)
        checkout_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        checkout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        checkout_btn.setStyleSheet(get_button_style('success') + "border-radius: 12px;")
        checkout_btn.clicked.connect(lambda: self.checkout(as_pdf=False))
        btns_layout.addWidget(checkout_btn)
        
        checkout_pdf_btn = QPushButton("📄 دفع وحفظ PDF")
        checkout_pdf_btn.setMinimumHeight(50)
        checkout_pdf_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        checkout_pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        checkout_pdf_btn.setStyleSheet("background-color: #607D8B; color: white; border-radius: 12px; padding: 5px;")
        checkout_pdf_btn.clicked.connect(lambda: self.checkout(as_pdf=True))
        btns_layout.addWidget(checkout_pdf_btn)
        
        sub_actions_layout = QHBoxLayout()
        
        hold_btn = QPushButton("⏸️ تعليق")
        hold_btn.setMinimumHeight(50)
        hold_btn.setStyleSheet(get_button_style('warning'))
        hold_btn.clicked.connect(self.hold_invoice)
        sub_actions_layout.addWidget(hold_btn)
        
        clear_btn = QPushButton("🗑️ مسح")
        clear_btn.setMinimumHeight(50)
        clear_btn.setStyleSheet(get_button_style('danger'))
        clear_btn.clicked.connect(self.clear_invoice)
        sub_actions_layout.addWidget(clear_btn)
        
        btns_layout.addLayout(sub_actions_layout)
        layout.addLayout(btns_layout)

    
    def refresh_page(self):
        """تحديث وتنشيط صفحة الكاشير"""
        self.setEnabled(True)
        self.content_widget.setEnabled(True)
        self.scan_input.setFocus()
        self.update_invoice_table()
        self.calculate_total()
        self.update()
    
    def search_product(self):
        """البحث عن المنتجات"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            QMessageBox.warning(self, "تنبيه", "أدخل رمز أو اسم المنتج")
            return
        
        try:
            # البحث في قاعدة البيانات
            cursor = self.db.cursor
            query = """
                SELECT id, product_code, product_name, sell_price 
                FROM products 
                WHERE product_code LIKE %s OR product_name LIKE %s
            """
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            products = cursor.fetchall()
            
            if not products:
                QMessageBox.information(self, "النتيجة", "لم يتم العثور على منتجات")
                self.products_table.setRowCount(0)
                return
            
            self.products_table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # رمز المنتج
                self.products_table.setItem(row, 0, QTableWidgetItem(product['product_code']))
                
                # اسم المنتج
                self.products_table.setItem(row, 1, QTableWidgetItem(product['product_name']))
                
                # السعر
                price = product['sell_price']
                self.products_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
                
                # الكمية المتاحة
                quantity = self.get_product_quantity(product['id'])
                self.products_table.setItem(row, 3, QTableWidgetItem(str(quantity)))
                
                # زر الإضافة
                add_btn = QPushButton("إضافة")
                add_btn.clicked.connect(
                    lambda checked, p_id=product['id'], p_code=product['product_code'],
                    p_name=product['product_name'], p_price=price: 
                    self.add_to_invoice(p_id, p_code, p_name, p_price)
                )
                self.products_table.setCellWidget(row, 4, add_btn)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في البحث: {str(e)}")
    
    def process_scan(self):
        """Handle product code scan"""
        code = self.scan_input.text().strip()
        if not code:
            return
            
        product = self.db.get_product_by_code(code)
        if not product:
            # Try barcode
            product = self.db.get_product_by_barcode(code)
            
        if product:
            self.add_to_invoice(product['id'], product['product_code'], 
                              product['product_name'], product['sell_price'])
            self.scan_input.clear()
        else:
            QMessageBox.warning(self, "خطأ", "المنتج غير موجود")
            self.scan_input.selectAll()

    def on_phone_changed(self):
        """Auto-fill customer data when phone number is entered"""
        phone = self.customer_phone.text().strip()
        
        # Only search if phone number is 11 digits (Egyptian phone number format)
        if len(phone) == 11 and phone.isdigit():
            customer_data = self.db.get_customer_by_phone(phone)
            
            if customer_data:
                # Only fill if the fields are empty or was just auto-filled (to avoid annoying overrides)
                if not self.customer_name.text() or self.customer_name.property("auto_filled"):
                    self.customer_name.setText(customer_data.get('customer_name', ''))
                    self.customer_name.setProperty("auto_filled", True)
                    # Add visual feedback
                    self.customer_name.setStyleSheet(INPUT_STYLE + "border-left: 3px solid #10B981;")
                
                if not self.customer_address.text() or self.customer_address.property("auto_filled"):
                    self.customer_address.setText(customer_data.get('customer_address', ''))
                    self.customer_address.setProperty("auto_filled", True)
                    # Add visual feedback
                    self.customer_address.setStyleSheet(INPUT_STYLE + "border-left: 3px solid #10B981;")
            else:
                # Reset styling/properties if no customer found
                self.customer_name.setProperty("auto_filled", False)
                self.customer_address.setProperty("auto_filled", False)
                self.customer_name.setStyleSheet(INPUT_STYLE)
                self.customer_address.setStyleSheet(INPUT_STYLE)
        else:
            # Reset styling when phone is incomplete
            self.customer_name.setProperty("auto_filled", False)
            self.customer_address.setProperty("auto_filled", False)
            self.customer_name.setStyleSheet(INPUT_STYLE)
            self.customer_address.setStyleSheet(INPUT_STYLE)

    def open_orders_dialog(self):
        """Open Call Center Orders List"""
        dialog = CallCenterOrdersDialog(self.db, self.user_info.get('store_id', 1), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            order = dialog.selected_order
            if order:
                self.load_order(order)

    def load_order(self, order):
        """Load Call Center Order Items"""
        self.clear_invoice()
        # Fill Customer Data if available
        self.current_order_id = order.get('id')
        self.customer_name.setText(order.get('customer_name', ''))
        self.customer_phone.setText(order.get('customer_phone', ''))
        self.customer_address.setText(order.get('customer_address', ''))
        
        items = self.db.get_order_details(order['id'])
        for item in items:
            self.invoice_items.append({
                'product_id': item['product_id'],
                'product_code': item['product_code'],
                'product_name': item['product_name'],
                'price': item['unit_price'],
                'quantity': item['quantity']
            })
        
        self.update_invoice_table()
        QMessageBox.information(self, "نجاح", "تم تحميل الطلب بنجاح")

    def open_held_bills_dialog(self):
        """Open Held Bills List"""
        dialog = HeldBillsDialog(self.db, self.user_info.get('store_id', 1), self.user_info, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            bill = dialog.selected_bill
            if bill:
                self.load_held_bill(bill)

    def open_product_inquiry(self):
        """فتح نافذة الاستعلام عن الأصناف"""
        dialog = ProductInquiryDialog(
            self.db, 
            self.user_info.get('store_id', 1),
            self
        )
        dialog.exec()

    def toggle_payment_inputs(self):
        """إظهار/إخفاء حقول الدفع المختلط وتعيين القيم الافتراضية"""
        method = self.payment_combo.currentText()
        total_str = self.total_label.text().split()[0]
        try:
            total = float(total_str)
        except:
            total = 0.0
            
        if "Mixed" in method:
            self.split_payment_widget.show()
            self.cash_amount_input.setValue(total)
            self.card_amount_input.setValue(0)
        elif "Credit" in method or "آجل" in method:
            self.split_payment_widget.hide()
            self.paid_amount_input.setValue(0)
        elif "Visa" in method:
            self.split_payment_widget.hide()
            self.paid_amount_input.setValue(total)
        else: # Cash
            self.split_payment_widget.hide()
            self.paid_amount_input.setValue(total)

    def open_history_dialog(self):
        """Open Invoices History"""
        dialog = InvoicesHistoryDialog(self.db, self.user_info, self)
        dialog.exec()

    def load_held_bill(self, bill):
        """Resume a held bill"""
        self.clear_invoice()
        self.customer_name.setText(bill.get('customer_name', ''))
        self.customer_phone.setText(bill.get('customer_phone', ''))
        self.customer_address.setText(bill.get('customer_address', ''))
        
        items = self.db.get_held_invoice_items(bill['id'])
        for item in items:
            self.invoice_items.append({
                'product_id': item['product_id'],
                'product_code': item['product_code'],
                'product_name': item['product_name'],
                'price': item['current_price'], # Use current price or saved price? Usually current for fresh billing
                'quantity': item['quantity']
            })
        
        # Delete the held bill after loading it (it will be created new if held again)
        self.db.delete_held_invoice(bill['id'])
        self.update_invoice_table()
        QMessageBox.information(self, "استكمال", "تم استرجاع الفاتورة المعلقة")
    
    def add_to_invoice(self, product_id, product_code, product_name, price):
        """إضافة منتج إلى الفاتورة"""
        # البحث عن المنتج في الفاتورة إن كان موجوداً
        for i, item in enumerate(self.invoice_items):
            if item['product_id'] == product_id:
                # زيادة الكمية
                item['quantity'] += 1
                self.update_invoice_table()
                return
        
        # إضافة منتج جديد
        self.invoice_items.append({
            'product_id': product_id,
            'product_code': product_code,
            'product_name': product_name,
            'price': price,
            'quantity': 1
        })
        
        self.update_invoice_table()
    
    def update_invoice_table(self):
        """تحديث جدول الفاتورة"""
        self.invoice_table.setRowCount(len(self.invoice_items))
        
        for row, item in enumerate(self.invoice_items):
            # الرمز
            self.invoice_table.setItem(row, 0, QTableWidgetItem(item['product_code']))
            
            # الاسم
            self.invoice_table.setItem(row, 1, QTableWidgetItem(item['product_name']))
            
            # السعر
            self.invoice_table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            
            # الكمية (قابل للتعديل)
            qty_spinbox = QSpinBox()
            qty_spinbox.setMinimum(1)
            qty_spinbox.setValue(item['quantity'])
            qty_spinbox.valueChanged.connect(
                lambda val, idx=row: self.update_quantity(idx, val)
            )
            self.invoice_table.setCellWidget(row, 3, qty_spinbox)
            
            # الإجمالي
            total = item['price'] * item['quantity']
            self.invoice_table.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))
            
            # زر الحذف
            del_btn = QPushButton("حذف")
            del_btn.clicked.connect(lambda checked, idx=row: self.remove_from_invoice(idx))
            self.invoice_table.setCellWidget(row, 5, del_btn)
        
        self.calculate_total()
    
    def update_quantity(self, row, value):
        """تحديث كمية المنتج"""
        if row < len(self.invoice_items):
            self.invoice_items[row]['quantity'] = value
            self.update_invoice_table()
    
    def remove_from_invoice(self, row):
        """إزالة منتج من الفاتورة"""
        if row < len(self.invoice_items):
            self.invoice_items.pop(row)
            self.update_invoice_table()
    
    def calculate_total(self):
        """حساب الإجمالي"""
        subtotal = float(sum(item['price'] * item['quantity'] for item in self.invoice_items))
        discount = self.discount_input.value()
        total = subtotal - discount
        
        self.total_label.setText(f"{total:.2f} ج.م")
        self.calculate_change()
    
    def calculate_change(self):
        """حساب الباقي من المبلغ المدفوع"""
        try:
            total = float(self.total_label.text().split()[0])
            paid = self.paid_amount_input.value()
            change = paid - total
            
            if paid == 0:
                self.change_label.setText("الباقي: 0.00 ج.م")
                self.change_label.setStyleSheet("color: #94A3B8; padding: 5px; background-color: #1E293B; border-radius: 8px;")
            elif change >= 0:
                self.change_label.setText(f"الباقي: {change:.2f} ج.م")
                self.change_label.setStyleSheet("color: #10B981; padding: 5px; background-color: #1E293B; border-radius: 8px;")
            else:
                self.change_label.setText(f"المتبقي على العميل: {abs(change):.2f} ج.م")
                self.change_label.setStyleSheet("color: #EF4444; padding: 5px; background-color: #1E293B; border-radius: 8px;")
        except:
            pass
    
    def hold_invoice(self):
        """Save invoice significantly to temporary_invoices"""
        if not self.invoice_items:
            QMessageBox.warning(self, "تنبيه", "الفاتورة فارغة")
            return
            
        if self.db.save_held_invoice(
            store_id=self.user_info.get('store_id', 1),
            cashier_id=self.user_info.get('id', 1),
            items=self.invoice_items,
            customer_name=self.customer_name.text(),
            customer_phone=self.customer_phone.text(),
            customer_address=self.customer_address.text()
        ):
            QMessageBox.information(self, "تم", "تم تعليق الفاتورة بنجاح")
            self.clear_invoice()
        else:
            QMessageBox.critical(self, "خطأ", "فشل تعليق الفاتورة")
    
    def checkout(self, as_pdf=False):
        """Finalize Sale and Print (or Save as PDF)"""
        if not self.invoice_items:
            QMessageBox.warning(self, "تنبيه", "الفاتورة فارغة")
            return
        
        try:
            payment_method = self.payment_combo.currentText()
            total_amount = float(self.total_label.text().split()[0])
            
            cash_amount = 0
            card_amount = 0
            db_method = 'Cash'
            
            if "Mixed" in payment_method:
                cash_amount = self.cash_amount_input.value()
                card_amount = self.card_amount_input.value()
                db_method = 'Mixed'
                
                # التحقق من أن المجموع صحيح
                if abs((cash_amount + card_amount) - total_amount) > 0.01:
                    QMessageBox.warning(self, "تنبيه", 
                        f"مجموع المبالغ ({cash_amount + card_amount:.2f}) لا يساوي الإجمالي ({total_amount:.2f})")
                    return
            elif "Visa" in payment_method:
                card_amount = total_amount
                cash_amount = 0
                db_method = 'Card'
            elif "Credit" in payment_method or "آجل" in payment_method:
                cash_amount = self.paid_amount_input.value()
                card_amount = 0
                db_method = 'Credit'
            else:
                # Cash - Default to what is in paid_amount_input (capped at total)
                cash_amount = min(self.paid_amount_input.value(), total_amount)
                card_amount = 0
                db_method = 'Cash'

            # Strict Validation: Prevent accidental debt (Lazy entry protection)
            paid_total = cash_amount + card_amount
            if db_method != 'Credit' and paid_total < total_amount - 0.01:
                QMessageBox.warning(self, "تحذير: دفع غير مكتمل", 
                    f"المبلغ المدفوع ({paid_total:.2f}) أقل من إجمالي الفاتورة ({total_amount:.2f}).\n\n"
                    "لتسجيل المبلغ المتبقي كدين على العميل، يرجى اختيار وسيلة الدفع 'Credit (آجل)' أولاً.")
                return
            
            # Get current drawer
            drawer = self.db.get_drawer_status(self.user_info.get('id', 1))
            drawer_id = None
            drawer_owner_name = self.user_info.get('name', 'Cashier')
            
            if drawer and drawer.get('is_open'):
                drawer_id = drawer.get('id')
            else:
                # Check for ANY open drawer in the SAME branch (For all roles now)
                store_id = self.user_info.get('store_id', 1)
                store_drawer = self.db.get_store_open_drawer(store_id)
                if store_drawer:
                    drawer_id = store_drawer['id']
                    drawer_owner_name = store_drawer['cashier_name']
                else:
                    # Block checkout if no drawer found in the branch
                    QMessageBox.warning(self, "تنبيه", 
                        "لا يوجد درج كاشير مفتوح في هذا الفرع!\n"
                        "يجب فتح درج كاشير أولاً قبل إتمام عملية البيع.")
                    return

            # Check Credit Limit (Advanced)
            if self.customer_phone.text():
                # Get customer ID temporarily to check limit
                self.db.cursor.execute("SELECT id FROM customers WHERE phone = %s", (self.customer_phone.text(),))
                cust_res = self.db.cursor.fetchone()
                if cust_res:
                    paid_so_far = cash_amount + card_amount
                    debt_amount = total_amount - paid_so_far
                    if debt_amount > 0:
                        is_allowed, msg = self.db.check_credit_limit(cust_res['id'], debt_amount)
                        if not is_allowed:
                            QMessageBox.critical(self, "خطأ: تجاوز الحد الائتماني", msg)
                            return

            invoice = self.db.create_invoice(
                store_id=self.user_info.get('store_id', 1),
                cashier_id=self.user_info.get('id', 1),
                customer_name=self.customer_name.text() or "Cash Customer",
                customer_phone=self.customer_phone.text(),
                customer_address=self.customer_address.text(),
                drawer_id=drawer_id,
                payment_method=db_method,
                cash_amount=cash_amount,
                card_amount=card_amount
            )
            
            if invoice:
                # Add Items
                for item in self.invoice_items:
                    self.db.add_invoice_item(
                        invoice_number=invoice,
                        product_id=item['product_id'],
                        quantity=item['quantity'],
                        unit_price=item['price'],
                        discount=0
                    )
                    # Update Inventory
                    self.db.update_inventory(
                        product_id=item['product_id'],
                        store_id=self.user_info.get('store_id', 1),
                        quantity=item['quantity'],
                        operation='subtract'
                    )
            
                # Finalize for Accounts (Record debt if any)
                self.db.finalize_invoice(invoice, self.user_info.get('id', 1))

                # If this was a Call Center order, mark it as Delivered
                if self.current_order_id:
                    self.db.update_order_status(self.current_order_id, 'Delivered')
                    print(f"✅ تم تحديث حالة الطلب {self.current_order_id} إلى منفذ")

                # PRINTING
                invoice_data = {
                    'invoice_number': invoice,
                    'customer_name': self.customer_name.text(),
                    'customer_phone': self.customer_phone.text(),
                    'customer_address': self.customer_address.text(),
                    'drawer_id': drawer_id,
                    'payment_method': db_method,
                    'cash_amount': cash_amount,
                    'card_amount': card_amount,
                    'total_amount': total_amount,
                'subtotal': sum(i['price']*i['quantity'] for i in self.invoice_items),
                    'discount': self.discount_input.value(),
                    'tendered': self.paid_amount_input.value(),
                    'change': max(0, self.paid_amount_input.value() - total_amount) if self.paid_amount_input.value() > 0 else 0
                }
                
                if as_pdf:
                    PrinterService.save_receipt_as_pdf(
                        invoice_data, 
                        self.invoice_items, 
                        drawer_owner_name, 
                        self.user_info.get('store_name', 'Store')
                    )
                else:
                    PrinterService.print_receipt(
                        invoice_data, 
                        self.invoice_items, 
                        drawer_owner_name, 
                        self.user_info.get('store_name', 'Store')
                    )
                
                QMessageBox.information(self, "نجاح", f"تم حفظ الفاتورة #{invoice} بنجاح")
                if self.parent and hasattr(self.parent, 'refresh_all_data'):
                    self.parent.refresh_all_data()
                
                self.sale_completed.emit()
                self.clear_invoice()
            else:
                QMessageBox.critical(self, "خطأ", "فشل إنشاء الفاتورة")
        
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ: {str(e)}")
    
    def clear_invoice(self):
        """مسح الفاتورة"""
        self.invoice_items = []
        self.current_order_id = None
        self.scan_input.clear()
        self.customer_name.clear()
        self.customer_phone.clear()
        self.invoice_table.setRowCount(0)
        self.discount_input.setValue(0)
        self.paid_amount_input.setValue(0)
        self.change_label.setText("الباقي: 0.00 ج.م")
        self.change_label.setStyleSheet("color: #94A3B8; padding: 5px; background-color: #1E293B; border-radius: 8px;")
        self.payment_combo.setCurrentIndex(0)
        self.total_label.setText("0.00 ج.م")
        self.scan_input.setFocus()
