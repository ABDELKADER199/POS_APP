"""
صفحة الإحصائيات والتقارير - Enhanced Version
Statistics and Reports Page with Charts
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, 
                             QFrame, QScrollArea, QAbstractItemView, QPushButton, 
                             QDateEdit, QMessageBox, QComboBox, QSizePolicy, QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction
from ui.styles import COLORS, TABLE_STYLE, GLOBAL_STYLE, GROUP_BOX_STYLE, get_button_style
from ui.custom_charts import SimpleBarChart, DonutChart
from datetime import datetime, timedelta
import openpyxl

class StatsPage(QWidget):
    """صفحة عرض إحصائيات المبيعات والمرتجعات مع رسوم بيانية"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.selected_store_id = None
        self.user_info = None
        self.view_sections = {} # Dictionary to store toggleable widgets
        self.init_ui()

    def set_user(self, user_info):
        """تعيين بيانات المستخدم والتحقق من الصلاحيات"""
        self.user_info = user_info
        role_id = self.user_info.get('role_id')
        
        # إظهار تقرير مبيعات الأصناف اليومية فقط لمدير النظام والمطور
        # Role 1 is Admin, Role 99 is Developer
        can_view_detailed = (role_id in [1, 99])
        
        if "مبيعات الأصناف اليومية" in self.view_sections:
            self.view_sections["مبيعات الأصناف اليومية"].setVisible(can_view_detailed)
        
    def init_ui(self):
        # المحتوى الرئيسي داخل ScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. Header & Filters
        self.create_header_section()
        
        # 2. Key Metrics Cards
        self.create_metrics_section()
        
        # 3. Charts Section
        self.create_charts_section()
        
        # 4. Branch Performance
        self.create_branch_section()
        
        # 5. Detailed Tables Grid
        self.create_detailed_tables_section()

        # Set Scroll Widget
        scroll.setWidget(container)
        
        # Main Layout (Page Wrapper)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
        # Initial Load
        self.refresh_data()

    def create_header_section(self):
        """Header and Filters"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E293B, stop:1 #0F172A);
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("📊 لوحة القيادة")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Store Filter
        header_layout.addWidget(QLabel("الفرع:", styleSheet="color: #94A3B8; font-weight: bold;"))
        self.store_combo = QComboBox()
        self.store_combo.setStyleSheet(GLOBAL_STYLE)
        self.store_combo.setMinimumWidth(150)
        self.store_combo.addItem("الكل", None)
        # Load stores (including inactive ones for historical data)
        stores = self.db.get_all_stores(include_inactive=True)
        for store in stores:
            self.store_combo.addItem(store['store_name'], store['id'])
        header_layout.addWidget(self.store_combo)

        # Date Presets
        presets = [("اليوم", self.set_filter_today), ("أسبوع", self.set_filter_week), ("شهر", self.set_filter_month)]
        for name, func in presets:
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['secondary']};
                    color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {COLORS['hover']}; }}
            """)
            btn.clicked.connect(func)
            header_layout.addWidget(btn)

        # Date Range
        self.date_from = QDateEdit(QDate.currentDate())
        self.date_to = QDateEdit(QDate.currentDate())
        for d in [self.date_from, self.date_to]:
            d.setDisplayFormat("yyyy-MM-dd")
            d.setCalendarPopup(True)
            d.setStyleSheet(GLOBAL_STYLE)
            d.setFixedWidth(110)
        
        header_layout.addWidget(QLabel("من:", styleSheet="color: #94A3B8;"))
        header_layout.addWidget(self.date_from)
        header_layout.addWidget(QLabel("إلى:", styleSheet="color: #94A3B8;"))
        header_layout.addWidget(self.date_to)
        
        # Apply Button
        apply_btn = QPushButton("تحديث")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white; border: none; padding: 6px 20px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        apply_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(apply_btn)
        
        # Customize View Button
        customize_btn = QPushButton("👁️ تخصيص")
        customize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        customize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #475569;
                color: white; border: none; padding: 6px 15px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #64748B; }}
        """)
        customize_btn.clicked.connect(self.show_customization_menu)
        header_layout.addWidget(customize_btn)

        # Quick Backup Button
        backup_btn = QPushButton("💾 نسخة احتياطية")
        backup_btn.setMinimumWidth(120)
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white; border: none; padding: 6px 15px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #4338ca; }}
        """)
        backup_btn.clicked.connect(self.quick_backup)
        header_layout.addWidget(backup_btn)
        
        self.main_layout.addWidget(header_frame)

    def quick_backup(self):
        """Execute a quick database backup"""
        success, message = self.db.backup_database()
        if success:
            QMessageBox.information(self, "نجاح", f"تم إنشاء النسخة الاحتياطية بنجاح:\n{message}")
        else:
            QMessageBox.critical(self, "خطأ", f"فشل إنشاء النسخة الاحتياطية:\n{message}")

    def create_metrics_section(self):
        """Top Grid of Cards"""
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(15)
        
        self.card_sales = self.create_metric_card("إجمالي المبيعات", "0.00", "ج.م", "#10B981", "💰")
        self.card_profit = self.create_metric_card("صافي الربح", "0.00", "ج.م", "#8B5CF6", "📈")
        self.card_atv = self.create_metric_card("متوسط البيع (ATV)", "0.00", "ج.م", "#3B82F6", "🛍️")
        self.card_margin = self.create_metric_card("هامش الربح", "0%", "", "#F59E0B", "📊")
        
        self.card_orders = self.create_metric_card("عدد الفواتير", "0", "فاتورة", "#06B6D4", "🧾")
        self.card_returns = self.create_metric_card("المرتجعات", "0.00", "ج.م", "#EF4444", "↩️")
        self.card_ret_rate = self.create_metric_card("معدل الارتجاع", "0%", "", "#F43F5E", "📉")
        self.card_retention = self.create_metric_card("الاحتفاظ بالعملاء", "0%", "", "#10B981", "👥")

        # New Cards: Snapshot Metrics (Global)
        self.card_inv_val = self.create_metric_card("إجمالي تكلفة البضاعة", "0.00", "ج.م", "#6366F1", "📦")
        self.card_total_paid_all = self.create_metric_card("إجمالي المسدد (للآن)", "0.00", "ج.م", "#10B981", "💸")
        self.card_total_debt_all = self.create_metric_card("إجمالي المديونية (للآن)", "0.00", "ج.م", "#F43F5E", "🤝")

        # Period Metric: Cash Mobility
        self.card_cash_flow = self.create_metric_card("صافي الحركة النقدية", "0.00", "ج.م", "#F59E0B", "💰")
        
        # New: Total Cash In / Out (for matching manual calculations)
        self.card_cash_in = self.create_metric_card("إجمالي المقبوضات النقدي", "0.00", "ج.م", "#10B981", "📥")
        self.card_cash_out = self.create_metric_card("إجمالي المدفوعات النقدي", "0.00", "ج.م", "#EF4444", "📤")

        # Cumulative Metric: Total Liquidity
        self.card_treasury_total = self.create_metric_card("السيولة الفعلية (حالياً)", "0.00", "ج.م", "#10B981", "🏦")

        # Row 0: Sales & Profits (المبيعات والأرباح)
        self.metrics_grid.addWidget(self.card_sales, 0, 0)
        self.metrics_grid.addWidget(self.card_profit, 0, 1)
        self.metrics_grid.addWidget(self.card_margin, 0, 2)
        self.metrics_grid.addWidget(self.card_atv, 0, 3)
        
        # Row 1: Invoices & Customers (الفواتير والعملاء)
        self.metrics_grid.addWidget(self.card_orders, 1, 0)
        self.metrics_grid.addWidget(self.card_returns, 1, 1)
        self.metrics_grid.addWidget(self.card_ret_rate, 1, 2)
        self.metrics_grid.addWidget(self.card_retention, 1, 3)

        # Row 2: Cash Movement (الحركة النقدية)
        self.metrics_grid.addWidget(self.card_cash_in, 2, 0)
        self.metrics_grid.addWidget(self.card_cash_out, 2, 1)
        self.metrics_grid.addWidget(self.card_cash_flow, 2, 2)
        self.metrics_grid.addWidget(self.card_treasury_total, 2, 3)
        
        # Row 3: Suppliers & Inventory (الموردين والمخزون)
        self.metrics_grid.addWidget(self.card_inv_val, 3, 0)
        self.metrics_grid.addWidget(self.card_total_paid_all, 3, 1)
        self.metrics_grid.addWidget(self.card_total_debt_all, 3, 2)
        
        self.main_layout.addLayout(self.metrics_grid)

    def create_metric_card(self, title, value, unit, color, icon):
        card = QFrame()
        card.setMinimumHeight(160)
        card.setMinimumWidth(220)
        
        # Use a Grid Layout to stack layers (Icon -> Overlay -> Text)
        stack_layout = QGridLayout(card)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)

        # Base card styling: Very dark navy/black
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #020617; 
                border: 2px solid {COLORS['border']};
                border-radius: 20px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                background-color: #0F172A;
            }}
        """)
        
        # Layer 1: Background Icon (Logo)
        # Using a slightly higher opacity (0.4) because it will be behind a dark overlay
        bg_icon = QLabel(icon)
        bg_icon.setStyleSheet(f"font-size: 160px; color: {color}66; background: transparent; border: none;")
        bg_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        stack_layout.addWidget(bg_icon, 0, 0)
        
        # Layer 2: Darkening Overlay (50% Black) 
        # This creates the "glass" effect where the icon is visible but darkened
        overlay = QFrame()
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-radius: 20px; border: none;")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        stack_layout.addWidget(overlay, 0, 0)
        
        # Layer 3: Content (Text: Title and Value)
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(5)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #94A3B8; font-size: 16px; font-weight: bold; background: transparent;")
        content_layout.addWidget(lbl_title)
        
        lbl_value = QLabel(f"{value} {unit}")
        lbl_value.setObjectName("value_label")
        # Bright color for the value to pop against the dark background
        lbl_value.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 900; background: transparent;")
        content_layout.addWidget(lbl_value)
        
        stack_layout.addWidget(content_widget, 0, 0)
        
        return card

    def create_charts_section(self):
        """Charts Row"""
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Sales Trend (Bar Chart)
        self.chart_trend = SimpleBarChart("📈 اتجاه المبيعات اليومية")
        container_trend = self.wrap_in_container(self.chart_trend)
        charts_layout.addWidget(container_trend, stretch=2)
        self.view_sections["مخطط المبيعات اليومية"] = container_trend
        
        # Hourly Heatmap (Bar Chart used as Heatmap)
        self.chart_hourly = SimpleBarChart("🕒 ذروة المبيعات حسب الساعة")
        container_hourly = self.wrap_in_container(self.chart_hourly)
        charts_layout.addWidget(container_hourly, stretch=2)
        self.view_sections["توزيع المبيعات بالساعة"] = container_hourly

        # Payment Method (Donut)
        self.chart_payment = DonutChart("💳 توزيع طرق الدفع")
        container_payment = self.wrap_in_container(self.chart_payment)
        charts_layout.addWidget(container_payment, stretch=1)
        self.view_sections["توزيع طرق الدفع"] = container_payment
        
        self.main_layout.addLayout(charts_layout)

    def create_branch_section(self):
        """Branch Sales Section"""
        self.branch_wrapper = QWidget()
        l = QVBoxLayout(self.branch_wrapper)
        l.setContentsMargins(0, 0, 0, 0)
        
        # Header
        lbl = QLabel("🏢 أداء الفروع")
        lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; margin-top: 10px;")
        l.addWidget(lbl)
        
        # Cards Layout
        self.branch_cards_layout = QGridLayout()
        self.branch_cards_layout.setSpacing(15)
        l.addLayout(self.branch_cards_layout)
        
        # Branch Table
        self.store_sales_table = self.create_table(["الفرع", "المبيعات", "عدد الفواتير"])
        self.branch_table_container = self.wrap_in_container(self.store_sales_table, "تفاصيل مبيعات الفروع")
        l.addWidget(self.branch_table_container)
        
        self.main_layout.addWidget(self.branch_wrapper)
        self.view_sections["أداء الفروع (الكروت والجدول)"] = self.branch_wrapper

    def create_detailed_tables_section(self):
        """Grid of tables"""
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # 1. Top Products
        self.top_products_table = self.create_table(["المنتج", "الكمية", "الإيراد"])
        c1 = self.wrap_in_container(self.top_products_table, "🏆 الأكثر مبيعاً")
        grid.addWidget(c1, 0, 0)
        self.view_sections["المنتجات الأكثر مبيعاً"] = c1
        
        # 2. Top Returned
        self.most_returned_table = self.create_table(["المنتج", "الكمية المرتجعة"])
        c2 = self.wrap_in_container(self.most_returned_table, "↩️ الأكثر ارتجاعاً")
        grid.addWidget(c2, 0, 1)
        self.view_sections["المنتجات الأكثر ارتجاعاً"] = c2
        
        # 3. Return Reasons
        self.reasons_table = self.create_table(["سبب المرتجع", "التكرار"])
        c3 = self.wrap_in_container(self.reasons_table, "📝 أسباب المرتجع")
        grid.addWidget(c3, 1, 0)
        self.view_sections["أسباب المرتجعات"] = c3
        
        # 4. Top Customers
        self.top_customers_table = self.create_table(["العميل", "الهاتف", "إجمالي الشراء", "المنتج المفضل"])
        self.top_customers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        c4 = self.wrap_in_container(self.top_customers_table, "👥 كبار العملاء")
        grid.addWidget(c4, 1, 1)
        self.view_sections["كبار العملاء (VIP)"] = c4

        # 5. Daily Product Sales per Branch
        self.product_sales_table = self.create_table(["الكود", "اسم الصنف", "الفرع", "التاريخ", "الكمية", "الإيراد", "إجمالي التكلفة"])
        self.product_sales_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Action buttons for the report
        export_layout = QHBoxLayout()
        export_excel_btn = QPushButton("📂 Excel")
        export_excel_btn.setStyleSheet(get_button_style("success"))
        export_excel_btn.setMinimumWidth(100)
        export_excel_btn.clicked.connect(self.export_to_excel)
        
        export_pdf_btn = QPushButton("📄 PDF")
        export_pdf_btn.setStyleSheet(get_button_style("danger"))
        export_pdf_btn.setMinimumWidth(100)
        export_pdf_btn.clicked.connect(self.export_to_pdf)
        
        export_layout.addWidget(export_excel_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addStretch()

        report_container = QWidget()
        report_layout = QVBoxLayout(report_container)
        report_layout.addLayout(export_layout)
        report_layout.addWidget(self.product_sales_table)

        c5 = self.wrap_in_container(report_container, "📦 مبيعات الأصناف اليومية")
        grid.addWidget(c5, 2, 0, 1, 2) # Span across 2 columns
        c5.hide() # Hide by default, shown in set_user if authorized
        self.view_sections["مبيعات الأصناف اليومية"] = c5

        # 6. Supplier Statistics
        self.supplier_stats_table = self.create_table(["المورد", "إجمالي المشتريات", "إجمالي المسدد", "الرصيد المتبقي", "عدد الأصناف", "عدد الفواتير"])
        self.supplier_stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        c6 = self.wrap_in_container(self.supplier_stats_table, "🤝 إحصائيات الموردين")
        grid.addWidget(c6, 3, 0, 1, 2) # Span across 2 columns
        self.view_sections["إحصائيات الموردين"] = c6
        
        self.main_layout.addLayout(grid)

    def show_customization_menu(self):
        """Show menu to toggle sections"""
        menu = QMenu(self)
        menu.setStyleSheet(GLOBAL_STYLE)
        
        for name, widget in self.view_sections.items():
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(not widget.isHidden())
            # Use default parameter value to capture current widget variable
            action.triggered.connect(lambda checked, w=widget: w.setVisible(checked))
            menu.addAction(action)
            
        customize_btn = self.sender()
        menu.exec(customize_btn.mapToGlobal(customize_btn.rect().bottomLeft()))

    def wrap_in_container(self, widget, title=None):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 0.5);
                border-radius: 20px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold; margin-bottom: 15px;")
            layout.addWidget(lbl)
        layout.addWidget(widget)
        return container

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Increase header height
        table.horizontalHeader().setMinimumHeight(55)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            {TABLE_STYLE}
            QTableWidget {{
                background-color: transparent;
                border: none;
            }}
            QHeaderView::section {{
                background-color: rgba(15, 23, 42, 0.8);
                color: {COLORS['success']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        table.setMinimumHeight(200)
        return table

    # --- Logic ---

    def set_filter_today(self):
        self.date_from.setDate(QDate.currentDate())
        self.date_to.setDate(QDate.currentDate())
        self.refresh_data()

    def set_filter_week(self):
        today = QDate.currentDate()
        self.date_from.setDate(today.addDays(-6))
        self.date_to.setDate(today)
        self.refresh_data()

    def set_filter_month(self):
        today = QDate.currentDate()
        self.date_from.setDate(QDate(today.year(), today.month(), 1))
        self.date_to.setDate(QDate(today.year(), today.month(), today.daysInMonth()))
        self.refresh_data()

    def refresh_data(self):
        try:
            s_date = self.date_from.date().toString("yyyy-MM-dd")
            e_date = self.date_to.date().toString("yyyy-MM-dd")
            store_id = self.store_combo.currentData() # None for All
            
            # NOTE: DB methods currently might not support store_id filter for all queries
            # For now, we will apply store_id filtering where possible or later expand DB methods
            # The current requirement was "add analytics", let's assume global or enhance later for specific store
            
            # 1. Metrics and KPIs
            stats = self.db.get_net_profit_stats(s_date, e_date, store_id)
            
            total_sales = stats.get('total_sales', 0)
            net_profit = stats.get('net_profit', 0)
            avg_ticket = stats.get('avg_ticket', 0)
            profit_margin = stats.get('profit_margin', 0)
            invoice_count = stats.get('invoice_count', 0)
            total_returns = stats.get('total_returns', 0)
            total_expenses = stats.get('total_expenses', 0)
            return_rate = stats.get('return_rate', 0)
            
            # Customer Insights
            retention = self.db.get_customer_retention_stats(s_date, e_date)
            ret_rate = retention.get('retention_rate', 0)
            
            # Count Invoices (Requires query with date)
            # We can get this from sales_by_store aggregation
            store_sales = self.db.get_sales_by_store(s_date, e_date)
            
            # Filter by store if selected
            if store_id:
                store_sales = [s for s in store_sales if s.get('store_name') == self.store_combo.currentText()]
                # If filtering by store, we should technically re-query metrics for that store only
                # For this iteration, we display global metrics if Store is "All", or we should fix Backend.
                # Let's perform a simple sum from store_sales if possible, but store_sales only has sales/count.
                # To be precise, let's keep it global for charts/trends unless we update DB to accept store_id everywhere.
            
            total_inv_count = sum(s.get('invoice_count', 0) for s in store_sales)
            
            # Update Cards
            self.card_sales.findChild(QLabel, "value_label").setText(f"{total_sales:,.2f} ج.م")
            self.card_profit.findChild(QLabel, "value_label").setText(f"{net_profit:,.2f} ج.م")
            self.card_atv.findChild(QLabel, "value_label").setText(f"{avg_ticket:,.2f} ج.م")
            self.card_margin.findChild(QLabel, "value_label").setText(f"{profit_margin:.1f}%")
            
            self.card_orders.findChild(QLabel, "value_label").setText(f"{invoice_count}")
            self.card_returns.findChild(QLabel, "value_label").setText(f"{total_returns:,.2f} ج.م")
            self.card_ret_rate.findChild(QLabel, "value_label").setText(f"{return_rate:.1f}%")
            self.card_retention.findChild(QLabel, "value_label").setText(f"{ret_rate:.1f}%")

            # Update Inventory and Debt (Branch-Specific)
            inv_val = self.db.get_inventory_valuation(store_id)
            total_paid_global = self.db.get_total_paid_to_suppliers(store_id)
            total_debt_global = self.db.get_total_supplier_debt(store_id)
            
            # Current Treasury Balance (Cumulative)
            treasury_balance = self.db.get_total_treasury_balance(store_id)
            
            # Period-based Cash Mobility from Treasury (Single Source of Truth)
            treasury_period = self.db.get_treasury_period_totals(s_date, e_date, store_id)
            cash_in = treasury_period['total_in']
            cash_out = treasury_period['total_out']
            net_cash_flow = treasury_period['net']
            
            self.card_inv_val.findChild(QLabel, "value_label").setText(f"{inv_val:,.2f} ج.م")
            self.card_total_paid_all.findChild(QLabel, "value_label").setText(f"{total_paid_global:,.2f} ج.م")
            self.card_total_debt_all.findChild(QLabel, "value_label").setText(f"{total_debt_global:,.2f} ج.م")
            self.card_cash_flow.findChild(QLabel, "value_label").setText(f"{net_cash_flow:,.2f} ج.م")
            
            # Update Cash Mobility Cards
            self.card_cash_in.findChild(QLabel, "value_label").setText(f"{cash_in:,.2f} ج.م")
            self.card_cash_out.findChild(QLabel, "value_label").setText(f"{cash_out:,.2f} ج.م")
            
            self.card_treasury_total.findChild(QLabel, "value_label").setText(f"{treasury_balance:,.2f} ج.م")
            
            # 2. Charts
            trend_data = self.db.get_daily_sales_trend(s_date, e_date)
            self.chart_trend.set_data(trend_data)
            
            # Hourly Heatmap
            hourly_data = self.db.get_hourly_sales_heatmap(s_date, e_date, store_id)
            # Adapt hourly data format for SimpleBarChart
            formatted_hourly = [{'date': f"{d['hour']}:00", 'total_sales': float(d['total_sales'] or 0)} for d in hourly_data]
            self.chart_hourly.set_data(formatted_hourly)
            
            pay_data = self.db.get_sales_by_payment_method(s_date, e_date)
            self.chart_payment.set_data(pay_data)
            
            # 3. Tables
            store_sales = self.db.get_sales_by_store(s_date, e_date)
            if store_id:
                store_sales = [s for s in store_sales if s.get('store_name') == self.store_combo.currentText()]
            
            self.populate_table(self.store_sales_table, store_sales, ['store_name', 'total_sales', 'invoice_count'])
            
            # Top Products
            top_selling = self.db.get_top_selling_products(10, s_date, e_date, store_id)
            self.populate_table(self.top_products_table, top_selling, ['product_name', 'total_qty', 'total_revenue'])
            
            # Most Returned
            most_ret = self.db.get_most_returned_products(10, s_date, e_date, store_id)
            self.populate_table(self.most_returned_table, most_ret, ['product_name', 'return_qty'])
            
            # Reasons
            reasons = self.db.get_return_reasons_summary(s_date, e_date, store_id)
            self.populate_table(self.reasons_table, reasons, ['reason', 'count'])
            
            # Customers
            customers = self.db.get_top_customers(10, s_date, e_date, store_id)
            self.populate_table(self.top_customers_table, customers, 
                                ['customer_name', 'customer_phone', 'total_spent', 'favorite_product'])

            # Product Sales Report
            prod_report = self.db.get_product_sales_report(s_date, e_date, store_id)
            self.populate_table(self.product_sales_table, prod_report,\
                                ['product_code', 'product_name', 'store_name', 'sale_date', 'total_qty', 'total_revenue', 'total_cost'])

            # Supplier Statistics
            supp_stats = self.db.get_supplier_stats()
            self.populate_table(self.supplier_stats_table, supp_stats, \
                                ['supplier_name', 'total_purchases', 'total_paid', 'balance', 'product_count', 'invoice_count'])

            # 4. Branch Cards (Refresh)
            self.refresh_branch_cards(store_sales)

        except Exception as e:
            print(f"Error refreshing stats: {e}")
            import traceback
            traceback.print_exc()

    def export_to_excel(self):
        """Export the product sales table to an Excel file"""
        if self.product_sales_table.rowCount() == 0:
            QMessageBox.warning(self, "تنبيه", "لا توجد بيانات لتصديرها")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ كملف Excel", 
            f"تقرير_مبيعات_الأصناف_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
            
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "مبيعات الأصناف اليومية"
            
            # Add Headers
            headers = ["الكود", "اسم الصنف", "الفرع", "التاريخ", "الكمية", "القيمة", "إجمالي التكلفة"]
            ws.append(headers)
            
            # Add Data
            for row in range(self.product_sales_table.rowCount()):
                row_data = []
                for col in range(self.product_sales_table.columnCount()):
                    item = self.product_sales_table.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)
                
            wb.save(file_path)
            QMessageBox.information(self, "نجاح", f"تم تصدير البيانات بنجاح إلى:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تصدير الملف: {str(e)}")

    def export_to_pdf(self):
        """Export the product sales table to a PDF file"""
        if self.product_sales_table.rowCount() == 0:
            QMessageBox.warning(self, "تنبيه", "لا توجد بيانات لتصديرها")
            return
            
        try:
            from utils.printer_service import PrinterService
            
            # Create HTML Table
            rows_html = ""
            for row in range(self.product_sales_table.rowCount()):
                rows_html += "<tr>"
                for col in range(self.product_sales_table.columnCount()):
                    item = self.product_sales_table.item(row, col)
                    rows_html += f"<td style='border: 1px solid #ccc; padding: 5px; text-align: right;'>{item.text() if item else ''}</td>"
                rows_html += "</tr>"
                
            html = f"""
            <html dir="rtl">
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="text-align: center;">تقرير مبيعات الأصناف اليومية</h2>
                <p style="text-align: center;">التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="border: 1px solid #ccc; padding: 8px;">الكود</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">اسم الصنف</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">الفرع</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">التاريخ</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">الكمية</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">القيمة</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">إجمالي التكلفة</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div style="margin-top: 20px; text-align: center; font-size: 10px; color: #666;">
                    تم الاستخراج بواسطة نظام إدارة المخازن
                </div>
            </body>
            </html>
            """
            
            # Use PrinterService internal save method (A4 width approx 595 pts)
            success = PrinterService._save_as_pdf(html, 595, filename_prefix="Report_Daily_Sales")
            
            if success:
                 QMessageBox.information(self, "نجاح", "تم إنشاء ملف PDF بنجاح")
            else:
                 QMessageBox.critical(self, "خطأ", "فشل في إنشاء ملف PDF")
                 
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تصدير PDF: {str(e)}")

    def refresh_branch_cards(self, data):
        # Clear
        while self.branch_cards_layout.count():
            item = self.branch_cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for i, store in enumerate(data):
            name = store.get('store_name', 'Unknown')
            sales = float(store.get('total_sales', 0))
            count = store.get('invoice_count', 0)
            
            color = "#10B981" if sales > 5000 else "#3B82F6" if sales > 0 else "#64748B"
            
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 8px;
                    color: white;
                }}
            """)
            card.setMinimumHeight(80)
            l = QVBoxLayout(card)
            l.addWidget(QLabel(name, styleSheet="font-weight: bold; font-size: 14px;"))
            l.addWidget(QLabel(f"{sales:,.0f} ج.م", styleSheet="font-size: 18px; font-weight: bold;"))
            l.addWidget(QLabel(f"{count} فاتورة", styleSheet="font-size: 12px; opacity: 0.8;"))
            
            self.branch_cards_layout.addWidget(card, i // 4, i % 4)

    def populate_table(self, table, data, keys):
        from decimal import Decimal
        table.setRowCount(0)
        for row_data in data:
            row_idx = table.rowCount()
            table.insertRow(row_idx)
            for col_idx, key in enumerate(keys):
                val = row_data.get(key, "")
                
                # Format numbers
                try:
                    is_num = isinstance(val, (int, float, Decimal))
                    if is_num and any(x in key for x in ['sales', 'revenue', 'spent', 'price', 'profit']):
                         val = f"{float(val):,.2f}"
                except: pass
                
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
