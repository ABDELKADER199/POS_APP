"""
صفحة تسجيل الدخول المحسّنة
Login Page with Security
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QCheckBox, QFrame,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles import GLOBAL_STYLE
import mysql.connector

class LoginPage(QWidget):
    """صفحة تسجيل الدخول"""
    
    login_success = pyqtSignal(dict)  # إشارة عند نجاح تسجيل الدخول
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.parent = parent
        self.db = db_manager

        # Login attempts state
        self.failed_attempts = 0
        self.max_attempts = 5

        self.init_ui()
    
    def init_ui(self):
        """إنشاء واجهة تسجيل دخول حديثة وأكثر احترافية."""
        self.setObjectName("loginPage")
        self.setStyleSheet("""
            QWidget#loginPage {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0B1220,
                    stop: 0.45 #10203F,
                    stop: 1 #091326
                );
            }
            QFrame#authShell {
                background-color: rgba(10, 18, 34, 0.72);
                border: 1px solid rgba(125, 167, 255, 0.22);
                border-radius: 26px;
            }
            QFrame#heroPanel {
                border-radius: 22px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1D4ED8,
                    stop: 0.55 #0E3A89,
                    stop: 1 #08224F
                );
            }
            QLabel#heroBadge {
                background: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.25);
                color: #F8FAFC;
                font-size: 30px;
                font-weight: 700;
                border-radius: 18px;
                padding: 10px 16px;
            }
            QLabel#heroTitle {
                color: #FFFFFF;
                font-size: 28px;
                font-weight: 800;
                background: transparent;
            }
            QLabel#heroSubtitle {
                color: #DBEAFE;
                font-size: 13px;
                line-height: 1.35em;
                background: transparent;
            }
            QLabel#heroFeature {
                background: rgba(255, 255, 255, 0.12);
                color: #EFF6FF;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 12px;
                padding: 9px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QFrame#formPanel {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.74);
                border-radius: 22px;
            }
            QLabel#formTitle {
                color: #0F172A;
                font-size: 23px;
                font-weight: 800;
                background: transparent;
            }
            QLabel#formSubtitle {
                color: #475569;
                font-size: 12px;
                background: transparent;
            }
            QLabel#fieldLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }
            QLabel#statusHint {
                color: #64748B;
                font-size: 12px;
                background: transparent;
                border: none;
            }
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 12px;
                padding: 12px 14px;
                background-color: #F8FAFC;
                color: #0F172A;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
                background-color: #FFFFFF;
            }
            QCheckBox {
                color: #334155;
                font-size: 12px;
                spacing: 8px;
                padding-right: 2px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #94A3B8;
                background: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background: #2563EB;
                border-color: #2563EB;
            }
            QPushButton#loginButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 700;
                min-height: 52px;
            }
            QPushButton#loginButton:hover { background-color: #1D4ED8; }
            QPushButton#loginButton:pressed { background-color: #1E40AF; }
            QPushButton#loginButton:disabled {
                background-color: #9CA3AF;
                color: #E5E7EB;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        shell = QFrame()
        shell.setObjectName("authShell")
        shell.setMaximumWidth(1020)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(55)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.GlobalColor.black)
        shell.setGraphicsEffect(shadow)

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(14)

        hero_panel = QFrame()
        hero_panel.setObjectName("heroPanel")
        hero_panel.setMinimumWidth(340)
        hero_panel.setMaximumWidth(390)
        hero_layout = QVBoxLayout(hero_panel)
        hero_layout.setContentsMargins(24, 26, 24, 24)
        hero_layout.setSpacing(12)

        hero_badge = QLabel("POS")
        hero_badge.setObjectName("heroBadge")
        hero_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_badge.setFixedWidth(110)
        hero_layout.addWidget(hero_badge, alignment=Qt.AlignmentFlag.AlignRight)

        hero_title = QLabel("نظام إدارة المبيعات")
        hero_title.setObjectName("heroTitle")
        hero_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        hero_layout.addWidget(hero_title)

        hero_subtitle = QLabel("وصول آمن وسريع إلى لوحة التحكم، المنتجات، الفواتير، والإحصائيات اليومية.")
        hero_subtitle.setObjectName("heroSubtitle")
        hero_subtitle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        hero_subtitle.setWordWrap(True)
        hero_layout.addWidget(hero_subtitle)

        for text in [
            "حماية الدخول بالبصمة الرقمية للجهاز",
            "تدقيق محاولات تسجيل الدخول لحظياً",
            "إدارة متعددة الفروع ضمن واجهة واحدة",
        ]:
            feature = QLabel(f"? {text}")
            feature.setObjectName("heroFeature")
            feature.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            hero_layout.addWidget(feature)
        hero_layout.addStretch()

        form_panel = QFrame()
        form_panel.setObjectName("formPanel")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(34, 30, 34, 28)
        form_layout.setSpacing(10)

        form_title = QLabel("تسجيل الدخول")
        form_title.setObjectName("formTitle")
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_title)

        form_subtitle = QLabel("أدخل بريدك وكلمة المرور للمتابعة")
        form_subtitle.setObjectName("formSubtitle")
        form_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(form_subtitle)
        form_layout.addSpacing(8)

        email_label = QLabel("البريد الإلكتروني")
        email_label.setObjectName("fieldLabel")
        email_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("name@example.com")
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setMinimumHeight(52)
        self.email_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.email_input)

        password_label = QLabel("كلمة المرور")
        password_label.setObjectName("fieldLabel")
        password_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setMinimumHeight(52)
        self.password_input.returnPressed.connect(self.login)
        form_layout.addWidget(self.password_input)

        self.show_password_check = QCheckBox("إظهار كلمة المرور")
        self.show_password_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password_check)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusHint")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addWidget(self.status_label)

        self.login_btn = QPushButton("تسجيل الدخول")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.login_btn.clicked.connect(self.login)
        form_layout.addWidget(self.login_btn)

        helper = QLabel("يتم التحقق من الجهاز وعنوان الشبكة تلقائياً لحماية الحساب")
        helper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        helper.setWordWrap(True)
        helper.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 2px;")
        form_layout.addWidget(helper)

        shell_layout.addWidget(hero_panel)
        shell_layout.addWidget(form_panel, 1)
        main_layout.addWidget(shell)
        self._update_attempts_hint()

    def toggle_password_visibility(self):
        """إظهار/إخفاء كلمة المرور"""
        if self.show_password_check.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _set_login_busy(self, busy: bool):
        """تحديث حالة زر تسجيل الدخول أثناء التحقق."""
        if not hasattr(self, "login_btn"):
            return
        if busy:
            self.login_btn.setText("جارٍ التحقق...")
            self.login_btn.setEnabled(False)
        else:
            if self.failed_attempts >= self.max_attempts:
                self.login_btn.setText("تم الإيقاف مؤقتاً")
                self.login_btn.setEnabled(False)
            else:
                self.login_btn.setText("تسجيل الدخول")
                self.login_btn.setEnabled(True)

    def _update_attempts_hint(self):
        """عرض حالة محاولات الدخول المتبقية للمستخدم."""
        if not hasattr(self, "status_label"):
            return
        remaining = max(0, self.max_attempts - self.failed_attempts)
        if self.failed_attempts == 0:
            self.status_label.setText("أدخل بياناتك للمتابعة بشكل آمن")
            self.status_label.setStyleSheet("color: #64748B; font-size: 12px;")
        elif self.failed_attempts < self.max_attempts:
            self.status_label.setText(f"تنبيه: تبقى {remaining} محاولة قبل إيقاف تسجيل الدخول")
            self.status_label.setStyleSheet("color: #B45309; font-size: 12px; font-weight: 600;")
        else:
            self.status_label.setText("تم إيقاف تسجيل الدخول مؤقتاً بسبب تجاوز عدد المحاولات")
            self.status_label.setStyleSheet("color: #B91C1C; font-size: 12px; font-weight: 700;")

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
        except (ImportError, KeyError, OSError, RuntimeError) as e:
            QMessageBox.critical(self, "خطأ", f"فشل في الحصول على معلومات الجهاز: {str(e)}")
            return
        
        # محاولة الاتصال بقاعدة البيانات
        try:
            # 1. التحقق من بيانات المستخدم
            user = self.db.authenticate_user(email, password)
            
            if not user:
                # فشل تسجيل الدخول - بيانات خاطئة
                self.failed_attempts += 1
                self._update_attempts_hint()
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
                    if hasattr(self, "login_btn"):
                        self.login_btn.setText("تم الإيقاف مؤقتاً")
                        self.login_btn.setEnabled(False)
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
                self._update_attempts_hint()
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
            self._update_attempts_hint()
            QMessageBox.information(self, "نجاح", f"مرحباً {user['name']}")
            self.parent.show_dashboard(user)
            
        except (mysql.connector.Error, KeyError, ValueError, TypeError) as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
            import traceback
            print(traceback.format_exc())

    
    def reset(self):
        """إعادة تعيين الصفحة"""
        self.email_input.clear()
        self.password_input.clear()
        self.show_password_check.setChecked(False)
        self.failed_attempts = 0
        if hasattr(self, "login_btn"):
            self.login_btn.setEnabled(True)
            self.login_btn.setText("تسجيل الدخول")
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self._update_attempts_hint()
        self.email_input.setFocus()
