"""
صفحة Call Center - إدارة أوامر العملاء
Call Center Page - Customer Order Management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QSpinBox, QTextEdit, QHeaderView,
    QTabWidget, QGroupBox, QFrame, QSplitter, QScrollArea, QGridLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime

from database_manager import DatabaseManager
from ui.styles import (
    GLOBAL_STYLE, BUTTON_STYLES, get_button_style,
    COLORS, TABLE_STYLE, GROUP_BOX_STYLE,
    INPUT_STYLE, LABEL_STYLE_HEADER,
    LABEL_STYLE_TITLE, TAB_STYLE, get_icon_button_style
)


class CallCenterPage(QWidget):
    """صفحة Call Center - إدارة أوامر العملاء"""

    def __init__(self, user_info=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.db = DatabaseManager()
        self.user_info = user_info or {}
        
        # مؤقت البحث (Debounce)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.search_products)
        
        self.init_ui()

    def set_user(self, user_info):
        self.user_info = user_info or {}
        self.load_stores()
        self.load_orders()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("☎️ Call Center - إدارة الأوامر")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_new_order_tab(), "أمر جديد")
        self.tabs.addTab(self.create_pending_orders_tab(), "الأوامر المعلقة")
        self.tabs.addTab(self.create_completed_orders_tab(), "الأوامر المنجزة")

        # لف علامات التبويب في ScrollArea للحماية من الاختفاء في الشاشات الصغيرة
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.tabs)
        layout.addWidget(scroll)
        self.setLayout(layout)

    # ================== Customer ==================
    def create_customer_group(self):
        """إنشاء مجموعة بيانات العميل بتنسيق عمودي للشريط الجانبي"""
        group = QGroupBox("📋 بيانات العميل")
        group.setStyleSheet(GROUP_BOX_STYLE)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 20)

        # الهاتف أولاً (لأنه يملأ البيانات تلقائياً)
        layout.addWidget(QLabel("رقم الهاتف:"))
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("01xxxxxxxxx")
        self.customer_phone.setStyleSheet(INPUT_STYLE)
        self.customer_phone.textChanged.connect(self.on_phone_changed)
        layout.addWidget(self.customer_phone)

        layout.addWidget(QLabel("اسم العميل:"))
        self.customer_name = QLineEdit()
        self.customer_name.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.customer_name)

        layout.addWidget(QLabel("العنوان بالتفصيل:"))
        self.customer_address = QTextEdit()
        self.customer_address.setPlaceholderText("المنطقة، الشارع، رقم العقار...")
        self.customer_address.setStyleSheet(INPUT_STYLE)
        self.customer_address.setMaximumHeight(80)
        layout.addWidget(self.customer_address)
        
        layout.addWidget(QLabel("توجيه إلى فرع:"))
        self.store_combo = QComboBox()
        self.store_combo.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.store_combo)

        layout.addStretch()
        
        # زر الحفظ في أسفل بيانات العميل
        self.save_btn = QPushButton("✅ حفظ وإرسال الطلب")
        self.save_btn.setStyleSheet(get_button_style("success"))
        self.save_btn.setMinimumHeight(50)
        self.save_btn.clicked.connect(self.save_order)
        layout.addWidget(self.save_btn)

        group.setLayout(layout)
        return group

    def load_stores(self):
        """تحميل قائمة الفروع لاختيار الفرع الموجه له الطلب وللفلترة"""
        self.store_combo.clear()
        self.pending_store_filter.clear()
        self.completed_store_filter.clear()
        
        self.pending_store_filter.addItem("جميع الفروع", None)
        self.completed_store_filter.addItem("جميع الفروع", None)
        
        stores = self.db.get_all_stores()
        for store in stores:
            self.store_combo.addItem(store['store_name'], store['id'])
            self.pending_store_filter.addItem(store['store_name'], store['id'])
            self.completed_store_filter.addItem(store['store_name'], store['id'])

    # ================== New Order (Redesigned) ==================
    def create_new_order_tab(self):
        """إعادة هيكلة تبويب أمر جديد بنظام الثلاث أعمدة العصرية"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setSpacing(10)
        
        # --- العمود 1: البحث عن المنتجات (35%) ---
        col1 = QFrame()
        col1_layout = QVBoxLayout(col1)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        
        search_group = QGroupBox("🔍 الأصناف")
        search_group.setStyleSheet(GROUP_BOX_STYLE)
        search_inner = QVBoxLayout()
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("ابحث باسم الصنف أو الكود...")
        self.product_search.setStyleSheet(INPUT_STYLE)
        self.product_search.textChanged.connect(self.start_search_timer)
        search_inner.addWidget(self.product_search)
        
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setStyleSheet("background-color: transparent; border: none;")
        self.products_grid_widget = QWidget()
        self.products_grid_widget.setStyleSheet("background-color: transparent;")
        self.products_grid = QGridLayout(self.products_grid_widget)
        self.products_grid.setSpacing(10)
        self.products_scroll.setWidget(self.products_grid_widget)
        search_inner.addWidget(self.products_scroll)
        
        search_group.setLayout(search_inner)
        col1_layout.addWidget(search_group)
        
        # --- العمود 2: سلة المشتريات (40%) ---
        col2 = QFrame()
        col2_layout = QVBoxLayout(col2)
        col2_layout.setContentsMargins(0, 0, 0, 0)
        
        cart_group = QGroupBox("🛒 فاتورة الطلب")
        cart_group.setStyleSheet(GROUP_BOX_STYLE)
        cart_inner = QVBoxLayout()
        
        self.order_items_table = QTableWidget(0, 5)
        self.order_items_table.setHorizontalHeaderLabels(["كود", "الصنف", "السعر", "الكمية", "حذف"])
        header = self.order_items_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.order_items_table.setColumnWidth(3, 85) # زيادة طفيفة لعرض عمود الكمية
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.order_items_table.setColumnWidth(4, 60) # زيادة طفيفة لعرض عمود الحذف
        
        self.order_items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.order_items_table.setStyleSheet(TABLE_STYLE)
        self.order_items_table.verticalHeader().setDefaultSectionSize(55) # زيادة ارتفاع الصفوف لوضوح أكبر
        cart_inner.addWidget(self.order_items_table)
        
        self.total_display = QFrame()
        self.total_display.setStyleSheet(f"background-color: {COLORS['bg_input']}; border-radius: 12px; margin-top: 10px;")
        total_layout = QHBoxLayout(self.total_display)
        self.total_label = QLabel("إجمالي الطلب: 0.00 ج.م")
        self.total_label.setStyleSheet("color: #10B981; font-size: 18px; font-weight: 800; border: none;")
        total_layout.addWidget(self.total_label)
        cart_inner.addWidget(self.total_display)
        
        cart_group.setLayout(cart_inner)
        col2_layout.addWidget(cart_group)
        
        # --- العمود 3: بيانات العميل والإنهاء (25%) ---
        self.customer_sidebar = self.create_customer_group()
        
        # إضافة الأعمدة للمخطط بنسب توزيع محسنة (20% للبحث، 55% للفاتورة، 25% للعميل)
        main_layout.addWidget(col1, 20)
        main_layout.addWidget(col2, 55)
        main_layout.addWidget(self.customer_sidebar, 25)
        
        return widget

    def create_pending_orders_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("تصفية حسب الفرع:"))
        self.pending_store_filter = QComboBox()
        self.pending_store_filter.setStyleSheet(INPUT_STYLE)
        self.pending_store_filter.currentIndexChanged.connect(self.load_orders)
        filter_layout.addWidget(self.pending_store_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.pending_orders_table = QTableWidget(0, 7)
        self.pending_orders_table.setHorizontalHeaderLabels([
            "رقم الأمر", "العميل", "الهاتف", "الفرع الاستلام",
            "التاريخ", "الإجمالي", "الحالة"
        ])
        self.pending_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pending_orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pending_orders_table.setStyleSheet(TABLE_STYLE)
        self.pending_orders_table.verticalHeader().setDefaultSectionSize(45)
        layout.addWidget(self.pending_orders_table)
        widget.setLayout(layout)
        return widget

    def create_completed_orders_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("تصفية حسب الفرع:"))
        self.completed_store_filter = QComboBox()
        self.completed_store_filter.setStyleSheet(INPUT_STYLE)
        self.completed_store_filter.currentIndexChanged.connect(self.load_orders)
        filter_layout.addWidget(self.completed_store_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.completed_orders_table = QTableWidget(0, 7)
        self.completed_orders_table.setHorizontalHeaderLabels([
            "رقم الأمر", "العميل", "الهاتف", "الفرع الاستلام",
            "التاريخ", "الإجمالي", "الحالة"
        ])
        self.completed_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.completed_orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.completed_orders_table.setStyleSheet(TABLE_STYLE)
        self.completed_orders_table.verticalHeader().setDefaultSectionSize(45)
        layout.addWidget(self.completed_orders_table)
        widget.setLayout(layout)
        return widget

    def get_status_widget(self, status):
        """إنشاء عرض بسيط وأنيق لحالة الطلب"""
        color_map = {
            'Pending': '#3B82F6',       # Blue
            'Accepted': '#10B981',      # Emerald
            'Processing': '#F59E0B',    # Amber
            'Out for Delivery': '#EC4899', # Pink
            'Delivered': '#059669',     # Green
            'Cancelled': '#EF4444',     # Red
        }
        text_map = {
            'Pending': 'قيد الانتظار',
            'Accepted': 'تم القبول',
            'Processing': 'جاري التحضير',
            'Out for Delivery': 'مع المندوب',
            'Delivered': 'تم التسليم',
            'Cancelled': 'ملغي',
        }
        
        color = color_map.get(status, '#94A3B8')
        text = text_map.get(status, status)
        
        label = QLabel(f"● {text}")
        label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; padding: 5px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    # ================== Logic ==================
    def on_phone_changed(self):
        phone = self.customer_phone.text().strip()
        if len(phone) == 11 and phone.isdigit():
            customer_data = self.db.get_customer_by_phone(phone)
            if customer_data:
                if not self.customer_name.text() or self.customer_name.property("auto_filled"):
                    self.customer_name.setText(customer_data.get('customer_name', ''))
                    self.customer_name.setProperty("auto_filled", True)
                    self.customer_name.setStyleSheet(INPUT_STYLE + "border-left: 3px solid #10B981;")
                
                if not self.customer_address.toPlainText().strip() or self.customer_address.property("auto_filled"):
                    self.customer_address.setText(customer_data.get('customer_address', ''))
                    self.customer_address.setProperty("auto_filled", True)
                    self.customer_address.setStyleSheet(INPUT_STYLE + "border-left: 3px solid #10B981;")
            else:
                self.customer_name.setProperty("auto_filled", False)
                self.customer_address.setProperty("auto_filled", False)
                self.customer_name.setStyleSheet(INPUT_STYLE)
                self.customer_address.setStyleSheet(INPUT_STYLE)
        else:
            self.customer_name.setProperty("auto_filled", False)
            self.customer_address.setProperty("auto_filled", False)
            self.customer_name.setStyleSheet(INPUT_STYLE)
            self.customer_address.setStyleSheet(INPUT_STYLE)

    def start_search_timer(self):
        self.search_timer.stop()
        self.search_timer.start(500) # تم تسريع البحث لـ 0.5 ثانية بدلاً من 2 لتحسين الشعور بالسرعة

    def search_products(self):
        term = self.product_search.text().strip()
        for i in reversed(range(self.products_grid.count())): 
            widget = self.products_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            
        if not term: return
            
        try:
            cursor = self.db.cursor
            # التحقق من نوع الاتصال (قاموس أم توبل)
            cursor.execute("""
                SELECT id, product_code, product_name, sell_price 
                FROM products 
                WHERE (product_code LIKE %s OR product_name LIKE %s) 
                AND is_active = TRUE LIMIT 20
            """, (f"%{term}%", f"%{term}%"))
            products = cursor.fetchall()
            
            for i, p in enumerate(products):
                card = self.create_product_card(p)
                # عرض المنتجات في عمود واحد لتقليل العرض الكلي للكروت
                self.products_grid.addWidget(card, i, 0)
        except Exception as e:
            print(f"Search Error: {e}")

    def create_product_card(self, product):
        card = QFrame()
        card.setObjectName("ProductCard")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumHeight(90) # تقليل الارتفاع لتغيير الشكل العام للكاراد
        card.setStyleSheet(f"""
            QFrame#ProductCard {{
                background-color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QFrame#ProductCard:hover {{
                border-color: {COLORS['accent']};
                background-color: #1E293B;
            }}
        """)
        
        layout = QVBoxLayout(card)
        name = QLabel(product['product_name'])
        name.setWordWrap(True)
        name.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(name)
        
        price = QLabel(f"{product['sell_price']:,.2f} ج.م")
        price.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        layout.addWidget(price)
        
        card.mousePressEvent = lambda e: self.add_card_product_to_order(product)
        return card

    def add_card_product_to_order(self, product):
        p_id, code, name, price = product['id'], product['product_code'], product['product_name'], product['sell_price']
        
        for r in range(self.order_items_table.rowCount()):
            if self.order_items_table.item(r, 0).text() == code:
                qty_spin = self.order_items_table.cellWidget(r, 3).findChild(QSpinBox)
                qty_spin.setValue(qty_spin.value() + 1)
                self.calculate_total()
                return

        row = self.order_items_table.rowCount()
        self.order_items_table.insertRow(row)
        
        item_code = QTableWidgetItem(code)
        item_code.setData(Qt.ItemDataRole.UserRole, p_id)
        self.order_items_table.setItem(row, 0, item_code)
        self.order_items_table.setItem(row, 1, QTableWidgetItem(name))
        self.order_items_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
        
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 1000)
        qty_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_input']};
                color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0px 5px;
                font-size: 12px;
                min-height: 28px !important;
                max-height: 28px !important;
                height: 28px !important;
            }}
        """)
        qty_spin.valueChanged.connect(self.calculate_total)
        
        qty_container = QWidget()
        qty_layout = QHBoxLayout(qty_container)
        qty_layout.setContentsMargins(0, 0, 0, 0)
        qty_layout.addWidget(qty_spin)
        qty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.order_items_table.setCellWidget(row, 3, qty_container)
        
        del_btn = QPushButton("🗑️ حذف")
        del_btn.setFixedSize(50, 28) # تقليل العرض والارتفاع قليلاً لشكل أكثر رشاقة
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(239, 68, 68, 0.1) !important;
                color: #FCA5A5 !important;
                border: 1px solid rgba(239, 68, 68, 0.3) !important;
                border-radius: 8px !important;
                font-size: 11px !important;
                font-weight: bold !important;
                padding: 0px 5px !important;
                min-height: 0px !important;
            }}
            QPushButton:hover {{
                background-color: #EF4444 !important;
                color: white !important;
                border: none !important;
            }}
        """)
        del_btn.clicked.connect(self.handle_delete_click)
        
        del_container = QWidget()
        del_layout = QHBoxLayout(del_container)
        del_layout.setContentsMargins(0, 0, 0, 0)
        del_layout.addWidget(del_btn)
        del_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.order_items_table.setCellWidget(row, 4, del_container)
        self.calculate_total()

    def handle_delete_click(self):
        """التعرف على الصف الصحيح وحذفه بناءً على الزر المضغوط"""
        button = self.sender()
        if button:
            # العثور على موضع الحاوية (Container) داخل الجدول
            pos = button.parent().parent().mapTo(self.order_items_table, button.parent().pos())
            index = self.order_items_table.indexAt(button.parent().pos())
            
            # طريقة أكثر أماناً: البحث في الخلايا عن الحاوية التي تحتوي على هذا الزر
            for row in range(self.order_items_table.rowCount()):
                if self.order_items_table.cellWidget(row, 4):
                    if self.order_items_table.cellWidget(row, 4).findChild(QPushButton) == button:
                        self.order_items_table.removeRow(row)
                        self.calculate_total()
                        return

    def remove_item(self, row):
        # تم استبدالها بـ handle_delete_click للأمان، ولكن نتركها للتوافق إذا استُدعت برمجياً
        if row >= 0:
            self.order_items_table.removeRow(row)
            self.calculate_total()

    def calculate_total(self):
        total = 0
        for r in range(self.order_items_table.rowCount()):
            price = float(self.order_items_table.item(r, 2).text())
            qty = self.order_items_table.cellWidget(r, 3).findChild(QSpinBox).value()
            total += price * qty
        self.total_label.setText(f"إجمالي الطلب: {total:,.2f} ج.م")

    def save_order(self):
        if self.order_items_table.rowCount() == 0:
            QMessageBox.warning(self, "تنبيه", "الطلب فارغ!")
            return
            
        if not self.customer_name.text() or not self.customer_phone.text():
            QMessageBox.warning(self, "تنبيه", "برجاء إدخال بيانات العميل")
            return

        try:
            name, phone = self.customer_name.text(), self.customer_phone.text()
            address = self.customer_address.toPlainText().strip()
            dest_id = self.store_combo.currentData()
            agent_id = self.user_info.get('id') or 1
            source_id = self.user_info.get('store_id') or 1

            order_num = self.db.create_order(name, phone, source_id, agent_id, dest_id, address)
            
            cursor = self.db.cursor
            cursor.execute("SELECT id FROM orders WHERE order_number = %s", (order_num,))
            order_id = cursor.fetchone()['id']

            total = 0
            for r in range(self.order_items_table.rowCount()):
                p_id = self.order_items_table.item(r, 0).data(Qt.ItemDataRole.UserRole)
                price = float(self.order_items_table.item(r, 2).text())
                qty = self.order_items_table.cellWidget(r, 3).findChild(QSpinBox).value()
                total += price * qty
                self.db.add_order_item(order_id, p_id, qty, price)

            cursor.execute("UPDATE orders SET total_amount = %s WHERE id = %s", (total, order_id))
            self.db.conn.commit()
            QMessageBox.information(self, "تم", f"تم الحفظ بنجاح برقم: {order_num}")
            
            self.order_items_table.setRowCount(0)
            self.customer_name.clear()
            self.customer_phone.clear()
            self.customer_address.clear()
            self.calculate_total()
            self.load_orders()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {e}")

    def load_orders(self):
        try:
            cursor = self.db.cursor
            # المعلقة
            f_id = self.pending_store_filter.currentData()
            q = "SELECT o.*, s.store_name FROM orders o LEFT JOIN stores s ON o.destination_store_id = s.id WHERE o.status NOT IN ('Delivered', 'Cancelled')"
            if f_id: q += f" AND o.destination_store_id = {f_id}"
            cursor.execute(q + " ORDER BY order_date DESC")
            orders = cursor.fetchall()
            self.pending_orders_table.setRowCount(len(orders))
            for i, o in enumerate(orders):
                self.pending_orders_table.setItem(i, 0, QTableWidgetItem(o['order_number']))
                self.pending_orders_table.setItem(i, 1, QTableWidgetItem(o['customer_name']))
                self.pending_orders_table.setItem(i, 2, QTableWidgetItem(o['customer_phone']))
                self.pending_orders_table.setItem(i, 3, QTableWidgetItem(o['store_name'] or ""))
                self.pending_orders_table.setItem(i, 4, QTableWidgetItem(str(o['order_date'])))
                self.pending_orders_table.setItem(i, 5, QTableWidgetItem(f"{o['total_amount']:,.2f}"))
                self.pending_orders_table.setCellWidget(i, 6, self.get_status_widget(o['status']))

            # المكتملة
            f_id = self.completed_store_filter.currentData()
            q = "SELECT o.*, s.store_name FROM orders o LEFT JOIN stores s ON o.destination_store_id = s.id WHERE o.status IN ('Delivered', 'Cancelled')"
            if f_id: q += f" AND o.destination_store_id = {f_id}"
            cursor.execute(q + " ORDER BY order_date DESC")
            orders = cursor.fetchall()
            self.completed_orders_table.setRowCount(len(orders))
            for i, o in enumerate(orders):
                self.completed_orders_table.setItem(i, 0, QTableWidgetItem(o['order_number']))
                self.completed_orders_table.setItem(i, 1, QTableWidgetItem(o['customer_name']))
                self.completed_orders_table.setItem(i, 2, QTableWidgetItem(o['customer_phone']))
                self.completed_orders_table.setItem(i, 3, QTableWidgetItem(o['store_name'] or ""))
                self.completed_orders_table.setItem(i, 4, QTableWidgetItem(str(o['order_date'])))
                self.completed_orders_table.setItem(i, 5, QTableWidgetItem(f"{o['total_amount']:,.2f}"))
                self.completed_orders_table.setCellWidget(i, 6, self.get_status_widget(o['status']))
        except Exception as e:
            print(f"Load Error: {e}")
