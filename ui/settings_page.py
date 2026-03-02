"""
صفحة إعدادات النظام
Settings Page - Global configuration and Backup
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QMessageBox, QGroupBox, QFileDialog, QFrame, QFormLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database_manager import DatabaseManager
from ui.styles import GLOBAL_STYLE, COLORS, get_button_style, PANEL_STYLE, INPUT_STYLE, GROUP_BOX_STYLE

class SettingsPage(QWidget):
    """صفحة إعدادات النظام ومسؤول التخزين"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setStyleSheet(GLOBAL_STYLE)
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Header
        header = QLabel("⚙️ إعدادات النظام")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        # Main Container
        container = QFrame()
        container.setStyleSheet(PANEL_STYLE)
        container.setMinimumHeight(650) # Increased height
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        
        # --- Store Info Section ---
        store_group = QGroupBox("🏢 معلومات المتجر (تظهر في الفواتير)")
        store_group.setStyleSheet(GROUP_BOX_STYLE)
        store_form = QFormLayout(store_group)
        store_form.setVerticalSpacing(25) # Restore spacing
        store_form.setContentsMargins(20, 20, 20, 20)

        self.store_name_input = QLineEdit()
        self.store_name_input.setStyleSheet(INPUT_STYLE)
        self.store_address_input = QLineEdit()
        self.store_address_input.setStyleSheet(INPUT_STYLE)
        self.store_phone_input = QLineEdit()
        self.store_phone_input.setStyleSheet(INPUT_STYLE)
        self.receipt_footer_input = QLineEdit()
        self.receipt_footer_input.setStyleSheet(INPUT_STYLE)

        store_form.addRow("اسم المحل:", self.store_name_input)
        store_form.addRow("العنوان:", self.store_address_input)
        store_form.addRow("رقم الهاتف:", self.store_phone_input)
        store_form.addRow("تذييل الفاتورة:", self.receipt_footer_input)

        container_layout.addWidget(store_group)

        # --- Backup Section ---
        backup_group = QGroupBox("💾 النسخ الاحتياطي")
        backup_group.setStyleSheet(GROUP_BOX_STYLE)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setContentsMargins(20, 20, 20, 20)

        path_layout = QHBoxLayout()
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setStyleSheet(INPUT_STYLE)
        self.backup_path_input.setPlaceholderText("مسار حفظ النسخ الاحتياطية...")
        
        browse_btn = QPushButton("📁 استعراض")
        browse_btn.setStyleSheet(get_button_style('info'))
        browse_btn.clicked.connect(self.browse_backup_path)
        
        path_layout.addWidget(self.backup_path_input)
        path_layout.addWidget(browse_btn)
        
        backup_layout.addLayout(path_layout)
        
        self.backup_now_btn = QPushButton("🚀 إنشاء نسخة احتياطية الآن")
        self.backup_now_btn.setStyleSheet(get_button_style('success'))
        self.backup_now_btn.setMinimumHeight(45)
        self.backup_now_btn.clicked.connect(self.run_backup)
        backup_layout.addWidget(self.backup_now_btn)

        container_layout.addWidget(backup_group)

        # --- Footer Actions ---
        actions_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 حفظ الإعدادات")
        self.save_btn.setStyleSheet(get_button_style('primary'))
        self.save_btn.setMinimumHeight(50)
        self.save_btn.clicked.connect(self.save_settings)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.save_btn)
        actions_layout.addStretch()
        
        container_layout.addLayout(actions_layout)
        layout.addWidget(container)
        layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def load_current_settings(self):
        """تحميل الإعدادات الحالية من قاعدة البيانات"""
        settings = self.db.get_settings()
        self.store_name_input.setText(settings.get('store_name', ''))
        self.store_address_input.setText(settings.get('store_address', ''))
        self.store_phone_input.setText(settings.get('store_phone', ''))
        self.receipt_footer_input.setText(settings.get('receipt_footer', ''))
        self.backup_path_input.setText(settings.get('backup_path', 'backups'))

    def save_settings(self):
        """حفظ الإعدادات في قاعدة البيانات"""
        settings = {
            'store_name': self.store_name_input.text(),
            'store_address': self.store_address_input.text(),
            'store_phone': self.store_phone_input.text(),
            'receipt_footer': self.receipt_footer_input.text(),
            'backup_path': self.backup_path_input.text()
        }
        
        if self.db.update_settings(settings):
            QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح")
        else:
            QMessageBox.critical(self, "خطأ", "فشل حفظ الإعدادات")

    def browse_backup_path(self):
        """اختيار مجلد النسخ الاحتياطي"""
        directory = QFileDialog.getExistingDirectory(self, "اختر مجلد النسخ الاحتياطي")
        if directory:
            self.backup_path_input.setText(directory)

    def run_backup(self):
        """تشغيل عملية النسخ الاحتياطي"""
        self.backup_now_btn.setEnabled(False)
        self.backup_now_btn.setText("⏳ جاري إنشاء النسخة...")
        
        # استخدام QTimer لتجنب تجميد الواجهة (اختياري، هنا سنقوم بالتشغيل المباشر)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._execute_backup)

    def _execute_backup(self):
        current_path = self.backup_path_input.text()
        success, message = self.db.backup_database(custom_dir=current_path)
        self.backup_now_btn.setEnabled(True)
        self.backup_now_btn.setText("🚀 إنشاء نسخة احتياطية الآن")
        
        if success:
            QMessageBox.information(self, "نجاح", f"تم إنشاء النسخة الاحتياطية بنجاح في:\n{message}")
        else:
            QMessageBox.critical(self, "خطأ", f"فشل إنشاء النسخة الاحتياطية:\n{message}")
