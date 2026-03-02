"""
تبويب إدارة الفروع
Branch Management Tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
                             QLineEdit, QComboBox, QHeaderView, QDialog, QFormLayout,
                             QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database_manager import DatabaseManager
from utils.device_manager import DeviceManager
from ui.styles import BUTTON_STYLES, get_button_style, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER

class BranchManagementTab(QWidget):
    """تبويب إدارة الفروع"""
    
    def __init__(self, db: DatabaseManager, user_info: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_info = user_info
        self.init_ui()
        self.load_branches()
    
    def init_ui(self):
        """إنشاء واجهة التبويب"""
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel("إدارة الفروع والمخازن")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(LABEL_STYLE_HEADER)
        layout.addWidget(title)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(get_button_style('info'))
        refresh_btn.clicked.connect(self.load_branches)
        buttons_layout.addWidget(refresh_btn)
        
        add_btn = QPushButton("➕ إضافة فرع جديد")
        add_btn.setStyleSheet(get_button_style('success'))
        add_btn.clicked.connect(self.add_branch)
        buttons_layout.addWidget(add_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # جدول الفروع
        self.branches_table = QTableWidget()
        self.branches_table.setColumnCount(7)
        self.branches_table.setHorizontalHeaderLabels([
            "اسم الفرع", "النوع", "نطاق IP (من)", "نطاق IP (إلى)", 
            "فحص IP", "الحالة", "الإجراءات"
        ])
        self.branches_table.setStyleSheet(TABLE_STYLE)
        self.branches_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.branches_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.branches_table.setAlternatingRowColors(True)
        # تقليل ارتفاع الصفوف لجعل الجدول مدمجاً
        self.branches_table.verticalHeader().setDefaultSectionSize(45)
        layout.addWidget(self.branches_table)
        
        self.setLayout(layout)
    
    def load_branches(self):
        """تحميل الفروع من قاعدة البيانات"""
        stores = self.db.get_all_stores(include_inactive=True)
        
        self.branches_table.setRowCount(0)
        
        for store in stores:
            row = self.branches_table.rowCount()
            self.branches_table.insertRow(row)
            
            # اسم الفرع
            self.branches_table.setItem(row, 0, QTableWidgetItem(store.get('store_name', '')))
            
            # النوع
            store_type = store.get('store_type', 'Branch')
            type_text = {
                'GM': 'مدير عام',
                'Main': 'مخزن رئيسي',
                'Warehouse': 'مخزن',
                'Branch': 'فرع'
            }.get(store_type, store_type)
            self.branches_table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # نطاق IP
            ip_start = store.get('ip_range_start', '')
            ip_end = store.get('ip_range_end', '')
            self.branches_table.setItem(row, 2, QTableWidgetItem(ip_start or '-'))
            self.branches_table.setItem(row, 3, QTableWidgetItem(ip_end or '-'))
            
            # فحص IP
            require_check = store.get('require_ip_check', True)
            check_item = QTableWidgetItem("✅ نعم" if require_check else "❌ لا")
            check_item.setForeground(Qt.GlobalColor.darkGreen if require_check else Qt.GlobalColor.red)
            self.branches_table.setItem(row, 4, check_item)
            
            # الحالة
            is_active = store.get('is_active', True)
            status_item = QTableWidgetItem("✅ نشط" if is_active else "🚫 معطّل")
            status_item.setForeground(Qt.GlobalColor.darkGreen if is_active else Qt.GlobalColor.red)
            self.branches_table.setItem(row, 5, status_item)
            
            # الإجراءات
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0) # الغاء البادينج تماماً لتوفير مساحة
            
            edit_btn = QPushButton("✏️ تعديل")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setFixedSize(70, 28)
            edit_btn.setStyleSheet(get_button_style('info') + " QPushButton { padding: 0px; min-height: 0px; font-size: 11px; border-radius: 6px; }")
            edit_btn.clicked.connect(lambda checked, s=store: self.edit_branch(s))
            
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setFixedSize(70, 28)
            delete_btn.setStyleSheet(get_button_style('danger') + " QPushButton { padding: 0px; min-height: 0px; font-size: 11px; border-radius: 6px; }")
            delete_btn.clicked.connect(lambda checked, s=store: self.delete_branch(s))
            
            actions_layout.addStretch()
            actions_layout.addWidget(edit_btn)
            actions_layout.addSpacing(5)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.branches_table.setCellWidget(row, 6, actions_widget)
    
    def add_branch(self):
        """إضافة فرع جديد"""
        dialog = AddBranchDialog(self.db, self.user_info, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_branches()
    
    def edit_branch(self, store):
        """تعديل فرع موجود"""
        dialog = AddBranchDialog(self.db, self.user_info, store, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_branches()

    def delete_branch(self, store):
        """حذف فرع"""
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف فرع '{store['store_name']}'؟\nلا يمكن التراجع عن هذا الإجراء.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db.delete_store(store['id'])
            if success:
                QMessageBox.information(self, "نجاح", message)
                self.load_branches()
            else:
                QMessageBox.critical(self, "خطأ", message)


class AddBranchDialog(QDialog):
    """نافذة إضافة/تعديل فرع"""
    
    def __init__(self, db: DatabaseManager, user_info: dict, store: dict = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_info = user_info
        self.store = store
        self.setWindowTitle("تعديل فرع" if store else "إضافة فرع جديد")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """إنشاء واجهة النافذة"""
        layout = QVBoxLayout()
        
        # مجموعة المعلومات الأساسية
        basic_group = QGroupBox("المعلومات الأساسية")
        basic_group.setStyleSheet(GROUP_BOX_STYLE)
        basic_layout = QFormLayout()
        
        # اسم الفرع
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: فرع الإسكندرية")
        self.name_input.setStyleSheet(INPUT_STYLE)
        basic_layout.addRow("اسم الفرع:", self.name_input)
        
        # نوع الفرع
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet(INPUT_STYLE)
        self.type_combo.addItem("فرع عادي", "Branch")
        self.type_combo.addItem("مدير عام", "GM")
        self.type_combo.addItem("مخزن رئيسي", "Main")
        self.type_combo.addItem("مخزن", "Warehouse")
        basic_layout.addRow("النوع:", self.type_combo)
        
        # حالة الفرع
        self.is_active_check = QCheckBox("نشط")
        self.is_active_check.setChecked(True)
        self.is_active_check.setStyleSheet("color: white; font-weight: bold;")
        basic_layout.addRow("الحالة:", self.is_active_check)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # مجموعة إعدادات IP
        ip_group = QGroupBox("إعدادات نطاق IP")
        ip_group.setStyleSheet(GROUP_BOX_STYLE)
        ip_layout = QFormLayout()
        
        # بداية النطاق
        self.ip_start_input = QLineEdit()
        self.ip_start_input.setPlaceholderText("مثال: 192.168.1.0")
        self.ip_start_input.setStyleSheet(INPUT_STYLE)
        ip_layout.addRow("بداية النطاق:", self.ip_start_input)
        
        # نهاية النطاق
        self.ip_end_input = QLineEdit()
        self.ip_end_input.setPlaceholderText("مثال: 192.168.1.255")
        self.ip_end_input.setStyleSheet(INPUT_STYLE)
        ip_layout.addRow("نهاية النطاق:", self.ip_end_input)
        
        # فحص IP
        self.require_ip_check = QCheckBox("تفعيل فحص نطاق IP")
        self.require_ip_check.setChecked(True)
        self.require_ip_check.setStyleSheet("color: white;")
        ip_layout.addRow("", self.require_ip_check)
        
        # ربط الجهاز الحالي (جديد)
        self.link_device_check = QCheckBox("✅ ربط هذا الجهاز بالفرع الحالي")
        self.link_device_check.setChecked(False)
        self.link_device_check.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")
        
        # اختيار المستخدم المرتبط بالجهاز
        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet(INPUT_STYLE)
        self.user_combo.addItem("سماح لجميع موظفي الفرع", None)
        
        # تحميل المستخدمين
        users = self.db.get_all_users()
        for u in users:
            self.user_combo.addItem(f"{u['name']} ({u['role_name']})", u['id'])
        
        self.user_combo.setEnabled(False) # تعطيل افتراضي حتى يتم تفعيل خيار الربط
        self.link_device_check.toggled.connect(self.user_combo.setEnabled)
        
        # تلميح للمستخدم
        device_hint = QLabel("سيقوم هذا الخيار بتسجيل جهازك الحالي فوراً في هذا الفرع")
        device_hint.setStyleSheet("color: #ecf0f1; font-size: 11px; margin-bottom: 5px;")
        
        ip_layout.addRow(self.link_device_check, device_hint)
        ip_layout.addRow("الموظف المسموح له:", self.user_combo)
        
        # ملاحظة
        note_label = QLabel("💡 المدير العام عادة لا يحتاج فحص IP")
        note_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        ip_layout.addRow("", note_label)
        
        ip_group.setLayout(ip_layout)
        layout.addWidget(ip_group)
        
        # تحميل البيانات إذا كان تعديل
        if self.store:
            self.name_input.setText(self.store.get('store_name', ''))
            
            store_type = self.store.get('store_type', 'Branch')
            index = self.type_combo.findData(store_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            self.ip_start_input.setText(self.store.get('ip_range_start', ''))
            self.ip_end_input.setText(self.store.get('ip_range_end', ''))
            self.require_ip_check.setChecked(self.store.get('require_ip_check', True))
            self.is_active_check.setChecked(self.store.get('is_active', True))
            
            # في حالة التعديل، نغير النص ليكون أوضح
            self.link_device_check.setText("✅ نقل هذا الجهاز إلى هذا الفرع")
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 حفظ")
        save_btn.setStyleSheet(get_button_style('success'))
        save_btn.clicked.connect(self.save_branch)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet(get_button_style('secondary'))
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def save_branch(self):
        """حفظ الفرع"""
        name = self.name_input.text().strip()
        store_type = self.type_combo.currentData()
        ip_start = self.ip_start_input.text().strip()
        ip_end = self.ip_end_input.text().strip()
        require_check = self.require_ip_check.isChecked()
        is_active = self.is_active_check.isChecked()
        link_device = self.link_device_check.isChecked()
        
        # التحقق من البيانات
        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الفرع")
            return
        
        try:
            store_id = None
            
            if self.store:
                # تعديل فرع موجود
                store_id = self.store['id']
                query = """
                UPDATE stores 
                SET store_name = %s, store_type = %s, 
                    ip_range_start = %s, ip_range_end = %s, require_ip_check = %s,
                    is_active = %s
                WHERE id = %s
                """
                self.db.cursor.execute(query, (
                    name, store_type, ip_start or None, ip_end or None, 
                    require_check, is_active, store_id
                ))
            else:
                # إضافة فرع جديد
                query = """
                INSERT INTO stores 
                (store_name, store_type, ip_range_start, ip_range_end, require_ip_check, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.db.cursor.execute(query, (
                    name, store_type, ip_start or None, ip_end or None, require_check, is_active
                ))
                store_id = self.db.cursor.lastrowid
            
            self.db.conn.commit()
            
            # === منطق ربط الجهاز الجديد ===
            if link_device and store_id:
                try:
                    from utils.device_manager import DeviceManager
                    device_info = DeviceManager.get_device_info()
                    # تسجيل الجهاز وربطه بالفرع الجديد والموظف المحدد
                    selected_user_id = self.user_combo.currentData()
                    
                    self.db.register_device(
                        device_id=device_info['device_id'],
                        device_name=device_info['device_name'],
                        mac_address=device_info['mac_address'],
                        store_id=store_id,
                        user_id=selected_user_id,
                        registered_by=self.user_info.get('id'),
                        notes=f"تم الربط تلقائياً لشخص محدد عند إنشاء/تعديل فرع {name}"
                    )
                    
                    target_msg = f"للموظف المختار" if selected_user_id else "لجميع موظفي الفرع"
                    QMessageBox.information(
                        self, "نجاح", 
                        f"تم حفظ الفرع وربط جهازك ({device_info['device_name']}) بنجاح {target_msg}"
                    )
                except Exception as dev_err:
                    print(f"Error linking device: {dev_err}")
                    QMessageBox.warning(self, "تنبيه", "تم حفظ الفرع ولكن فشل ربط الجهاز تلقائياً")
            else:
                QMessageBox.information(self, "نجاح", "تم حفظ الفرع بنجاح")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الفرع: {str(e)}")
