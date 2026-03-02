
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

class CallCenterOrdersDialog(QDialog):
    def __init__(self, db_manager, store_id, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.store_id = store_id
        self.selected_order = None
        
        self.setWindowTitle("طلبات الكول سنتر / Call Center Orders")
        self.resize(800, 500)
        self.init_ui()
        self.load_orders()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search Box
        search_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLabel, QLineEdit
        search_layout.addWidget(QLabel("بحث:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث برقم الطلب، اسم العميل، أو الهاتف...")
        self.search_input.textChanged.connect(self.load_orders)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Orders Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "رقم الطلب", "اسم العميل", "رقم الهاتف", "التاريخ", "الحالة", "المصدر/الكول سنتر"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        
        select_btn = QPushButton("تحميل الطلب المحدد")
        select_btn.clicked.connect(self.select_order)
        select_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        btn_layout.addWidget(select_btn)

        refresh_btn = QPushButton("تحديث القائمة")
        refresh_btn.clicked.connect(self.load_orders)
        btn_layout.addWidget(refresh_btn)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_orders(self):
        self.table.setRowCount(0)
        search_term = self.search_input.text().strip() or None
        orders = self.db.get_open_orders(self.store_id, search_term)
        
        if not orders:
            return

        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order['order_number'])))
            self.table.setItem(row, 1, QTableWidgetItem(order['customer_name']))
            self.table.setItem(row, 2, QTableWidgetItem(order['customer_phone']))
            self.table.setItem(row, 3, QTableWidgetItem(str(order['order_date'])))
            self.table.setItem(row, 4, QTableWidgetItem(order['status']))
            self.table.setItem(row, 5, QTableWidgetItem(order.get('call_center_agent', 'N/A')))
            
            # Store full address in hidden data if needed
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, order['id'])
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole + 1, order.get('customer_address', ''))

    def select_order(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد طلب أولاً")
            return
            
        order_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Confirmation
        reply = QMessageBox.question(self, "تأكيد", "هل تريد تحميل هذا الطلب للفاتورة؟", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_order = {
                'id': order_id,
                'customer_name': self.table.item(current_row, 1).text(),
                'customer_phone': self.table.item(current_row, 2).text(),
                'customer_address': self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole + 1),
            }
            self.accept()
