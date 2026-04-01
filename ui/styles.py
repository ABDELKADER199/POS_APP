"""
Unified design system for the POS desktop application.
Applies a professional, readable, and consistent UX across all pages.
"""

COLORS = {
    # Surfaces
    "bg_app": "#0B1220",
    "bg_panel": "#111A2E",
    "bg_elevated": "#17233B",
    "bg_input": "#0F1A30",

    # Brand and feedback
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "success": "#16A34A",
    "success_hover": "#15803D",
    "warning": "#D97706",
    "warning_hover": "#B45309",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "info": "#0891B2",
    "info_hover": "#0E7490",

    # Text and borders
    "text_primary": "#E5E7EB",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "text_dark": "#0F172A",
    "text_light": "#FFFFFF",
    "border": "#22314F",
    "border_soft": "#1A2740",

    # States
    "focus_ring": "#60A5FA",
    "selection": "rgba(37, 99, 235, 0.25)",
    "hover_surface": "#1A2A45",

    # Compatibility aliases (kept to avoid breakage in existing pages)
    "accent": "#16A34A",
    "accent_hover": "#15803D",
    "secondary": "#475569",
    "hover": "#334155",
    "bg_main": "#0B1220",
}

FONTS = {
    "main": "'Segoe UI', Tahoma, Arial",
}


def _btn(bg: str, bg_hover: str, text: str = COLORS["text_light"], border: str = "transparent") -> str:
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 9px 16px;
            min-height: 38px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
        }}
        QPushButton:pressed {{
            margin-top: 1px;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_elevated']};
            color: {COLORS['text_muted']};
            border-color: {COLORS['border_soft']};
        }}
    """


BUTTON_STYLES = {
    "primary": _btn(COLORS["primary"], COLORS["primary_hover"]),
    "success": _btn(COLORS["success"], COLORS["success_hover"]),
    "danger": _btn(COLORS["danger"], COLORS["danger_hover"]),
    "warning": _btn(COLORS["warning"], COLORS["warning_hover"]),
    "info": _btn(COLORS["info"], COLORS["info_hover"]),
    "outline": f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['text_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 9px 16px;
            min-height: 38px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['hover_surface']};
            border-color: {COLORS['focus_ring']};
        }}
        QPushButton:pressed {{
            margin-top: 1px;
        }}
    """,
}


def get_icon_button_style(color_key: str) -> str:
    color_map = {
        "danger": (COLORS["danger"], COLORS["danger_hover"]),
        "warning": (COLORS["warning"], COLORS["warning_hover"]),
        "success": (COLORS["success"], COLORS["success_hover"]),
        "primary": (COLORS["primary"], COLORS["primary_hover"]),
    }
    bg, hover = color_map.get(color_key, color_map["primary"])
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {COLORS['text_light']};
            border: none;
            border-radius: 8px;
            min-width: 28px;
            max-width: 28px;
            min-height: 28px;
            max-height: 28px;
            font-size: 14px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
    """


TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['bg_panel']};
        alternate-background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
        gridline-color: {COLORS['border_soft']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        selection-background-color: {COLORS['selection']};
        selection-color: {COLORS['text_light']};
        font-size: 12px;
    }}
    QHeaderView::section {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
        border: none;
        border-bottom: 1px solid {COLORS['border']};
        padding: 10px;
        font-size: 12px;
        font-weight: 700;
    }}
    QTableWidget::item {{
        padding: 6px;
        border-bottom: 1px solid {COLORS['border_soft']};
    }}
"""


INPUT_STYLE = f"""
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit, QDateEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 6px 10px;
        min-height: 36px;
        font-size: 12px;
    }}
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {{
        border: 1px solid {COLORS['focus_ring']};
    }}
    QLineEdit::placeholder, QTextEdit {{
        color: {COLORS['text_muted']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_panel']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['selection']};
        selection-color: {COLORS['text_light']};
    }}
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 0px;
        height: 0px;
        border: none;
    }}
    QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_muted']};
    }}
"""


