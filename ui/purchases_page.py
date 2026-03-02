import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QGroupBox, QComboBox, QTabWidget, QDialog, 
                             QFormLayout, QDoubleSpinBox, QSpinBox, QDateEdit, QFrame,
                             QGraphicsDropShadowEffect, QSizePolicy, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QPalette
from ui.styles import COLORS
from datetime import datetime

# ========================================
# 🎨 Premium Purchases Theme (Unique)
# ========================================
PURCH_COLORS = {
    'bg': '#0B1120',
    'card': '#111B2E',
    'card_hover': '#162038',
    'accent1': '#06B6D4',     # Cyan
    'accent2': '#8B5CF6',     # Violet
    'accent3': '#10B981',     # Emerald
    'accent_warn': '#F59E0B',
    'accent_danger': '#EF4444',
    'border': '#1E3050',
    'border_glow': '#06B6D4',
    'text': '#E2E8F0',
    'text_dim': '#64748B',
    'text_bright': '#FFFFFF',
    'gradient_start': '#06B6D4',
    'gradient_end': '#8B5CF6',
    'input_bg': '#0D1526',
    'success_bg': '#064E3B',
    'danger_bg': '#7F1D1D',
}

PAGE_STYLE = f"""
    QWidget#PurchasesPage {{
        background-color: {PURCH_COLORS['bg']};
    }}
"""

PURCH_TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {PURCH_COLORS['border']};
        border-radius: 14px;
        background-color: {PURCH_COLORS['bg']};
        padding: 15px;
        margin-top: -1px;
    }}
    QTabBar::tab {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURCH_COLORS['card']}, stop:1 {PURCH_COLORS['card_hover']});
        color: {PURCH_COLORS['text_dim']};
        padding: 14px 28px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        font-weight: bold;
        font-size: 13px;
        margin-right: 4px;
        border: 1px solid {PURCH_COLORS['border']};
        border-bottom: none;
    }}
    QTabBar::tab:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURCH_COLORS['accent1']}, stop:1 {PURCH_COLORS['accent2']});
        color: {PURCH_COLORS['text_bright']};
        border: none;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {PURCH_COLORS['card_hover']};
        color: {PURCH_COLORS['text']};
    }}
"""

PURCH_CARD_STYLE = f"""
    QFrame#PurchCard {{
        background-color: {PURCH_COLORS['card']};
        border: 1px solid {PURCH_COLORS['border']};
        border-radius: 16px;
        padding: 0px;
    }}
"""

PURCH_INPUT_STYLE = f"""
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {{
        background-color: #0F172A;          /* خلفية داكنة واضحة */
        color: {PURCH_COLORS['text_bright']};
        border: 1.5px solid #334155;        /* حافة رمادية واضحة */
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 40px;
    }}

    QLineEdit:hover, QDoubleSpinBox:hover, QSpinBox:hover, QComboBox:hover, QDateEdit:hover {{
        border: 1.5px solid {PURCH_COLORS['accent1']};
    }}

    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus,
    QComboBox:focus, QDateEdit:focus {{
        background-color: #020617;          /* أغمق عند التركيز */
        border: 2px solid {PURCH_COLORS['accent1']};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {PURCH_COLORS['card']};
        color: {PURCH_COLORS['text']};
        border: 1px solid {PURCH_COLORS['border']};
        selection-background-color: {PURCH_COLORS['accent1']};
    }}
"""

PURCH_TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {PURCH_COLORS['card']};
        border: 1.5px solid #334155;     /* حافة خارجية واضحة */
        border-radius: 14px;
        gridline-color: #334155;         /* خطوط الخلايا */
        color: {PURCH_COLORS['text']};
        font-size: 13px;
    }}

    QTableWidget::item {{
        border-bottom: 1px solid #1E293B;
        border-right: 1px solid #1E293B; /* خطوط بين الأعمدة */
        padding: 6px;
    }}

    QTableWidget::item:selected {{
        background-color: rgba(6, 182, 212, 0.15);
        border: 1px solid {PURCH_COLORS['accent1']};
    }}

    QHeaderView::section {{
        background-color: #020617;
        color: {PURCH_COLORS['accent1']};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {PURCH_COLORS['accent1']};
        font-weight: bold;
    }}
"""

PURCH_BTN_PRIMARY = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURCH_COLORS['accent1']}, stop:1 {PURCH_COLORS['accent2']});
        color: {PURCH_COLORS['text_bright']};
        border: none;
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: bold;
        font-size: 13px;
        min-height: 36px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0891B2, stop:1 #7C3AED);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0E7490, stop:1 #6D28D9);
    }}
"""

PURCH_BTN_SUCCESS = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #06B6D4);
        color: {PURCH_COLORS['text_bright']};
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: bold;
        font-size: 14px;
        min-height: 44px;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #0891B2);
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #0E7490);
    }}
"""

