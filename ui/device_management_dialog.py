"""
واجهة إدارة الأجهزة المصرح بها
Device Management Dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
                             QLineEdit, QComboBox, QTextEdit, QHeaderView, QGroupBox,
                             QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database_manager import DatabaseManager
from ui.styles import BUTTON_STYLES, get_button_style, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER
from datetime import datetime

class DeviceManagementDialog(QDialog):
    """نافذة إدارة الأجهزة المصرح بها"""
    
    def __init__(self, db: DatabaseManager, user_info: dict, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_info = user_info
        self.setWindowTitle("إدارة الأجهزة المصرح بها")
        self.setMinimumSize(1000, 600)
        self.init_ui()
        self.load_devices()
    
    def init_ui(self):
        """إنشاء واجهة النافذة"""
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel("🔐 إدارة الأجهزة المصرح بها")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(LABEL_STYLE_HEADER)
        layout.addWidget(title)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(get_button_style('info'))
        refresh_btn.clicked.connect(self.load_devices)
        buttons_layout.addWidget(refresh_btn)
        
        add_btn = QPushButton("➕ إضافة جهاز")
        add_btn.setStyleSheet(get_button_style('success'))
        add_btn.clicked.connect(self.add_device)
        buttons_layout.addWidget(add_btn)
        
        assign_btn = QPushButton("👤 إضافة مستخدم لجهاز")
        assign_btn.setStyleSheet(get_button_style('info'))
        assign_btn.clicked.connect(self.assign_user_to_device)
        buttons_layout.addWidget(assign_btn)
        
        activate_btn = QPushButton("✅ تفعيل")
        activate_btn.setStyleSheet(get_button_style('success'))
        activate_btn.clicked.connect(self.activate_selected)
        buttons_layout.addWidget(activate_btn)
        
        deactivate_btn = QPushButton("🚫 تعطيل")
        deactivate_btn.setStyleSheet(get_button_style('warning'))
        deactivate_btn.clicked.connect(self.deactivate_selected)
        buttons_layout.addWidget(deactivate_btn)
        
        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setStyleSheet(get_button_style('danger'))
        delete_btn.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # جدول الأجهزة
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(9)
        self.devices_table.setHorizontalHeaderLabels([
            "ID", "معرّف الجهاز", "اسم الجهاز", "MAC Address", 
            "الفرع", "المستخدم", "الحالة", "آخر استخدام", "ملاحظات"
        ])
        self.devices_table.setColumnHidden(0, True) # إخفاء عمود المعرف الداخلي
        self.devices_table.setStyleSheet(TABLE_STYLE)
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.devices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.devices_table.setAlternatingRowColors(True)
        layout.addWidget(self.devices_table)
        
        # زر الإغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.setStyleSheet(get_button_style('secondary'))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_devices(self):
        """تحميل الأجهزة من قاعدة البيانات"""
        devices = self.db.get_authorized_devices()
        
        self.devices_table.setRowCount(0)
        
        for device in devices:
            row = self.devices_table.rowCount()
            self.devices_table.insertRow(row)
            
            # تخزين المعرف الحقيقي في العمود الأول (مخفي)
            id_item = QTableWidgetItem(str(device.get('id', '')))
            id_item.setData(Qt.ItemDataRole.UserRole, device.get('id'))
            self.devices_table.setItem(row, 0, id_item)
            
            # معرّف الجهاز
            self.devices_table.setItem(row, 1, QTableWidgetItem(device.get('device_id', '')))
            
            # اسم الجهاز
            self.devices_table.setItem(row, 2, QTableWidgetItem(device.get('device_name', '')))
            
            # MAC Address
            self.devices_table.setItem(row, 3, QTableWidgetItem(device.get('mac_address', '')))
            
            # الفرع
            store_name = device.get('store_name', 'جميع الفروع')
            self.devices_table.setItem(row, 4, QTableWidgetItem(store_name or 'جميع الفروع'))
            
            # المستخدم
            user_name = device.get('user_name', 'جميع المستخدمين')
            self.devices_table.setItem(row, 5, QTableWidgetItem(user_name or 'جميع المستخدمين'))
            
            # الحالة
            is_active = device.get('is_active', False)
            status_item = QTableWidgetItem("✅ مفعّل" if is_active else "🚫 معطّل")
            status_item.setForeground(Qt.GlobalColor.darkGreen if is_active else Qt.GlobalColor.red)
            self.devices_table.setItem(row, 6, status_item)
            
            # آخر استخدام
            last_used = device.get('last_used')
            if last_used:
                last_used_str = last_used.strftime('%Y-%m-%d %H:%M') if isinstance(last_used, datetime) else str(last_used)
            else:
                last_used_str = "لم يُستخدم بعد"
            self.devices_table.setItem(row, 7, QTableWidgetItem(last_used_str))
            
            # ملاحظات
            notes = device.get('notes', '')
            self.devices_table.setItem(row, 8, QTableWidgetItem(notes or ''))
    
    def add_device(self):
        """إضافة جهاز جديد"""
        dialog = AddDeviceDialog(self.db, self.user_info, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_devices()

    def assign_user_to_device(self):
        """إضافة مستخدم لمسار جهاز موجود بالفعل"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار جهاز من الجدول أولاً")
            return
            
        row = selected_rows[0].row()
        device_id = self.devices_table.item(row, 1).text() # Device ID is now in column 1
        device_name = self.devices_table.item(row, 2).text()
        mac_address = self.devices_table.item(row, 3).text()
        
        device_data = {
            'device_id': device_id,
            'device_name': device_name,
            'mac_address': mac_address,
            'store_id': None 
        }
        
        dialog = AddDeviceDialog(self.db, self.user_info, device_data=device_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_devices()
    
    def activate_selected(self):
        """تفعيل الجهاز المحدد"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار جهاز")
            return
        
        row = selected_rows[0].row()
        record_pk = self.devices_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if self.db.activate_device(record_pk):
            QMessageBox.information(self, "نجاح", "تم تفعيل الجهاز بنجاح")
            self.load_devices()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في تفعيل الجهاز")
    
    def deactivate_selected(self):
        """تعطيل الجهاز المحدد"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار جهاز")
            return
        
        row = selected_rows[0].row()
        record_pk = self.devices_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل أنت متأكد من تعطيل هذا التصريح؟\nسيتم منع هذا المستخدم/الفرع من استخدام هذا الجهاز",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.deactivate_device(record_pk):
                QMessageBox.information(self, "نجاح", "تم تعطيل الجهاز بنجاح")
                self.load_devices()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في تعطيل الجهاز")
    
    def delete_selected(self):
        """حذف الجهاز المحدد"""
        selected_rows = self.devices_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار جهاز")
            return
        
        row = selected_rows[0].row()
        record_pk = self.devices_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل أنت متأكد من حذف هذا التصريح نهائياً؟\nسيتم إلغاء ربط هذا المستخدم بالجهاز",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_device(record_pk):
                QMessageBox.information(self, "نجاح", "تم حذف الجهاز بنجاح")
                self.load_devices()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حذف الجهاز")


