from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles import INPUT_STYLE, get_button_style, COLORS
from utils.license_manager import LicenseManager


class ActivationPage(QWidget):
    """شاشة تفعيل النسخة."""

    activation_success = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.hw_id = LicenseManager.get_hardware_id()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("activationPage")
        self.setStyleSheet(
            """
            QWidget#activationPage {
                background: qradialgradient(
                    cx: 0.15, cy: 0.1, radius: 1.2,
                    fx: 0.1, fy: 0.05,
                    stop: 0 #1E3A8A,
                    stop: 0.35 #0F274E,
                    stop: 1 #070D1A
                );
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(24, 24, 24, 24)

        panel = QFrame()
        panel.setObjectName("activationPanel")
        panel.setFixedWidth(560)
        panel.setStyleSheet(
            """
            QFrame#activationPanel {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.7);
                border-radius: 24px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: #0F172A;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(45)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.GlobalColor.black)
        panel.setGraphicsEffect(shadow)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(40, 34, 40, 34)
        panel_layout.setSpacing(14)

        title = QLabel("تفعيل نسخة البرنامج")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))
        panel_layout.addWidget(title)

        subtitle = QLabel("أرسل كود الجهاز للمطوّر، ثم أدخل مفتاح التفعيل المرسل لك")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #64748B; font-size: 12px; margin-bottom: 10px;")
        panel_layout.addWidget(subtitle)

        hw_label = QLabel("كود الجهاز")
        hw_label.setStyleSheet("color: #334155; font-size: 12px; font-weight: 600;")
        panel_layout.addWidget(hw_label)

        self.hw_id_display = QLineEdit(self.hw_id)
        self.hw_id_display.setReadOnly(True)
        self.hw_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hw_id_display.setMinimumHeight(48)
        self.hw_id_display.setStyleSheet(
            """
            QLineEdit {
                background-color: #F1F5F9;
                color: #0F172A;
                border: 1px dashed #2563EB;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 8px;
            }
            """
        )
        panel_layout.addWidget(self.hw_id_display)

        copy_btn = QPushButton("نسخ كود الجهاز")
        copy_btn.setStyleSheet(get_button_style("outline"))
        copy_btn.clicked.connect(self.copy_hw_id)
        panel_layout.addWidget(copy_btn)

        key_label = QLabel("مفتاح التفعيل")
        key_label.setStyleSheet("color: #334155; font-size: 12px; font-weight: 600;")
        panel_layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_input.setMinimumHeight(48)
        self.key_input.setStyleSheet(INPUT_STYLE)
        panel_layout.addWidget(self.key_input)

        activate_btn = QPushButton("تفعيل الآن")
        activate_btn.setStyleSheet(get_button_style("primary"))
        activate_btn.setMinimumHeight(50)
        activate_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        activate_btn.clicked.connect(self.process_activation)
        panel_layout.addWidget(activate_btn)

        note = QLabel("يعمل المفتاح على نفس الجهاز فقط.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 6px;")
        panel_layout.addWidget(note)

        layout.addWidget(panel)

    def copy_hw_id(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.hw_id)
            QMessageBox.information(self, "نجاح", "تم نسخ كود الجهاز بنجاح")

    def process_activation(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مفتاح التفعيل")
            return

        if self.db.activate_system(self.hw_id, key):
            QMessageBox.information(
                self,
                "نجاح",
                "تم تفعيل البرنامج بنجاح.\nسيتم فتح شاشة تسجيل الدخول الآن.",
            )
            self.activation_success.emit()
        else:
            QMessageBox.critical(
                self,
                "فشل",
                "مفتاح التفعيل غير صحيح أو لا يعمل على هذا الجهاز.",
            )
