"""
نافذة الاستعلام عن المنتجات
Product Inquiry Dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from ui.styles import (INPUT_STYLE, get_button_style, TABLE_STYLE, 
                       GROUP_BOX_STYLE, LABEL_STYLE_HEADER, COLORS)

class ProductInquiryDialog(QDialog):
    """ناقدة الاستعلام عن توافر منتج في الفروع"""
    
    def __init__(self, db, current_store_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_store_id = current_store_id
        self.setWindowTitle("🛠️ الاستعلام عن منتج")
        self.setMinimumSize(700, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- العنوان ---
        title = QLabel("🔍 استعلام عن توافر صنف")
        title.setStyleSheet(LABEL_STYLE_HEADER)
        layout.addWidget(title)
        
        # --- البحث ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل كود المنتج أو الباركود...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.returnPressed.connect(self.search_product)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 بحث")
        search_btn.setStyleSheet(get_button_style("primary"))
        search_btn.clicked.connect(self.search_product)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # --- معلومات المنتج ---
        self.product_info_box = QGroupBox("بيانات الصنف")
        self.product_info_box.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QHBoxLayout()
        
        self.name_label = QLabel("الاسم: -")
        self.name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        
        self.price_label = QLabel("السعر: -")
        self.price_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.price_label.setStyleSheet(f"color: {COLORS.get('success', 'green')};")
        
        info_layout.addWidget(self.name_label)
        info_layout.addStretch()
        info_layout.addWidget(self.price_label)
        
        self.product_info_box.setLayout(info_layout)
        self.product_info_box.hide()
        layout.addWidget(self.product_info_box)
        
        # --- جدول الكميات ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["الفرع", "الكمية المتاحة", "تنبيه"])
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # --- زر الإغلاق ---
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet(get_button_style("secondary"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def search_product(self):
        term = self.search_input.text().strip()
        if not term:
            return
            
        result = self.db.get_product_cross_branch_stock(term)
        
        if not result or not result.get('product'):
            self.product_info_box.hide()
            self.table.setRowCount(0)
            self.name_label.setText("الاسم: -")
            self.price_label.setText("السعر: -")
            # Message placeholder or alert could be added here
            return
            
        product = result['product']
        stocks = result['stocks']
        
        # تحديث العرض
        self.name_label.setText(f"الاسم: {product['product_name']} ({product['product_code']})")
        self.price_label.setText(f"السعر: {product['sell_price']:.2f} ج.م")
        self.product_info_box.show()
        
        self.table.setRowCount(0)
        for stock in stocks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            store_name = stock['store_name']
            if stock['store_id'] == self.current_store_id:
                store_name += " (الفرع الحالي)"
            
            name_item = QTableWidgetItem(store_name)
            qty = stock['quantity']
            qty_item = QTableWidgetItem(str(qty))
            
            # تمييز الفرع الحالي بلون واضح على الثيم الداكن
            if stock['store_id'] == self.current_store_id:
                highlight = QColor("#1a3a4a")  # Dark teal - readable on dark theme
                name_item.setBackground(highlight)
                qty_item.setBackground(highlight)
                name_item.setForeground(QColor("#FFFFFF"))
                qty_item.setForeground(QColor("#FFFFFF"))
                name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                qty_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                
            # تمييز الكميات المنخفضة
            alert_text = ""
            if qty <= 0:
                qty_item.setForeground(QColor(COLORS.get('danger', 'red')))
                alert_text = "نفد المخزون"
            elif qty <= 5:
                qty_item.setForeground(QColor(COLORS.get('warning', 'orange')))
                alert_text = "كمية محدودة"
            
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, qty_item)
            self.table.setItem(row, 2, QTableWidgetItem(alert_text))
            
        self.search_input.selectAll()
        self.search_input.setFocus()
