"""
ملف الأنماط والتصميم - Styles and Design System
تصميم عصري ونظام ألوان احترافي
"""

# لوحة الألوان (Premium Dark Theme)
COLORS = {
    'primary': '#1E293B',       # Charcoal Blue (Cards/Secondary BG)
    'bg_main': '#0F172A',       # Deep Navy (Main Background)
    'bg_input': '#111827',      # Near Black (Input Background)
    'accent': '#10B981',        # Emerald Green (Success/Actions)
    'success': '#10B981',       # Added for compatibility
    'accent_hover': '#059669',  # Darker Emerald
    'info': '#3B82F6',          # Bright Blue (Information)
    'danger': '#EF4444',        # Rose Red (Errors/Danger)
    'warning': '#F59E0B',       # Amber (Alerts)
    'border': '#334155',        # Slate Gray (Borders)
    'text_primary': '#F1F5F9',  # Off-White (Primary Text)
    'text_secondary': '#94A3B8',# Muted Slate (Secondary Text)
    'text_light': '#FFFFFF',    # Pure White
    'secondary': '#64748B',     # Slate Gray (Secondary Actions)
    'hover': '#475569'          # Hover state for secondary
}

FONTS = {
    'main': 'Inter, "Segoe UI", Roboto, Arial, sans-serif'
}

# الأزرار المتنوعة
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['info']};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 45px;
        }}
        QPushButton:hover {{
            background-color: #2563EB;
        }}
    """,
    'success': f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 45px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_hover']};
        }}
    """,
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: #DC2626;
        }}
    """,
    'warning': f"""
        QPushButton {{
            background-color: {COLORS['warning']};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: #D97706;
        }}
    """,
    'info': f"""
        QPushButton {{
            background-color: {COLORS['info']};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: #2563EB;
        }}
    """,
    'outline': f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_primary']};
            border: 2px solid {COLORS['border']};
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['text_secondary']};
        }}
    """
}

def get_icon_button_style(color_key):
    color = COLORS.get(color_key, COLORS['accent'])
    hover = "#DC2626" if color_key == 'danger' else "#059669"
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0px;
            min-height: 0px;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
    """

# الجداول
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['primary']};
        alternate-background-color: {COLORS['bg_input']};
        gridline-color: {COLORS['border']};
        border: 2px solid {COLORS['border']};
        border-radius: 16px;
        padding: 5px;
        selection-background-color: rgba(59, 130, 246, 0.2);
        selection-color: #FFFFFF;
    }}
    QHeaderView::section {{
        background-color: {COLORS['bg_input']};
        color: #FFFFFF;
        padding: 12px;
        border: none;
        font-weight: bold;
        font-size: 15px;
    }}
    QTableWidget::item {{
        padding: 8px;
        font-size: 14px;
    }}
"""

# حقول الإدخال
INPUT_STYLE = f"""
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit {{
        border: 2px solid {COLORS['border']};
        border-radius: 12px;
        padding: 5px 10px;
        font-size: 14px;
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        min-height: 45px;
    }}
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {{
        border: 2px solid {COLORS['accent']};
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_input']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['accent']};
        selection-color: white;
        color: {COLORS['text_primary']};
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 35px;
        padding-left: 10px;
    }}
    /* إخفاء أزرار الزيادة والنقصان عالمياً */
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 0px;
        height: 0px;
        border: none;
    }}
    QLineEdit:disabled {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['text_secondary']};
    }}
"""

# مجموعات البيانات
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 16px;
        margin-top: 15px;
        padding: 15px;
        font-weight: bold;
        color: {COLORS['text_primary']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 20px;
        padding: 4px 12px;
        background-color: {COLORS['primary']};
        border-radius: 8px;
    }}
"""

# التبويبات
TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 2px solid {COLORS['border']};
        border-radius: 16px;
        background-color: {COLORS['bg_main']};
        padding: 20px;
        margin-top: -1px;
    }}
    QTabBar::tab {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_secondary']};
        padding: 12px 30px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        font-weight: bold;
        margin-right: 5px;
        border: 2px solid {COLORS['border']};
        border-bottom: none;
    }}
    QTabBar::tab:selected {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['accent']};
        border-bottom: 2px solid {COLORS['bg_main']};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['primary']};
    }}
"""

# بطاقات المنتجات (للكول سنتر)
CARD_STYLE = f"""
    QFrame#ProductCard {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['border']};
        border-radius: 16px;
        padding: 15px;
    }}
    QFrame#ProductCard:hover {{
        border-color: {COLORS['accent']};
        background-color: {COLORS['bg_input']};
    }}
    QLabel#CardPrice {{
        color: {COLORS['accent']};
        font-weight: bold;
        font-size: 16px;
    }}
    QLabel#CardTitle {{
        color: {COLORS['text_primary']};
        font-weight: 500;
        font-size: 14px;
    }}
"""

LABEL_STYLE_HEADER = f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: bold;"
LABEL_STYLE_TITLE = f"color: {COLORS['text_secondary']}; font-size: 16px; font-weight: 600;"

GLOBAL_STYLE = f"""
    * {{
        font-family: {FONTS['main']};
        outline: none;
    }}
    QWidget {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['text_primary']};
    }}
    {TABLE_STYLE}
    {INPUT_STYLE}
    {TAB_STYLE}
    {GROUP_BOX_STYLE}
    {CARD_STYLE}
    
    /* ═══ Modern Scrollbar ═══ */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 4px 2px 4px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #334155, stop:1 #475569);
        min-height: 40px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #8B5CF6);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        border: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        border: none;
        background: transparent;
        height: 8px;
        margin: 0px 4px 2px 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #475569);
        min-width: 40px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06B6D4, stop:1 #8B5CF6);
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        border: none;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
"""

def get_button_style(type='primary'):
    return BUTTON_STYLES.get(type, BUTTON_STYLES['primary'])

# --- New Cashier Page Styles ---

PANEL_STYLE = f"""
    QFrame#LeftPanel, QFrame#RightPanel {{
        background-color: {COLORS['primary']};
        border-radius: 16px;
        border: 1px solid {COLORS['border']};
    }}
"""

TOTAL_DISPLAY_STYLE = f"""
    QLabel {{
        color: {COLORS['success']};
        background-color: #064E3B; /* Dark Green bg */
        border: 2px solid {COLORS['success']};
        border-radius: 12px;
        padding: 15px;
        font-weight: bold;
    }}
"""

ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        border-radius: 16px;
        font-weight: bold;
        color: white;
        border: none;
    }}
    QPushButton:pressed {{
        margin-top: 2px;
    }}
"""
