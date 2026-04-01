import sys
import os
import traceback
import logging
from datetime import datetime
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, 
                             QMessageBox, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont
from ui.login_page import LoginPage
from ui.dashboard_page import DashboardPage
from ui.returns_page import ReturnsPage
from ui.expenses_page import ExpensesPage
from ui.activation_page import ActivationPage
from utils.license_manager import LicenseManager
from ui.styles import GLOBAL_STYLE, COLORS
from database_manager import DatabaseManager
from utils.path_helper import resource_path
from utils.sync_manager import SyncManager
from ui.sync_dialog import SyncDialog

# إعداد نظام التنبيهات واللوج
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class POSApplication(QMainWindow):
    """تطبيق نقطة البيع الرئيسي"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.sync_manager = SyncManager() # مدير المزامنة
        self.setWindowTitle("نظام نقطة البيع المتكاملة - POS System")
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        
        # تعيين حجم صغير لصفحة تسجيل الدخول
        self.setFixedSize(700, 550)
        
        # تطبيق النمط الموحد
        self.setStyleSheet(GLOBAL_STYLE)
        
        # القائمة الرئيسية
        self.create_menu()
        
        # الصفحات المكدسة
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # إنشاء صفحات التطبيق
        # 1. Login Page
        self.login_page = LoginPage(self.db, self)
        self.stacked_widget.addWidget(self.login_page)
        
        # 2. Activation Page
        self.activation_page = ActivationPage(self.db)
        self.activation_page.activation_success.connect(self.show_login)
        self.stacked_widget.addWidget(self.activation_page)
        
        # 3. Dashboard (Empty for now, initialized after login)
        self.dashboard_page = None
        
        # التحقق من الاتصال بقاعدة البيانات
        self.check_database_connection()
        
        # --- NEW: Sync Recovery on Startup ---
        self.check_sync_recovery()
        
        # بدء المزامنة في الخلفية
        self.sync_manager.start_background_sync(interval=600) # كل 10 دقائق

    def create_menu(self):
        """إنشاء القائمة الرئيسية"""
        menubar = self.menuBar()
        
        # قائمة ملف
        file_menu = menubar.addMenu("ظ…ظ„ظپ")
        
        exit_action = file_menu.addAction("خروج")
        exit_action.triggered.connect(self.quit_application)
        
        # قائمة تحرير
        edit_menu = menubar.addMenu("تحرير")
        
        # قائمة مساعدة
        help_menu = menubar.addMenu("مساعدة")
        
        about_action = help_menu.addAction("عن التطبيق")
        about_action.triggered.connect(self.show_about)
    
    def check_database_connection(self):
        """التحقق من الاتصال بقاعدة البيانات"""
        try:
            if not self.db.cursor:
                raise RuntimeError("غير متصل بقاعدة البيانات")

            cursor = self.db.cursor
            cursor.execute("SELECT 1")
            cursor.fetchone()
        except (mysql.connector.Error, RuntimeError, AttributeError) as e:
            QMessageBox.critical(
                self, "خطأ الاتصال",
                f"فشل الاتصال بقاعدة البيانات:\n{str(e)}\n\nيرجى تشغيل خادم MySQL"
            )
            sys.exit(1)
            
    def check_sync_recovery(self):
        """التحقق من المزامنة عند الفتح"""
        try:
            logger.info("Checking sync on startup as requested...")
            from ui.sync_dialog import run_mandatory_sync
            run_mandatory_sync(self.sync_manager, self, "يجب مزامنة البيانات ومقارنتها مع السحابة عند فتح التطبيق")
        except Exception as e:
            logger.error(f"Startup sync recovery failed: {e}")
            
    def check_initial_page(self):
        """Check if system is activated and show appropriate page"""
        hw_id = LicenseManager.get_hardware_id()
        if self.db.check_system_license(hw_id):
            self.show_login()
        else:
            self.show_activation()

    def show_activation(self):
        self.stacked_widget.setCurrentWidget(self.activation_page)
        self.setWindowTitle("تفعيل النظام - POS System")

    def show_login(self, success_message=None):
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.setWindowTitle("تسجيل الدخول - POS System")
        if success_message:
            # Custom logic if needed
            pass

    def show_dashboard(self, user_info):
        """عرض لوحة المعلومات بعد تسجيل الدخول"""
        # تمكين تغيير الحجم وتكبير النافذة
        self.setMinimumSize(1000, 700)
        self.setMaximumSize(16777215, 16777215) # QWIDGETSIZE_MAX
        self.showMaximized()
        
        # إنشاء صفحة لوحة المعلومات
        self.dashboard_page = DashboardPage(self)
        
        # إزالة الصفحة السابقة إن وجدت
        if self.stacked_widget.count() > 1:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        
        # إضافة الصفحة الجديدة
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # تعيين المستخدم        
        # عرض الصفحة
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        QTimer.singleShot(0, lambda: self.dashboard_page.set_user(user_info))
    
    def logout(self):
        """تسجيل الخروج"""
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل تريد تسجيل الخروج؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from ui.sync_dialog import run_mandatory_sync
            run_mandatory_sync(self.sync_manager, self, "يجب مزامنة البيانات قبل تسجيل الخروج")
            
            # إزالة صفحة لوحة المعلومات
            if self.dashboard_page:
                self.stacked_widget.removeWidget(self.dashboard_page)
                self.dashboard_page = None
            
            # إعادة تعيين صفحة تسجيل الدخول
            self.login_page = LoginPage(self.db, self) # Re-initialize with db
            
            # إضافتها مرة أخرى
            # Remove existing login/activation pages if they are at index 0 or 1
            for i in range(self.stacked_widget.count()):
                widget = self.stacked_widget.widget(i)
                if isinstance(widget, (LoginPage, ActivationPage)):
                    self.stacked_widget.removeWidget(widget)
            
            self.stacked_widget.insertWidget(0, self.login_page) # Insert at the beginning
            self.stacked_widget.insertWidget(1, self.activation_page) # Insert activation page
            self.stacked_widget.setCurrentWidget(self.login_page)
            
            # إعادة الحجم الصغير
            self.showNormal()
            self.setFixedSize(700, 500)
    
    def show_about(self):
        """عرض نافذة حول التطبيق"""
        QMessageBox.information(
            self, "عن التطبيق",
            "نظام نقطة البيع المتكاملة (POS)\n\n"
            "إصدار: 1.0\n"
            "نظام متكامل لإدارة المبيعات والمخزون\n\n"
            "© 2024 - جميع الحقوق محفوظة\n"
            "تم التطوير بواسطة: عبدالقادر طارق\n"
            "للتواصل: [apdoarek22222@gmail.com]\n"
            "رقم الهاتف: 01070276578"
            
        )
    
    def quit_application(self):
        """إغلاق التطبيق"""
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل تريد إغلاق التطبيق؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def closeEvent(self, event):
        """حدث إغلاق النافذة - مزامنة البيانات قبل الخروج"""
        try:
            # 1. إيقاف المزامنة التلقائية (التي كانت تعمل في الخلفية)
            self.sync_manager.stop_background_sync()
            
            # 2. إجبار المزامنة قبل الخروج كما طلب المستخدم
            from ui.sync_dialog import run_mandatory_sync
            run_mandatory_sync(self.sync_manager, self, "يجب مزامنة البيانات قبل الخروج")
            
            # 3. إغلاق الاتصال بقاعدة البيانات
            self.db.close()
            
        except Exception as e:
            print(f"Failed to sync/close cleanly: {e}")
            logger.error("Close event error: %s", e, exc_info=True)

        event.accept()

def main():
    """نقطة البداية للتطبيق"""
    app = QApplication(sys.argv)
    
    # تعيين الخط العام
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # إنشاء نافذة التطبيق
    window = POSApplication()
    window.check_initial_page()
    
    # عرض النافذة
    window.show()
    
    # بدء حلقة أحداث التطبيق
    sys.exit(app.exec())

def exception_hook(exctype, value, tb):
    """Global exception handler to log errors to a file"""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("Uncaught exception:", error_msg)
    
    # Write to file
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"\n\n--- Error at {datetime.now()} ---\n")
        f.write(error_msg)
        
        
    # Show message box if GUI is alive
    try:
        if QApplication.instance():
            QMessageBox.critical(None, "Critical Error", f"حدث خطأ غير متوقع:\n{value}\n\nراجع ملف error.log للتفاصيل.")
    except (RuntimeError, TypeError) as e:
        print(f"Failed to show critical error dialog: {e}")

    sys.__excepthook__(exctype, value, tb)

if __name__ == "__main__":

    sys.excepthook = exception_hook
    main()





