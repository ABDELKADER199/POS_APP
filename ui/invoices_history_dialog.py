
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QMessageBox, QHeaderView, QLabel,
                             QGroupBox, QFormLayout, QLineEdit, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
from utils.printer_service import PrinterService

class InvoicesHistoryDialog(QDialog):
    def __init__(self, db_manager, user_info, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.user_info = user_info
        
        self.setWindowTitle("سجل الفواتير / Invoices History")
        self.resize(1000, 700)
        self.init_ui()
        self.load_invoices()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Header Info (Drawer, Cashier, Branch) ---
        info_group = QGroupBox("معلومات الوردية الحالية")
        info_layout = QHBoxLayout()
        
        info_layout.addWidget(QLabel(f"الفرع: {self.user_info.get('store_name', 'غير معروف')}"))
        info_layout.addSpacing(20)
        info_layout.addWidget(QLabel(f"الكاشير: {self.user_info.get('name', 'غير معروف')} (#{self.user_info.get('id', '-')})"))
        info_layout.addSpacing(20)
        
        drawer_status = self.db.get_drawer_status(self.user_info.get('id', 0))
        drawer_id = drawer_status.get('id', 'لا يوجد درج مفتوح') if drawer_status.get('is_open') else "مغلق"
        info_layout.addWidget(QLabel(f"رقم الدرج: {drawer_id}"))
        
        info_layout.addStretch()
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # --- Search & Filter Section ---
        filter_group = QGroupBox("بحث وتصفية")
        filter_layout = QHBoxLayout()

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث برقم الفاتورة أو آخر أرقام أو اسم العميل...")
        filter_layout.addWidget(QLabel("بحث:"))
        filter_layout.addWidget(self.search_input, 2)

        # Date Filters
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30)) # Default to last 30 days
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.date_to)

        # Search Button
        search_btn = QPushButton("🔍 بحث")
        search_btn.clicked.connect(self.load_invoices)
        search_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
        filter_layout.addWidget(search_btn)
        
        # Reset Button
        reset_btn = QPushButton("↺ ريست")
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # --- Invoices Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "رقم الفاتورة", "التاريخ", "العميل", "الإجمالي", "طريقة الدفع", "بواسطة"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_details)
        layout.addWidget(self.table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        
        details_btn = QPushButton("📄 عرض التفاصيل")
        details_btn.clicked.connect(self.view_details)
        details_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        btn_layout.addWidget(details_btn)

        # Restricted Reprint Button (Manager Only)
        user_role = self.user_info.get('role_id')
        if user_role in [1, 2]: # Admin or Manager
            reprint_layout = QHBoxLayout()
            
            reprint_btn = QPushButton("🖨️ إعادة طباعة")
            reprint_btn.clicked.connect(self.reprint_invoice)
            reprint_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; font-weight: bold;")
            reprint_layout.addWidget(reprint_btn)
            
            save_pdf_btn = QPushButton("📄 حفظ كـ PDF")
            save_pdf_btn.clicked.connect(self.save_invoice_as_pdf)
            save_pdf_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 8px; font-weight: bold;")
            reprint_layout.addWidget(save_pdf_btn)
            
            btn_layout.addLayout(reprint_layout)

        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.load_invoices)
        btn_layout.addWidget(refresh_btn)

        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def reset_filters(self):
        self.search_input.clear()
        self.date_from.setDate(QDate.currentDate())
        self.date_to.setDate(QDate.currentDate())
        self.load_invoices()

    def load_invoices(self):
        self.table.setRowCount(0)
        store_id = self.user_info.get('store_id', 1)
        
        # Get filter values
        search_term = self.search_input.text().strip() or None
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        
        # If reset or default, maybe show all? Or keep date filter?
        # User usually wants to see today's invoices by default.
        # But if they cleared search, they might still want date filter.
        
        invoices = self.db.get_completed_invoices(store_id, search_term, start_date, end_date)
        
        if not invoices:
            return # Table is already empty

        self.table.setRowCount(len(invoices))
        for row, inv in enumerate(invoices):
            self.table.setItem(row, 0, QTableWidgetItem(str(inv['invoice_number'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(inv['invoice_date'])))
            self.table.setItem(row, 2, QTableWidgetItem(inv.get('customer_name') or "ضيف"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{inv['total_amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(inv.get('payment_method')))
            self.table.setItem(row, 5, QTableWidgetItem(inv.get('cashier_name')))
            
            # Store ID for details
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, inv['id'])

    def view_details(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فاتورة لعرض تفاصيلها")
            return
            
        invoice_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        invoice_number = self.table.item(current_row, 0).text()
        
        items = self.db.get_invoice_items_details(invoice_id)
        
        # Create a simple dialog for details
        details_dialog = QDialog(self)
        details_dialog.setWindowTitle(f"تفاصيل الفاتورة # {invoice_number}")
        details_dialog.resize(600, 500)
        
        d_layout = QVBoxLayout()
        
        # Customer Info in Details
        cursor = self.db.conn.cursor(dictionary=True)
        cursor.execute("SELECT customer_name, customer_phone, customer_address FROM invoices WHERE id = %s", (invoice_id,))
        details = cursor.fetchone()
        
        if details:
            cust_group = QGroupBox("بيانات العميل")
            cust_layout = QFormLayout()
            cust_layout.addRow("الاسم:", QLabel(details.get('customer_name') or "ضيف"))
            cust_layout.addRow("الهاتف:", QLabel(details.get('customer_phone') or "-"))
            cust_layout.addRow("العنوان:", QLabel(details.get('customer_address') or "-"))
            cust_group.setLayout(cust_layout)
            d_layout.addWidget(cust_group)

        items_table = QTableWidget()
        items_table.setColumnCount(4)
        items_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "الإجمالي"])
        items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        items_table.setRowCount(len(items))
        for r, item in enumerate(items):
            items_table.setItem(r, 0, QTableWidgetItem(item['product_name']))
            items_table.setItem(r, 1, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            items_table.setItem(r, 2, QTableWidgetItem(str(item['quantity'])))
            items_table.setItem(r, 3, QTableWidgetItem(f"{item['total_price']:.2f}"))
            
        d_layout.addWidget(items_table)
        
        ok_btn = QPushButton("موافق")
        ok_btn.clicked.connect(details_dialog.accept)
        d_layout.addWidget(ok_btn)
        
        details_dialog.setLayout(d_layout)
        details_dialog.exec()

    def reprint_invoice(self):
        """Reprint the selected invoice (Manager Only)"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فاتورة لطباعتها")
            return
            
        invoice_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 1. Fetch full invoice data (re-using part of view_details logic but structured for printer)
        cursor = self.db.conn.cursor(dictionary=True)
        query = """
            SELECT i.*, u.name as cashier_name 
            FROM invoices i
            JOIN users u ON i.cashier_id = u.id
            WHERE i.id = %s
        """
        cursor.execute(query, (invoice_id,))
        invoice_data = cursor.fetchone()
        
        if not invoice_data:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على بيانات الفاتورة")
            return
            
        # 2. Fetch Items
        items = self.db.get_invoice_items_details(invoice_id)
        formatted_items = []
        for item in items:
            formatted_items.append({
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'price': item['unit_price'],
                'total': item['total_price']
            })
            
        # 3. Prepare Data (Calculate missing fields)
        total_amount = float(invoice_data.get('total_amount') or 0)
        discount = float(invoice_data.get('discount') or 0)
        subtotal = total_amount + discount
        
        invoice_data['subtotal'] = subtotal
        invoice_data['discount'] = discount
        invoice_data['total_amount'] = total_amount
            
        # 4. Print
        try:
            PrinterService.print_receipt(
                invoice_data, 
                formatted_items, 
                str(invoice_data['cashier_name']), 
                str(self.user_info.get('store_name', 'System'))
            )
            QMessageBox.information(self, "نجاح", "تم إرسال الفاتورة للطباعة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ الطباعة", str(e))
    def save_invoice_as_pdf(self):
        """Explicitly save the selected invoice as PDF"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد فاتورة لحفظها")
            return
            
        invoice_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # 1. Fetch data
        cursor = self.db.conn.cursor(dictionary=True)
        query = "SELECT i.*, u.name as cashier_name FROM invoices i JOIN users u ON i.cashier_id = u.id WHERE i.id = %s"
        cursor.execute(query, (invoice_id,))
        invoice_data = cursor.fetchone()
        
        if not invoice_data:
            return
            
        items = self.db.get_invoice_items_details(invoice_id)
        formatted_items = []
        for item in items:
            formatted_items.append({
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'price': item['unit_price'],
                'total': item['total_price']
            })
            
        # 2. Prepare Data
        total_amount = float(invoice_data.get('total_amount') or 0)
        discount = float(invoice_data.get('discount') or 0)
        invoice_data['subtotal'] = total_amount + discount
        invoice_data['discount'] = discount
        invoice_data['total_amount'] = total_amount
            
        # 3. Save as PDF
        try:
            if PrinterService.save_receipt_as_pdf(
                invoice_data, 
                formatted_items, 
                str(invoice_data['cashier_name']), 
                str(self.user_info.get('store_name', 'System'))
            ):
                QMessageBox.information(self, "نجاح", "تم حفظ الفاتورة كـ PDF بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", str(e))
