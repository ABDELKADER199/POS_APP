import os

def patch_db_manager():
    path = r"d:\Python Desktop\database_manager.py"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = -1
    for i, line in enumerate(lines):
        if "def __init__(self):" in line:
            start_idx = i
            break
            
    end_idx = -1
    for i, line in enumerate(lines):
        if "def load_config(self):" in line:
            end_idx = i
            break

    if start_idx == -1 or end_idx == -1:
        print(f"Error: Could not find markers. start={start_idx}, end={end_idx}")
        return

    # Replace everything from __init__ start to load_config start
    new_methods = """    def __init__(self):
        \"\"\"تهيئة اتصال قاعدة البيانات\"\"\"
        if not hasattr(self, 'host'):
            self.host = None
            self.user = None
            self.password = None
            self.database = None
            self.port = 3306
            self.ssl_mode = 'DISABLED'
            self.ssl_ca = ''
            self.conn = None
            self.cursor = None
            self._is_initialized = False
            self._verbose_diagnostics = str(
                os.getenv('POS_VERBOSE_DIAGNOSTICS', '0')
            ).strip().lower() in {'1', 'true', 'yes', 'on'}
        
        if hasattr(self, '_is_initialized') and self._is_initialized:
            return
        
        with DatabaseManager._lock:
            if hasattr(self, '_is_initialized') and self._is_initialized:
                return
            self._is_initialized = True
        
        self.load_config()
        
        if self.host and self.user:
            if self.connect():
                assert self.cursor is not None and self.conn is not None
                self.create_license_table()
                self.create_returns_tables()
                self.create_expenses_table()
                self.create_settings_table()
                self.create_purchases_tables()
                self.setup_accounts_system()
                self.create_sync_queue_table()
                self.apply_performance_indexes()

                self.apply_performance_indexes()
        else:
            logger.critical("DB config missing.")

    def _handle_non_critical_db_error(self, err, context=""):
        ignored_errnos = {1060, 1061, 1091, 1826}
        if getattr(err, "errno", None) in ignored_errnos:
            return
        logger.warning(f"DB error [{context}]: {err}")

    def create_license_table(self):
        try:
            assert self.cursor is not None and self.conn is not None
            self.cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS system_license (
                id INT PRIMARY KEY AUTO_INCREMENT,
                hardware_id VARCHAR(100) NOT NULL UNIQUE,
                activation_key VARCHAR(100) NOT NULL,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATE NULL,
                status VARCHAR(20) DEFAULT 'active'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            \"\"\")
            self.cursor.execute(\"SELECT id FROM roles WHERE id = 99\")
            if not self.cursor.fetchone():
                self.cursor.execute(\"INSERT INTO roles (id, role_name) VALUES (99, 'Developer')\")
            self.conn.commit()
        except Exception as err:
            logger.error(f\"License table error: {err}\")

    def check_system_license(self, hardware_id):
        try:
            query = \"SELECT activation_key FROM system_license WHERE hardware_id = %s AND status = 'active'\"
            self.cursor.execute(query, (hardware_id,))
            res = self.cursor.fetchone()
            if res:
                from utils.license_manager import LicenseManager
                return LicenseManager.verify_key(hardware_id, res['activation_key'])
            return False
        except Exception:
            return False

    def activate_system(self, hardware_id, key):
        from utils.license_manager import LicenseManager
        if LicenseManager.verify_key(hardware_id, key):
            try:
                query = \"INSERT INTO system_license (hardware_id, activation_key) VALUES (%s, %s)\"
                self.cursor.execute(query, (hardware_id, key.strip().upper()))
                self.conn.commit()
                return True
            except Exception:
                self.conn.rollback()
                return False
        return False

    def create_expenses_table(self):
        try:
            self.cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                store_id INT NOT NULL,
                user_id INT NOT NULL,
                expense_type VARCHAR(100) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description TEXT,
                expense_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES stores(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            \"\"\")
            self.conn.commit()
        except Exception as err:
            logger.error(f\"Expenses table error: {err}\")

    def create_settings_table(self):
        try:
            self.cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(50) PRIMARY KEY,
                setting_value TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            \"\"\")
            defaults = {
                'store_name': 'نظام POS المتكامل',
                'store_address': 'عنوان المحل غير محدد',
                'store_phone': '0123456789',
                'receipt_footer': 'شكراً لزيارتكم',
                'backup_path': 'backups'
            }
            for key, val in defaults.items():
                self.cursor.execute(\"INSERT IGNORE INTO system_settings (setting_key, setting_value) VALUES (%s, %s)\", (key, val))
            self.conn.commit()
        except Exception as err:
            logger.error(f\"Settings table error: {err}\")

    def get_settings(self):
        try:
            self.cursor.execute(\"SELECT setting_key, setting_value FROM system_settings\")
            results = self.cursor.fetchall()
            return {row['setting_key']: row['setting_value'] for row in results}
        except Exception:
            return {}

    def update_settings(self, settings):
        try:
            for key, val in settings.items():
                self.cursor.execute(\"\"\"
                    INSERT INTO system_settings (setting_key, setting_value) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                \"\"\", (key, str(val)))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def backup_database(self, custom_dir=None):
        \"\"\"إجراء نسخة احتياطية من قاعدة البيانات مع معالجة ذكية للمسار\"\"\"
        import subprocess
        from datetime import datetime
        if custom_dir:
            backup_dir = custom_dir
        else:
            settings = self.get_settings()
            backup_dir = settings.get('backup_path', 'backups')
        
        try:
            if not os.path.isabs(backup_dir):
                backup_dir = os.path.join(os.getcwd(), backup_dir)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
        except OSError:
            backup_dir = os.path.join(os.getcwd(), 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime(\"%Y-%m-%d_%H-%M-%S\")
        filename = f\"pos_backup_{timestamp}.sql\"
        filepath = os.path.join(backup_dir, filename)
        mysqldump_path = r\"C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe\"
        try:
            command = [mysqldump_path, f\"--host={self.host}\", f\"--user={self.user}\", f\"--password={self.password}\", self.database, f\"--result-file={filepath}\"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            return (True, filepath) if process.returncode == 0 else (False, error.decode('utf-8', errors='ignore'))
        except Exception as e:
            return (False, str(e))

"""
    new_lines = lines[:start_idx] + [new_methods] + lines[end_idx:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully patched DatabaseManager structure.")

if __name__ == "__main__":
    patch_db_manager()