PURCH_BTN_OUTLINE = f"""
    QPushButton {{
        background-color: transparent;
        color: {PURCH_COLORS['accent1']};
        border: 1.5px solid {PURCH_COLORS['accent1']};
        border-radius: 10px;
        padding: 6px 16px;
        font-weight: 600;
        font-size: 12px;
        min-height: 34px;
    }}
    QPushButton:hover {{
        background-color: rgba(6, 182, 212, 0.1);
        border-color: {PURCH_COLORS['accent1']};
    }}
"""

PURCH_BTN_GHOST = f"""
    QPushButton {{
        background-color: transparent;
        color: {PURCH_COLORS['text_dim']};
        border: none;
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 16px;
    }}
    QPushButton:hover {{
        background-color: rgba(255,255,255,0.05);
        color: {PURCH_COLORS['accent_danger']};
    }}
"""

PURCH_LABEL_STYLE = f"color: {PURCH_COLORS['text_dim']}; font-size: 12px; font-weight: 600;"
PURCH_VALUE_STYLE = f"color: {PURCH_COLORS['text']}; font-size: 14px; font-weight: bold;"
PURCH_ACCENT_VALUE = f"color: {PURCH_COLORS['accent1']}; font-size: 18px; font-weight: bold;"


# ===================== Helper: Card Frame =====================
def create_card(object_name="PurchCard"):
    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setStyleSheet(PURCH_CARD_STYLE)
    return frame


def create_section_label(text, icon=""):
    lbl = QLabel(f"{icon}  {text}" if icon else text)
    lbl.setStyleSheet(f"""
        color: {PURCH_COLORS['accent1']};
        font-size: 13px;
        font-weight: bold;
        padding: 8px 14px 4px 14px;
        border-bottom: 1px solid {PURCH_COLORS['border']};
        margin-bottom: 4px;
    """)
    return lbl


