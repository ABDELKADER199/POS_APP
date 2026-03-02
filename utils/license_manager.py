import subprocess
import hashlib
import os

class LicenseManager:
    """إدارة ترخيص البرنامج وربطه بالهاردوير"""
    
    SECRET_SALT = "Pos_Safe_2026_@Admin" # ملح سري خاص بك لتأمين المفاتيح

    @staticmethod
    def get_bios_serial():
        """جلب الرقم التسلسلي للـ BIOS"""
        try:
            # محاولة جلب الرقم التسلسلي للـ BIOS
            output = subprocess.check_output('wmic bios get serialnumber', shell=True).decode().split()
            if len(output) >= 2 and output[1] not in ['0', 'None', 'Default', 'To', 'be', 'filled']:
                return output[1].strip()
            
            # محاولة بديلة: UUID النظام
            output = subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split()
            if len(output) >= 2:
                return output[1].strip()
                
            return "UNKNOWN_HW_ID"
        except Exception:
            return "UNKNOWN_HW_ID"

    @classmethod
    def get_hardware_id(cls):
        """توليد كود الجهاز (Hardware ID) ليقوم العميل بإرساله لك"""
        bios = cls.get_bios_serial()
        # تشفير الرقم التسلسلي لجعله "كود طلب" غير مفهوم للعميل
        h = hashlib.sha256(f"{bios}{cls.SECRET_SALT}".encode()).hexdigest().upper()
        # نأخذ أول 16 حرفاً مقسمة لمجموعات لسهولة القراءة
        short_id = f"{h[:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"
        return short_id

    @classmethod
    def generate_activation_key(cls, hardware_id):
        """
        توليد مفتاح التفعيل (Activation Key) بناءً على كود الجهاز
        ملاحظة: هذه الدالة ستستخدمها أنت فقط في أداة خارجية أو مخفية
        """
        raw_key = f"{hardware_id}{cls.SECRET_SALT}_ACTIVATED".encode()
        h = hashlib.sha256(raw_key).hexdigest().upper()
        return f"{h[:4]}-{h[8:12]}-{h[16:20]}-{h[24:28]}"

    @classmethod
    def verify_key(cls, hardware_id, key):
        """التحقق من صحة مفتاح التفعيل المدخل"""
        expected_key = cls.generate_activation_key(hardware_id)
        return key.strip().upper() == expected_key
