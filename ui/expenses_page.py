from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QScrollArea, QGroupBox, QFormLayout, 
                             QDateEdit, QComboBox, QTabWidget, QFrame, QCheckBox, QGridLayout)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from ui.styles import (INPUT_STYLE, BUTTON_STYLES, TABLE_STYLE, 
                       get_button_style, COLORS, GROUP_BOX_STYLE, CARD_STYLE, TAB_STYLE,
                       LABEL_STYLE_TITLE, LABEL_STYLE_HEADER)
from datetime import datetime, timedelta

class ExpensesPage(QWidget):
    """صفحة المصروفات وتقارير الأرباح"""
    data_changed = pyqtSignal()
    
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db = db_manager
        self.user = current_user
        self.init_ui()
        
    def set_user(self, user_info):
        self.user = user_info
        self.refresh_ui()
        
    def init_ui(self):
        # --- Scroll Area Setup ---
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        
        # Tab 1: Manage Expenses
        self.manage_tab = QWidget()
        self.setup_manage_tab()
        self.tabs.addTab(self.manage_tab, "📝 إدارة المصروفات")
        
        # Tab 2: Financial Report
        self.report_tab = QWidget()
        self.setup_report_tab()
        self.tabs.addTab(self.report_tab, "💰 تقرير الأرباح")
        
        self.main_layout.addWidget(self.tabs)
        
        scroll.setWidget(container)
        
        # Set the scroll area as the main layout of the page
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)
        
    def refresh_ui(self):
        # Refresh data when user changes or tab selected
        if self.user:
            self.update_access_control()
            self.load_expenses()
            
    def update_access_control(self):
        """Update UI based on user role"""
        if not self.user: return
        
        # Role 1 = System Admin, Role 99 = Developer, Role 3 = Cashier
        if self.user.get('role_id') in [1, 99, 3]:
            self.form_group.show()
            self.store_label.show()
            self.store_combo.show()
            self.load_stores()
        else:
            self.form_group.hide()
            self.store_label.hide()
            self.store_combo.hide()
        
    # ==================== Tab 1: Manage Expenses ====================
    def setup_manage_tab(self):
        layout = QVBoxLayout(self.manage_tab)
        
        # --- Add Expense Form (Refactored to Grid) ---
        self.form_group = QGroupBox("إضافة مصروف جديد")
        self.form_group.setStyleSheet(GROUP_BOX_STYLE)
        self.form_group.hide() # Hidden by default until we check permissions in refresh_ui
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Store Selection (Admin Only)
        self.store_label = QLabel("الفرع:")
        self.store_label.hide()
        
        self.store_combo = QComboBox()
        self.store_combo.setStyleSheet(INPUT_STYLE)
        self.store_combo.setPlaceholderText("اختر الفرع")
        self.store_combo.hide()
        
        # Expense fields
        self.exp_type_input = QComboBox()
        self.exp_type_input.setEditable(True)
        self.exp_type_input.addItems(["كهرباء", "إيجار", "رواتب", "نثريات", "صيانة", "بضاعة", "شخصي"])
        self.exp_type_input.setStyleSheet(INPUT_STYLE)
        
        self.exp_amount_input = QLineEdit()
        self.exp_amount_input.setPlaceholderText("المبلغ")
        self.exp_amount_input.setStyleSheet(INPUT_STYLE)
        
        self.exp_desc_input = QLineEdit()
        self.exp_desc_input.setPlaceholderText("وصف إضافي (اختياري)")
        self.exp_desc_input.setStyleSheet(INPUT_STYLE)
        
        self.is_personal_check = QCheckBox("مصروف شخصي (مسحوبات)")
        self.is_personal_check.setStyleSheet("font-weight: bold; color: #e53e3e;")
        
        add_btn = QPushButton("➕ إضافة مصروف")
        add_btn.setMinimumHeight(40)
        add_btn.setStyleSheet(get_button_style("success"))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_expense)
        
        # Grid Layout Organization
        form_layout.addWidget(self.store_label, 0, 0)
        form_layout.addWidget(self.store_combo, 0, 1)
        form_layout.addWidget(QLabel("النوع:"), 0, 2)
        form_layout.addWidget(self.exp_type_input, 0, 3)
        
        form_layout.addWidget(QLabel("المبلغ:"), 1, 0)
        form_layout.addWidget(self.exp_amount_input, 1, 1)
        form_layout.addWidget(QLabel("الوصف:"), 1, 2)
        form_layout.addWidget(self.exp_desc_input, 1, 3)
        
        # Bottom row for checkbox and button
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.is_personal_check)
        bottom_layout.addStretch()
        bottom_layout.addWidget(add_btn)
        form_layout.addLayout(bottom_layout, 2, 0, 1, 4)
        
        self.form_group.setLayout(form_layout)
        layout.addWidget(self.form_group)
        
        # --- Table Section ---
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 5, 0, 0)
        
        # 🔍 إضافة البحث في المصروفات
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 بحث في المصروفات:"))
        self.exp_search_input = QLineEdit()
        self.exp_search_input.setPlaceholderText("ابحث حسب النوع، الوصف أو الكاشير...")
        self.exp_search_input.setStyleSheet(INPUT_STYLE)
        self.exp_search_input.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.exp_search_input)
        search_layout.addStretch()
        table_layout.addLayout(search_layout)
        
        self.exp_table = QTableWidget()
        self.exp_table.setMinimumHeight(450) # Increased height
        self.exp_table.setColumnCount(7)
        self.exp_table.setHorizontalHeaderLabels(["ID", "التاريخ", "النوع", "شخصي؟", "المبلغ", "الوصف", "بواسطة"])
        self.exp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.exp_table.setStyleSheet(TABLE_STYLE)
        table_layout.addWidget(self.exp_table)
        
        layout.addWidget(table_container)
        
        # --- Actions ---
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(get_button_style("primary"))
        refresh_btn.clicked.connect(self.load_expenses)
        
        del_btn = QPushButton("🗑️ حذف المحدد")
        del_btn.setStyleSheet(get_button_style("danger"))
        del_btn.clicked.connect(self.delete_expense)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

    def load_stores(self):
        """Load stores for admin selection"""
        stores = self.db.get_all_stores()
        self.store_combo.clear()
        for store in stores:
            self.store_combo.addItem(store['store_name'], store['id'])
            
        if stores:
            self.store_combo.setCurrentIndex(0)
            self.load_expenses() # Trigger load after setting index
            
        # Connect signal to reload when selection changes
        try:
            self.store_combo.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.store_combo.currentIndexChanged.connect(self.load_expenses)

    def add_expense(self):
        exp_type = self.exp_type_input.currentText().strip()
        amount_text = self.exp_amount_input.text().strip()
        desc = self.exp_desc_input.text().strip()
        is_personal = self.is_personal_check.isChecked()
        
        if not exp_type or not amount_text:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال النوع والمبلغ")
            return
            
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "المبلغ يجب أن يكون رقماً")
            return
            

        # Determine Store ID
        if self.user['role_id'] in [1, 99, 3]:
            store_id = self.store_combo.currentData()
            if not store_id:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار الفرع")
                return
        else:
            # Should not happen if Add is hidden, but safety check
            store_id = self.user.get('store_id')
            if not store_id:
                 QMessageBox.warning(self, "خطأ", "لا يوجد فرع محدد للمستخدم")
                 return

        if self.db.add_expense(store_id, self.user['id'], exp_type, amount, desc, is_personal):
            QMessageBox.information(self, "نجاح", "تم إضافة المصروف")
            self.load_expenses()
            self.data_changed.emit()
            self.exp_amount_input.clear()
            self.exp_desc_input.clear()
            self.is_personal_check.setChecked(False)
        else:
            QMessageBox.critical(self, "خطأ", "فشل إضافة المصروف")

    def load_expenses(self):
        # Determine Store ID based on role
        if self.user and self.user.get('role_id') == 1:
            store_id = self.store_combo.currentData()
        else:
            store_id = self.user.get('store_id') if self.user else None
            
        if not store_id: return
        
        expenses = self.db.get_expenses(store_id)
        self.exp_table.setRowCount(0)
        for exp in expenses:
            row = self.exp_table.rowCount()
            self.exp_table.insertRow(row)
            self.exp_table.setItem(row, 0, QTableWidgetItem(str(exp['id'])))
            self.exp_table.setItem(row, 1, QTableWidgetItem(str(exp['expense_date'])))
            self.exp_table.setItem(row, 2, QTableWidgetItem(exp['expense_type']))
            
            is_personal_text = "نعم" if exp.get('is_personal') else "لا"
            self.exp_table.setItem(row, 3, QTableWidgetItem(is_personal_text))
            
            self.exp_table.setItem(row, 4, QTableWidgetItem(f"{exp['amount']:.2f}"))
            self.exp_table.setItem(row, 5, QTableWidgetItem(exp['description'] or "-"))
            self.exp_table.setItem(row, 6, QTableWidgetItem(exp['user_name']))

    def delete_expense(self):
        row = self.exp_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد مصروف للحذف")
            return
            
        exp_id = int(self.exp_table.item(row, 0).text())
        confirm = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذا المصروف؟", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db.delete_expense(exp_id):
                self.load_expenses()
                self.data_changed.emit()
            else:
                QMessageBox.critical(self, "خطأ", "فشل الحذف")

    def filter_expenses(self):
        """تصفية جدول المصروفات"""
        search_text = self.exp_search_input.text().lower()
        for row in range(self.exp_table.rowCount()):
            match = False
            # Search in: Type (Col 2), Description (Col 5), Cashier (Col 6)
            for col in [2, 5, 6]:
                item = self.exp_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.exp_table.setRowHidden(row, not match)

    # ==================== Tab 2: Financial Report ====================
    def setup_report_tab(self):
        layout = QVBoxLayout(self.report_tab)
        
        # --- Filters ---
        filter_group = QGroupBox("فترة التقرير")
        filter_group.setStyleSheet(GROUP_BOX_STYLE)
        filter_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30)) # Default last 30 days
        self.start_date.setStyleSheet(INPUT_STYLE)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet(INPUT_STYLE)
        
        gen_btn = QPushButton("📊 عرض التقرير")
        gen_btn.setStyleSheet(get_button_style("primary"))
        gen_btn.clicked.connect(self.generate_report)
        
        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(gen_btn)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # --- Report Cards Area ---
        self.report_area = QScrollArea()
        self.report_area.setWidgetResizable(True)
        self.report_area.setStyleSheet("border: none; background: transparent;")
        
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.report_area.setWidget(self.report_container)
        layout.addWidget(self.report_area)
        
    def generate_report(self):
        # Determine Store ID based on role
        # We use the same store selection from the manage tab since it's a shared context page
        if self.user and self.user.get('role_id') in [1, 99, 3]:
            store_id = self.store_combo.currentData()
            if not store_id:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار الفرع من تبويب إدارة المصروفات أولاً")
                return
        else:
            store_id = self.user.get('store_id') if self.user else None
            
        if not store_id: return
        
        s_date = self.start_date.date().toString("yyyy-MM-dd")
        e_date = self.end_date.date().toString("yyyy-MM-dd")
        
        report = self.db.get_financial_report(store_id, s_date, e_date)
        if not report:
            QMessageBox.warning(self, "خطأ", "فشل جلب البيانات")
            return
            
        # Clear previous report
        while self.report_layout.count():
            item = self.report_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # Helper to create cards
        def create_card(title, value, color, icon="💰", subtitle=""):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['primary']};
                    border-left: 4px solid {color};
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 10px;
                }}
            """)
            cl = QVBoxLayout(card)
            
            top = QHBoxLayout()
            lbl_title = QLabel(f"{icon} {title}")
            lbl_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
            
            lbl_val = QLabel(f"{value:,.2f} ج.م")
            lbl_val.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            lbl_val.setStyleSheet(f"color: {color};")
            
            top.addWidget(lbl_title)
            top.addStretch()
            top.addWidget(lbl_val)
            cl.addLayout(top)
            
            if subtitle:
                lbl_sub = QLabel(subtitle)
                lbl_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
                cl.addWidget(lbl_sub)
                
            return card

        # 1. Total Sales
        self.report_layout.addWidget(create_card(
            "إجمالي المبيعات (Revenue)", 
            report['total_sales'], 
            "#3182ce", 
            "📈",
            f"مجموع الفواتير المكتملة ({report.get('total_returns', 0):,.2f}- مرتجعات = الصافي: {report['total_sales'] - report['total_returns']:,.2f})"
        ))
        
        # 2. COGS (Cost of Goods Sold)
        net_cogs = report['total_cogs'] - report['cost_of_returns']
        self.report_layout.addWidget(create_card(
            "تكلفة البضاعة المباعة (COGS)", 
            net_cogs, 
            "#dd6b20", 
            "📦",
            "تكلفة شراء المنتجات المباعة (بعد خصم تكلفة المرتجعات)"
        ))
        
        # 3. Expenses (Operational)
        self.report_layout.addWidget(create_card(
            "المصروفات التشغيلية", 
            report['total_expenses'], 
            "#e53e3e", 
            "💸",
            "مصروفات المحل فقط (كهرباء، رواتب، ...)"
        ))
        
        # 4. Net Profit (Operational)
        profit_color = "#38a169" if report['net_profit'] >= 0 else "#e53e3e"
        self.report_layout.addWidget(create_card(
            "صافي الربح التشغيلي", 
            report['net_profit'], 
            profit_color, 
            "💎",
            "ربح المحل الفعلي = (الصافي - المصروفات التشغيلية)"
        ))
        
        # 5. Personal Withdrawals
        self.report_layout.addWidget(create_card(
            "مسحوبات شخصية (Personal)", 
            report.get('personal_expenses', 0), 
            "#805ad5", 
            "👤",
            "مبالغ تم سحبها لأغراض شخصية (لا تؤثر على ربح المحل)"
        ))
        
        # 6. Net Cash Flow
        cash_color = "#319795" if report.get('net_cash', 0) >= 0 else "#e53e3e"
        self.report_layout.addWidget(create_card(
            "صافي النقدية (Net Cash)", 
            report.get('net_cash', 0), 
            cash_color, 
            "💵",
            "المتبقي في اليد = (صافي الربح التشغيلي - المسحوبات)"
        ))
