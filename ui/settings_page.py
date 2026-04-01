"""
صفحة إعدادات النظام.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QGroupBox,
    QFileDialog,
    QFrame,
    QFormLayout,
    QScrollArea,
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from database_manager import DatabaseManager
from ui.styles import GLOBAL_STYLE, get_button_style, PANEL_STYLE, INPUT_STYLE, GROUP_BOX_STYLE


class SettingsPage(QWidget):
    """صفحة إعدادات النظام وإدارة الاتصال."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.user_info = {}
        self.setStyleSheet(GLOBAL_STYLE)
        self.init_ui()
        self.load_current_settings()
        self.load_connection_settings()

    def set_user(self, user_info):
        """تحديث بيانات المستخدم للتحكم بالصلاحيات داخل الصفحة."""
        self.user_info = user_info or {}
        role_id = self.user_info.get("role_id")
        can_manage_db = role_id in [99, 1]
        self.db_connection_group.setVisible(can_manage_db)
        self.db_password_group.setVisible(can_manage_db)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QLabel("إعدادات النظام")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)

        container = QFrame()
        container.setStyleSheet(PANEL_STYLE)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)

        # Store Settings
        store_group = QGroupBox("معلومات المتجر")
        store_group.setStyleSheet(GROUP_BOX_STYLE)
        store_form = QFormLayout(store_group)
        store_form.setVerticalSpacing(20)
        store_form.setContentsMargins(20, 20, 20, 20)

        self.store_name_input = QLineEdit()
        self.store_name_input.setStyleSheet(INPUT_STYLE)
        self.store_address_input = QLineEdit()
        self.store_address_input.setStyleSheet(INPUT_STYLE)
        self.store_phone_input = QLineEdit()
        self.store_phone_input.setStyleSheet(INPUT_STYLE)
        self.receipt_footer_input = QLineEdit()
        self.receipt_footer_input.setStyleSheet(INPUT_STYLE)

        store_form.addRow("اسم المتجر:", self.store_name_input)
        store_form.addRow("العنوان:", self.store_address_input)
        store_form.addRow("رقم الهاتف:", self.store_phone_input)
        store_form.addRow("تذييل الفاتورة:", self.receipt_footer_input)
        container_layout.addWidget(store_group)

        # Backup Settings
        backup_group = QGroupBox("النسخ الاحتياطي")
        backup_group.setStyleSheet(GROUP_BOX_STYLE)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setContentsMargins(20, 20, 20, 20)

        path_layout = QHBoxLayout()
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setStyleSheet(INPUT_STYLE)
        self.backup_path_input.setPlaceholderText("مسار حفظ النسخ الاحتياطية...")

        browse_btn = QPushButton("استعراض")
        browse_btn.setStyleSheet(get_button_style("info"))
        browse_btn.clicked.connect(self.browse_backup_path)

        path_layout.addWidget(self.backup_path_input)
        path_layout.addWidget(browse_btn)
        backup_layout.addLayout(path_layout)

        self.backup_now_btn = QPushButton("إنشاء نسخة احتياطية الآن")
        self.backup_now_btn.setStyleSheet(get_button_style("success"))
        self.backup_now_btn.setMinimumHeight(45)
        self.backup_now_btn.clicked.connect(self.run_backup)
        backup_layout.addWidget(self.backup_now_btn)
        container_layout.addWidget(backup_group)

        # DB Connection Group
        self.db_connection_group = QGroupBox("إدارة اتصال قاعدة البيانات (.env)")
        self.db_connection_group.setStyleSheet(GROUP_BOX_STYLE)
        db_form = QFormLayout(self.db_connection_group)
        db_form.setVerticalSpacing(15)
        db_form.setContentsMargins(20, 20, 20, 20)

        self.db_host_input = QLineEdit()
        self.db_host_input.setStyleSheet(INPUT_STYLE)
        self.db_user_input = QLineEdit()
        self.db_user_input.setStyleSheet(INPUT_STYLE)
        self.db_pass_input = QLineEdit()
        self.db_pass_input.setStyleSheet(INPUT_STYLE)
        self.db_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_name_input = QLineEdit()
        self.db_name_input.setStyleSheet(INPUT_STYLE)
        self.db_port_input = QLineEdit()
        self.db_port_input.setStyleSheet(INPUT_STYLE)
        self.db_port_input.setPlaceholderText("3306")
        self.db_ssl_mode_input = QLineEdit()
        self.db_ssl_mode_input.setStyleSheet(INPUT_STYLE)
        self.db_ssl_mode_input.setPlaceholderText("DISABLED / REQUIRED / VERIFY_CA / VERIFY_IDENTITY")
        self.db_ssl_ca_input = QLineEdit()
        self.db_ssl_ca_input.setStyleSheet(INPUT_STYLE)
        self.db_ssl_ca_input.setPlaceholderText("مسار شهادة CA (عند استخدام VERIFY_CA/VERIFY_IDENTITY)")

        db_form.addRow("المضيف (Host):", self.db_host_input)
        db_form.addRow("المنفذ (Port):", self.db_port_input)
        db_form.addRow("اسم المستخدم:", self.db_user_input)
        db_form.addRow("كلمة المرور:", self.db_pass_input)
        db_form.addRow("اسم القاعدة:", self.db_name_input)
        db_form.addRow("وضع SSL:", self.db_ssl_mode_input)
        db_form.addRow("ملف CA:", self.db_ssl_ca_input)

        db_actions = QHBoxLayout()
        self.test_db_btn = QPushButton("اختبار الاتصال")
        self.test_db_btn.setStyleSheet(get_button_style("info"))
        self.test_db_btn.clicked.connect(self.test_db_connection)

        self.save_db_btn = QPushButton("حفظ وتفعيل الاتصال")
        self.save_db_btn.setStyleSheet(get_button_style("warning"))
        self.save_db_btn.clicked.connect(self.save_db_connection)

        db_actions.addWidget(self.test_db_btn)
        db_actions.addWidget(self.save_db_btn)
        db_form.addRow("", db_actions)
        container_layout.addWidget(self.db_connection_group)

        # DB Password Change Group
        self.db_password_group = QGroupBox("تغيير كلمة مرور مستخدم قاعدة البيانات على الخادم")
        self.db_password_group.setStyleSheet(GROUP_BOX_STYLE)
        db_pass_form = QFormLayout(self.db_password_group)
        db_pass_form.setVerticalSpacing(15)
        db_pass_form.setContentsMargins(20, 20, 20, 20)

        self.server_new_pass_input = QLineEdit()
        self.server_new_pass_input.setStyleSheet(INPUT_STYLE)
        self.server_new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.server_confirm_pass_input = QLineEdit()
        self.server_confirm_pass_input.setStyleSheet(INPUT_STYLE)
        self.server_confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        db_pass_form.addRow("كلمة المرور الجديدة:", self.server_new_pass_input)
        db_pass_form.addRow("تأكيد كلمة المرور:", self.server_confirm_pass_input)

        self.change_server_pass_btn = QPushButton("تغيير كلمة المرور")
        self.change_server_pass_btn.setStyleSheet(get_button_style("danger"))
        self.change_server_pass_btn.clicked.connect(self.change_server_password)
        db_pass_form.addRow("", self.change_server_pass_btn)
        container_layout.addWidget(self.db_password_group)

        # Save Common Settings
        actions_layout = QHBoxLayout()
        self.save_btn = QPushButton("حفظ إعدادات النظام")
        self.save_btn.setStyleSheet(get_button_style("primary"))
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
        """تحميل الإعدادات العامة من قاعدة البيانات."""
        settings = self.db.get_settings()
        self.store_name_input.setText(settings.get("store_name", ""))
        self.store_address_input.setText(settings.get("store_address", ""))
        self.store_phone_input.setText(settings.get("store_phone", ""))
        self.receipt_footer_input.setText(settings.get("receipt_footer", ""))
        self.backup_path_input.setText(settings.get("backup_path", "backups"))

    def load_connection_settings(self):
        """تحميل إعدادات اتصال قاعدة البيانات الحالية."""
        profile = self.db.get_connection_profile()
        self.db_host_input.setText(profile.get("host", ""))
        self.db_user_input.setText(profile.get("user", ""))
        self.db_pass_input.setText(profile.get("password", ""))
        self.db_name_input.setText(profile.get("database", ""))
        self.db_port_input.setText(profile.get("port", "3306"))
        self.db_ssl_mode_input.setText(profile.get("ssl_mode", "DISABLED"))
        self.db_ssl_ca_input.setText(profile.get("ssl_ca", ""))

    def save_settings(self):
        """حفظ إعدادات النظام العامة."""
        settings = {
            "store_name": self.store_name_input.text(),
            "store_address": self.store_address_input.text(),
            "store_phone": self.store_phone_input.text(),
            "receipt_footer": self.receipt_footer_input.text(),
            "backup_path": self.backup_path_input.text(),
        }
        if self.db.update_settings(settings):
            QMessageBox.information(self, "نجاح", "تم حفظ إعدادات النظام بنجاح")
        else:
            QMessageBox.critical(self, "خطأ", "فشل حفظ إعدادات النظام")

    def test_db_connection(self):
        """اختبار الاتصال بقيم الحقول الحالية."""
        try:
            port = int(self.db_port_input.text().strip() or "3306")
        except ValueError:
            QMessageBox.warning(self, "تنبيه", "المنفذ يجب أن يكون رقمًا صحيحًا")
            return

        ok, message = self.db.test_connection_config(
            self.db_host_input.text().strip(),
            self.db_user_input.text().strip(),
            self.db_pass_input.text(),
            self.db_name_input.text().strip(),
            port=port,
            ssl_mode=self.db_ssl_mode_input.text().strip() or "DISABLED",
            ssl_ca=self.db_ssl_ca_input.text().strip(),
        )
        if ok:
            QMessageBox.information(self, "نجاح", message)
        else:
            QMessageBox.critical(self, "فشل الاتصال", message)

    def save_db_connection(self):
        """حفظ إعدادات الاتصال في .env وتفعيلها داخل البرنامج."""
        try:
            port = int(self.db_port_input.text().strip() or "3306")
        except ValueError:
            QMessageBox.warning(self, "تنبيه", "المنفذ يجب أن يكون رقمًا صحيحًا")
            return

        ok, message = self.db.save_connection_config(
            host=self.db_host_input.text().strip(),
            user=self.db_user_input.text().strip(),
            password=self.db_pass_input.text(),
            database=self.db_name_input.text().strip(),
            port=port,
            ssl_mode=self.db_ssl_mode_input.text().strip() or "DISABLED",
            ssl_ca=self.db_ssl_ca_input.text().strip(),
            reconnect=True,
        )
        if ok:
            QMessageBox.information(self, "نجاح", message)
        else:
            QMessageBox.critical(self, "خطأ", message)

    def change_server_password(self):
        """تغيير كلمة مرور مستخدم قاعدة البيانات على الخادم."""
        new_pass = self.server_new_pass_input.text()
        confirm = self.server_confirm_pass_input.text()

        if not new_pass:
            QMessageBox.warning(self, "تنبيه", "أدخل كلمة المرور الجديدة")
            return
        if new_pass != confirm:
            QMessageBox.warning(self, "تنبيه", "تأكيد كلمة المرور غير مطابق")
            return

        ok, message = self.db.change_server_user_password(new_pass)
        if ok:
            self.db_pass_input.setText(new_pass)
            self.server_new_pass_input.clear()
            self.server_confirm_pass_input.clear()
            QMessageBox.information(self, "نجاح", message)
        else:
            QMessageBox.critical(self, "فشل", message)

    def browse_backup_path(self):
        directory = QFileDialog.getExistingDirectory(self, "اختر مجلد النسخ الاحتياطي")
        if directory:
            self.backup_path_input.setText(directory)

    def run_backup(self):
        self.backup_now_btn.setEnabled(False)
        self.backup_now_btn.setText("جارٍ إنشاء النسخة...")
        QTimer.singleShot(100, self._execute_backup)

    def _execute_backup(self):
        current_path = self.backup_path_input.text()
        success, message = self.db.backup_database(custom_dir=current_path)
        self.backup_now_btn.setEnabled(True)
        self.backup_now_btn.setText("إنشاء نسخة احتياطية الآن")

        if success:
            QMessageBox.information(self, "نجاح", f"تم إنشاء النسخة الاحتياطية في:\n{message}")
        else:
            QMessageBox.critical(self, "خطأ", f"فشل إنشاء النسخة الاحتياطية:\n{message}")
