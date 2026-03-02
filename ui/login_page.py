"""
صفحة تسجيل الدخول المحسّنة
Login Page with Security
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from database_manager import DatabaseManager
from ui.styles import GLOBAL_STYLE, BUTTON_STYLES, get_button_style, COLORS, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER, LABEL_STYLE_TITLE, TAB_STYLE
import bcrypt

class LoginPage(QWidget):
    """صفحة تسجيل الدخول"""
    
    login_success = pyqtSignal(dict)  # إشارة عند نجاح تسجيل الدخول
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.parent = parent
        self.db = db_manager
        self.init_ui()
        
        # متغير لتخزين محاولات الدخول الفاشلة
        self.failed_attempts = 0
        self.max_attempts = 5
    
    def init_ui(self):
        """إنشاء واجهة الصفحة"""
        self.setObjectName("loginPage")
        
        # خلفية متدرجة حديثة - نستخدم ID selector لتطبيقها فقط على الويجت الرئيسي
        self.setStyleSheet("""
            QWidget#loginPage {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #2c3e50, stop:1 #3498db);
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # حاوية البطاقة البيضاء
        card_widget = QWidget()
        card_widget.setObjectName("cardWidget")
        card_widget.setFixedWidth(500)
        
        # ستايل البطاقة ومحتوياتها
        card_widget.setStyleSheet("""
            QWidget#cardWidget {
                background-color: white;
                border-radius: 20px;
            }
            QLabel {
                color: #2c3e50;
                background-color: transparent;
                border: none;
            }
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(40, 40, 40, 40)
        
        # الشعار/الأيقونة
        icon_label = QLabel("🛒")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Fallback fonts
        icon_label.setFont(QFont("Segoe UI Emoji, Apple Color Emoji, Arial", 48))
        card_layout.addWidget(icon_label)
        
        # العنوان الرئيسي
        title = QLabel("نظام إدارة المبيعات")
        title.setFont(QFont("Segoe UI, Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        
        # النص الفرعي
        subtitle = QLabel("تسجيل الدخول للمتابعة")
        subtitle.setFont(QFont("Segoe UI, Arial", 11))
        # استخدام color مباشرة هنا لضمان التطبيق
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)
        
        # حقل البريد
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("✉️  البريد الإلكتروني")
        self.email_input.setFont(QFont("Segoe UI, Arial", 11))
        self.email_input.setMinimumHeight(50)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """)
        card_layout.addWidget(self.email_input)
        self.email_input.returnPressed.connect(self.login)
        
        # حقل كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("🔒  كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Segoe UI, Arial", 11))
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 10px 15px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """)
        card_layout.addWidget(self.password_input)
        self.password_input.returnPressed.connect(self.login)
        
        # خيار إظهار كلمة المرور
        self.show_password_check = QCheckBox("إظهار كلمة المرور")
        self.show_password_check.setFont(QFont("Segoe UI, Arial", 10))
        self.show_password_check.setCursor(Qt.CursorShape.PointingHandCursor)
        # إجبار اللون على أن يكون مرئياً
        self.show_password_check.setStyleSheet("""
            QCheckBox { 
                spacing: 8px; 
                color: #555555; 
                background: transparent;
            }
            QCheckBox::indicator { 
                width: 18px; 
                height: 18px; 
                border-radius: 4px; 
                border: 2px solid #bdc3c7; 
            }
            QCheckBox::indicator:checked { 
                background-color: #3498db; 
                border-color: #3498db; 
            }
        """)
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        card_layout.addWidget(self.show_password_check)
        
        card_layout.addSpacing(10)
        
        # زر الدخول
        login_btn = QPushButton("تسجيل الدخول")
        login_btn.setMinimumHeight(55)
        login_btn.setFont(QFont("Segoe UI, Arial", 12, QFont.Weight.Bold))
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
                margin-top: -2px;
            }
            QPushButton:pressed {
                background-color: #2574a9;
                margin-top: 0px;
            }
        """)
        login_btn.clicked.connect(self.login)
        card_layout.addWidget(login_btn)
        
        card_widget.setLayout(card_layout)
        main_layout.addWidget(card_widget)
        
        self.setLayout(main_layout)
    
    def toggle_password_visibility(self):
        """إظهار/إخفاء كلمة المرور"""
        if self.show_password_check.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def login(self):
        """محاولة تسجيل الدخول مع التحقق من الموقع والجهاز"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # التحقق من الحقول الفارغة
        if not email or not password:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال البريد وكلمة المرور")
            return
        
        # التحقق من صيغة البريد
        if "@" not in email:
            QMessageBox.warning(self, "خطأ", "صيغة البريد غير صحيحة")
            return
        
        # الحصول على معلومات الجهاز والموقع
        try:
            from utils.device_manager import DeviceManager
            device_info = DeviceManager.get_device_info()
            device_id = device_info['device_id']
            device_name = device_info['device_name']
            ip_address = device_info['ip_address']
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في الحصول على معلومات الجهاز: {str(e)}")
            return
        
        # محاولة الاتصال بقاعدة البيانات
        try:
            # 1. التحقق من بيانات المستخدم
            user = self.db.authenticate_user(email, password)
            
            if not user:
                # فشل تسجيل الدخول - بيانات خاطئة
                self.failed_attempts += 1
                remaining = self.max_attempts - self.failed_attempts
                
                # تسجيل المحاولة الفاشلة
                self.db.log_login_attempt(
                    email=email,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                    success=False,
                    failure_reason="بيانات دخول غير صحيحة"
                )
                
                if self.failed_attempts >= self.max_attempts:
                    QMessageBox.critical(
                        self, "خطأ",
                        "لقد تجاوزت الحد الأقصى لمحاولات الدخول\n"
                        "يرجى المحاولة لاحقاً"
                    )
                    self.password_input.setEnabled(False)
                    self.email_input.setEnabled(False)
                else:
                    QMessageBox.warning(
                        self, "خطأ",
                        f"بيانات غير صحيحة\nلديك {remaining} محاولات متبقية"
                    )
                
                self.password_input.clear()
                return
            
            # 2. التحقق من صلاحية الدور
            user_role = user.get('role_name', '')
            user_id = user.get('id')
            role_id = user.get('role_id')
            
            # --- تحديد الفرع بناءً على الجهاز (جديد) ---
            device_store_id = self.db.get_device_store_id(device_id)
            if device_store_id:
                store_id = device_store_id
                # تحديث الجلسة بالفرع الجديد الخاص بالجهاز
                user['store_id'] = store_id
                # جلب اسم الفرع لعرضه لاحقاً
                store_info = self.db.get_store_info(store_id)
                if store_info:
                    user['store_name'] = store_info['store_name']
            else:
                store_id = user.get('store_id')

            # رتبة المطور (99) والمدير العام (1)
            is_developer = (role_id == 99) or (email == 'dev@admin.com')
            is_admin = (role_id == 1) or is_developer

            # === المطور معفي تماماً من جميع القيود (الجهاز و IP) ===
            if is_developer:
                # تسجيل المحاولة الناجحة
                self.db.log_login_attempt(
                    email=email,
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                    success=True
                )
                
                self.failed_attempts = 0
                QMessageBox.information(
                    self, "نجاح", 
                    f"مرحباً {user['name']}\n"
                    f"وضع المطور: تسجيل دخول بدون قيود"
                )
                self.parent.show_dashboard(user)
                return

            # 3. التحقق من الجهاز المصرح به (لبقية المستخدمين)
            # أولاً: التحقق مما إذا كان الجهاز محظوراً
            if self.db.check_device_banned(device_id):
                self.db.log_login_attempt(
                    email=email,
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                    success=False,
                    failure_reason="جهاز محظور (تم تعطيله)"
                )
                QMessageBox.critical(
                    self, "وصول مرفوض", 
                    "🚫 هذا الجهاز تم تعطيله من قبل الإدارة.\n"
                    "لا يمكنك تسجيل الدخول من هذا الجهاز حتى لو كنت داخل نطاق الشبكة."
                )
                self.password_input.clear()
                return

            is_device_authorized = self.db.check_device_authorization(
                device_id=device_id,
                user_id=user_id,
                store_id=store_id
            )
            
            # 4. التحقق من نطاق IP (للموظفين فقط)
            ip_valid = True
            ip_message = ""
            
            # إذا كان الجهاز مصرحاً به بشكل صريح، نتجاوز فحص IP
            # هذا يسمح للأجهزة المسجلة بالعمل دون الحاجة لعنوان IP ثابت (للأجهزة المحمولة أو Offline)
            if is_device_authorized:
                ip_valid = True
                ip_message = "مجاز بناءً على بصمة الجهاز"
            elif not is_admin:
                # فقط إذا لم يكن مديراً ولم يكن جهازه مصرحاً (وهذا لن يحدث لأننا نمنع غير المصرح في الخطوة السابقة)
                # ولكن كإجراء احتياطي أو للزوار في المستقبل:
                ip_valid, ip_message = self.db.check_ip_in_range(
                    ip=ip_address,
                    store_id=store_id
                )
            
            # 5. معالجة نتائج التحقق
            if not is_device_authorized:
                # الجهاز غير مصرح به للموظفين: رفض الدخول وطلب موافقة المدير
                self.db.log_login_attempt(
                    email=email,
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                    success=False,
                    failure_reason="جهاز غير مصرح به"
                )
                
                QMessageBox.critical(
                    self, "وصول مرفوض",
                    "🚫 هذا الجهاز غير مصرح به\n\n"
                    f"معرّف الجهاز: {device_name}\n"
                    f"عنوان IP: {ip_address}\n\n"
                    "يرجى التواصل مع المدير لتفعيل هذا الجهاز"
                )
                self.password_input.clear()
                return
            
            # 6. التحقق من نطاق IP (إذا كان مطلوباً)
            if not ip_valid:
                # IP خارج النطاق المسموح
                self.db.log_login_attempt(
                    email=email,
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    ip_address=ip_address,
                    success=False,
                    failure_reason=f"IP خارج النطاق: {ip_message}"
                )
                
                QMessageBox.critical(
                    self, "وصول مرفوض",
                    f"🚫 لا يمكنك تسجيل الدخول من هذا الموقع\n\n"
                    f"السبب: {ip_message}\n"
                    f"عنوان IP الحالي: {ip_address}\n\n"
                    "يجب أن تكون متصلاً بشبكة الفرع"
                )
                self.password_input.clear()
                return
            
            # 7. تسجيل دخول ناجح
            self.db.log_login_attempt(
                email=email,
                user_id=user_id,
                device_id=device_id,
                device_name=device_name,
                ip_address=ip_address,
                success=True
            )
            
            self.failed_attempts = 0
            QMessageBox.information(self, "نجاح", f"مرحباً {user['name']}")
            self.parent.show_dashboard(user)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
            import traceback
            print(traceback.format_exc())

    
    def reset(self):
        """إعادة تعيين الصفحة"""
        self.email_input.clear()
        self.password_input.clear()
        self.show_password_check.setChecked(False)
        self.failed_attempts = 0
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.email_input.setFocus()
