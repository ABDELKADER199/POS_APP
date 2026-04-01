"""
صفحة الإدارة - تشمل المستخدمين ومراقبة الأدراج
Admin Panel - User Management & Drawer Monitoring
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QComboBox, QDialog, QFormLayout, QSpinBox, QTabWidget, QHeaderView, QScrollArea, QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import mysql.connector
from database_manager import DatabaseManager
from ui.styles import GLOBAL_STYLE, BUTTON_STYLES, get_button_style, COLORS, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER, LABEL_STYLE_TITLE, TAB_STYLE
import bcrypt

class AdminPanel(QWidget):
    """صفحة الإدارة - تشمل المستخدمين ومراقبة الأدراج"""
    
    def __init__(self, user_info=None, parent=None, auto_load=True):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.db = DatabaseManager()
        self.user_info = user_info or {}
        self.auto_load = auto_load
        self._is_loaded = False
        self.init_ui()
        if self.auto_load:
            self.ensure_loaded(force=True)
    
    def set_user(self, user_info):
        """تعيين بيانات المستخدم وتحديث التبويبات"""
        self.user_info = user_info or {}
        
        # التأكد من وجود/عدم وجود تبويب إدارة الأجهزة بناءً على الرتبة
        is_developer = (self.user_info.get('role_id') == 99)
        
        # البحث عن التبويب الحالي إذا كان موجوداً
        devices_tab_index = -1
        for i in range(self.tabs.count()):
            if "إدارة الأجهزة" in self.tabs.tabText(i):
                devices_tab_index = i
                break
        
        if is_developer:
            if devices_tab_index == -1:
                # إضافة التبويب إذا لم يكن موجوداً (نضيفه قبل إدارة الفروع)
                devices_tab = self.create_devices_tab()
                # نحاول إضافته في المركز الثاني أو قبل الأخير
                self.tabs.insertTab(self.tabs.count() - 1, devices_tab, "🔐 إدارة الأجهزة")
        else:
            if devices_tab_index != -1:
                # إزالة التبويب إذا كان موجوداً والمستخدم ليس مطوراً
                self.tabs.removeTab(devices_tab_index)

        if self.auto_load or self._is_loaded:
            self.ensure_loaded(force=True)

    def ensure_loaded(self, force=False):
        """Load users/drawers only when the tab is opened."""
        if force or not self._is_loaded:
            self.load_users()
            self.load_drawers()
            self._is_loaded = True
    
    def init_ui(self):
        """إنشاء واجهة الصفحة"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # التبويبات الرئيسية
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; background: white; border-radius: 5px; }
            QTabBar::tab { padding: 12px 25px; font-weight: bold; background: #ecf0f1; border: 1px solid #bdc3c7; margin-right: 2px; }
            QTabBar::tab:selected { background: white; border-bottom-color: white; color: #3498db; }
        """)
        
        # 1. تبويب إدارة المستخدمين
        users_tab = self.create_users_tab()
        self.tabs.addTab(users_tab, "👥 إدارة المستخدمين")
        
        # 2. تبويب مراقبة الأدراج
        drawers_tab = self.create_drawers_tab()
        self.tabs.addTab(drawers_tab, "💰 مراقبة الأدراج")
        
        # 3. تبويب إدارة الأجهزة (للمطور فقط)
        if self.user_info.get('role_id') == 99:
            devices_tab = self.create_devices_tab()
            self.tabs.addTab(devices_tab, "🔐 إدارة الأجهزة")
        
        # 3. تبويب إدارة الفروع
        branches_tab = self.create_branches_tab()
        self.tabs.addTab(branches_tab, "🏢 إدارة الفروع")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_users_tab(self):
        """تبويب المستخدمين"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # العنوان
        title = QLabel("إدارة المستخدمين")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # زر إضافة مستخدم جديد
        button_layout = QHBoxLayout()
        add_btn = QPushButton("➕ إضافة مستخدم جديد")
        add_btn.setStyleSheet(get_button_style('success'))
        add_btn.clicked.connect(self.add_user)
        button_layout.addWidget(add_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # جدول المستخدمين
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels(
            ["#", "الاسم", "البريد", "الدور", "الفرع", "الهاتف", "الإجراءات"]
        )
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setColumnWidth(0, 50)
        
        # تحسين مظهر الجدول
        self.users_table.verticalHeader().setDefaultSectionSize(60)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.users_table.setStyleSheet(TABLE_STYLE)
        
        layout.addWidget(self.users_table)
        
        scroll.setWidget(container)
        return scroll


    def load_users(self):
        """تحميل قائمة المستخدمين"""
        try:
            users = self.db.get_all_users()
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['name']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user['email']))
                self.users_table.setItem(row, 3, QTableWidgetItem(user['role_name']))
                self.users_table.setItem(row, 4, QTableWidgetItem(user['store_name'] or "---"))
                self.users_table.setItem(row, 5, QTableWidgetItem(user['phone'] or ""))
                
                # الإجراءات
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("تعديل")
                edit_btn.setStyleSheet(f"background-color: {COLORS['info']}; color: white; border-radius: 4px; padding: 5px;")
                edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("حذف")
                delete_btn.setStyleSheet(f"background-color: {COLORS['danger']}; color: white; border-radius: 4px; padding: 5px;")
                delete_btn.clicked.connect(lambda checked, u_id=user['id']: self.delete_user(u_id))
                if user['id'] == 1: delete_btn.setEnabled(False)
                actions_layout.addWidget(delete_btn)
                
                self.users_table.setCellWidget(row, 6, actions_widget)
        except Exception as e:
            print(f"Error loading users: {e}")


    def create_drawers_tab(self):
        """تبويب مراقبة أدراج الكاشير"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # هيدر التبويب مع زر تحديث
        header_layout = QHBoxLayout()
        title = QLabel("تقرير الأدراج المفتوحة والمغلقة")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setStyleSheet(get_button_style('info'))
        refresh_btn.clicked.connect(self.load_drawers)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # جدول الأدراج
        self.drawers_table = QTableWidget()
        self.drawers_table.setColumnCount(10) # Added Actions column
        self.drawers_table.setHorizontalHeaderLabels([
            "الكاشير", "الفرع", "وقت الفتح", "الحالة", 
            "الرصيد الافتتاحي", "المبيعات", "المبلغ المتوقع", "الرصيد الفعلي", "الفرق", "طباعة"
        ])
        self.drawers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.drawers_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.drawers_table.setColumnWidth(9, 120)
        self.drawers_table.verticalHeader().setVisible(False)
        self.drawers_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.drawers_table.setStyleSheet(TABLE_STYLE)
        self.drawers_table.verticalHeader().setDefaultSectionSize(60)
        
        layout.addWidget(self.drawers_table)
        
        scroll.setWidget(container)
        return scroll

    def load_drawers(self):
        """تحميل تقرير الأدراج"""
        try:
            report = self.db.get_drawers_report()
            self.drawers_table.setRowCount(len(report))
            
            for row, data in enumerate(report):
                # البيانات الأساسية
                self.drawers_table.setItem(row, 0, QTableWidgetItem(data['cashier_name']))
                self.drawers_table.setItem(row, 1, QTableWidgetItem(data['store_name']))
                
                open_time = data['opening_date'].strftime("%Y-%m-%d %H:%M") if data['opening_date'] else ""
                self.drawers_table.setItem(row, 2, QTableWidgetItem(open_time))
                
                status_item = QTableWidgetItem("🟢 مفتوح" if data['status'] == 'Open' else "🔴 مغلق")
                if data['status'] == 'Open': status_item.setForeground(QColor("#27ae60"))
                self.drawers_table.setItem(row, 3, status_item)
                
                # مبالغ
                opening = float(data['opening_balance'] or 0)
                sales = float(data['mبيعات_الدرج'] or 0)
                cash_sales = float(data.get('cash_sales', 0) or 0)
                cash_returns = float(data.get('cash_returns', 0) or 0)
                expected = opening + cash_sales - cash_returns
                actual = float(data['closing_balance'] or 0) if data['status'] == 'Closed' else 0
                diff = actual - expected if data['status'] == 'Closed' else 0
                
                self.drawers_table.setItem(row, 4, QTableWidgetItem(f"{opening:,.2f}"))
                self.drawers_table.setItem(row, 5, QTableWidgetItem(f"{sales:,.2f}"))
                self.drawers_table.setItem(row, 6, QTableWidgetItem(f"{expected:,.2f}"))
                
                actual_item = QTableWidgetItem(f"{actual:,.2f}" if data['status'] == 'Closed' else "---")
                self.drawers_table.setItem(row, 7, actual_item)
                
                diff_item = QTableWidgetItem(f"{diff:,.2f}" if data['status'] == 'Closed' else "---")
                if diff < 0: diff_item.setForeground(QColor("#e74c3c"))
                elif diff > 0: diff_item.setForeground(QColor("#27ae60"))
                self.drawers_table.setItem(row, 8, diff_item)

                # Print Button
                print_btn = QPushButton("🖨️ طباعة")
                print_btn.setToolTip("طباعة تقرير الإغلاق")
                print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                print_btn.setStyleSheet(f"background-color: {COLORS['secondary']}; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
                print_btn.setMinimumHeight(40)
                print_btn.clicked.connect(lambda checked, d_id=data['id']: self.print_drawer_receipt(d_id))
                
                # Only enable print if closed? Or allow current status print? 
                # User asked for "Closing Receipt", so typically for closed drawers.
                # But sometimes helpful to print interim too. Let's allow all, database method handles summary.
                
                self.drawers_table.setCellWidget(row, 9, print_btn)

        except Exception as e:
            print(f"Error loading drawers: {e}")

    def print_drawer_receipt(self, drawer_id):
        """Print drawer report"""
        try:
            from utils.printer_service import PrinterService
            summary = self.db.get_drawer_summary(drawer_id)
            if summary:
                PrinterService.print_drawer_report(summary)
                QMessageBox.information(self, "طباعة", "تم إرسال أمر الطباعة بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "تعذر العثور على بيانات الدرج")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل الطباعة: {e}")

    def create_devices_tab(self):
        """تبويب إدارة الأجهزة"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # العنوان
        title = QLabel("إدارة الأجهزة المصرح بها")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # زر فتح نافذة إدارة الأجهزة
        button_layout = QHBoxLayout()
        
        open_devices_btn = QPushButton("🔐 فتح إدارة الأجهزة")
        open_devices_btn.setStyleSheet(get_button_style('primary'))
        open_devices_btn.clicked.connect(self.open_device_management)
        button_layout.addWidget(open_devices_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # معلومات
        info_label = QLabel(
            "من هنا يمكنك إدارة الأجهزة المصرح بها لتسجيل الدخول\n"
            "• إضافة أجهزة جديدة للموظفين\n"
            "• تفعيل/تعطيل الأجهزة\n"
            "• عرض سجل استخدام الأجهزة"
        )
        info_label.setStyleSheet("color: #7f8c8d; padding: 20px; background: #ecf0f1; border-radius: 5px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        return scroll
    
    def create_branches_tab(self):
        """تبويب إدارة الفروع"""
        from ui.branch_management_tab import BranchManagementTab
        return BranchManagementTab(self.db, self.user_info)
    
    def open_device_management(self):
        """فتح نافذة إدارة الأجهزة"""
        from ui.device_management_dialog import DeviceManagementDialog
        dialog = DeviceManagementDialog(self.db, self.user_info, self)
        dialog.exec()
    
    def add_user(self):
        dialog = AddUserDialog(self.db, user=None, current_user_info=self.user_info, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted: self.load_users()
    
    def edit_user(self, user):
        dialog = AddUserDialog(self.db, user, current_user_info=self.user_info, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted: self.load_users()

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, "تأكيد", "هل تريد حذف هذا المستخدم؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db.delete_user(user_id)
                if success:
                    QMessageBox.information(self, "نجاح", "تم حذف المستخدم بنجاح")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في حذف المستخدم من قاعدة البيانات")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحذف: {str(e)}")

class AddUserDialog(QDialog):
    """نافذة حوار إضافة/تعديل مستخدم"""
    
    def __init__(self, db, user=None, current_user_info=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.current_user_info = current_user_info or {}
        self.setWindowTitle("تعديل مستخدم" if user else "إضافة مستخدم جديد")
        self.setGeometry(200, 200, 400, 450)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        self.name_input = QLineEdit()
        layout.addRow("الاسم:", self.name_input)
        self.email_input = QLineEdit()
        layout.addRow("البريد الإلكتروني:", self.email_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("اتركه فارغاً إذا لم ترد التغيير" if self.user else "")
        layout.addRow("كلمة المرور:", self.password_input)
        self.phone_input = QLineEdit()
        layout.addRow("رقم الهاتف:", self.phone_input)
        self.role_combo = QComboBox()
        self.role_combo.addItem("مدير", 1)
        self.role_combo.addItem("مدير فرع", 2)
        self.role_combo.addItem("كاشير", 3)
        self.role_combo.addItem("Call Center", 4)
        self.role_combo.addItem("موظف المخزن", 5)
        layout.addRow("الدور:", self.role_combo)
        self.store_combo = QComboBox()
        self.load_stores()
        layout.addRow("الفرع:", self.store_combo)
        
        if self.user:
            self.name_input.setText(self.user['name'])
            self.email_input.setText(self.user['email'])
            self.phone_input.setText(self.user['phone'] or "")
            index = self.role_combo.findData(self.user['role_id'])
            if index >= 0: self.role_combo.setCurrentIndex(index)
            index = self.store_combo.findData(self.user['store_id'])
            if index >= 0: self.store_combo.setCurrentIndex(index)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def load_stores(self):
        try:
            # Add "No Store" option for General Managers
            self.store_combo.addItem("--- (إدارة عامة / بدون فرع)", None)
            
            cursor = self.db.cursor
            cursor.execute("SELECT id, store_name FROM stores WHERE is_active = TRUE")
            for store in cursor.fetchall(): 
                self.store_combo.addItem(store['store_name'], store['id'])
        except (mysql.connector.Error, AttributeError, KeyError, TypeError):
            pass
    
    def save_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        phone = self.phone_input.text().strip()
        role_id = self.role_combo.currentData()
        store_id = self.store_combo.currentData()
        
        # Validation
        if not all([name, email, role_id]):
            QMessageBox.warning(self, "خطأ", "يرجى ملء الاسم والبريد والدور"); return

        # Store is mandatory for non-admins (Role 1 is usually Admin/General Manager)
        # Assuming Role 1 = Admin/GM. Adjust if needed.
        if role_id != 1 and not store_id:
             QMessageBox.warning(self, "خطأ", "يرجى تحديد الفرع لهذا المستخدم"); return
        try:
            creator_id = self.current_user_info.get('id', 13) # Default to 13 if unknown (based on your current DB)
            if self.user: success = self.db.update_user(self.user['id'], name, email, phone, role_id, store_id, password if password else None)
            else: success = self.db.create_user(name, email, password, phone, role_id, store_id, created_by=creator_id)
            if success: QMessageBox.information(self, "نجاح", "تم الحفظ بنجاح"); self.accept()
            else: QMessageBox.critical(self, "خطأ", "فشل الحفظ")
        except Exception as e: QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
