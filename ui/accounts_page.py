"""
صفحة الحسابات - إدارة حسابات العملاء والموردين والسجل المالي
Accounts Page - Customer, Supplier accounts and Financial Ledger
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QDoubleSpinBox, QHeaderView,
    QTabWidget, QGroupBox, QFrame, QDialog, QFormLayout, QAbstractItemView, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database_manager import DatabaseManager
from ui.purchases_page import PurchasesPage
from ui.expenses_page import ExpensesPage
from ui.styles import (
    GLOBAL_STYLE, BUTTON_STYLES, get_button_style,
    COLORS, TABLE_STYLE, GROUP_BOX_STYLE,
    INPUT_STYLE, LABEL_STYLE_HEADER
)

class AccountsPage(QWidget):
    """صفحة الحسابات المركزية"""
    
    def __init__(self, user_info=None, parent=None, auto_load=True):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.db = DatabaseManager()
        self.user_info = user_info or {}
        self.auto_load = auto_load
        self._is_loaded = False
        
        # New sub-pages
        self.purchases_page = PurchasesPage(self.db, self.user_info, auto_load=auto_load)
        self.expenses_page = ExpensesPage(self.db, self.user_info, auto_load=auto_load)
        
        self.init_ui()

    def set_user(self, user_info):
        """تعيين بيانات المستخدم"""
        self.user_info = user_info or {}
        
        if self.auto_load or self._is_loaded:
            if hasattr(self, 'purchases_page') and hasattr(self.purchases_page, 'set_user'):
                self.purchases_page.set_user(self.user_info)
            if hasattr(self, 'expenses_page') and hasattr(self.expenses_page, 'set_user'):
                self.expenses_page.set_user(self.user_info)
            self.refresh_data()
        else:
            # Keep sub-pages in sync without triggering DB-heavy refresh.
            if hasattr(self, 'purchases_page'):
                self.purchases_page.user = self.user_info
            if hasattr(self, 'expenses_page'):
                self.expenses_page.user = self.user_info

    def ensure_loaded(self, force=False):
        """تحميل بيانات الحسابات عند فتح التبويب."""
        if force or not self._is_loaded:
            if hasattr(self, 'purchases_page') and hasattr(self.purchases_page, 'set_user'):
                self.purchases_page.set_user(self.user_info)
            if hasattr(self, 'expenses_page') and hasattr(self.expenses_page, 'set_user'):
                self.expenses_page.set_user(self.user_info)
            self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_layout = QHBoxLayout()
        title = QLabel("💰 إدارة الحسابات والمالية")
        title.setStyleSheet(LABEL_STYLE_HEADER)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setStyleSheet(get_button_style('info'))
        refresh_btn.clicked.connect(self.refresh_data)
        title_layout.addWidget(refresh_btn)
        
        layout.addLayout(title_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_customers_tab(), "👤 حسابات العملاء")
        self.tabs.addTab(self.create_suppliers_tab(), "🚛 حسابات الموردين")
        self.tabs.addTab(self.purchases_page, "🛒 المشتريات")
        self.tabs.addTab(self.expenses_page, "📝 المصروفات")
        self.tabs.addTab(self.create_ledger_tab(), "📑 السجل المالي")
        self.tabs.addTab(self.create_treasury_tab(), "💰 الخزينة المركزية")
        self.tabs.addTab(self.create_analytics_tab(), "📊 تحليل الديون")
        
        layout.addWidget(self.tabs)
        if self.auto_load:
            self.refresh_data()

    def create_treasury_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary
        summary = QHBoxLayout()
        self.treasury_balance_lbl = QLabel("رصيد الخزينة الحالي: 0.00")
        self.treasury_balance_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #10B981;")
        summary.addWidget(self.treasury_balance_lbl)
        summary.addStretch()
        
        add_btn = QPushButton("+ تسجيل حركة يدوي")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self.open_treasury_dialog)
        summary.addWidget(add_btn)
        layout.addLayout(summary)
        
        # Table
        self.treasury_table = QTableWidget(0, 6)
        self.treasury_table.setHorizontalHeaderLabels(["التاريخ", "النوع", "المبلغ", "المصدر", "الوصف", "المستخدم"])
        self.treasury_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.treasury_table.verticalHeader().setDefaultSectionSize(60)
        self.treasury_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.treasury_table)
        
        return widget

    def create_analytics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("📉 تحليل تقادم الديون وإحصائيات الائتمان")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3748;")
        layout.addWidget(header)
        
        # Stats summary
        stats_layout = QHBoxLayout()
        self.total_debt_stat = QLabel("إجمالي الديون: 0.00")
        self.total_debt_stat.setStyleSheet("background: #FFF5F5; padding: 10px; border-radius: 8px; color: #E53E3E; font-weight: bold;")
        stats_layout.addWidget(self.total_debt_stat)
        
        self.overdue_stat = QLabel("حسابات متأخرة (>30 يوم): 0")
        self.overdue_stat.setStyleSheet("background: #FFFFF0; padding: 10px; border-radius: 8px; color: #B7791F; font-weight: bold;")
        stats_layout.addWidget(self.overdue_stat)
        
        refresh_btn = QPushButton("🔄 تحديث التحليل")
        refresh_btn.setStyleSheet(get_button_style('primary'))
        refresh_btn.clicked.connect(self.load_aging)
        stats_layout.addWidget(refresh_btn)
        
        layout.addLayout(stats_layout)
        
        self.aging_table = QTableWidget(0, 3)
        self.aging_table.setHorizontalHeaderLabels(["الاسم", "إجمالي الدين", "أيام منذ آخر فاتورة"])
        self.aging_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.aging_table.verticalHeader().setDefaultSectionSize(60)
        self.aging_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.aging_table)
        
        export_btn = QPushButton("📄 تصدير تقرير الديون (PDF)")
        export_btn.setStyleSheet(get_button_style('info'))
        export_btn.clicked.connect(self.export_debt_report)
        layout.addWidget(export_btn)
        
        return widget

    def create_customers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search and Filters
        filter_layout = QHBoxLayout()
        self.cust_search = QLineEdit()
        self.cust_search.setPlaceholderText("🔍 بحث باسم العميل أو رقم الهاتف...")
        self.cust_search.setStyleSheet(INPUT_STYLE)
        self.cust_search.textChanged.connect(self.load_customers)
        filter_layout.addWidget(self.cust_search)
        
        self.cust_filter_debt = QComboBox()
        self.cust_filter_debt.addItems(["الكل", "عليهم مديونية", "ليس عليهم ديون"])
        self.cust_filter_debt.setStyleSheet(INPUT_STYLE)
        self.cust_filter_debt.currentIndexChanged.connect(self.load_customers)
        filter_layout.addWidget(self.cust_filter_debt)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.cust_table = QTableWidget(0, 6)
        self.cust_table.setHorizontalHeaderLabels(["المعرف", "الاسم", "الهاتف", "الرصيد", "الحد الائتماني", "إجراءات"])
        self.cust_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cust_table.verticalHeader().setDefaultSectionSize(60)
        self.cust_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cust_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.cust_table)
        
        return widget

    def create_suppliers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search
        filter_layout = QHBoxLayout()
        self.supp_search = QLineEdit()
        self.supp_search.setPlaceholderText("🔍 بحث باسم المورد...")
        self.supp_search.setStyleSheet(INPUT_STYLE)
        self.supp_search.textChanged.connect(self.load_suppliers)
        filter_layout.addWidget(self.supp_search)
        layout.addLayout(filter_layout)
        
        # Table
        self.supp_table = QTableWidget(0, 5)
        self.supp_table.setHorizontalHeaderLabels(["المعرف", "الاسم", "الهاتف", "الرصيد المستحق لهم", "إجراءات"])
        self.supp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.supp_table.verticalHeader().setDefaultSectionSize(60)
        self.supp_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.supp_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.supp_table)
        
        return widget

    def create_ledger_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary Header
        summary_layout = QHBoxLayout()
        self.total_cust_debt_lbl = QLabel("إجمالي ديون العملاء: 0.00")
        self.total_cust_debt_lbl.setStyleSheet("font-weight: bold; color: #EF4444; font-size: 16px;")
        summary_layout.addWidget(self.total_cust_debt_lbl)
        
        self.total_supp_debt_lbl = QLabel("إجمالي مستحقات الموردين: 0.00")
        self.total_supp_debt_lbl.setStyleSheet("font-weight: bold; color: #F59E0B; font-size: 16px;")
        summary_layout.addWidget(self.total_supp_debt_lbl)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("بحث:"))
        self.ledger_search = QLineEdit()
        self.ledger_search.setPlaceholderText("بحث في الوصف أو المرجع...")
        self.ledger_search.setStyleSheet(INPUT_STYLE)
        self.ledger_search.textChanged.connect(self.load_ledger)
        search_layout.addWidget(self.ledger_search)

        search_layout.addWidget(QLabel("النوع:"))
        self.ledger_type_filter = QComboBox()
        self.ledger_type_filter.addItems(["الكل", "Customer", "Supplier", "Expense", "System"])
        self.ledger_type_filter.setStyleSheet(INPUT_STYLE)
        self.ledger_type_filter.currentIndexChanged.connect(self.load_ledger)
        search_layout.addWidget(self.ledger_type_filter)
        
        search_layout.addStretch()
        
        export_btn = QPushButton("💹 تصدير Excel")
        export_btn.setStyleSheet(get_button_style('success'))
        export_btn.clicked.connect(lambda: self.export_to_excel(self.ledger_table, "سجل_العمليات_المالية"))
        search_layout.addWidget(export_btn)
        
        layout.addLayout(summary_layout)
        layout.addLayout(search_layout)
        
        # Ledger Table
        self.ledger_table = QTableWidget(0, 8) # Columns: Date, Type, Acc, Trans, Amt, Ref, Desc, Attach
        self.ledger_table.setHorizontalHeaderLabels(["التاريخ", "النوع", "الاسم/المعرف", "العملية", "المبلغ", "المرجع", "الوصف", "المرفق"])
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ledger_table.verticalHeader().setDefaultSectionSize(60)
        self.ledger_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ledger_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.ledger_table)
        
        return widget

    def refresh_data(self):
        self._is_loaded = True
        self.load_customers()
        self.load_suppliers()
        self.load_ledger()
        self.load_treasury()
        self.load_aging()
        
        # Refresh integrated pages
        if hasattr(self.purchases_page, 'ensure_loaded'):
            self.purchases_page.ensure_loaded(force=False)
        elif hasattr(self.purchases_page, 'load_suppliers'):
            self.purchases_page.load_suppliers()

        if hasattr(self.expenses_page, 'ensure_loaded'):
            self.expenses_page.ensure_loaded(force=False)
        elif hasattr(self.expenses_page, 'refresh_ui'):
            self.expenses_page.refresh_ui()

    def load_treasury(self):
        try:
            self.db.cursor.execute("SELECT * FROM treasury ORDER BY created_at DESC LIMIT 50")
            rows = self.db.cursor.fetchall()
            self.treasury_table.setRowCount(len(rows))
            
            total_in = 0
            total_out = 0
            
            for i, r in enumerate(rows):
                self.treasury_table.setItem(i, 0, QTableWidgetItem(str(r['created_at'])))
                self.treasury_table.setItem(i, 1, QTableWidgetItem(r['transaction_type']))
                
                amt = float(r['amount'])
                if r['transaction_type'] == 'In': total_in += amt
                else: total_out += amt
                
                amt_item = QTableWidgetItem(f"{amt:,.2f}")
                amt_item.setForeground(Qt.GlobalColor.green if r['transaction_type'] == 'In' else Qt.GlobalColor.red)
                self.treasury_table.setItem(i, 2, amt_item)
                
                self.treasury_table.setItem(i, 3, QTableWidgetItem(r['source_type']))
                self.treasury_table.setItem(i, 4, QTableWidgetItem(r['description'] or ""))
                self.treasury_table.setItem(i, 5, QTableWidgetItem(str(r['created_by'])))

            # Simplified balance: In - Out (Note: This is just recent 50 for table, but we should get full for balance)
            self.db.cursor.execute("SELECT SUM(CASE WHEN transaction_type='In' THEN amount ELSE -amount END) as balance FROM treasury")
            bal_res = self.db.cursor.fetchone()
            balance = float(bal_res['balance'] or 0)
            self.treasury_balance_lbl.setText(f"رصيد الخزينة الحالي: {balance:,.2f} ج.م")
            
        except Exception as e: print(f"Treasury error: {e}")

    def load_aging(self):
        aging = self.db.get_debt_aging_report()
        self.aging_table.setRowCount(len(aging))
        total_debt = 0
        overdue_count = 0
        
        for i, a in enumerate(aging):
            bal = float(a['current_balance'])
            total_debt += bal
            
            self.aging_table.setItem(i, 0, QTableWidgetItem(a['name']))
            self.aging_table.setItem(i, 1, QTableWidgetItem(f"{bal:,.2f}"))
            
            days = a['days_since_last_sale']
            if days is None: days = 0 # Safety
            
            days_item = QTableWidgetItem(str(days))
            if days > 90: days_item.setForeground(Qt.GlobalColor.red)
            elif days > 30: 
                days_item.setForeground(Qt.GlobalColor.darkYellow)
                overdue_count += 1
            self.aging_table.setItem(i, 2, days_item)
            
        self.total_debt_stat.setText(f"إجمالي الديون: {total_debt:,.2f} ج.م")
        self.overdue_stat.setText(f"حسابات متأخرة (>30 يوم): {overdue_count}")

    def load_customers(self):
        term = self.cust_search.text().lower()
        debt_filter = self.cust_filter_debt.currentText()
        
        customers = self.db.get_customer_accounts()
        # Filter
        filtered = []
        for c in customers:
            if term and term not in (c['name'].lower() or "") and term not in (c['phone'] or ""):
                continue
            balance = float(c['current_balance'] or 0)
            if debt_filter == "عليهم مديونية" and balance <= 0: continue
            if debt_filter == "ليس عليهم ديون" and balance > 0: continue
            filtered.append(c)
            
        self.cust_table.setRowCount(len(filtered))
        for i, c in enumerate(filtered):
            self.cust_table.setItem(i, 0, QTableWidgetItem(str(c['id'])))
            self.cust_table.setItem(i, 1, QTableWidgetItem(c['name']))
            self.cust_table.setItem(i, 2, QTableWidgetItem(c['phone'] or "-"))
            
            balance = float(c['current_balance'] or 0)
            balance_item = QTableWidgetItem(f"{balance:,.2f}")
            if balance > 0: balance_item.setForeground(Qt.GlobalColor.red)
            self.cust_table.setItem(i, 3, balance_item)
            
            limit = float(c.get('credit_limit') or 0)
            limit_item = QTableWidgetItem(f"{limit:,.2f}" if limit > 0 else "∞")
            self.cust_table.setItem(i, 4, limit_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 6, 6, 6)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            pay_btn = QPushButton("💰 تحصيل")
            pay_btn.setFixedHeight(32)
            pay_btn.setToolTip("تسجيل دفعة")
            pay_btn.setStyleSheet("""
                QPushButton {
                    background-color: #16a34a; color: white;
                    border: none; border-radius: 6px;
                    font-size: 12px; padding: 2px 8px;
                    min-width: 20px;
                }
                QPushButton:hover { background-color: #15803d; }
                QPushButton:pressed { background-color: #166534; }
            """)
            pay_btn.clicked.connect(lambda checked, cid=c['id'], name=c['name']: self.open_payment_dialog('Customer', cid, name))
            actions_layout.addWidget(pay_btn)
            
            hist_btn = QPushButton("📋كشف")
            hist_btn.setFixedHeight(32)
            hist_btn.setToolTip("كشف حساب")
            hist_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0284c7; color: white;
                    border: none; border-radius: 6px;
                    font-size: 12px; padding: 2px 8px;
                    min-width: 20px;
                }
                QPushButton:hover { background-color: #0369a1; }
                QPushButton:pressed { background-color: #075985; }
            """)
            hist_btn.clicked.connect(lambda checked, cid=c['id'], name=c['name']: self.view_history('Customer', cid, name))
            actions_layout.addWidget(hist_btn)

            settle_btn = QPushButton("⚖️تسوية")
            settle_btn.setFixedHeight(32)
            settle_btn.setToolTip("تسوية الرصيد")
            settle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d97706; color: white;
                    border: none; border-radius: 6px;
                    font-size: 12px; padding: 2px 8px;
                    min-width: 20px;
                }
                QPushButton:hover { background-color: #b45309; }
                QPushButton:pressed { background-color: #92400e; }
            """)
            settle_btn.clicked.connect(lambda checked, cid=c['id'], name=c['name']: self.open_settlement_dialog('Customer', cid, name))
            actions_layout.addWidget(settle_btn)

            limit_btn = QPushButton("⚙️حد")
            limit_btn.setFixedHeight(32)
            limit_btn.setToolTip("إعداد الحد الائتماني")
            limit_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent; color: #94a3b8;
                    border: 1px solid #475569; border-radius: 6px;
                    font-size: 12px; padding: 2px 8px;
                    min-width: 20px;
                }
                QPushButton:hover { background-color: #1e293b; color: white; }
                QPushButton:pressed { background-color: #0f172a; }
            """)
            limit_btn.clicked.connect(lambda checked, cid=c['id'], name=c['name'], lim=limit: self.open_limit_dialog(cid, name, lim))
            actions_layout.addWidget(limit_btn)
            
            self.cust_table.setCellWidget(i, 5, actions_widget)

    def load_suppliers(self):
        term = self.supp_search.text().lower()
        suppliers = self.db.get_all_suppliers()
        
        filtered = [s for s in suppliers if not term or term in s['name'].lower()]
        self.supp_table.setRowCount(len(filtered))
        
        for i, s in enumerate(filtered):
            self.supp_table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
            self.supp_table.setItem(i, 1, QTableWidgetItem(s['name']))
            self.supp_table.setItem(i, 2, QTableWidgetItem(s['phone'] or "-"))
            
            balance = float(s['current_balance'] or 0)
            balance_item = QTableWidgetItem(f"{balance:,.2f}")
            if balance > 0: balance_item.setForeground(Qt.GlobalColor.red)
            self.supp_table.setItem(i, 3, balance_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 6, 6, 6)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            pay_btn = QPushButton("💸 دفع للمورد")
            pay_btn.setFixedHeight(32)
            pay_btn.setStyleSheet("""
                QPushButton {
                    background-color: #c2410c; color: white;
                    border: none; border-radius: 6px;
                    font-size: 12px; padding: 2px 10px;
                    min-width: 100px;
                }
                QPushButton:hover { background-color: #9a3412; }
                QPushButton:pressed { background-color: #7c2d12; }
            """)
            pay_btn.clicked.connect(lambda checked, sid=s['id'], name=s['name']: self.open_payment_dialog('Supplier', sid, name))
            actions_layout.addWidget(pay_btn)
            
            hist_btn = QPushButton("📋 كشف الحساب")
            hist_btn.setFixedHeight(32)
            hist_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0284c7; color: white;
                    border: none; border-radius: 6px;
                    font-size: 12px; padding: 2px 10px;
                    min-width: 100px;
                }
                QPushButton:hover { background-color: #0369a1; }
                QPushButton:pressed { background-color: #075985; }
            """)
            hist_btn.clicked.connect(lambda checked, sid=s['id'], name=s['name']: self.view_history('Supplier', sid, name))
            actions_layout.addWidget(hist_btn)
            
            self.supp_table.setCellWidget(i, 4, actions_widget)

    def load_ledger(self):
        try:
            term = self.ledger_search.text().lower()
            acc_type = self.ledger_type_filter.currentText()
            
            query = """
                SELECT l.*, 
                    CASE WHEN l.account_type = 'Customer' THEN c.name 
                         WHEN l.account_type = 'Supplier' THEN s.name
                         WHEN l.account_type = 'Expense' THEN '🧾 مصروف'
                         ELSE 'System' END as name
                FROM financial_ledger l
                LEFT JOIN customers c ON l.account_type = 'Customer' AND l.account_id = c.id
                LEFT JOIN suppliers s ON l.account_type = 'Supplier' AND l.account_id = s.id
            """
            params = []
            
            conditions = []
            if term:
                conditions.append("(l.description LIKE %s OR l.reference_type LIKE %s OR c.name LIKE %s OR s.name LIKE %s)")
                params.extend([f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"])
            
            if acc_type != "الكل":
                conditions.append("l.account_type = %s")
                params.append(acc_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY l.transaction_date DESC LIMIT 100"
            
            self.db.cursor.execute(query, tuple(params))
            logs = self.db.cursor.fetchall()
            self.ledger_table.setRowCount(len(logs))
            
            total_cust_debt = 0
            total_supp_debt = 0
            
            for i, l in enumerate(logs):
                self.ledger_table.setItem(i, 0, QTableWidgetItem(str(l['transaction_date'])))
                self.ledger_table.setItem(i, 1, QTableWidgetItem(l['account_type']))
                self.ledger_table.setItem(i, 2, QTableWidgetItem(l['name'] or str(l['account_id'] or ""))) # Display name or ID
                self.ledger_table.setItem(i, 3, QTableWidgetItem(l['transaction_type']))
                
                amount = float(l['amount'])
                amount_item = QTableWidgetItem(f"{amount:,.2f}")
                if l['transaction_type'] == 'Credit': # Assuming Credit means money out/debt increase
                    amount_item.setForeground(Qt.GlobalColor.red)
                else: # Debit means money in/debt decrease
                    amount_item.setForeground(Qt.GlobalColor.green)
                self.ledger_table.setItem(i, 4, amount_item)
                
                self.ledger_table.setItem(i, 5, QTableWidgetItem(f"{l['reference_type']} #{l['reference_id'] or ''}")) # Reference column
                self.ledger_table.setItem(i, 6, QTableWidgetItem(l['description'] or "")) # Description column
                
                # Attachment button
                if l.get('attachment_path'):
                    container = QWidget()
                    btn_layout = QHBoxLayout(container)
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    view_btn = QPushButton("👁️")
                    view_btn.setToolTip("عرض المرفق")
                    view_btn.setFixedSize(32, 32)
                    from ui.styles import get_icon_button_style
                    view_btn.setStyleSheet(get_icon_button_style('info'))
                    view_btn.clicked.connect(lambda _, p=l['attachment_path']: self.view_attachment(p))
                    
                    btn_layout.addWidget(view_btn)
                    self.ledger_table.setCellWidget(i, 7, container)
                else:
                    self.ledger_table.setItem(i, 7, QTableWidgetItem("-"))

            # Calculate Totals
            self.db.cursor.execute("SELECT SUM(current_balance) as total FROM customers")
            r1 = self.db.cursor.fetchone()
            total_cust_debt = float(r1['total'] or 0)
            
            self.db.cursor.execute("SELECT SUM(current_balance) as total FROM suppliers")
            r2 = self.db.cursor.fetchone()
            total_supp_debt = float(r2['total'] or 0)
            
            self.total_cust_debt_lbl.setText(f"إجمالي ديون العملاء: {total_cust_debt:,.2f} ج.م")
            self.total_supp_debt_lbl.setText(f"إجمالي مستحقات الموردين: {total_supp_debt:,.2f} ج.م")
            
        except Exception as e:
            print(f"Ledger Load Error: {e}")

    def open_payment_dialog(self, account_type, account_id, name):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"تسجيل عملية دفع/تحصيل: {name}")
        dialog.setFixedWidth(400)
        layout = QFormLayout(dialog)
        
        amt_spin = QDoubleSpinBox()
        amt_spin.setRange(0.01, 1000000)
        amt_spin.setSuffix(" ج.م")
        amt_spin.setStyleSheet(INPUT_STYLE)
        layout.addRow("المبلغ:", amt_spin)
        
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("الوصف (مثلاً: دفعة تحت الحساب)")
        desc_input.setStyleSheet(INPUT_STYLE)
        layout.addRow("الوصف:", desc_input)
        
        # Attachment
        file_layout = QHBoxLayout()
        self.selected_file_path = ""
        file_path_lbl = QLabel("لا يوجد ملف")
        browse_btn = QPushButton("📁 اختر صورة وصل")
        browse_btn.setStyleSheet(get_button_style('outline'))
        browse_btn.clicked.connect(lambda: self.browse_file(file_path_lbl))
        file_layout.addWidget(file_path_lbl)
        file_layout.addWidget(browse_btn)
        layout.addRow("المرفق:", file_layout)
        
        btn = QPushButton("حفظ العملية")
        btn.setStyleSheet(get_button_style('success'))
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = amt_spin.value()
            desc = desc_input.text()
            user_id = self.user_info.get('id', 1)
            
            res = self.db.record_payment(account_type, account_id, amount, user_id, desc)
            if res:
                if self.selected_file_path:
                    # Update last ledger entry with file path
                    self.db.cursor.execute("SELECT MAX(id) as last_id FROM financial_ledger")
                    last_id = self.db.cursor.fetchone()['last_id']
                    self.db.cursor.execute("UPDATE financial_ledger SET attachment_path = %s WHERE id = %s", (self.selected_file_path, last_id))
                    self.db.conn.commit()
                QMessageBox.information(self, "تم", "تم تسجيل العملية بنجاح وتحديث الرصيد")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "خطأ", "فشل تسجيل العملية")

    def browse_file(self, label):
        path, _ = QFileDialog.getOpenFileName(self, "اختر ملف", "", "Images (*.png *.jpg *.jpeg *.pdf);;All Files (*)")
        if path:
            self.selected_file_path = path
            label.setText(os.path.basename(path))

    def view_attachment(self, path):
        if os.path.exists(path):
            try:
                os.startfile(path) # For Windows
            except AttributeError:
                import subprocess
                subprocess.call(['open', path]) # For macOS
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل فتح الملف: {e}")
        else:
            QMessageBox.warning(self, "خطأ", "الملف غير موجود")

    def view_history(self, account_type, account_id, name):
        history = self.db.get_account_history(account_type, account_id)
        if not history:
            QMessageBox.information(self, "تنبيه", "لا يوجد سجل عمليات لهذا الحساب")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"كشف حساب: {name}")
        dialog.resize(800, 500)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget(len(history), 5)
        table.setHorizontalHeaderLabels(["التاريخ", "النوع", "المبلغ", "المرجع", "الوصف"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet(TABLE_STYLE)
        
        for i, h in enumerate(history):
            table.setItem(i, 0, QTableWidgetItem(str(h['transaction_date'])))
            table.setItem(i, 1, QTableWidgetItem(h['transaction_type']))
            table.setItem(i, 2, QTableWidgetItem(f"{float(h['amount']):,.2f}"))
            table.setItem(i, 3, QTableWidgetItem(f"{h['reference_type']} #{h['reference_id'] or ''}"))
            table.setItem(i, 4, QTableWidgetItem(h['description'] or ""))
            
        layout.addWidget(table)
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def open_limit_dialog(self, cid, name, current_limit):
        val, ok = QDoubleSpinBox(), False
        dialog = QDialog(self)
        dialog.setWindowTitle(f"الحد الائتماني: {name}")
        layout = QFormLayout(dialog)
        
        limit_spin = QDoubleSpinBox()
        limit_spin.setRange(0, 1000000)
        limit_spin.setValue(current_limit)
        limit_spin.setStyleSheet(INPUT_STYLE)
        layout.addRow("الحد الائتماني المسموح به:", limit_spin)
        
        btns = QHBoxLayout()
        save = QPushButton("حفظ")
        save.setStyleSheet(get_button_style('success'))
        save.clicked.connect(dialog.accept)
        btns.addWidget(save)
        layout.addRow(btns)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_limit = limit_spin.value()
            self.db.cursor.execute("UPDATE customers SET credit_limit = %s WHERE id = %s", (new_limit, cid))
            self.db.conn.commit()
            self.refresh_data()

    def open_settlement_dialog(self, account_type, account_id, name):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"تسوية حساب: {name}")
        dialog.setFixedWidth(400)
        layout = QFormLayout(dialog)
        
        amt_spin = QDoubleSpinBox()
        amt_spin.setRange(0.01, 1000000)
        amt_spin.setSuffix(" ج.م")
        amt_spin.setStyleSheet(INPUT_STYLE)
        layout.addRow("مبلغ التسوية (خصم من الدين):", amt_spin)
        
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("سبب التسوية (مثلاً: خصم تعثر سداد)")
        desc_input.setStyleSheet(INPUT_STYLE)
        layout.addRow("السبب:", desc_input)
        
        # Attachment
        file_layout = QHBoxLayout()
        self.selected_file_path = ""
        file_path_lbl = QLabel("لا يوجد ملف")
        browse_btn = QPushButton("📁 أرفق مستند")
        browse_btn.setStyleSheet(get_button_style('outline'))
        browse_btn.clicked.connect(lambda: self.browse_file(file_path_lbl))
        file_layout.addWidget(file_path_lbl)
        file_layout.addWidget(browse_btn)
        layout.addRow("المرفق:", file_layout)
        
        btn = QPushButton("تنفيذ التسوية")
        btn.setStyleSheet(get_button_style('warning'))
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_id = self.user_info.get('id', 1)
            if self.db.record_settlement(account_type, account_id, amt_spin.value(), desc_input.text(), user_id):
                if self.selected_file_path:
                    # Update last ledger entry with file path
                    self.db.cursor.execute("SELECT MAX(id) as last_id FROM financial_ledger")
                    last_id = self.db.cursor.fetchone()['last_id']
                    self.db.cursor.execute("UPDATE financial_ledger SET attachment_path = %s WHERE id = %s", (self.selected_file_path, last_id))
                    self.db.conn.commit()
                QMessageBox.information(self, "نجاح", "تمت التسوية بنجاح")
                self.refresh_data()

    def open_treasury_dialog(self):
        # Implementation for manual treasury entry (Simplified)
        dialog = QDialog(self)
        dialog.setWindowTitle("تسجيل حركة خزينة")
        layout = QFormLayout(dialog)
        
        type_cb = QComboBox()
        type_cb.addItems(["In", "Out"])
        layout.addRow("النوع:", type_cb)
        
        amt = QDoubleSpinBox()
        amt.setRange(1, 1000000)
        layout.addRow("المبلغ:", amt)
        
        desc = QLineEdit()
        layout.addRow("الوصف:", desc)
        
        btn = QPushButton("حفظ")
        btn.clicked.connect(dialog.accept)
        layout.addRow(btn)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.db.record_treasury_transaction(
                self.user_info.get('store_id', 1),
                type_cb.currentText(),
                amt.value(),
                'Adjustment',
                None,
                desc.text(),
                self.user_info.get('id', 1)
            )
            self.refresh_data()

    def export_debt_report(self):
        self.export_to_excel(self.aging_table, "تقرير_تقادم_الديون")

    def export_to_excel(self, table_widget, filename_prefix):
        try:
            import pandas as pd
            from PyQt6.QtWidgets import QFileDialog
            
            # Extract data from QTableWidget
            data = []
            headers = []
            for j in range(table_widget.columnCount()):
                headers.append(table_widget.horizontalHeaderItem(j).text())
                
            for i in range(table_widget.rowCount()):
                row_data = []
                for j in range(table_widget.columnCount()):
                    item = table_widget.item(i, j)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
                
            df = pd.DataFrame(data, columns=headers)
            
            # Save dialog
            path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف Excel", f"{filename_prefix}.xlsx", "Excel Files (*.xlsx)")
            if path:
                df.to_excel(path, index=False)
                QMessageBox.information(self, "نجاح", f"تم حفظ الملف بنجاح في:\n{path}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصدير", f"حدث خطأ أثناء تصدير الملف: {str(e)}")
