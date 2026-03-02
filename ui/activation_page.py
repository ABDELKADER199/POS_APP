from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from ui.styles import (INPUT_STYLE, get_button_style, COLORS, GROUP_BOX_STYLE)
from utils.license_manager import LicenseManager

class ActivationPage(QWidget):
    """شاشة تفعيل البرنامج برخصة رقمية"""
    activation_success = pyqtSignal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.hw_id = LicenseManager.get_hardware_id()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container
        frame = QFrame()
        frame.setFixedWidth(450)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 15px;
                padding: 30px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        frame_layout = QVBoxLayout(frame)
        
        # Title
        title = QLabel("🛡️ تفعيل نسخة البرنامج")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['primary']}; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)
        
        frame_layout.addSpacing(20)
        
        # Hardware ID Section
        hw_label = QLabel("كود الجهاز الخاص بك:")
        hw_label.setStyleSheet("color: #888; border: none;")
        frame_layout.addWidget(hw_label)
        
        self.hw_id_display = QLineEdit(self.hw_id)
        self.hw_id_display.setReadOnly(True)
        self.hw_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hw_id_display.setStyleSheet(f"""
            background-color: {COLORS['bg_input']};
            color: {COLORS['success']};
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
            border: 1px dashed {COLORS['success']};
            border-radius: 5px;
        """)
        frame_layout.addWidget(self.hw_id_display)
        
        copy_btn = QPushButton("نسخ الكود")
        copy_btn.setStyleSheet(get_button_style("secondary"))
        copy_btn.clicked.connect(self.copy_hw_id)
        frame_layout.addWidget(copy_btn)
        
        frame_layout.addSpacing(30)
        
        # Activation Key Section
        key_label = QLabel("أدخل مفتاح التفعيل:")
        key_label.setStyleSheet("color: white; font-weight: bold; border: none;")
        frame_layout.addWidget(key_label)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setStyleSheet(INPUT_STYLE)
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.key_input)
        
        frame_layout.addSpacing(20)
        
        # Activate Button
        activate_btn = QPushButton("🚀 تفعيل الآن")
        activate_btn.setStyleSheet(get_button_style("primary"))
        activate_btn.setFixedHeight(45)
        activate_btn.clicked.connect(self.process_activation)
        frame_layout.addWidget(activate_btn)
        
        # Instructions
        info = QLabel("يرجى إرسال كود الجهاز للمطور للحصول على رقم التفعيل.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #aaa; font-size: 11px; margin-top: 10px; border: none;")
        frame_layout.addWidget(info)
        
        layout.addWidget(frame)
        
    def copy_hw_id(self):
        from PyQt6.QtWidgets import QApplication
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
            QMessageBox.information(self, "نجاح", "✅ تم تفعيل البرنامج بنجاح!\nسيتم فتح شاشة الدخول الآن.")
            self.activation_success.emit()
        else:
            QMessageBox.critical(self, "فشل", "❌ مفتاح التفعيل غير صحيح أو لا يعمل على هذا الجهاز.")
