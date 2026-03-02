import os
import shutil
import datetime

release_dir = "InventoryPOS_Release"
exe_path = "dist/InventoryPOS.exe"
config_path = "config.json"
template_path = "template_products_import.xlsx"
readme_file = "README_FINAL.md"
readme_content = """# InventoryPOS - نظام إدارة المخزون والمبيعات
الإصدار: 1.0.0
التاريخ: {date}

## تعليمات التشغيل لأول مرة:

1. **تأكد من وجود الملفات التالية في نفس المجلد:**
   - `InventoryPOS.exe`: ملف البرنامج الرئيسي.
   - `config.json`: ملف إعدادات قاعدة البيانات.
   - `template_products_import.xlsx`: قالب استيراد المنتجات (اختياري).
   - هذا الملف (`README.txt`).

2. **قاعدة البيانات:**
   - تأكد من تشغيل خادم MySQL (مثل XAMPP).
   - البرنامج سيقوم تلقائياً بإنشاء الجداول عند التشغيل لأول مرة إذا كانت قاعدة البيانات فارغة.
   - إذا كنت تنقل البرنامج من جهاز لآخر، تأكد من تعديل `config.json` ليشير إلى عنوان الخادم الصحيح (مثلاً `localhost` أو IP الجهاز الخادم).

3. **تسجيل الدخول:**
   - الحساب الافتراضي للمسؤول (إذا تم إنشاؤه):
     - البريد: admin@admin.com
     - كلمة المرور: admin123
   - يمكنك تغيير كلمة المرور بعد الدخول من إعدادات المستخدم.

4. **الدعم الفني:**
   - للإبلاغ عن أي مشاكل، يرجى التواصل مع مطور النظام.

## الملاحظات الهامة:
- لا تقم بحذف ملف `config.json` وإلا سيفقد البرنامج الاتصال بقاعدة البيانات.
- يمكنك نسخ المجلد بالكامل (`InventoryPOS_Release`) إلى أي مكان على جهازك وتشغيله.
"""

def create_release():
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
        print(f"✅ Created release directory: {release_dir}")
    else:
        print(f"ℹ️ Release directory exists: {release_dir}")

    # Copy EXE
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, os.path.join(release_dir, "InventoryPOS.exe"))
        print(f"✅ Copied EXE to release folder.")
    else:
        print(f"❌ EXE not found at {exe_path}")

    # Copy Config
    if os.path.exists(config_path):
        shutil.copy2(config_path, os.path.join(release_dir, "config.json"))
        print(f"✅ Copied config.json.")
    else:
        print(f"⚠️ config.json not found.")

    # Copy Template
    if os.path.exists(template_path):
        shutil.copy2(template_path, os.path.join(release_dir, "template_products_import.xlsx"))
        print(f"✅ Copied template xlsx.")
    else:
        print(f"⚠️ Template xlsx not found.")

    # Create README
    with open(os.path.join(release_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content.format(date=datetime.datetime.now().strftime("%Y-%m-%d")))
    print(f"✅ Created README.txt.")

    print(f"🎉 Release ready at: {os.path.abspath(release_dir)}")

if __name__ == "__main__":
    create_release()