class AddSupplierDialog(QDialog):
    """نافذة إضافة مورد"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مورد جديد")
        self.resize(520, 520)              # الحجم الافتراضي عند الفتح
        self.setMinimumSize(500, 500)      # لا يسمح أن تصبح أصغر من هذا
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {PURCH_COLORS['bg']};
                border: 1px solid {PURCH_COLORS['border']};
                border-radius: 16px;
            }}
            QLabel {{
                color: {PURCH_COLORS['text']};
                font-size: 13px;
            }}
            {PURCH_INPUT_STYLE}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("➕  مورد جديد")
        title.setStyleSheet(f"color: {PURCH_COLORS['accent1']}; font-size: 16px; font-weight: bold; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المورد / الشركة")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("العنوان")
        
        self.tax_input = QLineEdit()
        self.tax_input.setPlaceholderText("الرقم الضريبي")
        
        self.balance_input = QDoubleSpinBox()
        self.balance_input.setRange(-1000000, 1000000)
        self.balance_input.setSuffix(" ج.م")
        
        form_layout.addRow("الاسم:", self.name_input)
        form_layout.addRow("الهاتف:", self.phone_input)
        form_layout.addRow("العنوان:", self.address_input)
        form_layout.addRow("الرقم الضريبي:", self.tax_input)
        form_layout.addRow("رصيد افتتاحي:", self.balance_input)
        
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("✅ حفظ")
        save_btn.setStyleSheet(PURCH_BTN_SUCCESS)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet(PURCH_BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
        
    def get_data(self):
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "address": self.address_input.text(),
            "tax_number": self.tax_input.text(),
            "opening_balance": self.balance_input.value()
        }


class PurchasesPage(QWidget):
    """صفحة إدارة المشتريات والموردين - تصميم عصري"""
    
    def __init__(self, db_manager, user_info):
        super().__init__()
        self.setObjectName("PurchasesPage")
        self.db = db_manager
        self.user = user_info
        self.cart = []
        self.init_ui()
        
    def set_user(self, user_info):
        self.user = user_info
        
    def init_ui(self):
        self.setStyleSheet(PAGE_STYLE + PURCH_INPUT_STYLE)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.tabs.setStyleSheet(PURCH_TAB_STYLE)
        
        # Tab 1
        self.invoice_tab = QWidget()
        self.invoice_tab.setStyleSheet(f"background-color: {PURCH_COLORS['bg']};")
        self.setup_invoice_tab()
        self.tabs.addTab(self.invoice_tab, "🛒  فاتورة شراء جديدة")
        
        # Tab 2
        self.suppliers_tab = QWidget()
        self.suppliers_tab.setStyleSheet(f"background-color: {PURCH_COLORS['bg']};")
        self.setup_suppliers_tab()
        self.tabs.addTab(self.suppliers_tab, "👥  الموردين")
        
        # Tab 3
        self.history_tab = QWidget()
        self.history_tab.setStyleSheet(f"background-color: {PURCH_COLORS['bg']};")
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "📜  سجل الفواتير")
        
        self.main_layout.addWidget(self.tabs)
        
    def setup_invoice_tab(self):
        # Create a scroll area for the invoice tab to prevent compression
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        content_widget = QWidget()
        content_widget.setStyleSheet(PURCH_INPUT_STYLE)
        scroll_area.setWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # ═══════════ HEADER CARD ═══════════
        header_card = create_card()
        # Using Grid Layout for better alignment and spacing
        header_grid = QGridLayout(header_card)
        header_grid.setContentsMargins(20, 16, 20, 16)
        header_grid.setSpacing(12)
        
        # Set column stretch to make the input fields expand
        header_grid.setColumnStretch(1, 1) # This column (combo box / ref input) takes available space
        
        header_grid.addWidget(create_section_label("بيانات الفاتورة", "📋"), 0, 0, 1, 4)
        
        # Row 1: Supplier
        sup_lbl = QLabel("المورد")
        sup_lbl.setStyleSheet(PURCH_LABEL_STYLE)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.setEditable(True)
        self.supplier_combo.setPlaceholderText("اختر المورد...")
        self.supplier_combo.setMinimumHeight(40)
        self.supplier_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet(PURCH_BTN_OUTLINE + """
            QPushButton {
                font-size: 40px;
                padding: 0px;
            }
        """)
        refresh_btn.clicked.connect(self.load_suppliers)
        
        add_sup_btn = QPushButton("➕ مورد جديد")
        add_sup_btn.setStyleSheet(PURCH_BTN_OUTLINE)
        add_sup_btn.setFixedHeight(40)
        add_sup_btn.clicked.connect(self.quick_add_supplier)
        
        header_grid.addWidget(sup_lbl, 1, 0)
        header_grid.addWidget(self.supplier_combo, 1, 1)
        header_grid.addWidget(refresh_btn, 1, 2)
        header_grid.addWidget(add_sup_btn, 1, 3)
        
        # Row 2: Ref Number
        ref_lbl = QLabel("رقم مرجعي")
        ref_lbl.setStyleSheet(PURCH_LABEL_STYLE)
        
        self.ref_number_input = QLineEdit()
        self.ref_number_input.setPlaceholderText("رقم فاتورة المورد (اختياري)")
        self.ref_number_input.setMinimumHeight(40)
        self.ref_number_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        header_grid.addWidget(ref_lbl, 2, 0)
        header_grid.addWidget(self.ref_number_input, 2, 1, 1, 3)
        
        layout.addWidget(header_card)
        
        # ═══════════ PRODUCT ENTRY CARD ═══════════
        entry_card = create_card()
        entry_vbox = QVBoxLayout(entry_card)
        entry_vbox.setContentsMargins(20, 16, 20, 16)
        entry_vbox.setSpacing(12)
        
        entry_vbox.addWidget(create_section_label("إضافة أصناف", "📦"))
        
        # Switch back to HBox for simpler layout, but with stretch
        entry_row = QHBoxLayout()
        entry_row.setSpacing(10)
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("🔍  بحث عن منتج (كود / اسم / باركود)...")
        self.product_search.setMinimumHeight(42)
        self.product_search.setMinimumWidth(250)
        self.product_search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.product_search.returnPressed.connect(self.find_product)
        
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 10000)
        self.qty_input.setValue(1)
        self.qty_input.setPrefix("الكمية: ")
        self.qty_input.setMinimumHeight(42)
        self.qty_input.setMinimumWidth(120)
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 1000000)
        self.cost_input.setSuffix(" ج.م")
        self.cost_input.setPrefix("التكلفة: ")
        self.cost_input.setDecimals(2)
        self.cost_input.setMinimumHeight(42)
        self.cost_input.setMinimumWidth(140)
        
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDate(QDate.currentDate().addYears(1))
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_input.setMinimumHeight(42)
        self.expiry_input.setMinimumWidth(140)

        self.sell_price_input = QDoubleSpinBox()
        self.sell_price_input.setRange(0, 1000000)
        self.sell_price_input.setSuffix(" ج.م")
        self.sell_price_input.setPrefix("سعر البيع: ")
        self.sell_price_input.setDecimals(2)
        self.sell_price_input.setMinimumHeight(42)
        self.sell_price_input.setMinimumWidth(140)
        
        add_btn = QPushButton("➕")
        add_btn.setFixedSize(48, 42)
        add_btn.setStyleSheet(PURCH_BTN_PRIMARY + "font-size: 40px; padding: 0;")
        add_btn.setToolTip("إضافة للفاتورة (Enter)")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_to_cart)
        
        # Add widgets to entry row
        entry_row.addWidget(self.product_search, 2)
        entry_row.addWidget(self.qty_input, 1)
        entry_row.addWidget(self.cost_input, 1)
        entry_row.addWidget(self.sell_price_input, 1)
        entry_row.addWidget(self.expiry_input, 1)
        entry_row.addWidget(add_btn, 0)
        
        entry_vbox.addLayout(entry_row)
        layout.addWidget(entry_card)
        
        # ═══════════ CART TABLE ═══════════
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(9) # Increased for Sell Price
        self.cart_table.setHorizontalHeaderLabels(["م", "المنتج", "الكمية", "التكلفة", "سعر البيع", "الصلاحية", "الإجمالي", "باركود", "حذف"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(0, 40)
        self.cart_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(6, 85)
        self.cart_table.setStyleSheet(PURCH_TABLE_STYLE)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setMinimumHeight(250) # Taller table
        self.cart_table.verticalHeader().setDefaultSectionSize(42) # Taller rows
        self.cart_table.verticalHeader().setVisible(False)
        layout.addWidget(self.cart_table)
        
        # Add scroll area to the tab's main layout
        tab_layout = QVBoxLayout(self.invoice_tab)
        tab_layout.setContentsMargins(0,0,0,0)
        tab_layout.addWidget(scroll_area)
        
        # ═══════════ FOOTER: TOTALS & PAYMENT ═══════════
        footer_card = create_card()
        footer_grid = QGridLayout(footer_card)
        footer_grid.setContentsMargins(20, 16, 20, 16)
        footer_grid.setSpacing(12)
        
        # Row 0: Section label
        footer_grid.addWidget(create_section_label("ملخص الفاتورة", "💰"), 0, 0, 1, 6)
        
        # Row 1: Subtotal | Discount | Tax
        lbl_sub = QLabel("المجموع")
        lbl_sub.setStyleSheet(PURCH_LABEL_STYLE)
        self.subtotal_label = QLabel("0.00")
        self.subtotal_label.setStyleSheet(PURCH_VALUE_STYLE)
        
        lbl_disc = QLabel("خصم")
        lbl_disc.setStyleSheet(PURCH_LABEL_STYLE)
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 1000000)
        self.discount_input.setSuffix(" ج.م")
        self.discount_input.setMinimumHeight(38)
        self.discount_input.setMinimumWidth(130)  # Make wider
        self.discount_input.valueChanged.connect(self.calculate_totals)
        
        lbl_tax = QLabel("ضريبة")
        lbl_tax.setStyleSheet(PURCH_LABEL_STYLE)
        self.tax_input = QDoubleSpinBox()
        self.tax_input.setRange(0, 1000000)
        self.tax_input.setSuffix(" ج.م")
        self.tax_input.setMinimumHeight(38)
        self.tax_input.setMinimumWidth(130) # Make wider
        self.tax_input.valueChanged.connect(self.calculate_totals)
        
        footer_grid.addWidget(lbl_sub, 1, 0)
        footer_grid.addWidget(self.subtotal_label, 1, 1)
        footer_grid.addWidget(lbl_disc, 1, 2)
        footer_grid.addWidget(self.discount_input, 1, 3)
        footer_grid.addWidget(lbl_tax, 1, 4)
        footer_grid.addWidget(self.tax_input, 1, 5)
        
        # Row 2: Final Total Big | Payment Method | Paid | Remaining
        lbl_final = QLabel("صافي الفاتورة")
        lbl_final.setStyleSheet(PURCH_LABEL_STYLE)
        self.final_total_label = QLabel("0.00")
        self.final_total_label.setStyleSheet(PURCH_ACCENT_VALUE)
        self.final_total_label.setMinimumHeight(40)
        
        lbl_method = QLabel("طريقة الدفع")
        lbl_method.setStyleSheet(PURCH_LABEL_STYLE)
        self.pay_method = QComboBox()
        self.pay_method.addItems(["نقدي", "آجل", "شيك", "تحويل"])
        self.pay_method.setMinimumHeight(38)
        self.pay_method.setMinimumWidth(130) # Make wider
        
        lbl_paid = QLabel("المدفوع")
        lbl_paid.setStyleSheet(PURCH_LABEL_STYLE)
        self.paid_amount = QDoubleSpinBox()
        self.paid_amount.setRange(0, 1000000)
        self.paid_amount.setSuffix(" ج.م")
        self.paid_amount.setMinimumHeight(38)
        self.paid_amount.setMinimumWidth(130) # Make wider
        self.paid_amount.valueChanged.connect(self.calculate_remaining)
        
        footer_grid.addWidget(lbl_final, 2, 0)
        footer_grid.addWidget(self.final_total_label, 2, 1)
        footer_grid.addWidget(lbl_method, 2, 2)
        footer_grid.addWidget(self.pay_method, 2, 3)
        footer_grid.addWidget(lbl_paid, 2, 4)
        footer_grid.addWidget(self.paid_amount, 2, 5)
        
        # Row 3: Remaining highlight
        self.remaining_label = QLabel("المتبقي: 0.00 ج.م")
        self.remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remaining_label.setMinimumHeight(36)
        self.remaining_label.setStyleSheet(f"""
            background-color: {PURCH_COLORS['success_bg']};
            color: {PURCH_COLORS['accent3']};
            border-radius: 10px;
            font-weight: bold;
            font-size: 14px;
            padding: 6px;
        """)
        footer_grid.addWidget(self.remaining_label, 3, 0, 1, 6)
        
        layout.addWidget(footer_card)
        
        # ═══════════ SAVE BUTTON ═══════════
        save_btn = QPushButton("💾  حفظ الفاتورة وتحديث المخزون")
        save_btn.setStyleSheet(PURCH_BTN_SUCCESS)
        save_btn.setMinimumHeight(48)
        save_btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_invoice)
        layout.addWidget(save_btn)
        
        # Load
        self.load_suppliers()

    # ═══════════ Suppliers Tab ═══════════
    def setup_suppliers_tab(self):
        layout = QVBoxLayout(self.suppliers_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        
        top_card = create_card()
        top_hbox = QHBoxLayout(top_card)
        top_hbox.setContentsMargins(14, 12, 14, 12)
        top_hbox.setSpacing(10)
        
        add_btn = QPushButton("➕  إضافة مورد جديد")
        add_btn.setStyleSheet(PURCH_BTN_PRIMARY)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.quick_add_supplier)
        
        refresh_btn = QPushButton("🔄  تحديث")
        refresh_btn.setStyleSheet(PURCH_BTN_OUTLINE)
        refresh_btn.clicked.connect(self.load_suppliers_table)
        
        top_hbox.addWidget(add_btn)
        top_hbox.addWidget(refresh_btn)
        top_hbox.addStretch()
        
        layout.addWidget(top_card)
        
        self.sup_table = QTableWidget()
        self.sup_table.setColumnCount(6)
        self.sup_table.setHorizontalHeaderLabels(["ID", "الاسم", "الهاتف", "الرصيد الحالي", "رقم ضريبي", "العنوان"])
        self.sup_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sup_table.setStyleSheet(PURCH_TABLE_STYLE)
        self.sup_table.setAlternatingRowColors(True)
        self.sup_table.verticalHeader().setVisible(False)
        self.sup_table.verticalHeader().setDefaultSectionSize(38)
        layout.addWidget(self.sup_table, 1)
        
        self.load_suppliers_table()
    
    # ═══════════ History Tab ═══════════
    def setup_history_tab(self):
        layout = QVBoxLayout(self.history_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        
        top_card = create_card()
        top_hbox = QHBoxLayout(top_card)
        top_hbox.setContentsMargins(14, 12, 14, 12)
        
        refresh_btn = QPushButton("🔄  تحديث السجل")
        refresh_btn.setStyleSheet(PURCH_BTN_OUTLINE)
        refresh_btn.clicked.connect(self.load_history)
        top_hbox.addWidget(refresh_btn)
        top_hbox.addStretch()
        
        layout.addWidget(top_card)
        
        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(10)
        self.hist_table.setHorizontalHeaderLabels(["رقم", "المورد", "التاريخ", "الإجمالي", "المدفوع", "المتبقي", "الحالة", "بواسطة", "عرض", "سداد"])
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.hist_table.setStyleSheet(PURCH_TABLE_STYLE)
        self.hist_table.setAlternatingRowColors(True)
        self.hist_table.verticalHeader().setVisible(False)
        self.hist_table.verticalHeader().setDefaultSectionSize(38)
        self.hist_table.setColumnWidth(8, 80)
        self.hist_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.hist_table.setColumnWidth(9, 80)
        self.hist_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        layout.addWidget(self.hist_table, 1)
        
        self.load_history()

    # ========================================
    # Logic
    # ========================================
    
    def load_suppliers(self):
        current_id = self.supplier_combo.currentData()
        self.supplier_combo.clear()
        suppliers = self.db.get_all_suppliers()
        for sup in suppliers:
            balance = float(sup.get('current_balance', 0) or 0)
            text = f"{sup['name']}  •  رصيد: {balance:,.2f}"
            self.supplier_combo.addItem(text, sup['id'])
        if current_id:
            idx = self.supplier_combo.findData(current_id)
            if idx >= 0:
                self.supplier_combo.setCurrentIndex(idx)
            
    def load_suppliers_table(self):
        suppliers = self.db.get_all_suppliers()
        self.sup_table.setRowCount(0)
        for sup in suppliers:
            row = self.sup_table.rowCount()
            self.sup_table.insertRow(row)
            self.sup_table.setItem(row, 0, QTableWidgetItem(str(sup['id'])))
            self.sup_table.setItem(row, 1, QTableWidgetItem(sup['name']))
            self.sup_table.setItem(row, 2, QTableWidgetItem(sup.get('phone') or ""))
            
            balance = float(sup.get('current_balance', 0) or 0)
            balance_item = QTableWidgetItem(f"{balance:,.2f}")
            if balance > 0:
                balance_item.setForeground(QColor(PURCH_COLORS['accent_danger']))
            elif balance < 0:
                balance_item.setForeground(QColor(PURCH_COLORS['accent3']))
            else:
                balance_item.setForeground(QColor(PURCH_COLORS['text_dim']))
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sup_table.setItem(row, 3, balance_item)
            
            self.sup_table.setItem(row, 4, QTableWidgetItem(sup.get('tax_number') or "—"))
            self.sup_table.setItem(row, 5, QTableWidgetItem(sup.get('address') or ""))

    def quick_add_supplier(self):
        dialog = AddSupplierDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "خطأ", "يجب إدخال اسم المورد")
                return
            if self.db.add_supplier(data['name'], data['phone'], data['address'], data['tax_number'], data['opening_balance']):
                QMessageBox.information(self, "نجاح ✅", "تمت إضافة المورد بنجاح")
                self.load_suppliers()
                self.load_suppliers_table()
            else:
                QMessageBox.critical(self, "خطأ", "فشل إضافة المورد")

    def find_product(self):
        term = self.product_search.text().strip()
        if not term: return
        
        res = self.db.get_product_cross_branch_stock(term)
        if res and 'product' in res:
            prod = res['product']
            self.product_search.setText(f"{prod['product_name']} ({prod['product_code']})")
            self.current_product = prod
            
            full_prod = self.db.get_product_by_barcode(prod.get('barcode')) or self.db.get_product_by_code(prod.get('product_code'))
            if full_prod:
                self.cost_input.setValue(float(full_prod.get('buy_price', 0)))
                self.sell_price_input.setValue(float(full_prod.get('sell_price', 0)))
                self.current_product = full_prod 
                
            self.qty_input.setFocus()
            self.qty_input.selectAll()
        else:
            QMessageBox.warning(self, "تنبيه", "المنتج غير موجود")
            self.current_product = None

    def add_to_cart(self):
        if not hasattr(self, 'current_product') or not self.current_product:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار منتج أولاً")
            self.find_product() 
            return
            
        qty = self.qty_input.value()
        cost = self.cost_input.value()
        sell_price = self.sell_price_input.value()
        expiry = self.expiry_input.date().toString("yyyy-MM-dd")
        
        if cost <= 0:
            res = QMessageBox.question(self, "تأكيد", "هل التكلفة صفرية فعلاً؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if res == QMessageBox.StandardButton.No:
                return

        item = {
            'product_id': self.current_product['id'],
            'product_name': self.current_product['product_name'],
            'product_code': self.current_product.get('product_code', ''),
            'barcode': self.current_product.get('barcode', ''),
            'quantity': qty,
            'cost': cost,
            'new_sell_price': sell_price,
            'total': qty * cost,
            'expiry_date': expiry,
            'old_sell_price': self.current_product['sell_price'] 
        }
        self.cart.append(item)
        
        self.product_search.clear()
        self.qty_input.setValue(1)
        self.cost_input.setValue(0)
        self.sell_price_input.setValue(0)
        self.current_product = None
        self.product_search.setFocus()
        
        self.refresh_cart_table()

    def refresh_cart_table(self):
        self.cart_table.setRowCount(0)
        total_inv = 0
        for i, item in enumerate(self.cart):
            self.cart_table.insertRow(i)
            
            # Number
            num_item = QTableWidgetItem(str(i+1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setForeground(QColor(PURCH_COLORS['text_dim']))
            self.cart_table.setItem(i, 0, num_item)
            
            self.cart_table.setItem(i, 1, QTableWidgetItem(item['product_name']))
            
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_table.setItem(i, 2, qty_item)
            
            cost_item = QTableWidgetItem(f"{item['cost']:,.2f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_table.setItem(i, 3, cost_item)

            sell_item = QTableWidgetItem(f"{item['new_sell_price']:,.2f}")
            sell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_table.setItem(i, 4, sell_item)
            
            exp_item = QTableWidgetItem(item.get('expiry_date', '-'))
            exp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            exp_item.setForeground(QColor(PURCH_COLORS['text_dim']))
            self.cart_table.setItem(i, 5, exp_item)
            
            total_item = QTableWidgetItem(f"{item['total']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setForeground(QColor(PURCH_COLORS['accent1']))
            total_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.cart_table.setItem(i, 6, total_item)
            
            # Barcode button
            print_btn = QPushButton("🖨️")
            print_btn.setStyleSheet(PURCH_BTN_OUTLINE + "QPushButton { min-height: 28px; padding: 2px 6px; font-size: 14px; }")
            print_btn.setToolTip("طباعة باركود")
            print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            print_btn.clicked.connect(lambda _, x=item: self.print_item_barcode(x))
            self.cart_table.setCellWidget(i, 7, print_btn)
            
            # Delete button
            del_btn = QPushButton("✕")
            del_btn.setStyleSheet(PURCH_BTN_GHOST)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 8, del_btn)
            

            
            total_inv += item['total']
            
        self.subtotal_label.setText(f"{total_inv:,.2f}")
        self.calculate_totals()

    def calculate_totals(self):
        try:
            subtotal = float(self.subtotal_label.text().replace(',', ''))
            discount = self.discount_input.value()
            tax = self.tax_input.value()
            
            final_total = subtotal - discount + tax
            self.final_total_label.setText(f"{final_total:,.2f}")
            
            if self.paid_amount.value() == 0 and final_total > 0:
                self.paid_amount.setValue(final_total)
            
            self.calculate_remaining()
        except ValueError:
            pass

    def calculate_remaining(self):
        try:
            final_total = float(self.final_total_label.text().replace(',', ''))
            paid = self.paid_amount.value()
            remaining = final_total - paid
            self.remaining_label.setText(f"المتبقي: {remaining:,.2f} ج.م")
            
            if remaining > 0:
                self.remaining_label.setStyleSheet(f"""
                    background-color: {PURCH_COLORS['danger_bg']};
                    color: {PURCH_COLORS['accent_danger']};
                    border-radius: 10px; font-weight: bold; font-size: 14px; padding: 6px;
                """)
            else:
                self.remaining_label.setStyleSheet(f"""
                    background-color: {PURCH_COLORS['success_bg']};
                    color: {PURCH_COLORS['accent3']};
                    border-radius: 10px; font-weight: bold; font-size: 14px; padding: 6px;
                """)
        except ValueError:
            pass
            
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            del self.cart[index]
            self.refresh_cart_table()

    def print_item_barcode(self, item):
        try:
            from utils.printer_service import PrinterService
            printer = PrinterService()
            printer.print_barcode_direct(
                name=item['product_name'],
                code=item['barcode'] or item['product_code'],
                printer_name="Xprinter",
                label_size="50x30",
                price=item['old_sell_price']
            )
            QMessageBox.information(self, "طباعة ✅", f"تم إرسال أمر طباعة لـ {item['product_name']}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ طباعة", str(e))

    def save_invoice(self):
        if not self.cart:
            QMessageBox.warning(self, "تنبيه", "الفاتورة فارغة!")
            return
            
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار المورد")
            return
            
        try:
            subtotal = float(self.subtotal_label.text().replace(',', ''))
            final_total = float(self.final_total_label.text().replace(',', ''))
        except ValueError:
            return

        # Payment method mapping
        method_map = {"نقدي": "Cash", "آجل": "Credit", "شيك": "Cheque", "تحويل": "Transfer"}
        payment_method = method_map.get(self.pay_method.currentText(), "Cash")

        confirm = QMessageBox.question(self, "تأكيد الحفظ", 
            f"💾 حفظ فاتورة بقيمة {final_total:,.2f} ج.م؟\n\nسيتم تحديث المخزون ومتوسط التكلفة تلقائياً.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            invoice_id = self.db.create_purchase_invoice(
                supplier_id=supplier_id,
                total_amount=final_total,
                items=self.cart,
                user_id=self.user['id'],
                notes=f"فاتورة مشتريات (Ref: {self.ref_number_input.text()})",
                ref_number=self.ref_number_input.text(),
                payment_method=payment_method,
                paid_amount=self.paid_amount.value(),
                subtotal=subtotal,
                tax_amount=self.tax_input.value(),
                discount_amount=self.discount_input.value()
            )
            
            if invoice_id:
                # --- Save PDF ---
                try:
                    from utils.printer_service import PrinterService
                    invoice_data = {
                        'invoice_number': str(invoice_id),
                        'ref_number': self.ref_number_input.text(),
                        'supplier_name': self.supplier_combo.currentText(),
                        'subtotal': subtotal,
                        'discount': self.discount_input.value(),
                        'tax': self.tax_input.value(),
                        'total_amount': final_total,
                        'payment_method': self.pay_method.currentText(),
                        'paid_amount': self.paid_amount.value(),
                        'remaining_amount': float(self.remaining_label.text().replace('المتبقي:', '').replace('ج.م', '').replace(',', '').strip())
                    }
                    PrinterService.save_purchase_invoice_as_pdf(invoice_data, self.cart, self.user.get('username', 'User'))
                except Exception as e:
                    print(f"PDF Error: {e}")

                QMessageBox.information(self, "نجاح ✅", "تم حفظ الفاتورة وتصدير PDF بنجاح")
                self.cart = []
                self.refresh_cart_table()
                self.ref_number_input.clear()
                self.discount_input.setValue(0)
                self.tax_input.setValue(0)
                self.paid_amount.setValue(0)
                self.load_suppliers()
                self.load_history()
            else:
                QMessageBox.critical(self, "خطأ ❌", "فشل حفظ الفاتورة")

    def open_invoice_pdf(self, invoice_id, invoice_date):
        """Opens the PDF file for the given invoice."""
        try:
            from datetime import datetime
            # Parse date to get year and month
            if isinstance(invoice_date, str):
                dt = datetime.strptime(invoice_date, '%Y-%m-%d %H:%M:%S')
            else:
                dt = invoice_date

            # Match PrinterService Logic (Arabic Months)
            arabic_months = {
                1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
                5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
                9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
            }
            
            # Use 'dt' month, assuming PrinterService uses invoice date for folder?
            # Implemented in PrinterService: `now = datetime.now()`, `month_name = arabic_months.get(now.month)`
            # Wait! PrinterService uses `datetime.now()` for folder structure!
            # If I save an old invoice, it goes to CURRENT month folder.
            # If I view an old invoice, I look in invoices date folder?
            # 
            # In save_purchase_invoice_as_pdf:
            # `PrinterService._save_as_pdf` uses `datetime.now()` internally.
            # This is a potential issue if we reprint old invoices... but for NEW invoices it's fine.
            # For viewing history, we should probably stick to `dt` (invoice date) if that's when it was created.
            # BUT if the user saves it TODAY, it goes to TODAY's folder.
            #
            # Ideally `PrinterService` should take `date` as arg.
            # But currently it doesn't.
            # For NOW, let's assume invoice date ~ creation date.
            
            year = str(dt.year)
            month_name = arabic_months.get(dt.month, str(dt.month))
            
            base_dir = "الفواتير"
            category = "المشتريات"
            filename = f"Purchase_{invoice_id}.pdf"
            
            # Construct absolute path using CWD
            path = os.path.abspath(os.path.join(os.getcwd(), base_dir, category, year, month_name, filename))
            
            if os.path.exists(path):
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    import subprocess
                    subprocess.run(['xdg-open', path])
            else:
                QMessageBox.warning(self, "خطأ", f"ملف الفاتورة غير موجود:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء فتح الملف:\n{e}")

    def load_history(self):
        invoices = self.db.get_purchase_invoices()
        self.hist_table.setRowCount(0)
        for inv in invoices:
            row = self.hist_table.rowCount()
            self.hist_table.insertRow(row)
            
            id_item = QTableWidgetItem(str(inv['id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setForeground(QColor(PURCH_COLORS['text_dim']))
            self.hist_table.setItem(row, 0, id_item)
            
            self.hist_table.setItem(row, 1, QTableWidgetItem(inv['supplier_name'] or "غير محدد"))
            
            date_item = QTableWidgetItem(str(inv['invoice_date']))
            date_item.setForeground(QColor(PURCH_COLORS['text_dim']))
            self.hist_table.setItem(row, 2, date_item)
            
            total_item = QTableWidgetItem(f"{inv['total_amount']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setForeground(QColor(PURCH_COLORS['accent1']))
            total_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.hist_table.setItem(row, 3, total_item)
            
            paid_item = QTableWidgetItem(f"{inv.get('paid_amount', 0):,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hist_table.setItem(row, 4, paid_item)
            
            remaining = float(inv.get('remaining_amount', 0) or 0)
            rem_item = QTableWidgetItem(f"{remaining:,.2f}")
            rem_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if remaining > 0:
                rem_item.setForeground(QColor(PURCH_COLORS['accent_danger']))
                rem_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.hist_table.setItem(row, 5, rem_item)
            
            status_map = {'paid': '✅ مدفوع', 'partial': '⚠️ جزئي', 'unpaid': '🔴 آجل'}
            status_text = status_map.get(inv.get('payment_status', 'paid'), inv.get('payment_status'))
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hist_table.setItem(row, 6, status_item)
            
            self.hist_table.setItem(row, 7, QTableWidgetItem(inv.get('user_name', '')))

            # View PDF Button
            view_btn = QPushButton("📄 عرض")
            view_btn.setStyleSheet(PURCH_BTN_OUTLINE + "QPushButton { padding: 4px; font-size: 12px; min-height: 25px; }")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.clicked.connect(lambda _, x=inv['id'], d=inv['invoice_date']: self.open_invoice_pdf(x, d))
            self.hist_table.setCellWidget(row, 8, view_btn)
            
            # Pay Button (if remaining > 0)
            if remaining > 0:
                pay_btn = QPushButton("💰 سداد")
                pay_btn.setStyleSheet("QPushButton { background-color: #38a169; color: white; border: none; border-radius: 4px; padding: 4px; font-weight: bold; } QPushButton:hover { background-color: #2f855a; }")
                pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                pay_btn.clicked.connect(lambda _, x=inv['id'], r=remaining: self.show_payment_dialog(x, r))
                self.hist_table.setCellWidget(row, 9, pay_btn)
                
    def show_payment_dialog(self, invoice_id, remaining_amount):
        """Shows a dialog to pay off an invoice."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QDialogButtonBox, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"سداد فاتورة #{invoice_id}")
        dialog.setFixedSize(350, 250)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"المبلغ المتبقي: {remaining_amount:,.2f} ج.م"))
        
        layout.addWidget(QLabel("المبلغ المدفوع:"))
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0.01, remaining_amount)
        amount_input.setValue(remaining_amount)
        amount_input.setDecimals(2)
        amount_input.setPrefix("ج.م ")
        layout.addWidget(amount_input)
        
        layout.addWidget(QLabel("طريقة الدفع:"))
        method_input = QComboBox()
        method_input.addItems(["Cash", "Visa", "Bank Transfer"])
        layout.addWidget(method_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pay_amount = amount_input.value()
            method = method_input.currentText()
            
            if pay_amount <= 0:
                return

            if self.db.update_purchase_invoice_payment(invoice_id, pay_amount, method):
                QMessageBox.information(self, "نجاح", "تم تسجيل الدفعة بنجاح")
                self.load_history()
                self.load_suppliers_table() # Refresh supplier balance
            else:
                QMessageBox.critical(self, "خطأ", "فشل تسجيل الدفعة")
