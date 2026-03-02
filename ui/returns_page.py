from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QScrollArea, QGroupBox, QFormLayout, QSpinBox, 
                             QAbstractItemView, QDialog, QDialogButtonBox, QDateEdit, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QColor
from ui.styles import (INPUT_STYLE, BUTTON_STYLES, TABLE_STYLE, 
                       get_button_style, COLORS, GROUP_BOX_STYLE)

class ReturnsPage(QWidget):
    """صفحة مرتجعات المبيعات"""
    return_processed = pyqtSignal() # Signal to notify when a return is done
    
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db = db_manager
        self.user = current_user
        self.current_invoice = None
        self.init_ui()
        
    def set_user(self, user_info):
        """تحديث بيانات المستخدم الحالي"""
        self.user = user_info
        self.refresh_ui()
        
    def check_permissions(self):
        """التحقق من صلاحية المستخدم للوصول للمرتجعات"""
        if not self.user:
            return False
            
        role_name = self.user.get('role_name', '').lower()
        role_id = self.user.get('role_id', -1)
        
        # السماح للمدراء (Admin, System Admin, Manager) والمدير العام
        # Check by role name
        allowed_roles = ['admin', 'system admin', 'مدير عام', 'manager', 'مدير فرع', 'developer']
        name_match = any(role in role_name for role in allowed_roles)
        
        # Check by role ID (1: Admin, 2: Manager, 99: Developer)
        id_match = role_id in [1, 2, 99]
        
        return name_match or id_match
        
    def init_ui(self):
        """تهيئة الواجهة الأولية"""
        self.main_layout = QVBoxLayout(self)
        self.refresh_ui()

    def refresh_ui(self):
        """تحديث الواجهة بناءً على الصلاحيات"""
        # تنظيف المحتوى السابق
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # التحقق من الصلاحيات
        if not self.check_permissions():
            role_name = "N/A"
            role_id = "N/A"
            if self.user:
                role_name = self.user.get('role_name', 'N/A')
                role_id = self.user.get('role_id', 'N/A')
            
            user_msg = f"الدور: {role_name} ({role_id})"
            
            lbl = QLabel(f"⛔ عذراً، ليس لديك صلاحية الوصول لهذه الصفحة\n\n{user_msg}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            lbl.setStyleSheet("color: red; margin-top: 50px;")
            self.main_layout.addWidget(lbl)
            return

        # بناء الواجهة للمستخدمين المصرح لهم
        self.setup_authorized_ui()

    def setup_authorized_ui(self):
        """بناء عناصر صفحة المرتجعات"""
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # --- Search Section ---
        search_group = QGroupBox("البحث عن فاتورة")
        search_group.setStyleSheet(GROUP_BOX_STYLE)
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل رقم الفاتورة أو آخر 4 أرقام...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.returnPressed.connect(self.search_invoice)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 بحث")
        search_btn.setStyleSheet(get_button_style("primary"))
        search_btn.clicked.connect(self.search_invoice)
        search_layout.addWidget(search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # --- Invoice Info Section ---
        self.info_group = QGroupBox("بيانات الفاتورة")
        self.info_group.setStyleSheet(GROUP_BOX_STYLE)
        self.info_group.hide()
        info_layout = QFormLayout()
        
        self.lbl_date = QLabel("-")
        self.lbl_customer = QLabel("-")
        self.lbl_total = QLabel("-")
        
        info_layout.addRow("تاريخ الفاتورة:", self.lbl_date)
        info_layout.addRow("اسم العميل:", self.lbl_customer)
        info_layout.addRow("إجمالي الفاتورة:", self.lbl_total)
        
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)
        
        # --- Items Table ---
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(
            ["المنتج", "السعر", "الكمية المباعة", "الكمية المرتجعة", "الإجمالي"]
        )
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.verticalHeader().setDefaultSectionSize(50)
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.items_table)
        
        # --- Return Summary & Action ---
        actions_layout = QHBoxLayout()
        
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("سبب المرتجع...")
        self.reason_input.setStyleSheet(INPUT_STYLE)
        actions_layout.addWidget(self.reason_input)
        
        self.process_btn = QPushButton("🔄 إتمام المرتجع")
        self.process_btn.setStyleSheet(get_button_style("success"))
        self.process_btn.clicked.connect(self.process_return)
        self.process_btn.setEnabled(False)
        actions_layout.addWidget(self.process_btn)
        
        history_btn = QPushButton("📜 سجل المرتجعات")
        history_btn.setStyleSheet(get_button_style("info"))
        history_btn.clicked.connect(self.show_history)
        actions_layout.addWidget(history_btn)
        
        clear_btn = QPushButton("🗑️ مسح")
        clear_btn.setStyleSheet(get_button_style("secondary"))
        clear_btn.clicked.connect(self.clear_page)
        actions_layout.addWidget(clear_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        self.scroll.setWidget(container)
        self.main_layout.addWidget(self.scroll)

    def search_invoice(self):
        invoice_num = self.search_input.text().strip()
        if not invoice_num:
            return
            
        invoice = self.db.get_invoice_by_number(invoice_num)
        if not invoice:
            QMessageBox.warning(self, "خطأ", "الفاتورة غير موجودة")
            return
            
        self.current_invoice = invoice
        self.lbl_date.setText(str(invoice['invoice_date']))
        self.lbl_customer.setText(invoice['customer_name'] or "عميل نقدي")
        self.lbl_total.setText(f"{invoice['total_amount']} ج.م")
        self.info_group.show()
        
        # تحميل الأصناف
        items = self.db.get_invoice_items_details(invoice['id'])
        self.display_items(items)
        self.process_btn.setEnabled(True)

    def display_items(self, items):
        self.items_table.setRowCount(0)
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            sold_qty = item['quantity']
            returned_already = item.get('returned_quantity', 0)
            available_qty = max(0, sold_qty - returned_already)
            
            # اسم المنتج مع تخزين معرف المنتج في البيانات الخفية
            prod_item = QTableWidgetItem(item['product_name'])
            prod_item.setData(Qt.ItemDataRole.UserRole, item['product_id'])
            self.items_table.setItem(row, 0, prod_item)
            
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['unit_price'])))
            
            # الكمية المباعة (المتبقية)
            qty_text = f"{sold_qty}" if returned_already == 0 else f"{available_qty} (من اصل {sold_qty})"
            qty_item = QTableWidgetItem(qty_text)
            self.items_table.setItem(row, 2, qty_item)
            
            # SpinBox لـ الكمية المرتجعة
            return_qty_spin = QSpinBox()
            return_qty_spin.setRange(0, int(available_qty))
            return_qty_spin.setStyleSheet(INPUT_STYLE)
            
            if available_qty <= 0:
                return_qty_spin.setEnabled(False)
                qty_item.setText(f"تم الإرجاع بالكامل ({sold_qty})")
                qty_item.setForeground(QColor(COLORS.get('danger', '#FF0000')))
            
            self.items_table.setCellWidget(row, 3, return_qty_spin)
            self.items_table.setItem(row, 4, QTableWidgetItem("0.00"))
            
            # ربط التحديث التلقائي للإجمالي
            return_qty_spin.valueChanged.connect(lambda v, r=row, p=item['unit_price']: 
                                               self.items_table.setItem(r, 4, QTableWidgetItem(f"{v * float(p):.2f}")))

    def process_return(self):
        if not self.current_invoice or not self.user:
            return
            
        items_to_return = []
        for row in range(self.items_table.rowCount()):
            qty_widget = self.items_table.cellWidget(row, 3)
            if not qty_widget:
                continue
                
            qty = qty_widget.value()
            if qty > 0:
                prod_item = self.items_table.item(row, 0)
                product_id = prod_item.data(Qt.ItemDataRole.UserRole)
                product_name = prod_item.text()
                unit_price = float(self.items_table.item(row, 1).text())
                
                items_to_return.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': qty,
                    'unit_price': unit_price
                })
        
        if not items_to_return:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد كميات للمرتجع")
            return
            
        reason = self.reason_input.text().strip()
        
        # الحصول على رقم الدرج المفتوح حالياً (إذا وجد) لخصم المرتجع منه
        drawer_id = None
        status = self.db.get_drawer_status(self.user.get('id', 0))
        drawer_owner_name = self.user.get('name', 'Cashier')
        
        if status and status.get('is_open'):
            drawer_id = status['id']
        else:
            # Check for ANY open drawer in the SAME branch (For all roles now)
            store_id = self.user.get('store_id', 1)
            store_drawer = self.db.get_store_open_drawer(store_id)
            if store_drawer:
                drawer_id = store_drawer['id']
                drawer_owner_name = store_drawer['cashier_name']
            else:
                # Block return if no drawer found in the branch
                QMessageBox.warning(self, "تنبيه", 
                    "لا يوجد درج كاشير مفتوح في هذا الفرع!\n"
                    "يجب فتح درج كاشير أولاً قبل إتمام عملية المرتجع.")
                return

        ret_num = self.db.process_return(
            self.current_invoice['id'],
            items_to_return,
            reason,
            self.user['id'],
            self.current_invoice['store_id'],
            drawer_id=drawer_id
        )
        
        if ret_num:
            # Prepare data for printing
            return_data = {
                'return_number': ret_num,
                'invoice_number': self.current_invoice.get('invoice_number'),
                'total_amount': sum(item['quantity'] * item['unit_price'] for item in items_to_return),
                'reason': reason
            }
            
            # Offer choice: Print or PDF? Or just do both?
            # To be safe and simple, we'll keep the print call but also ensure 
            # the user can print/save later from history if needed.
            # But let's add an option to save as PDF immediately.
            
            from utils.printer_service import PrinterService
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("نجاح المرتجع")
            msg_box.setText(f"تمت عملية المرتجع بنجاح (رقم: {ret_num})")
            msg_box.setInformativeText("هل تريد طباعة الإيصال أم حفظه كـ PDF؟")
            
            print_btn = msg_box.addButton("🖨️ طباعة", QMessageBox.ButtonRole.ActionRole)
            pdf_btn = msg_box.addButton("📄 حفظ PDF", QMessageBox.ButtonRole.ActionRole)
            close_btn = msg_box.addButton("إغلاق", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == print_btn:
                PrinterService.print_return_receipt(
                    return_data, 
                    items_to_return, 
                    drawer_owner_name, 
                    self.user.get('store_name', 'Store')
                )
            elif msg_box.clickedButton() == pdf_btn:
                PrinterService.save_return_as_pdf(
                    return_data, 
                    items_to_return, 
                    drawer_owner_name, 
                    self.user.get('store_name', 'Store')
                )

            QMessageBox.information(self, "نجاح", f"تمت عملية المرتجع بنجاح\nرقم المرتجع: {ret_num}")
            self.return_processed.emit() # Notify other components
            self.clear_page()
        else:
            QMessageBox.critical(self, "خطأ", "فشلت عملية المرتجع")

    def clear_page(self):
        self.search_input.clear()
        self.reason_input.clear()
        self.lbl_date.setText("-")
        self.lbl_customer.setText("-")
        self.lbl_total.setText("-")
        self.items_table.setRowCount(0)
        self.info_group.hide()
        self.process_btn.setEnabled(False)
        self.current_invoice = None

    def show_history(self):
        """Show returns history dialog"""
        dialog = ReturnsHistoryDialog(self.db, self.user, self)
        dialog.exec()



class ReturnsHistoryDialog(QDialog):
    """Dialog to show returns history and reprint receipts"""
    def __init__(self, db_manager, user_info, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.user = user_info
        self.setWindowTitle("سجل المرتجعات")
        self.resize(800, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Filter Section ---
        filter_group = QGroupBox("🔍 خيارات الفلترة")
        filter_group.setStyleSheet(GROUP_BOX_STYLE)
        filter_layout = QHBoxLayout()
        
        # 1. Branch Filter (For Admins)
        self.is_admin = self.user.get('role_id') == 1
        if self.is_admin:
            filter_layout.addWidget(QLabel("الفرع:"))
            self.branch_combo = QComboBox()
            self.branch_combo.setStyleSheet(INPUT_STYLE)
            self.branch_combo.addItem("الكل", None)
            
            stores = self.db.get_all_stores()
            for s in stores:
                self.branch_combo.addItem(s['store_name'], s['id'])
            filter_layout.addWidget(self.branch_combo)
        
        # 2. Date Filter
        filter_layout.addWidget(QLabel("من:"))
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet(INPUT_STYLE)
        filter_layout.addWidget(self.start_date_edit)
        
        filter_layout.addWidget(QLabel("إلى:"))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet(INPUT_STYLE)
        filter_layout.addWidget(self.end_date_edit)
        
        # 3. Return Number Search
        filter_layout.addWidget(QLabel("رقم المرتجع:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث...")
        self.search_input.setStyleSheet(INPUT_STYLE)
        filter_layout.addWidget(self.search_input)
        
        # 4. Search Button
        search_btn = QPushButton("🔎 بحث")
        search_btn.setStyleSheet(get_button_style("info"))
        search_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(search_btn)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # --- Table ---
        self.table = QTableWidget()
        
        headers = ["رقم المرتجع", "تاريخ المرتجع", "رقم الفاتورة", "الكاشير"]
        if self.is_admin:
            headers.append("الفرع")
        headers.extend(["المبلغ", "السبب"])
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ طباعة الإيصال")
        print_btn.setStyleSheet(get_button_style("info"))
        print_btn.clicked.connect(self.print_selected)
        btn_layout.addWidget(print_btn)

        save_pdf_btn = QPushButton("📄 حفظ كـ PDF")
        save_pdf_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 5px;")
        save_pdf_btn.clicked.connect(self.print_selected_as_pdf)
        btn_layout.addWidget(save_pdf_btn)
        
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet(get_button_style("secondary"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.load_data()
        
    def load_data(self):
        # 1. Get Filter Values
        if self.is_admin:
            selected_store_id = self.branch_combo.currentData()
        else:
            selected_store_id = self.user.get('store_id')
            
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        ret_num = self.search_input.text().strip()
        
        # 2. Fetch Filtered Data
        history = self.db.get_returns_history(
            store_id=selected_store_id,
            start_date=start_date,
            end_date=end_date,
            return_number=ret_num,
            limit=100
        )
        self.table.setRowCount(0)
        
        for ret in history:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(ret['return_number'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(ret['return_date'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(ret['invoice_number'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(ret['cashier_name'])))
            
            if self.is_admin:
                self.table.setItem(row, 4, QTableWidgetItem(str(ret.get('store_name', '-'))))
                self.table.setItem(row, 5, QTableWidgetItem(f"{ret['total_return_amount']:.2f}"))
                self.table.setItem(row, 6, QTableWidgetItem(str(ret['reason'])))
            else:
                self.table.setItem(row, 4, QTableWidgetItem(f"{ret['total_return_amount']:.2f}"))
                self.table.setItem(row, 5, QTableWidgetItem(str(ret['reason'])))
            
            # Store full object for printing
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, ret)
            
    def print_selected(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار مرتجع من الجدول")
            return
            
        ret_data = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        if not ret_data:
            return
            
        from utils.printer_service import PrinterService
        
        # Prepare data structured for printer service
        # We need 'items' which are fetched in get_returns_history
        
        PrinterService.print_return_receipt(
            ret_data,
            ret_data.get('items', []),
            ret_data.get('cashier_name', 'Unknown'),
            self.user.get('store_name', 'Store')
        )
    def print_selected_as_pdf(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار مرتجع من الجدول")
            return
            
        ret_data = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        if not ret_data:
            return
            
        from utils.printer_service import PrinterService
        
        try:
            if PrinterService.save_return_as_pdf(
                ret_data,
                ret_data.get('items', []),
                ret_data.get('cashier_name', 'Unknown'),
                self.user.get('store_name', 'Store')
            ):
                QMessageBox.information(self, "نجاح", "تم حفظ المرتجع كـ PDF بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", str(e))
