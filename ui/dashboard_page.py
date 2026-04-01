"""
صفحة لوحة التحكم الرئيسية
Dashboard Page
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTabWidget, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from ui.purchases_page import PurchasesPage
from ui.styles import GLOBAL_STYLE, BUTTON_STYLES, get_button_style, COLORS, TABLE_STYLE, GROUP_BOX_STYLE, INPUT_STYLE, LABEL_STYLE_HEADER, LABEL_STYLE_TITLE, TAB_STYLE

from database_manager import DatabaseManager
from ui.admin_panel import AdminPanel
from ui.cashier_page import CashierPage
from ui.call_center_page import CallCenterPage
from ui.products_page import ProductsPage
from ui.drawer_page import DrawerPage
from ui.returns_page import ReturnsPage
from ui.stats_page import StatsPage
from ui.accounts_page import AccountsPage
from ui.settings_page import SettingsPage
from ui.purchases_page import PurchasesPage 

class DashboardPage(QWidget):
    """صفحة لوحة التحكم الرئيسية"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.parent = parent
        self.user_info = None
        self.db = DatabaseManager()
        self._loaded_tabs = set()
        self.init_ui()
    
    def init_ui(self):
        """إنشاء واجهة الصفحة"""
        main_layout = QVBoxLayout()
        
        # شريط العنوان والمعلومات
        header_layout = QHBoxLayout()
        
        # العنوان
        title = QLabel("لوحة التحكم الرئيسية")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # المسافة
        header_layout.addStretch()
        
        # معلومات المستخدم
        self.user_label = QLabel()
        self.user_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(self.user_label)
        
        # زر التحديث
        refresh_btn = QPushButton("🔄 تحديث البيانات")
        refresh_btn.setMinimumWidth(150)
        refresh_btn.setStyleSheet(get_button_style("primary"))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_all_data)
        header_layout.addWidget(refresh_btn)
        
        # حاوية التنبيهات (ستظهر فقط عند الحاجة)
        self.alert_container = QWidget()
        self.alert_layout = QHBoxLayout(self.alert_container)
        self.alert_layout.setContentsMargins(10, 0, 10, 0)
        self.alert_label = QLabel()
        self.alert_label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold; font-size: 14px; background: #fff5f5; padding: 5px 15px; border: 1px solid {COLORS['danger']}; border-radius: 5px;")
        self.alert_layout.addWidget(self.alert_label)
        self.alert_container.hide()
        self.alert_container.installEventFilter(self)
        self.alert_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header_layout.addWidget(self.alert_container)
        
        # زر تسجيل الخروج
        logout_btn = QPushButton("تسجيل الخروج")
        logout_btn.setMinimumWidth(120)
        logout_btn.setStyleSheet(get_button_style("danger"))
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        
        main_layout.addLayout(header_layout)
        
        # إضافة فاصل
        main_layout.addSpacing(20)
        
        # إنشاء علامات التبويب
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # سيتم إضافة الصفحات بناءً على دور المستخدم
        self.admin_panel = AdminPanel(auto_load=False)
        self.cashier_page = CashierPage()
        self.call_center_page = CallCenterPage(auto_load=False)
        self.products_page = ProductsPage(auto_load=False)
        self.drawer_page = DrawerPage()
        self.returns_page = ReturnsPage(self.db, self.user_info)
        self.stats_page = StatsPage(self.db, auto_load=False)
        self.accounts_page = AccountsPage(self.user_info, auto_load=False)
        self.purchases_page = PurchasesPage(self.db, self.user_info, auto_load=False)
        self.settings_page = SettingsPage()
        
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
    
    def set_user(self, user_info):
        """تعيين معلومات المستخدم"""
        self.user_info = user_info
        self._loaded_tabs.clear()
        
        # تحديث صفحة الكاشير وصفحة الدرج بمعلومات المستخدم
        if hasattr(self.cashier_page, 'set_user'):
            self.cashier_page.set_user(user_info)
        if hasattr(self.drawer_page, 'set_user'):
            self.drawer_page.set_user(user_info)
            # Connect drawer signals
            try:
                self.drawer_page.drawer_opened.disconnect()
                self.drawer_page.drawer_closed.disconnect()
            except TypeError:
                pass # Not connected
            self.drawer_page.drawer_opened.connect(self.on_drawer_opened)
            self.drawer_page.drawer_closed.connect(self.on_drawer_closed)
        
        if hasattr(self.returns_page, 'set_user'):
            self.returns_page.set_user(user_info)
            # Connect return processed signal to refresh inventory
            try:
                self.returns_page.return_processed.disconnect()
            except TypeError:
                pass
            self.returns_page.return_processed.connect(self.refresh_all_data)

        if hasattr(self.call_center_page, 'set_user'):
            self.call_center_page.set_user(user_info)

        if hasattr(self.admin_panel, 'set_user'):
            self.admin_panel.set_user(user_info)

        if hasattr(self.products_page, 'set_user'):
            self.products_page.set_user(user_info)
            # Connect product data change signal
            try:
                self.products_page.data_changed.disconnect()
            except (TypeError, AttributeError):
                pass
            self.products_page.data_changed.connect(self.refresh_all_data)

        if hasattr(self.accounts_page, 'set_user'):
            self.accounts_page.set_user(user_info)
        if hasattr(self.purchases_page, 'set_user'):
            self.purchases_page.set_user(user_info)
        if hasattr(self.settings_page, 'set_user'):
            self.settings_page.set_user(user_info)
            
        if hasattr(self.cashier_page, 'sale_completed'):
            try:
                self.cashier_page.sale_completed.disconnect()
            except TypeError:
                pass
            self.cashier_page.sale_completed.connect(self.refresh_all_data)
        
        # تحديث معلومات المستخدم في الواجهة
        self.user_label.setText(
            f"👤 المستخدِم: <b style='color: {COLORS['text_light']}'>{user_info['name']}</b> | "
            f"📍 الفرع: <b style='color: {COLORS['success']}'>{user_info.get('store_name', 'غير محدد')}</b> | "
            f"🛡️ الدور: {user_info['role_name']}"
        )
        self.user_label.setTextFormat(Qt.TextFormat.RichText)
        
        # التحقق من النواقص (للمديرين فقط)
        if user_info['role_id'] in [99, 1, 2]:
            QTimer.singleShot(1500, self.check_low_stock)
        else:
            self.alert_container.hide()
        
        # تنظيف علامات التبويب السابقة
        self.tabs.clear()
        
        # إضافة علامات التبويب بناءً على الدور
        role = user_info['role_id']
        
        if role in [99, 3, 1]:  # Developer, Cashier (Mirrored), or Admin
            self.tabs.addTab(self.stats_page, "الإحصائيات")
            self.tabs.addTab(self.admin_panel, "إدارة المستخدمين")
            self.tabs.addTab(self.products_page, "إدارة المنتجات")
            self.tabs.addTab(self.purchases_page, "🛒 المشتريات والموردين")
            self.tabs.addTab(self.accounts_page, "💰 الحسابات والمالية")
            self.tabs.addTab(self.returns_page, "مرتجع فواتير")
            self.tabs.addTab(self.cashier_page, "الكاشير")
            self.tabs.addTab(self.call_center_page, "Call Center")
            self.tabs.addTab(self.drawer_page, "درج الكاشير")
            self.tabs.addTab(self.settings_page, "⚙️ الإعدادات")
        
        elif role == 2:  # Manager
            self.tabs.addTab(self.products_page, "إدارة المنتجات")
            self.tabs.addTab(self.purchases_page, "🛒 المشتريات والموردين")
            self.tabs.addTab(self.accounts_page, "💰 الحسابات والمالية")
            self.tabs.addTab(self.returns_page, "مرتجع فواتير")
            self.tabs.addTab(self.cashier_page, "الكاشير")
            self.tabs.addTab(self.call_center_page, "Call Center")
            self.tabs.addTab(self.drawer_page, "درج الكاشير")
        
        elif role == 4:  # Call Center
            self.tabs.addTab(self.call_center_page, "Call Center")
        
        elif role == 5:  # Warehouse Staff
            self.tabs.addTab(self.products_page, "المنتجات")
            self.tabs.addTab(self.accounts_page, "💰 الحسابات")
            
        # Check Drawer Logic - تم نقله إلى set_user لأن user_info غير متوفر هنا
        # self.check_drawer_access(user_info)
        
        # إعداد الاختصارات بعد إضافة التبويبات
        self.setup_shortcuts()
        
        # افتح على تبويب الكاشير افتراضيًا لتقليل حمل البداية
        cashier_idx = self.tabs.indexOf(self.cashier_page)
        if cashier_idx >= 0:
            self.tabs.setCurrentIndex(cashier_idx)
        
        # تحميل بيانات التبويب الحالي فقط
        QTimer.singleShot(0, lambda: self.on_tab_changed(self.tabs.currentIndex()))

    def on_tab_changed(self, index: int):
        """تحميل بيانات التبويب عند فتحه لأول مرة."""
        if index < 0:
            return
        widget = self.tabs.widget(index)
        self._ensure_tab_loaded(widget, force=False)

    def _ensure_tab_loaded(self, widget, force: bool = False):
        if widget is None:
            return

        key = id(widget)
        if (not force) and key in self._loaded_tabs:
            return

        try:
            if widget == self.products_page and hasattr(self.products_page, 'ensure_loaded'):
                self.products_page.ensure_loaded(force=force)
            elif widget == self.stats_page and hasattr(self.stats_page, 'ensure_loaded'):
                self.stats_page.ensure_loaded(force=force)
            elif widget == self.accounts_page and hasattr(self.accounts_page, 'ensure_loaded'):
                self.accounts_page.ensure_loaded(force=force)
            elif widget == self.purchases_page and hasattr(self.purchases_page, 'ensure_loaded'):
                self.purchases_page.ensure_loaded(force=force)
            elif widget == self.admin_panel:
                if hasattr(self.admin_panel, 'ensure_loaded'):
                    self.admin_panel.ensure_loaded(force=force)
                else:
                    self.admin_panel.load_users()
                    self.admin_panel.load_drawers()
            elif widget == self.call_center_page:
                if hasattr(self.call_center_page, 'ensure_loaded'):
                    self.call_center_page.ensure_loaded(force=force)
                else:
                    self.call_center_page.load_orders()
            elif widget == self.drawer_page:
                self.drawer_page.check_drawer_status()
        finally:
            self._loaded_tabs.add(key)

    def setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        # 1. التنقل بين التبويبات (F1 - F12)
        for i in range(min(self.tabs.count(), 12)):
            key = getattr(Qt.Key, f"Key_F{i+1}")
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda index=i: self.tabs.setCurrentIndex(index))

        # 2. تحديث البيانات (F5)
        self.refresh_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F5), self)
        self.refresh_shortcut.activated.connect(self.refresh_all_data)

        # 3. تسجيل الخروج (Ctrl + L)
        self.logout_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.logout_shortcut.activated.connect(self.logout)

        # 4. إغلاق البرنامج (Ctrl + Q)
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(lambda: self.parent.close() if self.parent else self.close())

        # 5. اختصار مخصص للمرتجعات (Ctrl + R)
        self.returns_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.returns_shortcut.activated.connect(self.switch_to_returns)

    def switch_to_returns(self):
        """الانتقال لتبويب المرتجعات"""
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == self.returns_page:
                self.tabs.setCurrentIndex(i)
                break
        
    def on_drawer_opened(self):
        """يتم استدعاؤها عند فتح الدرج لتوجيه المستخدم للكاشير"""
        # تحديث الصلاحيات والوصول أولاً
        self.check_drawer_access(self.user_info)
        # الانتقال المباشر لتبويب الكاشير
        if hasattr(self, 'cashier_page'):
            self.tabs.setCurrentWidget(self.cashier_page)
            # تنشيط الصفحة وتجهيزها
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.cashier_page.refresh_page)
        
        # ميزة إضافية: تحديث البيانات فور الفتح
        self.refresh_all_data()

    def on_drawer_closed(self):
        """يتم استدعاؤها عند إغلاق الدرج للخروج من البرنامج"""
        self.check_drawer_access(self.user_info)
        # إغلاق البرنامج بالكامل كما طلب المستخدم
        if self.parent:
            # استدعاء دالة الخروج في النافذة الرئيسية
            self.parent.close()

    def check_drawer_access(self, user_info):
        """التحقق من صلاحيات الدرج وتأمين الوصول للكاشير"""
        if not user_info:
            return

        store_id = user_info.get('store_id')
        user_id = user_info.get('id')
        role_id = user_info.get('role_id')
        
        # 1. جلب حالة الدرج في المتجر
        drawer_status = self.db.get_store_open_drawer(store_id)
        
        # البحث عن رقم تبويب الكاشير
        cashier_tab_index = -1
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == self.cashier_page:
                cashier_tab_index = i
                break

        # سيناريو 1: لا يوجد درج مفتوح
        if not drawer_status:
            if cashier_tab_index != -1:
                self.tabs.setTabEnabled(cashier_tab_index, False)
                self.tabs.setTabToolTip(cashier_tab_index, "يجب فتح درج أولاً")
            
            # إذا كان المستخدم كاشير وصار الدرج مغلق، اجبره يروح لصفحة الدرج
            if role_id == 3:
                self.tabs.setCurrentWidget(self.drawer_page)
            return

        # سيناريو 2: يوجد درج مفتوح باسم مستخدم آخر
        if drawer_status['cashier_id'] != user_id:
            # المطور والمديرين مسموح لهم باستخدام درج مشترك
            if role_id not in [99, 1, 2]:
                if cashier_tab_index != -1:
                    self.tabs.setTabEnabled(cashier_tab_index, False)
                    self.tabs.setTabToolTip(cashier_tab_index, f"الجهاز مشغول بدرج مفتوح لـ: {drawer_status['cashier_name']}")
                
                if role_id == 3: # كاشير يحاول يدخل وزميله فاتح الدرج
                    self.tabs.setCurrentWidget(self.drawer_page)
            else:
                # المدير/مدير الفرع/المطور مسموح له بالدخول للكاشير حتى لو الدرج لغيره
                if cashier_tab_index != -1:
                    self.tabs.setTabEnabled(cashier_tab_index, True)
                    self.tabs.setTabToolTip(cashier_tab_index, f"استخدام درج (Shared Mode): {drawer_status['cashier_name']}")
            return
            
        # سيناريو 3: الدرج مفتوح باسمي - السماح بالكاشير
        if cashier_tab_index != -1:
            self.tabs.setTabEnabled(cashier_tab_index, True)
            self.tabs.setTabToolTip(cashier_tab_index, "")

    def logout(self):
        """تسجيل الخروج"""
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل تريد تسجيل الخروج؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.parent.logout()

    def refresh_all_data(self):
        """Refresh visible tab data without reloading all heavy tabs."""
        current_widget = self.tabs.currentWidget()
        self._ensure_tab_loaded(current_widget, force=True)

        if current_widget is not None:
            self._loaded_tabs = {id(current_widget)}

        if self.user_info:
            if self.user_info["role_id"] in [99, 1, 2]:
                self.check_low_stock()
            self.check_drawer_alert()

    def check_low_stock(self):
        """التحقق من وجود أصناف تحت حد الأمان"""
        try:
            store_id = self.user_info.get('store_id') if self.user_info['role_id'] != 99 else None
            low_stock_items = self.db.get_low_stock_alerts(store_id)
            
            if low_stock_items:
                # إذا وجدنا نواقص، نحدث النص ونظهر الحاوية (إلا إذا كان هناك تنبيه أهم)
                if not self.alert_container.isVisible() or "درج" not in self.alert_label.text():
                    self.alert_label.setText(f"⚠️ يوجد {len(low_stock_items)} صنف تحت حد الأمان!")
                    self.alert_container.show()
                return True
            return False
        except Exception as e:
            print(f"Error checking low stock: {e}")
            return False

    def check_drawer_alert(self):
        """تنبيه المستخدم إذا لم يكن هناك درج مفتوح في الفرع"""
        if not self.user_info: return
        
        store_id = self.user_info.get('store_id')
        drawer = self.db.get_store_open_drawer(store_id)
        
        if not drawer:
            self.alert_label.setText("⚠️ تنبيه: لا يوجد درج كاشير نشط في هذا الفرع!")
            # تغيير الستايل ليكون أكثر بروزاً لو أردنا، أو البقاء على الأحمر
            self.alert_container.show()
            self.alert_container.setToolTip("اضغط هنا لفتح درج جديد")
            return True
        else:
            # إذا كان الدرج مفتوحاً، نخفي التنبيه (إلا لو كان هناك تنبيه نواقص)
            if "درج" in self.alert_label.text():
                self.alert_container.hide()
                # نعيد فحص النواقص ليظهر إذا كان موجوداً
                if self.user_info['role_id'] in [99, 1, 2]:
                    self.check_low_stock()
            return False

    def eventFilter(self, source, event):
        """معالجة أحداث النقر على التنبيهات"""
        if (source == self.alert_container and 
            event.type() == event.Type.MouseButtonPress):
            self.tabs.setCurrentWidget(self.products_page)
            if hasattr(self.products_page, 'tabs'):
                self.products_page.tabs.setCurrentIndex(1)
            return True
        return super().eventFilter(source, event)
