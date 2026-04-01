from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class SyncWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)

    def __init__(self, sync_manager):
        super().__init__()
        self.sync_manager = sync_manager

    def run(self):
        try:
            success = self.sync_manager.sync_to_cloud(
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.finished.emit(success)
        except Exception as e:
            logger.error(f"Sync thread error: {e}")
            self.finished.emit(False)

class SyncDialog(QDialog):
    """نافذة تقدم المزامنة عند إغلاق البرنامج"""
    def __init__(self, sync_manager, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.success = False
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.setModal(True)
        self.setWindowTitle("جاري مزامنة البيانات...")
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("جاري الاتصال بالسحاب ومزامنة العمليات المعلقة...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.worker = SyncWorker(self.sync_manager)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        
    def start_sync(self):
        self.worker.start()
        
    def update_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.label.setText(msg)
        
    def on_finished(self, success):
        self.success = success
        if success:
            self.label.setText("تمت المزامنة بنجاح! جاري الإغلاق...")
            self.progress_bar.setValue(100)
        else:
            self.label.setText("فشلت المزامنة. يرجى التحقق من الإنترنت.")
        
        # الانتظار قليلاً ليتمكن المستخدم من رؤية النتيجة
        QThread.msleep(1000)
        self.accept()

from PyQt6.QtWidgets import QMessageBox

def run_mandatory_sync(sync_manager, parent, context_msg="يجب مزامنة البيانات قبل الخروج"):
    """دالة مساعدة لعرض الرسالة الإجبارية ثم نافذة المزامنة"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("تنبيه مزامنة")
    msg.setText(context_msg)
    msg.addButton("موافق", QMessageBox.ButtonRole.AcceptRole)
    msg.exec()
    
    sync_dlg = SyncDialog(sync_manager, parent)
    sync_dlg.show()
    sync_dlg.start_sync()
    sync_dlg.exec()
    
    if not sync_dlg.success:
        QMessageBox.warning(
            parent,
            "فشل المزامنة",
            "يرجى التأكد من فحص اتصال الإنترنت والمحاولة مرة أخرى عند فتح التطبيق في وقت لاحق."
        )
    return sync_dlg.success