GROUP_BOX_STYLE = f"""
    QGroupBox {{
        background-color: {COLORS['bg_panel']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        margin-top: 14px;
        padding: 12px;
        font-weight: 700;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 2px 8px;
        color: {COLORS['text_secondary']};
        background-color: {COLORS['bg_app']};
        border-radius: 6px;
    }}
"""


TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        top: -1px;
        background-color: {COLORS['bg_app']};
    }}
    QTabBar::tab {{
        background-color: {COLORS['bg_panel']};
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 9px 16px;
        margin-right: 4px;
        font-size: 12px;
        font-weight: 700;
        min-height: 26px;
    }}
    QTabBar::tab:selected {{
        color: {COLORS['text_light']};
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['hover_surface']};
        color: {COLORS['text_primary']};
    }}
"""


CARD_STYLE = f"""
    QFrame#ProductCard {{
        background-color: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 10px;
    }}
    QFrame#ProductCard:hover {{
        border-color: {COLORS['focus_ring']};
        background-color: {COLORS['hover_surface']};
    }}
    QLabel#CardTitle {{
        color: {COLORS['text_primary']};
        font-size: 13px;
        font-weight: 700;
    }}
    QLabel#CardPrice {{
        color: {COLORS['success']};
        font-size: 14px;
        font-weight: 800;
    }}
"""


LABEL_STYLE_HEADER = f"color: {COLORS['text_light']}; font-size: 22px; font-weight: 800;"
LABEL_STYLE_TITLE = f"color: {COLORS['text_secondary']}; font-size: 14px; font-weight: 600;"


GLOBAL_STYLE = f"""
    * {{
        font-family: {FONTS['main']};
        outline: none;
    }}

    QWidget {{
        background-color: {COLORS['bg_app']};
        color: {COLORS['text_primary']};
        font-size: 12px;
    }}

    QMainWindow, QDialog {{
        background-color: {COLORS['bg_app']};
    }}

    QLabel {{
        color: {COLORS['text_primary']};
    }}

    QMenuBar {{
        background-color: {COLORS['bg_panel']};
        color: {COLORS['text_primary']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 6px 10px;
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS['hover_surface']};
        border-radius: 6px;
    }}
    QMenu {{
        background-color: {COLORS['bg_panel']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
    }}
    QMenu::item:selected {{
        background-color: {COLORS['selection']};
    }}

    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_light']};
        border: none;
        border-radius: 10px;
        padding: 9px 16px;
        min-height: 38px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_muted']};
    }}

    {TABLE_STYLE}
    {INPUT_STYLE}
    {TAB_STYLE}
    {GROUP_BOX_STYLE}
    {CARD_STYLE}

    QCheckBox {{
        color: {COLORS['text_secondary']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['bg_input']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['border']};
        min-height: 24px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['focus_ring']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['border']};
        min-width: 24px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['focus_ring']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    QMessageBox {{
        background-color: {COLORS['bg_panel']};
    }}
    QMessageBox QLabel {{
        color: {COLORS['text_primary']};
        font-size: 13px;
    }}
"""


def get_button_style(btn_type: str = "primary") -> str:
    return BUTTON_STYLES.get(btn_type, BUTTON_STYLES["primary"])


PANEL_STYLE = f"""
    QFrame#LeftPanel, QFrame#RightPanel {{
        background-color: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
    }}
"""


TOTAL_DISPLAY_STYLE = f"""
    QLabel {{
        color: {COLORS['text_light']};
        background-color: {COLORS['primary']};
        border: 1px solid {COLORS['primary_hover']};
        border-radius: 10px;
        padding: 12px;
        font-weight: 800;
        font-size: 14px;
    }}
"""


ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        border-radius: 12px;
        font-weight: 700;
        color: {COLORS['text_light']};
        border: none;
        min-height: 36px;
    }}
    QPushButton:pressed {{
        margin-top: 1px;
    }}
"""