class AddDeviceDialog(QDialog):
    """نافذة إضافة جهاز جديد"""
    
    def __init__(self, db: DatabaseManager, user_info: dict, device_data: dict = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_info = user_info
        self.device_data = device_data
        self.setWindowTitle("إضافة مستخدم لجهاز" if device_data else "إضافة جهاز جديد")
        self.setMinimumWidth(500)
        self.init_ui()
        
        if self.device_data:
            self.device_id_input.setText(self.device_data.get('device_id', ''))
            self.device_name_input.setText(self.device_data.get('device_name', ''))
            self.mac_input.setText(self.device_data.get('mac_address', ''))
            # Lock these fields to avoid mistakes if assigning user to existing device
            self.device_id_input.setReadOnly(True)
            self.mac_input.setReadOnly(True)
            self.device_id_input.setStyleSheet(INPUT_STYLE + "background-color: #f0f0f0;")
            self.mac_input.setStyleSheet(INPUT_STYLE + "background-color: #f0f0f0;")
    
    def init_ui(self):
        """إنشاء واجهة النافذة"""
        layout = QVBoxLayout()
        
        # مجموعة معلومات الجهاز
        group = QGroupBox("معلومات الجهاز")
        group.setStyleSheet(GROUP_BOX_STYLE)
        form_layout = QFormLayout()
        
        # معرّف الجهاز
        self.device_id_input = QLineEdit()
        self.device_id_input.setPlaceholderText("مثال: aa:bb:cc:dd:ee:ff_PC-Name")
        self.device_id_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow("معرّف الجهاز:", self.device_id_input)
        
        # اسم الجهاز
        self.device_name_input = QLineEdit()
        self.device_name_input.setPlaceholderText("مثال: PC-Alex-01")
        self.device_name_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow("اسم الجهاز:", self.device_name_input)
        
        # MAC Address
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("مثال: aa:bb:cc:dd:ee:ff")
        self.mac_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow("MAC Address:", self.mac_input)
        
        # الفرع
        self.store_combo = QComboBox()
        self.store_combo.setStyleSheet(INPUT_STYLE)
        self.store_combo.addItem("جميع الفروع", None)
        
        stores = self.db.get_all_stores()
        for store in stores:
            self.store_combo.addItem(store['store_name'], store['id'])
        
        form_layout.addRow("الفرع:", self.store_combo)
        
        # المستخدم (اختياري)
        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet(INPUT_STYLE)
        self.user_combo.addItem("جميع المستخدمين", None)
        
        users = self.db.get_all_users()
        for user in users:
            self.user_combo.addItem(user['name'], user['id'])
        
        form_layout.addRow("المستخدم:", self.user_combo)
        
        # ملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("ملاحظات إضافية...")
        self.notes_input.setStyleSheet(INPUT_STYLE)
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 حفظ")
        save_btn.setStyleSheet(get_button_style('success'))
        save_btn.clicked.connect(self.save_device)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet(get_button_style('secondary'))
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def save_device(self):
        """حفظ الجهاز الجديد"""
        device_id = self.device_id_input.text().strip()
        device_name = self.device_name_input.text().strip()
        mac_address = self.mac_input.text().strip()
        store_id = self.store_combo.currentData()
        user_id = self.user_combo.currentData()
        notes = self.notes_input.toPlainText().strip()
        
        # التحقق من البيانات
        if not device_id:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال معرّف الجهاز")
            return
        
        if not device_name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الجهاز")
            return
        
        if not mac_address:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال MAC Address")
            return
        
        # حفظ الجهاز
        if self.db.register_device(
            device_id=device_id,
            device_name=device_name,
            mac_address=mac_address,
            store_id=store_id,
            user_id=user_id,
            registered_by=self.user_info.get('id'),
            notes=notes
        ):
            QMessageBox.information(self, "نجاح", "تم إضافة الجهاز بنجاح")
            self.accept()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في إضافة الجهاز\nقد يكون الجهاز مسجلاً مسبقاً")
