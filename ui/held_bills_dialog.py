
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

class HeldBillsDialog(QDialog):
    def __init__(self, db_manager, store_id, user_info=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.store_id = store_id
        self.user_info = user_info or {}
        self.selected_bill = None
        
        self.setWindowTitle("الفواتير المعلقة / Held Bills")
        self.resize(800, 500)
        self.init_ui()
        self.load_bills()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search Box
        search_layout = QHBoxLayout()
        from PyQt6.QtWidgets import QLabel, QLineEdit
        search_layout.addWidget(QLabel("بحث:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث برقم الفاتورة أو اسم العميل...")
        self.search_input.textChanged.connect(self.load_bills)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Bills Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "كود الفاتورة", "العميل", "التاريخ", "الإجمالي", "حفظ بواسطة"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        
        resume_btn = QPushButton("استكمال الفاتورة")
        resume_btn.clicked.connect(self.resume_bill)
        resume_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        btn_layout.addWidget(resume_btn)

        delete_btn = QPushButton("حذف الفاتورة")
        delete_btn.clicked.connect(self.delete_bill)
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        
        # Check permissions: Admin (1) or Manager (2)
        role_id = self.user_info.get('role_id')
        if role_id not in [1, 2]:
            delete_btn.setEnabled(False)
            delete_btn.setToolTip("لا تملك صلاحية حذف الفواتير المعلقة")
            delete_btn.setStyleSheet("background-color: #cccccc; color: #666666; padding: 5px;")
            
        btn_layout.addWidget(delete_btn)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_bills(self):
        self.table.setRowCount(0)
        search_term = self.search_input.text().strip() or None
        bills = self.db.get_held_invoices(self.store_id, search_term)
        
        if not bills:
            return

        self.table.setRowCount(len(bills))
        for row, bill in enumerate(bills):
            self.table.setItem(row, 0, QTableWidgetItem(str(bill['temp_invoice_code'])))
            self.table.setItem(row, 1, QTableWidgetItem(bill.get('customer_name') or "ضيف"))
            self.table.setItem(row, 2, QTableWidgetItem(str(bill['saved_at'])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{bill['total_amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(bill.get('cashier_name') or "Unknown"))
            
            # Store full details in hidden data
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, bill['id'])
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole + 1, bill.get('customer_phone', ''))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole + 2, bill.get('customer_address', ''))

    def resume_bill(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فاتورة")
            return
            
        bill_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "تأكيد", "هل تريد استكمال هذه الفاتورة؟", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_bill = {
                'id': bill_id,
                'customer_name': self.table.item(current_row, 1).text(),
                'customer_phone': self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole + 1),
                'customer_address': self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole + 2),
            }
            self.accept()

    def delete_bill(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فاتورة")
            return
            
        bill_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.warning(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذه الفاتورة نهائياً؟", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_held_invoice(bill_id):
                self.load_bills()
                QMessageBox.information(self, "نجاح", "تم حذف الفاتورة")
            else:
                QMessageBox.critical(self, "خطأ", "فشل حذف الفاتورة")
