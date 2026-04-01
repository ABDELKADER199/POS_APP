"""
فئة DatabaseManager - للتعامل مع جميع عمليات قاعدة البيانات مع معالجة ذكية للمسار"""
import mysql.connector
import bcrypt
import json
import os
import logging
from typing import List, Dict, Optional, Tuple, Any, cast
from datetime import datetime
import sys
from threading import Lock

# إعداد نظام Logging
logger = logging.getLogger(__name__)
_log_level_name = (os.getenv('POS_LOG_LEVEL') or os.getenv('DB_LOG_LEVEL') or 'WARNING').upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logger.setLevel(_log_level)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(_log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class DatabaseManager:
    """فئة شاملة للتعامل مع قاعدة البيانات مع معالجة ذكية للمسار"""
    
    _instance = None
    _lock = Lock()
    
    def __init__(self):
        """تهيئة اتصال قاعدة البيانات"""
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.port = 3306
        self.ssl_mode = 'DISABLED'
        self.ssl_ca = ''
        self.conn = None
        self.cursor = None
        self._verbose_diagnostics = str(
            os.getenv('POS_VERBOSE_DIAGNOSTICS', '0')
        ).strip().lower() in {'1', 'true', 'yes', 'on'}
        
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

                # (Removed auto-initialization of SyncManager to avoid recursion)
        else:
            logger.critical("DB config missing.")

    def _handle_non_critical_db_error(self, err, context=""):
        ignored_errnos = {1060, 1061, 1091, 1826}
        if getattr(err, "errno", None) in ignored_errnos:
            return
        logger.warning(f"DB error [{context}]: {err}")

    def _execute_safe(self, query):
        """تنفيذ استعلام مع تجاهل الأخطاء الشائعة (مثل تكرار الفهرس)"""
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            # تجاهل خطأ تكرار الفهرس (1061)
            if err.errno != 1061:
                logger.debug(f"Info: Safe execute skipped: {err}")

    def create_sync_queue_table(self):
        """إنشاء جدول طابور المزامنة للعمل أوفلاين"""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                record_id VARCHAR(100) NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                data_json LONGTEXT NOT NULL,
                status ENUM('pending', 'synced', 'failed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP NULL,
                error_message TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            self.conn.commit()
            logger.info("✅ جدول طابور المزامنة جاهز")
        except mysql.connector.Error as err:
            logger.error(f"❌ خطأ في إنشاء جدول المزامنة: {err}")

    def apply_performance_indexes(self):
        """إضافة فهارس تحسين الأداء للجداول الرئيسية"""
        try:
            # 1. Products Indexes
            self._execute_safe("CREATE INDEX idx_product_code ON products(product_code)")
            self._execute_safe("CREATE INDEX idx_barcode ON products(barcode)")
            
            # 2. Inventory Indexes
            self._execute_safe("CREATE INDEX idx_inv_product ON product_inventory(product_id)")
            self._execute_safe("CREATE INDEX idx_inv_store ON product_inventory(store_id)")
            
            # 3. Invoices Indexes
            self._execute_safe("CREATE INDEX idx_invoice_date ON invoices(invoice_date)")
            self._execute_safe("CREATE INDEX idx_invoice_status ON invoices(status)")
            self._execute_safe("CREATE INDEX idx_cust_phone ON invoices(customer_phone)")
            
            # 4. Sync Queue Indexes
            self._execute_safe("CREATE INDEX idx_sync_status ON sync_queue(status)")
            
            self.conn.commit()
            logger.info("✅ تم تطبيق فهارس تحسين الأداء")
        except mysql.connector.Error as err:
            logger.warning(f"⚠️ تنبيه فهارس الأداء: {err}")

    def create_license_table(self):
        try:
            assert self.cursor is not None and self.conn is not None
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_license (
                id INT PRIMARY KEY AUTO_INCREMENT,
                hardware_id VARCHAR(100) NOT NULL UNIQUE,
                activation_key VARCHAR(100) NOT NULL,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATE NULL,
                status VARCHAR(20) DEFAULT 'active'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            self.cursor.execute("SELECT id FROM roles WHERE id = 99")
            if not self.cursor.fetchone():
                self.cursor.execute("INSERT INTO roles (id, role_name) VALUES (99, 'Developer')")
            self.conn.commit()
        except Exception as err:
            logger.error(f"License table error: {err}")

    def check_system_license(self, hardware_id):
        try:
            query = "SELECT activation_key FROM system_license WHERE hardware_id = %s AND status = 'active'"
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
                query = "INSERT INTO system_license (hardware_id, activation_key) VALUES (%s, %s)"
                self.cursor.execute(query, (hardware_id, key.strip().upper()))
                self.conn.commit()
                return True
            except Exception:
                self.conn.rollback()
                return False
        return False

    def create_expenses_table(self):
        try:
            self.cursor.execute("""
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
            """)
            self.conn.commit()
        except Exception as err:
            logger.error(f"Expenses table error: {err}")

    def create_settings_table(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(50) PRIMARY KEY,
                setting_value TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            defaults = {
                'store_name': 'نظام POS المتكامل',
                'store_address': 'عنوان المحل غير محدد',
                'store_phone': '0123456789',
                'receipt_footer': 'شكراً لزيارتكم',
                'backup_path': 'backups'
            }
            for key, val in defaults.items():
                self.cursor.execute("INSERT IGNORE INTO system_settings (setting_key, setting_value) VALUES (%s, %s)", (key, val))
            self.conn.commit()
        except Exception as err:
            logger.error(f"Settings table error: {err}")

    def get_settings(self):
        try:
            self.cursor.execute("SELECT setting_key, setting_value FROM system_settings")
            results = self.cursor.fetchall()
            return {row['setting_key']: row['setting_value'] for row in results}
        except Exception:
            return {}

    def update_settings(self, settings):
        try:
            for key, val in settings.items():
                self.cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (key, str(val)))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def backup_database(self, custom_dir=None):
        """إجراء نسخة احتياطية من قاعدة البيانات مع معالجة ذكية للمسار"""
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
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"pos_backup_{timestamp}.sql"
        filepath = os.path.join(backup_dir, filename)
        mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
        try:
            command = [mysqldump_path, f"--host={self.host}", f"--user={self.user}", f"--password={self.password}", self.database, f"--result-file={filepath}"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            return (True, filepath) if process.returncode == 0 else (False, error.decode('utf-8', errors='ignore'))
        except Exception as e:
            return (False, str(e))

    def load_config(self):
        """تحميل إعدادات قاعدة البيانات - السحابية من .env والمحلية من config.json"""
        try:
            self._load_env_file()
            
            # الإعدادات المحمية (Hardcoded but Obfuscated)
            protected_cloud = {
                'host': self._deobfuscate('Ny4nOiQgP3VuHFVHGzMqPSshICpobhxAQFk0YTIoIG8yLDtQU15ZJSt9PDws'),
                'user': self._deobfuscate('YwsUJxk2PzAcUGBwRxN7fS08LjI='),
                'password': self._deobfuscate('GyhjEgt2PzAafmNTdx8eIg=='),
                'database': self._deobfuscate('JCogKw=='),
                'port': 4000,
                'ssl_mode': 'VERIFY_IDENTITY'
            }
            
            protected_local = {
                'host': self._deobfuscate('PCAwPj8pKTYr'),
                'user': self._deobfuscate('IiA8Kw=='),
                'password': self._deobfuscate('YX1g'),
                'database': self._deobfuscate('Izs8PDgy'),
                'port': 3306,
                'ssl_mode': 'DISABLED'
            }

            # 1. جلب الإعدادات السحابية (من المتغيرات البيئية أو المحمية)
            env_cloud = self._load_config_values_from_env()
            # نتجاهل القيم إذا كانت "HIDDEN" أو فارغة
            if env_cloud and all(v != "HIDDEN" for v in env_cloud.values()):
                self.cloud_config = env_cloud
            else:
                self.cloud_config = protected_cloud
            
            # 2. جلب الإعدادات المحلية (من ملف config.json أو المحمية)
            file_local = self._load_config_values_from_file()
            if file_local and all(v != "HIDDEN" for v in file_local.values()):
                self.local_config = file_local
            else:
                self.local_config = protected_local
            
            # التعيين الأولي
            if self.cloud_config:
                self._apply_config(self.cloud_config)
                logger.info("تم تحميل إعدادات السحابة (محمية)")
            elif self.local_config:
                self._apply_config(self.local_config)
                logger.info("تم تحميل إعدادات الاتصال المحلي (محمية)")

        except Exception as e:
            logger.error(f'Failed to load DB configuration: {e}', exc_info=True)

    def _obfuscate(self, text: str, key: str = "POS_SAFE_2026") -> str:
        """تحويل النص إلى صيغة غير مفهومة"""
        if not text: return ""
        import base64
        result = []
        for i in range(len(text)):
            char = text[i]
            key_char = key[i % len(key)]
            result.append(chr(ord(char) ^ ord(key_char)))
        return base64.b64encode("".join(result).encode('utf-8')).decode('utf-8')

    def _deobfuscate(self, token: str, key: str = "POS_SAFE_2026") -> str:
        """استعادة النص الأصلي من الرمز المشفر"""
        if not token: return ""
        import base64
        try:
            decoded = base64.b64decode(token.encode('utf-8')).decode('utf-8')
            result = []
            for i in range(len(decoded)):
                char = decoded[i]
                key_char = key[i % len(key)]
                result.append(chr(ord(char) ^ ord(key_char)))
            return "".join(result)
        except Exception:
            return token

    def _get_valid_user_id(self, user_id: int) -> int:
        """التحقق من وجود المعرف في جدول المستخدمين لتجنب أخطاء Foreign Key (خاصة عند الانتقال بين السحابي والمحلي)"""
        if not user_id:
            user_id = 0
        try:
            self.cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if self.cursor.fetchone():
                return user_id
            
            # إذا لم يوجد، نأخذ أول مستخدم متاح كبديل
            self.cursor.execute("SELECT id FROM users LIMIT 1")
            res = self.cursor.fetchone()
            if res:
                return res['id']
            return user_id
        except Exception:
            return user_id

    def _queue_sync(self, table_name: str, record_id: any, action: str, data: dict):
        """إضافة عملية إلى طابور المزامنة في قاعدة البيانات المحلية"""
        if self.host != 'localhost' and self.host != '127.0.0.1':
            return # إذا كنا متصلين بالسحاب مباشرة (حالة نادرة الآن)، لا نحتاج للطابور
            
        try:
            query = """
            INSERT INTO sync_queue (table_name, record_id, action_type, data_json)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (
                table_name, 
                str(record_id), 
                action, 
                json.dumps(data, ensure_ascii=False, default=str)
            ))
            self.conn.commit()
            logger.debug(f"Queued sync for {table_name} ID {record_id}")
        except Exception as e:
            logger.error(f"Failed to queue sync: {e}")

    def _load_config_values_from_file(self) -> Dict:
        """جلب الإعدادات من ملف config.json كـ dictionary"""
        try:
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))

            config_path = os.path.join(current_dir, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    db_config = config.get('database', {})
                    return {
                        'host': db_config.get('host', 'localhost'),
                        'user': db_config.get('user', 'root'),
                        'password': db_config.get('password', ''),
                        'database': db_config.get('database', 'stocks'),
                        'port': int(db_config.get('port', 3306)),
                        'ssl_mode': str(db_config.get('ssl_mode', 'DISABLED')).upper(),
                        'ssl_ca': db_config.get('ssl_ca', '')
                    }
        except Exception as e:
            logger.debug(f"Note: Could not load config.json: {e}")
        return {}

    def _load_config_values_from_env(self) -> Dict:
        """جلب الإعدادات من المتغيرات البيئية كـ dictionary"""
        host = os.getenv('POS_DB_HOST') or os.getenv('DB_HOST')
        user = os.getenv('POS_DB_USER') or os.getenv('DB_USER')
        password = os.getenv('POS_DB_PASSWORD') or os.getenv('DB_PASSWORD')
        database = os.getenv('POS_DB_NAME') or os.getenv('DB_NAME')
        
        if host and user and database:
            port_raw = os.getenv('POS_DB_PORT') or os.getenv('DB_PORT') or '3306'
            ssl_mode = (os.getenv('POS_DB_SSL_MODE') or os.getenv('DB_SSL_MODE') or 'DISABLED').upper()
            ssl_ca = os.getenv('POS_DB_SSL_CA') or os.getenv('DB_SSL_CA') or ''
            
            # Safe defaults for TiDB Cloud
            if 'tidbcloud.com' in host and not os.getenv('POS_DB_SSL_MODE'):
                ssl_mode = 'VERIFY_IDENTITY'
            
            return {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'port': int(port_raw),
                'ssl_mode': ssl_mode,
                'ssl_ca': ssl_ca
            }
        return {}

    def _apply_config(self, config: Dict):
        """تطبيق قاموس الإعدادات على كائن الـ Manager"""
        self.host = config.get('host')
        self.user = config.get('user')
        self.password = config.get('password')
        self.database = config.get('database')
        self.port = config.get('port', 3306)
        self.ssl_mode = config.get('ssl_mode', 'DISABLED')
        self.ssl_ca = config.get('ssl_ca', '')

    def _load_env_file(self) -> None:
        """Load .env values to os.environ without overriding existing environment variables."""
        candidate_dirs = []
        if getattr(sys, 'frozen', False):
            candidate_dirs.append(os.path.dirname(sys.executable))
        else:
            candidate_dirs.append(os.path.dirname(os.path.abspath(__file__)))
        candidate_dirs.append(os.getcwd())

        seen = set()
        for base_dir in candidate_dirs:
            if base_dir in seen:
                continue
            seen.add(base_dir)

            env_path = os.path.join(base_dir, '.env')
            if not os.path.exists(env_path):
                continue

            try:
                with open(env_path, 'r', encoding='utf-8') as env_file:
                    for raw_line in env_file:
                        line = raw_line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue

                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if (
                            len(value) >= 2
                            and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"))
                        ):
                            value = value[1:-1]

                        if key and key not in os.environ:
                            os.environ[key] = value

                logger.info(f'Loaded environment from: {env_path}')
                return
            except (OSError, UnicodeDecodeError, ValueError) as e:
                logger.error(f'Failed to read .env at {env_path}: {e}', exc_info=True)

    def _load_config_from_env(self) -> bool:
        """Populate DB config from environment variables."""
        host = os.getenv('POS_DB_HOST') or os.getenv('DB_HOST')
        user = os.getenv('POS_DB_USER') or os.getenv('DB_USER')
        password = os.getenv('POS_DB_PASSWORD') or os.getenv('DB_PASSWORD')
        database = os.getenv('POS_DB_NAME') or os.getenv('DB_NAME')
        port_raw = os.getenv('POS_DB_PORT') or os.getenv('DB_PORT') or '3306'
        ssl_mode = (os.getenv('POS_DB_SSL_MODE') or os.getenv('DB_SSL_MODE') or 'DISABLED').upper()
        ssl_ca = os.getenv('POS_DB_SSL_CA') or os.getenv('DB_SSL_CA') or ''

        # Safe defaults for TiDB Cloud when SSL vars are not explicitly set.
        if host and 'tidbcloud.com' in host and not os.getenv('POS_DB_SSL_MODE'):
            ssl_mode = 'VERIFY_IDENTITY'
            if not ssl_ca:
                certifi_bundle = os.path.join(
                    os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)),
                    '.venv', 'Lib', 'site-packages', 'pip', '_vendor', 'certifi', 'cacert.pem'
                )
                if os.path.exists(certifi_bundle):
                    ssl_ca = certifi_bundle

        if host and user and database:
            self.host = host
            self.user = user
            self.password = password
            self.database = database
            try:
                self.port = int(port_raw)
            except (ValueError, TypeError):
                self.port = 3306
            self.ssl_mode = ssl_mode
            self.ssl_ca = ssl_ca
            logger.info('Loaded database config from environment variables.')
            return True

        return False

    def _get_env_path(self) -> str:
        """Resolve writable .env path for runtime configuration updates."""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, '.env')

    def _write_env_values(self, values: Dict[str, str]) -> None:
        """Update/create key-value pairs inside .env while preserving other lines."""
        env_path = self._get_env_path()
        existing_lines: List[str] = []

        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                existing_lines = f.read().splitlines()

        keys_lower = {k.lower(): k for k in values.keys()}
        updated: List[str] = []
        seen: set[str] = set()

        for raw_line in existing_lines:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in raw_line:
                updated.append(raw_line)
                continue

            key = raw_line.split('=', 1)[0].strip()
            key_l = key.lower()
            if key_l in keys_lower:
                new_key = keys_lower[key_l]
                updated.append(f"{new_key}={values[new_key]}")
                seen.add(new_key)
            else:
                updated.append(raw_line)

        for key, value in values.items():
            if key not in seen:
                updated.append(f"{key}={value}")

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated).rstrip() + '\n')

    def get_connection_profile(self) -> Dict[str, str]:
        """Return current active DB connection settings."""
        return {
            'host': self.host or '',
            'user': self.user or '',
            'password': self.password or '',
            'database': self.database or '',
            'port': str(self.port or 3306),
            'ssl_mode': self.ssl_mode or 'DISABLED',
            'ssl_ca': self.ssl_ca or '',
        }

    def _build_connection_kwargs(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int,
        ssl_mode: str,
        ssl_ca: str,
    ) -> Dict[str, Any]:
        """Build mysql.connector kwargs with optional SSL behavior."""
        kwargs: Dict[str, Any] = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'use_pure': True,
            'autocommit': True,
        }

        timeout_raw = os.getenv('POS_DB_TIMEOUT') or os.getenv('DB_TIMEOUT') or '8'
        try:
            timeout = int(timeout_raw)
        except (TypeError, ValueError):
            timeout = 8
        timeout = max(3, min(timeout, 60))
        kwargs['connection_timeout'] = timeout
        kwargs['read_timeout'] = max(timeout, 12)
        kwargs['write_timeout'] = max(timeout, 12)

        mode = (ssl_mode or 'DISABLED').upper()
        ca_path = (ssl_ca or '').strip()

        if mode == 'DISABLED':
            kwargs['ssl_disabled'] = True
            return kwargs

        kwargs['ssl_disabled'] = False
        if ca_path:
            kwargs['ssl_ca'] = ca_path

        if mode == 'VERIFY_IDENTITY':
            kwargs['ssl_verify_identity'] = True
            kwargs['ssl_verify_cert'] = True
        elif mode == 'VERIFY_CA':
            kwargs['ssl_verify_cert'] = True

        return kwargs

    def test_connection_config(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        ssl_mode: str = 'DISABLED',
        ssl_ca: str = '',
    ) -> Tuple[bool, str]:
        """Test a DB configuration without changing current app connection."""
        try:
            kwargs = self._build_connection_kwargs(host, user, password, database, port, ssl_mode, ssl_ca)
            test_conn = mysql.connector.connect(**kwargs)
            test_conn.close()
            return True, "?? ?????? ??????? ?????"
        except mysql.connector.Error as err:
            return False, f"??? ???????: {err}"

    def save_connection_config(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        ssl_mode: str = 'DISABLED',
        ssl_ca: str = '',
        reconnect: bool = True
    ) -> Tuple[bool, str]:
        """Persist DB connection config to .env and optionally reconnect."""
        host = (host or '').strip()
        user = (user or '').strip()
        database = (database or '').strip()
        password = password or ''
        try:
            port = int(port)
        except (TypeError, ValueError):
            return False, "???? ?????? ??? ?????"

        ssl_mode = (ssl_mode or 'DISABLED').upper()
        ssl_ca = (ssl_ca or '').strip()

        if not host or not user or not database:
            return False, "??? ????? ?????? ???? ???????? ???? ????? ????????"

        ok, message = self.test_connection_config(
            host, user, password, database, port=port, ssl_mode=ssl_mode, ssl_ca=ssl_ca
        )
        if not ok:
            return False, message

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.ssl_mode = ssl_mode
        self.ssl_ca = ssl_ca

        os.environ['POS_DB_HOST'] = host
        os.environ['POS_DB_USER'] = user
        os.environ['POS_DB_PASSWORD'] = password
        os.environ['POS_DB_NAME'] = database
        os.environ['POS_DB_PORT'] = str(port)
        os.environ['POS_DB_SSL_MODE'] = ssl_mode
        os.environ['POS_DB_SSL_CA'] = ssl_ca

        try:
            self._write_env_values({
                'POS_DB_HOST': host,
                'POS_DB_USER': user,
                'POS_DB_PASSWORD': password,
                'POS_DB_NAME': database,
                'POS_DB_PORT': str(port),
                'POS_DB_SSL_MODE': ssl_mode,
                'POS_DB_SSL_CA': ssl_ca,
            })
        except OSError as err:
            return False, f"?? ??????? ??? ??? ??? .env: {err}"

        if reconnect:
            try:
                self.close()
            except (AttributeError, RuntimeError):
                pass
            self.conn = None
            self.cursor = None
            if not self.connect():
                return False, "?? ??? ????????? ??? ??? ????? ???????? ??? ????? ????????"

        return True, "?? ??? ??????? ??????? ???????? ?????"

    def change_server_user_password(self, new_password: str) -> Tuple[bool, str]:
        """Change current DB user password on DB server and sync .env."""
        if not new_password:
            return False, "كلمة المرور الجديدة مطلوبة"
        if not self.cursor or not self.conn:
            return False, "غير متصل بقاعدة البيانات"

        escaped_password = new_password.replace("\\", "\\\\").replace("'", "''")
        escaped_user = (self.user or '').replace("\\", "\\\\").replace("'", "''")

        statements = []
        if escaped_user:
            statements.append(f"ALTER USER '{escaped_user}'@'%' IDENTIFIED BY '{escaped_password}'")
            statements.append(f"ALTER USER '{escaped_user}'@'localhost' IDENTIFIED BY '{escaped_password}'")
        statements.append(f"ALTER USER USER() IDENTIFIED BY '{escaped_password}'")

        last_error: Optional[Exception] = None
        for stmt in statements:
            try:
                self.cursor.execute(stmt)
                self.conn.commit()
                self.password = new_password
                os.environ['POS_DB_PASSWORD'] = new_password
                self._write_env_values({'POS_DB_PASSWORD': new_password})
                return True, "تم تغيير كلمة مرور مستخدم قاعدة البيانات بنجاح"
            except mysql.connector.Error as err:
                last_error = err

        return False, f"فشل تغيير كلمة المرور: {last_error}"

    def connect(self):
        """الاتصال بقاعدة البيانات - الأولوية للمحلي (Local-First)"""
        # 1. محاولة الاتصال بالمحلي أولاً دائماً كما طلب المستخدم
        if hasattr(self, 'local_config') and self.local_config:
            logger.info("Connecting to Local database first...")
            self._apply_config(self.local_config)
            if self._do_connect():
                logger.info("✅ Connected to Local database")
                return True

        # 2. إذا فشل المحلي، نحاول السحاب (كاحتياطي)
        logger.warning("⚠️ Local connection failed, trying Cloud...")
        self._load_config_values_from_env()
        if self._do_connect():
            return True
                
        return False

    def _do_connect(self):
        """القيام بعملية الاتصال الفعلية"""
        try:
            kwargs = self._build_connection_kwargs(
                host=self.host or '',
                user=self.user or '',
                password=self.password or '',
                database=self.database or '',
                port=self.port or 3306,
                ssl_mode=self.ssl_mode or 'DISABLED',
                ssl_ca=self.ssl_ca or '',
            )
            self.conn = mysql.connector.connect(**kwargs)
            self.cursor = self.conn.cursor(dictionary=True, buffered=True)
            logger.info(f"✅ تم الاتصال بـ ({self.host}) بنجاح")
            return True
        except mysql.connector.Error as err:
            logger.debug(f"Connection attempt failed for {self.host}: {err}")
            return False

    def close(self):
        """إغلاق الاتصال"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("تم إغلاق اتصال قاعدة البيانات")
    
    def get_all_stores(self, include_inactive: bool = False) -> List[Dict]:
        """الحصول على قائمة بجميع الفروع والمخازن (النشطة افتراضياً)"""
        try:
            query = "SELECT * FROM stores"
            if not include_inactive:
                query += " WHERE is_active = TRUE"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب الفروع: {err}", exc_info=True)
            return []
    
    # ==================== تسجيل الدخول ====================
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """التحقق من بيانات المستخدم"""
        try:
            query = """
            SELECT u.id, u.name, u.email, u.password, u.role_id, u.store_id, u.is_active,
                   r.role_name, s.store_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN stores s ON u.store_id = s.id
            WHERE u.email = %s AND u.is_active = TRUE
            """
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
                # تحديث آخر دخول
                update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
                self.cursor.execute(update_query, (user['id'],))
                self.conn.commit()
                
                # إزالة كلمة المرور من النتيجة
                user.pop('password')
                return user
            
            return None
        except mysql.connector.Error as err:
            logger.error(f"خطأ في التحقق من بيانات المستخدم: {err}", exc_info=True)
            return None
    
    # ==================== إدارة المستخدمين ====================
    
    def create_user(self, name: str, email: str, password: str, phone: str,
                   role_id: int, store_id: int, created_by: int) -> bool:
        """إنشاء مستخدم جديد"""
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            query = """
            INSERT INTO users (name, email, password, phone, role_id, store_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (name, email, hashed_password, phone, role_id, store_id, created_by))
            self.conn.commit()
            logger.info(f"تم إنشاء المستخدم: {name}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إنشاء المستخدم {name}: {err}", exc_info=True)
            self.conn.rollback()
            return False

    def update_user(self, user_id, name, email, phone, role_id, store_id, password=None):
        """تحديث بيانات المستخدم"""
        try:
            cursor = self.conn.cursor()
            if password:
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
                query = """
                    UPDATE users 
                    SET name=%s, email=%s, password=%s, phone=%s, role_id=%s, store_id=%s
                    WHERE id=%s
                """
                cursor.execute(query, (name, email, hashed_pw, phone, role_id, store_id, user_id))
            else:
                query = """
                    UPDATE users 
                    SET name=%s, email=%s, phone=%s, role_id=%s, store_id=%s
                    WHERE id=%s
                """
                cursor.execute(query, (name, email, phone, role_id, store_id, user_id))
            
            self.conn.commit()
            logger.info(f"تم تحديث المستخدم: {name}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث المستخدم {name}: {err}", exc_info=True)
            self.conn.rollback()
            return False

    def delete_user(self, user_id: int) -> bool:
        """تعطيل المستخدم (Soft Delete)"""
        try:
            query = "UPDATE users SET is_active = FALSE WHERE id = %s"
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
            logger.info(f"تم تعطيل المستخدم رقم: {user_id}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في حذف المستخدم {user_id}: {err}", exc_info=True)
            self.conn.rollback()
            return False
    
    def get_all_users(self, store_id: Optional[int] = None) -> List[Dict]:
        """الحصول على قائمة المستخدمين"""
        try:
            query = """
            SELECT u.id, u.name, u.email, u.phone, u.is_active, u.role_id, u.store_id,
                   r.role_name, s.store_name, u.created_at
            FROM users u
            JOIN roles r ON u.role_id = r.id
            LEFT JOIN stores s ON u.store_id = s.id
            WHERE u.is_active = TRUE
            """
            
            if store_id:
                query += " AND u.store_id = %s"
                self.cursor.execute(query, (store_id,))
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب المستخدمين: {err}", exc_info=True)
            return []
    
    # ==================== إدارة المنتجات ====================
    
    def add_product(self, product_code: str, product_name: str, category_id: int,
                   buy_price: float, sell_price: float, supplier_id: int = None,
                   unit: str = 'piece', barcode: str = None, description: str = None,
                   initial_stock: int = 0, store_id: int = None) -> Optional[int]:
        """إضافة منتج جديد"""
        try:
            query = """
            INSERT INTO products (product_code, product_name, category_id, buy_price, 
                                 sell_price, supplier_id, unit, barcode, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (product_code, product_name, category_id, buy_price,
                                       sell_price, supplier_id, unit, barcode, description))
            product_id = self.cursor.lastrowid
            
            # ربط المنتج بجميع المخزون لـ {len(stores)} فروع: {product_name}")
            self.cursor.execute("SELECT id FROM stores WHERE is_active = TRUE")
            stores = self.cursor.fetchall()
            for store in stores:
                # إذا تم تحديد مخزن معين وكمية أولية، نضعها له، وإلا صفر
                qty = initial_stock if store_id == store['id'] else 0
                
                self.cursor.execute("""
                    INSERT IGNORE INTO product_inventory (product_id, store_id, quantity_in_stock)
                    VALUES (%s, %s, %s)
                """, (product_id, store['id'], qty))
            
            self.conn.commit()
            logger.info(f"تم إضافة المنتج وتجهيز المخزون لـ {len(stores)} فروع: {product_name}")
            return product_id
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إضافة المنتج {product_name}: {err}", exc_info=True)
            self.conn.rollback()
            return None
    
    def get_product_cross_branch_stock(self, search_term: str) -> Dict:
        """البحث عن منتج وجلب كمياته في كافة الفروع"""
        try:
            # 1. البحث عن المنتج أولاً (بكود المنتج أو الباركود)
            query_product = """
            SELECT p.id, p.product_code, p.product_name, p.sell_price, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (p.product_code = %s OR p.barcode = %s) AND p.is_active = TRUE
            """
            self.cursor.execute(query_product, (search_term, search_term))
            product = self.cursor.fetchone()
            
            if not product:
                return {}
            
            # 2. جلب الكميات من كافة الفروع
            query_stock = """
            SELECT s.id as store_id, s.store_name, COALESCE(pi.quantity_in_stock, 0) as quantity
            FROM stores s
            LEFT JOIN product_inventory pi ON s.id = pi.store_id AND pi.product_id = %s
            WHERE s.is_active = TRUE
            """
            self.cursor.execute(query_stock, (product['id'],))
            stocks = self.cursor.fetchall()
            
            return {
                'product': product,
                'stocks': stocks
            }
        except mysql.connector.Error as err:
            logger.error(f"خطأ في استعلام فروع المنتج: {err}", exc_info=True)
            return {}
    
    def get_product_by_code(self, product_code: str) -> Optional[Dict]:
        """البحث عن منتج برقمه (للتوافق مع الكود القديم)"""
        result = self.get_product_cross_branch_stock(product_code)
        return result.get('product')
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """البحث عن منتج برقم الباركود"""
        try:
            query = """
            SELECT p.*, c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.barcode = %s AND p.is_active = TRUE
            """
            
            self.cursor.execute(query, (barcode,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في البحث عن المنتج برقم الباركود: {err}", exc_info=True)
            return None
    
    def get_all_products(self, category_id: Optional[int] = None) -> List[Dict]:
        """الحصول على قائمة المنتجات"""
        try:
            query = """
            SELECT p.*, c.category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = TRUE
            """
            
            if category_id:
                query += " AND p.category_id = %s"
                self.cursor.execute(query, (category_id,))
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب المنتجات: {err}", exc_info=True)
            return []
    
    def update_product_price(self, product_id: int, new_sell_price: float = None,
                            new_buy_price: float = None, changed_by: int = None,
                            notes: str = None) -> bool:
        """تحديث سعر المنتج وحفظ السجل"""
        try:
            # الحصول على الأسعار القديمة
            query = "SELECT buy_price, sell_price FROM products WHERE id = %s"
            self.cursor.execute(query, (product_id,))
            old_prices = self.cursor.fetchone()
            
            if not old_prices:
                return False
            
            final_sell_price = new_sell_price if new_sell_price is not None else float(old_prices['sell_price'])

            # تحديث السعر
            update_query = "UPDATE products SET sell_price = %s"
            params = [final_sell_price]
            
            if new_buy_price is not None:
                update_query += ", buy_price = %s"
                params.append(new_buy_price)
            
            update_query += " WHERE id = %s"
            params.append(product_id)
            
            self.cursor.execute(update_query, params)
            
            # حفظ في سجل التاريخ
            history_query = """
            INSERT INTO price_history (product_id, old_buy_price, new_buy_price,
                                      old_sell_price, new_sell_price, changed_by, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(history_query, (
                product_id,
                old_prices['buy_price'],
                new_buy_price if new_buy_price is not None else old_prices['buy_price'],
                old_prices['sell_price'],
                final_sell_price,
                changed_by,
                notes
            ))
            
            self.conn.commit()
            logger.info(f"تم تحديث سعر المنتج رقم {product_id}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث سعر المنتج {product_id}: {err}", exc_info=True)
            self.conn.rollback()
    
    def fix_zero_costs(self, margin_percent: float = 25.0) -> int:
        """
        Update buy_price for products where it is 0 or NULL, 
        based on sell_price and a default margin.
        New Cost = Sell Price * (1 - margin/100)
        """
        try:
            # Calculate cost factor (e.g. 25% margin -> 0.75 cost factor)
            factor = 1.0 - (margin_percent / 100.0)
            
            query = """
                UPDATE products 
                SET buy_price = sell_price * %s 
                WHERE (buy_price IS NULL OR buy_price = 0) 
                  AND sell_price > 0
            """
            self.cursor.execute(query, (factor,))
            self.conn.commit()
            
            count = self.cursor.rowcount
            logger.info(f"تم تحديث تكلفة {count} منتج بنسبة ربح افتراضية {margin_percent}%")
            return count
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث التكاليف: {err}", exc_info=True)
            return 0
    
    def get_inventory(self, store_id: int, product_id: Optional[int] = None) -> List[Dict]:
        """الحصول على المخزون"""
        try:
            query = """
            SELECT pi.*, p.product_code, p.product_name, p.sell_price,
                   (pi.quantity_in_stock * p.sell_price) AS inventory_value,
                   CASE 
                       WHEN pi.quantity_in_stock <= pi.minimum_quantity THEN 'Low Stock'
                       ELSE 'OK'
                   END AS stock_status
            FROM product_inventory pi
            JOIN products p ON pi.product_id = p.id
            WHERE pi.store_id = %s
            """
            
            params = [store_id]
            
            if product_id:
                query += " AND pi.product_id = %s"
                params.append(product_id)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب المخزون: {err}", exc_info=True)
            return []
    
    def update_inventory(self, product_id: int, store_id: int, quantity: int,
                        operation: str = 'set') -> bool:
        """تحديث المخزون مع معالجة احتمالية عدم وجود سجل مسبق"""
        try:
            if operation == 'add':
                query = """
                    INSERT INTO product_inventory (product_id, store_id, quantity_in_stock)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity_in_stock = quantity_in_stock + %s
                """
                self.cursor.execute(query, (product_id, store_id, quantity, quantity))
            elif operation == 'subtract':
                query = """
                    INSERT INTO product_inventory (product_id, store_id, quantity_in_stock)
                    VALUES (%s, %s, -%s)
                    ON DUPLICATE KEY UPDATE quantity_in_stock = quantity_in_stock - %s
                """
                self.cursor.execute(query, (product_id, store_id, quantity, quantity))
            else: # set
                query = """
                    INSERT INTO product_inventory (product_id, store_id, quantity_in_stock)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity_in_stock = %s
                """
                self.cursor.execute(query, (product_id, store_id, quantity, quantity))
            
            self.conn.commit()
            logger.info(f"تم تحديث المخزون: {operation} {quantity} للمنتج {product_id} في المتجر {store_id}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث المخزون للمنتج {product_id}: {err}", exc_info=True)
            self.conn.rollback()
            return False
    
    def clear_transactional_data(self) -> bool:
        """مسح كافة البيانات المعاملاتية مع الاحتفاظ بحساب المطور فقط والأجهزة"""
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tables_to_clear = [
                "audit_logs",
                "login_attempts",
                "drawer_closing_details",
                "drawer_logs",
                "transfer_items",
                "warehouse_transfers",
                "temporary_invoice_items",
                "temporary_invoices",
                "order_items",
                "orders",
                "invoice_items",
                "invoices",
                "purchase_items",
                "purchase_invoices",
                "price_history",
                "product_inventory",
                "products",
                "categories",
                "suppliers",
                "customers",
                "financial_ledger",
                "treasury",
                "sales_returns",
                "return_items",
                "expenses"
            ]
            
            for table in tables_to_clear:
                self.cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if self.cursor.fetchone():
                    self.cursor.execute(f"TRUNCATE TABLE {table}")
                    logger.info(f"تم مسح بيانات الجدول: {table}")
            
            # 2. تصفير أرصدة الموردين والعملاء (جداول محذوفة البيانات لكن للتأكيد)
            # بما أننا عملنا Truncate للجداول أعلاه، فهي فارغة بالفعل.
            
            # 3. حذف المستخدمين ما عدا المطور
            self.cursor.execute("DELETE FROM users WHERE email != 'dev@admin.com'")
            logger.info("تم حذف كافة المستخدمين مع الاحتفاظ بحساب المطور")
            
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.conn.commit()
            logger.info("تم تصفير كافة البيانات بنجاح تام")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ أثناء مسح البيانات: {err}", exc_info=True)
            self.conn.rollback()
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            return False
    
    # ==================== الفلاتر المتقدمة ====================
    
    def get_advanced_product_search(self, store_id: int, supplier_id: int = None, 
                                  invoice_date: str = None) -> List[Dict]:
        """
        بحث متقدم عن المنتجات مع تفاصيل الشراء والبيع حسب المورد والتاريخ.
        يعيد قائمة بالمنتجات التي قل مخزونها عن الحد الأدنى"""
        try:
            # استعلام محسّن: استخدام GROUP BY و LEFT JOIN بدل حلقة (إزالة مشكلة N+1)
            query = """
                SELECT 
                    p.id, p.product_name, p.product_code, p.buy_price, p.sell_price, 
                    p.last_supplier, p.last_purchase_date,
                    COALESCE(pi_inv.quantity_in_stock, 0) as quantity_in_stock,
                    pur_item.quantity as purchase_qty,
                    pur_inv.invoice_date,
                    sup.name as supplier_name,
                    pur_inv.id as invoice_id,
                    COALESCE(SUM(ii.quantity), 0) as sold_qty_since_purchase
                FROM products p
                LEFT JOIN product_inventory pi_inv ON p.id = pi_inv.product_id AND pi_inv.store_id = %s
                JOIN purchase_items pur_item ON p.id = pur_item.product_id
                JOIN purchase_invoices pur_inv ON pur_item.invoice_id = pur_inv.id
                JOIN suppliers sup ON pur_inv.supplier_id = sup.id
                LEFT JOIN invoice_items ii ON p.id = ii.product_id
                LEFT JOIN invoices i ON ii.invoice_id = i.id AND i.invoice_date >= pur_inv.invoice_date AND i.status = 'Completed'
                WHERE 1=1
            """
            params = [store_id]
            
            if supplier_id:
                query += " AND pur_inv.supplier_id = %s"
                params.append(supplier_id)
            
            if invoice_date:
                query += " AND DATE(pur_inv.invoice_date) = %s"
                params.append(invoice_date)
            
            # Group by and order
            query += " GROUP BY p.id, pur_inv.id ORDER BY pur_inv.invoice_date DESC, p.product_name"
            
            self.cursor.execute(query, params)
            products = self.cursor.fetchall()
            
            # تحويل sold_qty إلى float
            for prod in products:
                prod['sold_qty_since_purchase'] = float(prod['sold_qty_since_purchase'] or 0)
                
            logger.info(f"تم البحث المتقدم عن {len(products)} منتج")
            return products

        except mysql.connector.Error as err:
            logger.error(f"خطأ في البحث المتقدم عن المنتجات: {err}", exc_info=True)
            return []

    # ==================== الفواتير ====================
    
    def get_low_stock_alerts(self, store_id: Optional[int] = None) -> List[Dict]:
        """الحصول على قائمة الأصناف التي قل مخزونها عن الحد الأدنى"""
        try:
            query = """
                SELECT 
                    p.id, p.product_code, p.product_name, p.sell_price,
                    pi.quantity_in_stock, pi.minimum_quantity, s.store_name
                FROM product_inventory pi
                JOIN products p ON pi.product_id = p.id
                JOIN stores s ON pi.store_id = s.id
                WHERE pi.quantity_in_stock <= pi.minimum_quantity
                AND p.is_active = TRUE
            """
            params = []
            if store_id:
                query += " AND pi.store_id = %s"
                params.append(store_id)
            
            self.cursor.execute(query, params)
            columns = [col[0] for col in self.cursor.description]
            results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return results
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب نبهات المخزون المنخفض: {err}", exc_info=True)
            return []

    def update_product_min_stock(self, product_id: int, store_id: int, min_stock: int) -> bool:
        """تحديث الحد الأدنى للمخزون لصنف معين في مخزن معين"""
        try:
            query = """
                UPDATE product_inventory 
                SET minimum_quantity = %s 
                WHERE product_id = %s AND store_id = %s
            """
            self.cursor.execute(query, (min_stock, product_id, store_id))
            self.conn.commit()
            logger.info(f"تم تحديث الحد الأدنى للمخزون للموردين معين الاحتفاظ بحساب المطور")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث الحد الأدنى للمخزون: {err}", exc_info=True)
            self.conn.rollback()
            return False

    def get_next_invoice_number(self) -> str:
        """الحصول على الرقم التسلسلي التالي للفواتير"""
        try:
            query = "SELECT MAX(id) as max_id FROM invoices"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            next_id = 1
            if result and result['max_id']:
                next_id = int(result['max_id']) + 1
            logger.debug(f"رقم الفاتورة التالي: {next_id}")
            return str(next_id)
        except (mysql.connector.Error, ValueError, TypeError, KeyError) as e:
            logger.error(f"خطأ في الحصول على رقم الفاتورة التالي: {e}", exc_info=True)
            return str(int(datetime.now().timestamp()))

    def get_next_order_number(self) -> str:
        """الحصول على الرقم التسلسلي التالي للطلبات"""
        try:
            query = "SELECT MAX(id) as max_id FROM orders"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            next_id = 1
            if result and result['max_id']:
                next_id = int(result['max_id']) + 1
            logger.debug(f"رقم الطلب التالي: {next_id}")
            return str(next_id)
        except (mysql.connector.Error, ValueError, TypeError, KeyError) as e:
            logger.error(f"خطأ في الحصول على رقم الفاتورة التالي: {e}", exc_info=True)
            return str(int(datetime.now().timestamp()))

    def create_invoice(self, store_id: int, cashier_id: int, customer_name: str = None,
                      customer_phone: str = None, customer_address: str = None, 
                      drawer_id: int = None, payment_method: str = 'Cash',
                      cash_amount: float = 0, card_amount: float = 0) -> Optional[str]:
        """إنشاء فاتورة جديدة برقم متسلسل"""
        try:
            invoice_number = self.get_next_invoice_number()
            
            # معالجة العميل
            customer_id = self._get_or_create_customer(customer_name, customer_phone, customer_address)
            
            query = """
            INSERT INTO invoices (invoice_number, store_id, cashier_id, customer_id, customer_name,
                                customer_phone, customer_address, drawer_id, payment_method, 
                                cash_amount, card_amount, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
            """
            
            self.cursor.execute(query, (invoice_number, store_id, cashier_id, customer_id,
                                       customer_name, customer_phone, customer_address, 
                                       drawer_id, payment_method, cash_amount, card_amount))
            invoice_id = self.cursor.lastrowid
            
            # 2. Record Cash in Treasury if it's a cash payment
            if cash_amount > 0:
                self.record_treasury_transaction(
                    store_id=store_id,
                    trans_type='In',
                    amount=cash_amount,
                    source='Sale',
                    ref_id=invoice_id,
                    desc=f"مبيعات نقدية: فاتورة رقم {invoice_number}",
                    user_id=cashier_id
                )
                
            self.conn.commit()
            
            # Queue for sync
            self._queue_sync('invoices', invoice_number, 'INSERT', {
                'invoice_number': invoice_number, 'store_id': store_id, 
                'cashier_id': cashier_id, 'customer_id': customer_id,
                'customer_name': customer_name, 'customer_phone': customer_phone,
                'customer_address': customer_address, 'drawer_id': drawer_id,
                'payment_method': payment_method, 'cash_amount': cash_amount,
                'card_amount': card_amount
            })
            
            logger.info(f"تم إنشاء فاتورة: {invoice_number}")
            return invoice_number
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إنشاء الفاتورة: {err}", exc_info=True)
            self.conn.rollback()
            return None
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إنشاء الفاتورة: {err}", exc_info=True)
            return None
    
    def add_invoice_item(self, invoice_number: str, product_id: int,
                        quantity: int, unit_price: float, discount: float = 0) -> bool:
        """إضافة منتج للفاتورة"""
        try:
            # الحصول على معرف الفاتورة
            query = "SELECT id FROM invoices WHERE invoice_number = %s"
            self.cursor.execute(query, (invoice_number,))
            invoice = self.cursor.fetchone()
            
            if not invoice:
                return False
            
            # الحصول على سعر الشراء الحالي للصنف
            self.cursor.execute("SELECT buy_price FROM products WHERE id = %s", (product_id,))
            prod = self.cursor.fetchone()
            buy_price = float(prod['buy_price'] or 0) if prod else 0.0
            
            # إضافة البند
            total_price = (quantity * unit_price) - discount
            
            item_query = """
            INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, buy_price, discount, total_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(item_query, (invoice['id'], product_id, quantity, unit_price, buy_price, discount, total_price))
        
            # Update Invoice Total manually (since trigger is missing/unreliable)
            update_total_query = """
            UPDATE invoices 
            SET total_amount = (SELECT SUM(total_price) FROM invoice_items WHERE invoice_id = %s)
            WHERE id = %s
            """
            self.cursor.execute(update_total_query, (invoice['id'], invoice['id']))
        
            self.conn.commit()
            
            # Queue for sync
            self._queue_sync('invoice_items', f"{invoice_number}_{product_id}", 'INSERT', {
                'invoice_number': invoice_number, 'product_id': product_id,
                'quantity': quantity, 'unit_price': unit_price, 'discount': discount
            })
            
            logger.info(f"تم إضافة منتج إلى الفاتورة: {invoice_number}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إضافة بند الفاتورة: {err}", exc_info=True)
            self.conn.rollback()
            return False
    
    # ==================== المرتجعات ====================
    
    def create_returns_tables(self):
        """إنشاء جداول المرتجعات إن لم تكن موجودة"""
        try:
            if not self.cursor:
                return False

            # 1. جدول المرتجعات
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_returns (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    return_number VARCHAR(50) NOT NULL UNIQUE,
                    invoice_id INT NOT NULL,
                    store_id INT NOT NULL,
                    cashier_id INT NOT NULL,
                    drawer_id INT NULL,
                    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_return_amount DECIMAL(12, 2) NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                    FOREIGN KEY (store_id) REFERENCES stores(id),
                    FOREIGN KEY (cashier_id) REFERENCES users(id),
                    FOREIGN KEY (drawer_id) REFERENCES drawer_logs(id) ON DELETE SET NULL
                )
            """)
            
            # 2. جدول بنود المرتجع
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS return_items (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    return_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    buy_price DECIMAL(10, 2) DEFAULT 0,
                    total_price DECIMAL(12, 2) NOT NULL,
                    FOREIGN KEY (return_id) REFERENCES sales_returns(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Ensure buy_price exists in return_items
            try:
                self.cursor.execute("ALTER TABLE return_items ADD COLUMN buy_price DECIMAL(10, 2) DEFAULT 0")
            except mysql.connector.Error as column_err:
                # العمود موجود بالفعل أو حدث خطأ آخر
                logger.debug(f"العمود buy_price موجود أو حدث خطأ: {column_err}")
            self.conn.commit()
            logger.info("جداول المرتجعات جاهزة")
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إنشاء جداول المرتجعات: {err}", exc_info=True)
            return False

    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """Fetch invoice header by number (supports full number or last few digits)"""
        try:
            # 1. Try exact match first for performance and precision
            query = "SELECT * FROM invoices WHERE invoice_number = %s"
            self.cursor.execute(query, (invoice_number,))
            res = self.cursor.fetchone()
            if res:
                return res
            
            # 2. If no exact match and input looks like a suffix (at least 3 characters)
            if invoice_number and len(invoice_number) >= 3:
                query = """
                    SELECT * FROM invoices 
                    WHERE invoice_number LIKE %s 
                    ORDER BY invoice_date DESC 
                    LIMIT 1
                """
                # This matches anything ending with the provided digits/string
                self.cursor.execute(query, (f"%{invoice_number}",))
                return self.cursor.fetchone()
                
            return None
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب الفاتورة: {err}", exc_info=True)
            return None

    def get_next_return_number(self) -> str:
        """الحصول على الرقم التسلسلي التالي للمرتجعات"""
        try:
            query = "SELECT MAX(id) as max_id FROM sales_returns"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            next_id = 1
            if result and result['max_id']:
                next_id = int(result['max_id']) + 1
            logger.debug(f"رقم المرتجع التالي: {next_id}")
            return str(next_id)
        except (mysql.connector.Error, ValueError, TypeError, KeyError) as e:
            logger.error(f"خطأ في الحصول على رقم المرتجعات التالي: {e}", exc_info=True)
            return str(int(datetime.now().timestamp()))

    def process_return(self, invoice_id: int, items_to_return: List[Dict], reason: str, 
                       cashier_id: int, store_id: int, drawer_id: int = None) -> Optional[str]:
        """Process a sales return transaction with sequential return number"""
        try:
            # 1. Create return number
            return_number = self.get_next_return_number()
            total_amount = sum(item['quantity'] * item['unit_price'] for item in items_to_return)
            
            # 2. Insert into sales_returns
            query = """
                INSERT INTO sales_returns (return_number, invoice_id, store_id, cashier_id, drawer_id, total_return_amount, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (return_number, invoice_id, store_id, cashier_id, drawer_id, total_amount, reason))
            return_id = self.cursor.lastrowid
            
            # 3. Insert items and update inventory
            item_query = """
                INSERT INTO return_items (return_id, product_id, quantity, unit_price, buy_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for item in items_to_return:
                # Get current buy_price (cost at time of return)
                self.cursor.execute("SELECT buy_price FROM products WHERE id = %s", (item['product_id'],))
                prod = self.cursor.fetchone()
                buy_price = float(prod['buy_price'] or 0) if prod else 0.0
                
                subtotal = item['quantity'] * item['unit_price']
                self.cursor.execute(item_query, (return_id, item['product_id'], item['quantity'], item['unit_price'], buy_price, subtotal))
                
                # Update inventory (Return = Add back to stock)
                self.update_inventory(item['product_id'], store_id, item['quantity'], operation='add')
            
            self.conn.commit()
            
            # Record Treasury Out if refund
            self.record_treasury_transaction(
                store_id=store_id,
                trans_type='Out',
                amount=total_amount,
                source='Return',
                ref_id=return_number,
                desc=f"مرتجع مبيعات - رقم {return_number}",
                user_id=cashier_id
            )
            
            return return_number
        except mysql.connector.Error as err:
            logger.error(f"خطأ في معالجة المرتجعات: {err}", exc_info=True)
            self.conn.rollback()
            return None

    def get_returns_history(self, store_id: int = None, limit: int = 50, 
                            start_date: str = None, end_date: str = None, 
                            return_number: str = None) -> List[Dict]:
        """Fetch recent returns history with details and filters"""
        try:
            where_clauses = []
            params = []
            
            if store_id:
                where_clauses.append("sr.store_id = %s")
                params.append(store_id)
            
            if start_date and end_date:
                where_clauses.append("DATE(sr.return_date) BETWEEN %s AND %s")
                params.extend([start_date, end_date])
            
            if return_number:
                where_clauses.append("sr.return_number LIKE %s")
                params.append(f"%{return_number}%")
                
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            params.append(limit)
            
            query = f"""
            SELECT sr.id, sr.return_number, sr.return_date, sr.total_return_amount, sr.reason,
                   i.invoice_number, u.name as cashier_name, s.store_name
            FROM sales_returns sr
            JOIN invoices i ON sr.invoice_id = i.id
            JOIN users u ON sr.cashier_id = u.id
            JOIN stores s ON sr.store_id = s.id
            {where_clause}
            ORDER BY sr.return_date DESC
            LIMIT %s
            """
            self.cursor.execute(query, params)
            returns = self.cursor.fetchall()
            
            # Fetch items for each return to allow re-printing
            for ret in returns:
                item_query = """
                SELECT ri.*, p.product_name 
                FROM return_items ri
                JOIN products p ON ri.product_id = p.id
                WHERE ri.return_id = %s
                """
                self.cursor.execute(item_query, (ret['id'],))
                ret['items'] = self.cursor.fetchall()
                
            return returns
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب سجل المرتجعات: {err}", exc_info=True)
            return []

    def get_completed_invoices(self, store_id: int, search_term: str = None, 
                             start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch completed invoices for history with optional filtering"""
        try:
            query = """
                SELECT i.*, u.name as cashier_name 
                FROM invoices i
                JOIN users u ON i.cashier_id = u.id
                WHERE i.store_id = %s AND i.status = 'Completed'
            """
            params = [store_id]
            
            if search_term:
                query += " AND (i.invoice_number LIKE %s OR i.customer_name LIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])
            
            if start_date:
                query += " AND DATE(i.invoice_date) >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(i.invoice_date) <= %s"
                params.append(end_date)
            
            query += " ORDER BY i.invoice_date DESC LIMIT 500"
            
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب الفواتير المكتملة: {err}", exc_info=True)
            return []

    def get_invoice_items_details(self, invoice_id: int) -> List[Dict]:
        """Fetch items for a specific invoice properly joined with products"""
        try:
            query = """
            SELECT ii.*, p.product_code, p.product_name,
                   COALESCE((
                       SELECT SUM(ri.quantity)
                       FROM return_items ri
                       JOIN sales_returns sr ON ri.return_id = sr.id
                       WHERE sr.invoice_id = ii.invoice_id AND ri.product_id = ii.product_id
                   ), 0) as returned_quantity
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            WHERE ii.invoice_id = %s
            """
            self.cursor.execute(query, (invoice_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب بنود الفاتورة المكتملة: {err}", exc_info=True)
            return []

    def get_held_invoices(self, store_id: int, search_term: str = None) -> List[Dict]:
        """Fetch all held (temporary) invoices for a store with optional filtering"""
        try:
            query = """
            SELECT ti.*, u.name as cashier_name
            FROM temporary_invoices ti
            JOIN users u ON ti.cashier_id = u.id
            WHERE ti.store_id = %s
            """
            params = [store_id]
            
            if search_term:
                query += " AND (ti.temp_invoice_code LIKE %s OR ti.customer_name LIKE %s)"
                pattern = f"%{search_term}%"
                params.extend([pattern, pattern])
                
            query += " ORDER BY ti.saved_at DESC"
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب الفواتير المعلقة: {err}", exc_info=True)
            return []

    def get_held_invoice_items(self, temp_invoice_id: int) -> List[Dict]:
        """Fetch items for a specific held invoice"""
        try:
            query = """
            SELECT tii.*, p.product_code, p.product_name, p.sell_price as current_price
            FROM temporary_invoice_items tii
            JOIN products p ON tii.product_id = p.id
            WHERE tii.temp_invoice_id = %s
            """
            self.cursor.execute(query, (temp_invoice_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب بنود الفاتورة المعلقة: {err}", exc_info=True)
            return []

    def save_held_invoice(self, store_id: int, cashier_id: int, items: List[Dict], 
                         customer_name: str = None, customer_phone: str = None, customer_address: str = None) -> bool:
        """Save a new held invoice"""
        try:
            # معالجة العميل
            customer_id = self._get_or_create_customer(customer_name, customer_phone, customer_address)
            
            # 1. Insert header
            header_query = """
                INSERT INTO temporary_invoices 
                (store_id, cashier_id, customer_id, customer_name, customer_phone, customer_address) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(header_query, (store_id, cashier_id, customer_id, customer_name, customer_phone, customer_address))
            temp_id = self.cursor.lastrowid
            
            # 2. Insert items
            item_query = """
                INSERT INTO temporary_invoice_items 
                (temp_invoice_id, product_id, quantity, current_price) 
                VALUES (%s, %s, %s, %s)
            """
            for item in items:
                self.cursor.execute(item_query, (temp_id, item['product_id'], item['quantity'], item['price']))
            
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في حفظ الفاتورة المعلقة: {err}", exc_info=True)
            self.conn.rollback()
            return False

    def delete_held_invoice(self, temp_invoice_id: int) -> bool:
        """Delete a held invoice (after resuming or cancelling)"""
        try:
            self.cursor.execute("DELETE FROM temporary_invoices WHERE id = %s", (temp_invoice_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في حذف الفاتورة المعلقة: {err}", exc_info=True)
            return False
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """البحث عن بيانات العميل من خلال رقم الهاتف في الفواتير والطلبات"""
        try:
            if not phone or len(phone) < 11:
                return None
                
            # 1. البحث في الفواتير أولاً (الأحدث)
            query_invoices = """
            SELECT customer_name, customer_address, customer_phone
            FROM invoices
            WHERE customer_phone = %s AND customer_name IS NOT NULL
            ORDER BY invoice_date DESC
            LIMIT 1
            """
            self.cursor.execute(query_invoices, (phone,))
            res = self.cursor.fetchone()
            if res:
                return res
            
            # 2. إذا لم يوجد، البحث في الطلبات
            query_orders = """
            SELECT customer_name, customer_address, customer_phone
            FROM orders
            WHERE customer_phone = %s AND customer_name IS NOT NULL
            ORDER BY order_date DESC
            LIMIT 1
            """
            self.cursor.execute(query_orders, (phone,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب بيانات العميل: {err}", exc_info=True)
            return None
    
    # ==================== الطلبات ====================
    
    def create_order(self, customer_name: str, customer_phone: str,
                    source_store_id: int, call_center_user_id: int,
                    destination_store_id: int = None, customer_address: str = None,
                    customer_city: str = None) -> Optional[str]:
        """إنشاء طلب جديد من Call Center"""
        try:
            order_number = self.get_next_order_number()
            
            # معالجة العميل
            customer_id = self._get_or_create_customer(customer_name, customer_phone, customer_address)
            
            query = """
            INSERT INTO orders (order_number, customer_id, customer_name, customer_phone, 
                               source_store_id, call_center_user_id, destination_store_id,
                               customer_address, customer_city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (order_number, customer_id, customer_name, customer_phone,
                                       source_store_id, call_center_user_id, destination_store_id,
                                       customer_address, customer_city))
            self.conn.commit()
            return order_number
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إنشاء الطلب: {err}", exc_info=True)
            return None

    def get_open_orders(self, store_id: int, search_term: str = None) -> List[Dict]:
        """Fetch pending orders for a specific store with optional filtering"""
        try:
            query = """
            SELECT o.*, u.name as call_center_agent 
            FROM orders o
            JOIN users u ON o.call_center_user_id = u.id
            WHERE o.destination_store_id = %s 
            AND o.status IN ('Pending', 'Confirmed')
            """
            params = [store_id]
            
            if search_term:
                query += " AND (o.order_number LIKE %s OR o.customer_name LIKE %s OR o.customer_phone LIKE %s)"
                pattern = f"%{search_term}%"
                params.extend([pattern, pattern, pattern])
                
            query += " ORDER BY o.order_date DESC"
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب الطلبات المفتوحة: {err}", exc_info=True)
            return []

    def update_order_status(self, order_id: int, status: str) -> bool:
        """تحديث حالة الطلب (مثلاً من Pending إلى Delivered)"""
        try:
            query = "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s"
            self.cursor.execute(query, (status, order_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في تحديث حالة الطلب: {err}", exc_info=True)
            return False

    def add_order_item(self, order_id: int, product_id: int, quantity: int, 
                       unit_price: float) -> bool:
        """إضافة بند إلى الطلب"""
        try:
            total_price = quantity * unit_price
            query = """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (order_id, product_id, quantity, unit_price, total_price))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            logger.error(f"خطأ في إضافة بند الطلب: {err}", exc_info=True)
            return False

    def get_order_details(self, order_id: int) -> List[Dict]:
        """Fetch items for a specific order"""
        try:
            query = """
            SELECT oi.*, p.product_code, p.product_name 
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
            """
            self.cursor.execute(query, (order_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب بنود الطلب: {err}", exc_info=True)
            return []
    
    # ==================== درج الكاشير ====================
    
    def get_drawer_status(self, cashier_id: int) -> Optional[Dict]:
        """Get the current status of the cashier's drawer."""
        try:
            query = """
            SELECT id, opening_date, opening_balance, status 
            FROM drawer_logs 
            WHERE cashier_id = %s AND status = 'Open'
            ORDER BY opening_date DESC LIMIT 1
            """
            self.cursor.execute(query, (cashier_id,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'is_open': True,
                    'opened_at': row['opening_date'],
                    'opening_balance': row['opening_balance']
                }
            return {'is_open': False}
        except mysql.connector.Error as err:
            logger.error(f"خطأ في الحصول على حالة درج المتجر: {err}", exc_info=True)
            return None

    def get_supplier_stats(self) -> List[Dict]:
        """
        جلب إحصائيات الموردين: إجمالي المشتريات، المسدد، المتبقي، عدد الأصناف، عدد الفواتير.
        """
        try:
            query = """
                SELECT 
                    s.name as supplier_name,
                    COALESCE((SELECT SUM(total_amount) FROM purchase_invoices WHERE supplier_id = s.id), 0) as total_purchases,
                    COALESCE((SELECT SUM(amount) FROM financial_ledger WHERE account_id = s.id AND account_type = 'Supplier' AND transaction_type = 'Credit'), 0) as total_paid,
                    s.current_balance as balance,
                    (SELECT COUNT(DISTINCT pi.product_id) 
                     FROM purchase_items pi 
                     JOIN purchase_invoices pinv ON pi.invoice_id = pinv.id 
                     WHERE pinv.supplier_id = s.id) as product_count,
                    (SELECT COUNT(*) FROM purchase_invoices WHERE supplier_id = s.id) as invoice_count
                FROM suppliers s
                WHERE s.is_active = TRUE
                ORDER BY s.current_balance DESC, s.name ASC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب إحصائيات الموردين: {err}", exc_info=True)
            return []

    def get_inventory_valuation(self, store_id: int = None) -> float:
        """
        حساب القيمة الإجمالية للمخزون (الكمية * سعر الشراء).
        """
        try:
            query = """
                SELECT SUM(COALESCE(i.quantity_in_stock, 0) * p.buy_price) as total_val
                FROM products p
                LEFT JOIN product_inventory i ON p.id = i.product_id
                WHERE p.is_active = TRUE
            """
            params = []
            if store_id:
                query += " AND i.store_id = %s"
                params.append(store_id)
            
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            return float(res['total_val'] or 0) if res else 0.0
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب تقييم المخزون: {err}", exc_info=True)
            return 0.0

    def get_total_supplier_debt(self, store_id: int = None) -> float:
        """
        حساب إجمالي المديونية للموردين.
        """
        try:
            if store_id:
                # If store_id is provided, we calculate debt based on purchase invoices remaining amount
                # joined with users to find the branch of the creator
                query = """
                    SELECT SUM(pi.remaining_amount) as total_debt 
                    FROM purchase_invoices pi
                    JOIN users u ON pi.created_by = u.id
                    WHERE u.store_id = %s AND pi.status = 'completed'
                """
                self.cursor.execute(query, (store_id,))
            else:
                # Global snapshot: Sum current balance of all active suppliers
                query = "SELECT SUM(current_balance) as total_debt FROM suppliers WHERE is_active = TRUE"
                self.cursor.execute(query)
                
            res = self.cursor.fetchone()
            return float(res['total_debt'] or 0) if res else 0.0
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب إجمالي المدفوعات للموردين: {err}", exc_info=True)
            return 0.0

    def get_total_paid_to_suppliers(self, store_id: int = None) -> float:
        """
        حساب إجمالي المبيانات للموردين من السجل المالي (النقدي).
        """
        try:
            query = """
                SELECT SUM(l.amount) as total 
                FROM financial_ledger l 
            """
            params = []
            if store_id:
                query += " JOIN users u ON l.created_by = u.id WHERE u.store_id = %s AND "
                params.append(store_id)
            else:
                query += " WHERE "
                
            query += "l.account_type = 'Supplier' AND l.transaction_type = 'Credit'"
            
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            return float(res['total'] or 0) if res else 0.0
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب إجمالي المدفوعات للموردين: {err}", exc_info=True)
            return 0.0

    def get_total_treasury_balance(self, store_id: int = None) -> float:
        """
        حساب الرصيد الفعلي الحالي في الخزينة المركزية (تراكمي - غير مرتبط بفترة).
        رصيد السيولة الحقيقية المتاح الآن.
        """
        try:
            query = "SELECT SUM(CASE WHEN transaction_type = 'In' THEN amount ELSE -amount END) as balance FROM treasury"
            params = []
            if store_id:
                query += " WHERE store_id = %s"
                params.append(store_id)
            
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            return float(res['balance'] or 0) if res else 0.0
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب رصيد الخزينة: {err}", exc_info=True)
            return 0.0

    def get_treasury_period_totals(self, start_date: str = None, end_date: str = None, store_id: int = None) -> Dict:
        """
        حساب إجمالي الداخل والخارج من الخزينة لفترة معينة (من كل المصادر).
        يُستخدم كمصدر وحيد للحقيقة لبطاقات الكاش.
        """
        try:
            base = "FROM treasury WHERE 1=1"
            params = []
            if store_id:
                base += " AND store_id = %s"
                params.append(store_id)
            if start_date and end_date:
                base += " AND DATE(created_at) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            # Total In
            self.cursor.execute(f"SELECT SUM(amount) as total {base} AND transaction_type = 'In'", params)
            res = self.cursor.fetchone()
            total_in = float(res['total'] or 0) if res else 0.0
            
            # Total Out
            self.cursor.execute(f"SELECT SUM(amount) as total {base} AND transaction_type = 'Out'", params)
            res = self.cursor.fetchone()
            total_out = float(res['total'] or 0) if res else 0.0
            
            return {'total_in': total_in, 'total_out': total_out, 'net': total_in - total_out}
        except mysql.connector.Error as err:
            logger.error(f"خطأ في جلب إجمالي المداخل والخارج من الخزينة لفترة معينة: {err}", exc_info=True)
            return {'total_in': 0.0, 'total_out': 0.0, 'net': 0.0}
    
    def get_store_open_drawer(self, store_id: int) -> Optional[Dict]:
        """Check if ANY drawer is open in the store. Returns details if yes."""
        try:
            query = """
            SELECT dl.id, dl.cashier_id, u.name as cashier_name, dl.opening_date, dl.opening_balance 
            FROM drawer_logs dl
            JOIN users u ON dl.cashier_id = u.id
            WHERE dl.store_id = %s AND dl.status = 'Open'
            ORDER BY dl.opening_date DESC LIMIT 1
            """
            self.cursor.execute(query, (store_id,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'cashier_id': row['cashier_id'],
                    'cashier_name': row['cashier_name'],
                    'opened_at': row['opening_date'],
                    'opening_balance': row['opening_balance']
                }
            return None
        except mysql.connector.Error as err:
            logger.error(f"خطأ في الحصول على حالة درج المتجر: {err}", exc_info=True)
            return None
    
    def get_drawer_summary(self, drawer_id: int) -> Dict:
        """جلب ملخص العمليات المالية للدرج"""
        try:
            # 1. جلب بيانات افتتاح الدرج
            query_opening = "SELECT * FROM drawer_logs WHERE id = %s"
            self.cursor.execute(query_opening, (drawer_id,))
            drawer = self.cursor.fetchone()
            
            if not drawer:
                return {}
            
            cashier_id = drawer['cashier_id']
            store_id = drawer['store_id']
            
            # 2. جلب إحصائيات المبيعات
            query_sales = """
                SELECT 
                    COUNT(*) as count,
                    COALESCE(SUM(total_amount), 0) as total_sales,
                    COALESCE(SUM(cash_amount), 0) as total_cash,
                    COALESCE(SUM(card_amount), 0) as total_card
                FROM invoices 
                WHERE drawer_id = %s
            """
            self.cursor.execute(query_sales, (drawer_id,))
            sales = self.cursor.fetchone()
            
            # 3. جلب إجمالي المرتجعات التي تمت على هذا الدرج
            query_returns = """
                SELECT COALESCE(SUM(total_return_amount), 0) as total_returns, COUNT(*) as count
                FROM sales_returns 
                WHERE drawer_id = %s
            """
            self.cursor.execute(query_returns, (drawer_id,))
            returns = self.cursor.fetchone()
            
            # 4. جلب تفاصيل الفئات والفيزا الفعلية عند الإغلاق
            query_details = "SELECT * FROM drawer_closing_details WHERE drawer_log_id = %s"
            self.cursor.execute(query_details, (drawer_id,))
            details = self.cursor.fetchall()
            
            actual_visa = 0
            for d in details:
                if d['denomination'] == "Visa":
                    actual_visa = float(d['total_amount'])
            
            # 5. جلب أسماء الكاشير والفرع
            self.cursor.execute("SELECT name FROM users WHERE id = %s", (cashier_id,))
            cashier = self.cursor.fetchone()
            self.cursor.execute("SELECT store_name FROM stores WHERE id = %s", (store_id,))
            store = self.cursor.fetchone()
            
            opening_balance = float(drawer['opening_balance'] or 0)
            total_sales = float(sales['total_sales'] or 0)
            total_cash_sales = float(sales['total_cash'] or 0)
            total_card_sales = float(sales['total_card'] or 0)
            total_returns = float(returns['total_returns'] or 0)
            actual_cash = float(drawer['closing_balance'] or 0)
            
            # حساب المبالغ الآجلة (الباقي بعد الكاش والفيزا)
            total_deferred = total_sales - total_cash_sales - total_card_sales
            
            # 5b. حساب المرتجعات النقدية فقط (التي كانت فاتورتها الأصلية كاش)
            query_cash_returns = """
                SELECT COALESCE(SUM(sr.total_return_amount), 0) as cash_returns
                FROM sales_returns sr
                JOIN invoices i ON sr.invoice_id = i.id
                WHERE sr.drawer_id = %s AND i.cash_amount > 0
            """
            self.cursor.execute(query_cash_returns, (drawer_id,))
            cash_returns_res = self.cursor.fetchone()
            total_cash_returns = float(cash_returns_res['cash_returns'] or 0) if cash_returns_res else 0.0
            
            # الرصيد المتوقع في "الدرج" (الكاش فقط - يخصم المرتجعات النقدية فقط)
            expected_cash = opening_balance + total_cash_sales - total_cash_returns
            
            return {
                'drawer_id': drawer_id,
                'opened_at': drawer['opening_date'],
                'closed_at': drawer['closing_date'],
                'cashier_name': cashier['name'] if cashier else "غير معروف",
                'store_name': store['store_name'] if store else "غير معروف",
                'opening_balance': opening_balance,
                'total_sales': total_sales,
                'total_cash_sales': total_cash_sales,
                'total_card_sales': total_card_sales,
                'total_deferred': total_deferred,
                'sales_count': sales['count'],
                'total_returns': total_returns,
                'total_cash_returns': total_cash_returns,
                'returns_count': returns['count'],
                'expected_cash': expected_cash,
                'actual_cash': actual_cash,
                'actual_visa': actual_visa,
                'difference': actual_cash - expected_cash,
                'visa_difference': actual_visa - total_card_sales,
                'denominations': details
            }
        except mysql.connector.Error as err:
            print(f"❌ خطأ في ملخص الدرج: {err}")
            return {}
            
    def open_drawer(self, store_id: int, cashier_id: int, opening_balance: float = 0) -> Optional[int]:
        """فتح درج الكاشير"""
        try:
            query = """
            INSERT INTO drawer_logs (store_id, cashier_id, opening_balance, status)
            VALUES (%s, %s, %s, 'Open')
            """
            
            self.cursor.execute(query, (store_id, cashier_id, opening_balance))
            self.conn.commit()
            
            drawer_id = self.cursor.lastrowid
            
            # Queue for sync
            self._queue_sync('drawer_logs', drawer_id, 'OPEN', {
                'store_id': store_id, 'cashier_id': cashier_id,
                'opening_balance': opening_balance
            })
            
            print(f"✅ تم فتح الدرج {drawer_id}")
            return drawer_id
        except mysql.connector.Error as err:
            print(f"❌ خطأ: {err}")
            return None
    
    def close_drawer(self, drawer_id: int, closing_balance: float,
                    denomination_details: Dict[str, int]) -> bool:
        """إغلاق درج الكاشير مع تفاصيل فئات النقود"""
        try:
            # تحديث درج الكاشير
            query = """
            UPDATE drawer_logs
            SET closing_balance = %s, closing_date = NOW(), status = 'Closed'
            WHERE id = %s
            """
            
            self.cursor.execute(query, (closing_balance, drawer_id))
            
            # إضافة تفاصيل الفئات والفيزا الفعلية عند الإغلاق
            for denomination, quantity in denomination_details.items():
                detail_query = """
                INSERT INTO drawer_closing_details (drawer_log_id, denomination, quantity, total_amount)
                VALUES (%s, %s, %s, %s)
                """
                
                if denomination == "Visa":
                    # بالنسبة للفيزا، الكمية هي 1 والمبلغ هو الإجمالي المدخل
                    total = float(quantity)
                    qty = 1
                else:
                    # تحويل الفئة النقدية المعيارية (مثلاً "100ج") إلى رقم
                    denom_value = float(denomination.replace('ج', '').strip())
                    total = quantity * denom_value
                    qty = quantity
                
                self.cursor.execute(detail_query, (drawer_id, denomination, qty, total))
            
            self.conn.commit()
            
            # Queue for sync
            self._queue_sync('drawer_logs', drawer_id, 'CLOSE', {
                'closing_balance': closing_balance,
                'denomination_details': denomination_details,
                'cashier_id': self.get_drawer_cashier(drawer_id) # Need this to find the drawer on cloud
            })
            
            print(f"✅ تم إضافة معالجة المرتجعات النقود")
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ: {err}")
            return False

    def get_drawer_cashier(self, drawer_id: int) -> Optional[int]:
        """الحصول على معرف الكاشير للدرج المحدد"""
        try:
            self.cursor.execute("SELECT cashier_id FROM drawer_logs WHERE id = %s", (drawer_id,))
            res = self.cursor.fetchone()
            return res['cashier_id'] if res else None
        except:
            return None

    def get_drawers_report(self) -> List[Dict]:
        """جلب تقرير شامل عن جميع الأدراج (للمدير)"""
        try:
            query = """
            SELECT 
                dl.id,
                u.name as cashier_name,
                s.store_name,
                dl.opening_date,
                dl.closing_date,
                dl.status,
                dl.opening_balance,
            dl.closing_balance,
            COALESCE((
                SELECT SUM(total_amount) 
                FROM invoices 
                WHERE drawer_id = dl.id
                  AND status = 'Completed'
            ), 0) as `mبيعات_الدرج`,
            COALESCE((
                SELECT SUM(cash_amount) 
                FROM invoices 
                WHERE drawer_id = dl.id
                  AND status = 'Completed'
            ), 0) as cash_sales,
            COALESCE((
                SELECT SUM(card_amount) 
                FROM invoices 
                WHERE drawer_id = dl.id
                  AND status = 'Completed'
            ), 0) as card_sales,
            COALESCE((
                SELECT SUM(sr.total_return_amount) 
                FROM sales_returns sr
                JOIN invoices i ON sr.invoice_id = i.id
                WHERE sr.drawer_id = dl.id AND i.cash_amount > 0
            ), 0) as cash_returns
            FROM drawer_logs dl
            JOIN users u ON dl.cashier_id = u.id
            JOIN stores s ON dl.store_id = s.id
            ORDER BY dl.opening_date DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب تقرير الأدراج: {err}")
            return []

    def get_last_closed_drawer_id(self, store_id: int, cashier_id: int) -> Optional[int]:
        """Get the ID of the last closed drawer for re-printing"""
        try:
            query = """
            SELECT id FROM drawer_logs 
            WHERE store_id = %s AND cashier_id = %s AND status = 'Closed'
            ORDER BY closing_date DESC LIMIT 1
            """
            self.cursor.execute(query, (store_id, cashier_id))
            res = self.cursor.fetchone()
            if res:
                return res['id']
            return None
        except mysql.connector.Error as err:
            print(f"Error fetching last closed drawer: {err}")
            return None

    def get_closed_drawers_history(self, store_id: int, limit: int = 50) -> List[Dict]:
        """Fetch history of closed drawers with financial summaries"""
        try:
            query = """
            SELECT 
                dl.id, dl.closing_date, dl.opening_date, dl.closing_balance, dl.opening_balance,
                u.name as cashier_name,
                (SELECT COALESCE(SUM(cash_amount), 0) FROM invoices WHERE drawer_id = dl.id AND status = 'Completed') as cash_sales,
                (SELECT COALESCE(SUM(total_return_amount), 0) FROM sales_returns WHERE drawer_id = dl.id) as total_returns
            FROM drawer_logs dl
            JOIN users u ON dl.cashier_id = u.id
            WHERE dl.store_id = %s AND dl.status = 'Closed'
            ORDER BY dl.closing_date DESC
            LIMIT %s
            """
            self.cursor.execute(query, (store_id, limit))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching drawers history: {err}")
            return []
    
    # ==================== Utilities ====================
    
    def get_statistics(self, store_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على إحصائيات المبيعات"""
        try:
            result = {}
            
            # إجمالي المبيعات
            query = "SELECT SUM(total_amount) as total_sales FROM invoices WHERE store_id = %s AND status = 'Completed'"
            params = [store_id]
            
            if start_date and end_date:
                query += " AND DATE(invoice_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            self.cursor.execute(query, params)
            result['total_sales'] = self.cursor.fetchone()
            
            # عدد الفواتير
            query = "SELECT COUNT(*) as total_invoices FROM invoices WHERE store_id = %s AND status = 'Completed'"
            params = [store_id]
            
            if start_date and end_date:
                query += " AND DATE(invoice_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            self.cursor.execute(query, params)
            result['total_invoices'] = self.cursor.fetchone()
            
            return result
        except mysql.connector.Error as err:
            print(f"❌ خطأ: {err}")
            return {}
    def get_net_profit_stats(self, start_date: str = None, end_date: str = None, store_id: int = None) -> Dict:
        """Calculate Net Profit: (Sales - Returns) - (COGS - Returned Cost) - Op Expenses"""
        try:
            params = []
            date_filter_inv = ""
            date_filter_ret = ""
            date_filter_exp = ""
            store_filter_inv = ""
            store_filter_ret = ""
            store_filter_exp = ""
            
            if store_id:
                store_filter_inv = " AND store_id = %s"
                store_filter_ret = " AND store_id = %s"
                store_filter_exp = " AND store_id = %s"
                params.append(store_id)

            if start_date and end_date:
                date_filter_inv = " AND DATE(invoice_date) BETWEEN %s AND %s"
                date_filter_ret = " AND DATE(return_date) BETWEEN %s AND %s"
                date_filter_exp = " AND DATE(expense_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            # Define a helper to build params per query
            def get_p(needs_store=True, needs_date=True):
                p = []
                if needs_store and store_id: p.append(store_id)
                if needs_date and start_date and end_date: p.extend([start_date, end_date])
                return p
            
            # 1. Total Sales Revenue (Accrual)
            sales_query = f"SELECT SUM(total_amount) as total FROM invoices WHERE status = 'Completed'{store_filter_inv}{date_filter_inv}"
            self.cursor.execute(sales_query, get_p())
            res = self.cursor.fetchone()
            total_sales = float(res['total'] or 0) if res else 0.0

            # 1b. Total Collected (Cash + Card separately) for detailed reporting
            collected_cash_query = f"SELECT SUM(COALESCE(cash_amount, 0)) as total FROM invoices WHERE status = 'Completed'{store_filter_inv}{date_filter_inv}"
            self.cursor.execute(collected_cash_query, get_p())
            res = self.cursor.fetchone()
            total_cash_collected = float(res['total'] or 0) if res else 0.0

            collected_card_query = f"SELECT SUM(COALESCE(card_amount, 0)) as total FROM invoices WHERE status = 'Completed'{store_filter_inv}{date_filter_inv}"
            self.cursor.execute(collected_card_query, get_p())
            res = self.cursor.fetchone()
            total_card_collected = float(res['total'] or 0) if res else 0.0
            
            total_collected = total_cash_collected + total_card_collected
            
            # 2. Total Returns Value
            returns_query = f"SELECT SUM(total_return_amount) as total FROM sales_returns WHERE 1=1{store_filter_ret}{date_filter_ret}"
            self.cursor.execute(returns_query, get_p())
            res = self.cursor.fetchone()
            total_returns = float(res['total'] or 0) if res else 0.0
            
            # 3. Cost of Goods Sold (COGS)
            cogs_query = f"""
                SELECT SUM(ii.quantity * COALESCE(NULLIF(ii.buy_price, 0), p.buy_price, 0)) as total
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE i.status = 'Completed'{store_filter_inv.replace('store_id', 'i.store_id')}{date_filter_inv.replace('invoice_date', 'i.invoice_date')}
            """
            self.cursor.execute(cogs_query, get_p())
            res = self.cursor.fetchone()
            total_cogs = float(res['total'] or 0) if res else 0.0
            
            # 4. Cost of Returned Goods
            returned_cost_query = f"""
                SELECT SUM(ri.quantity * COALESCE(NULLIF(ri.buy_price, 0), p.buy_price, 0)) as total
                FROM return_items ri
                JOIN products p ON ri.product_id = p.id
                JOIN sales_returns sr ON ri.return_id = sr.id
                WHERE 1=1{store_filter_ret.replace('store_id', 'sr.store_id')}{date_filter_ret.replace('return_date', 'sr.return_date')}
            """
            self.cursor.execute(returned_cost_query, get_p())
            res = self.cursor.fetchone()
            total_returned_cost = float(res['total'] or 0) if res else 0.0
            
            # 5. Total Expenses (Operational Only)
            expenses_query = f"SELECT SUM(amount) as total FROM expenses WHERE is_personal = 0{store_filter_exp}{date_filter_exp}"
            self.cursor.execute(expenses_query, get_p())
            res = self.cursor.fetchone()
            total_expenses = float(res['total'] or 0) if res else 0.0

            # 6. Total Invoices Count
            count_query = f"SELECT COUNT(*) as cnt FROM invoices WHERE status = 'Completed'{store_filter_inv}{date_filter_inv}"
            self.cursor.execute(count_query, get_p())
            res = self.cursor.fetchone()
            invoice_count = int(res['cnt'] or 0) if res else 0

            # 7. Total Supplier Payments (Branch Aware)
            # Filter by store_id by joining with users table
            pay_query = f"""
                SELECT SUM(l.amount) as total 
                FROM financial_ledger l 
                JOIN users u ON l.created_by = u.id 
                WHERE l.account_type = 'Supplier' AND l.transaction_type = 'Credit' 
                {store_filter_inv.replace('store_id', 'u.store_id')} 
                {date_filter_inv.replace('invoice_date', 'l.transaction_date')}
            """
            self.cursor.execute(pay_query, get_p())
            res = self.cursor.fetchone()
            total_supplier_paid = float(res['total'] or 0) if res else 0.0

            # 7b. Treasury Out Transactions (Manual Adjustments only to avoid double counting with ledger/expenses)
            # These are manual cash exits not captured in standard forms
            treasury_out_query = "SELECT SUM(amount) as total FROM treasury WHERE transaction_type = 'Out' AND source_type = 'Adjustment'"
            treasury_params_out = []
            if store_id:
                treasury_out_query += " AND store_id = %s"
                treasury_params_out.append(store_id)
            if start_date and end_date:
                treasury_out_query += " AND DATE(created_at) BETWEEN %s AND %s"
                treasury_params_out.extend([start_date, end_date])
            self.cursor.execute(treasury_out_query, treasury_params_out)
            res = self.cursor.fetchone()
            total_treasury_out = float(res['total'] or 0) if res else 0.0

            # 7c. Treasury In Transactions (Manual deposits and other non-sale/non-settlement inflows)
            # We already have Sales (total_collected) and Debt Coll (total_debt_collected) handled.
            # We filter for 'Adjustment' to find manual cash injections
            treasury_in_query = "SELECT SUM(amount) as total FROM treasury WHERE transaction_type = 'In' AND source_type = 'Adjustment'"
            treasury_params_in = []
            if store_id:
                treasury_in_query += " AND store_id = %s"
                treasury_params_in.append(store_id)
            if start_date and end_date:
                treasury_in_query += " AND DATE(created_at) BETWEEN %s AND %s"
                treasury_params_in.extend([start_date, end_date])
            self.cursor.execute(treasury_in_query, treasury_params_in)
            res = self.cursor.fetchone()
            total_treasury_in = float(res['total'] or 0) if res else 0.0

            # 8. Independent Customer Payments (Branch Aware)
            coll_query = f"""
                SELECT SUM(l.amount) as total 
                FROM financial_ledger l 
                JOIN users u ON l.created_by = u.id 
                WHERE l.account_type = 'Customer' AND l.transaction_type = 'Debit' 
                {store_filter_inv.replace('store_id', 'u.store_id')} 
                {date_filter_inv.replace('invoice_date', 'l.transaction_date')}
            """
            self.cursor.execute(coll_query, get_p())
            res = self.cursor.fetchone()
            total_debt_collected = float(res['total'] or 0) if res else 0.0

            # Calculations
            net_sales = total_sales - total_returns
            total_cogs_net = total_cogs - total_returned_cost
            gross_profit = net_sales - total_cogs_net
            net_profit = gross_profit - total_expenses
            
            if self._verbose_diagnostics:
                logger.info(
                    "STATS DIAGNOSTICS | store=%s | period=%s..%s | sales=%.2f | collected=%.2f | debt_collected=%.2f | cogs=%.2f | returns=%.2f | expenses=%.2f | supplier_paid=%.2f | treasury_out=%.2f | treasury_in=%.2f | invoices=%s",
                    store_id if store_id is not None else 'ALL',
                    start_date,
                    end_date,
                    total_sales,
                    total_collected,
                    total_debt_collected,
                    total_cogs,
                    total_returns,
                    total_expenses,
                    total_supplier_paid,
                    total_treasury_out,
                    total_treasury_in,
                    invoice_count,
                )

            return {
                'total_sales': total_sales,
                'total_collected': total_collected,
                'total_cash_collected': total_cash_collected,
                'total_card_collected': total_card_collected,
                'total_debt_collected': total_debt_collected,
                'total_returns': total_returns,
                'total_cogs': total_cogs,
                'total_returned_cost': total_returned_cost,
                'total_expenses': total_expenses,
                'total_supplier_paid': total_supplier_paid,
                'total_treasury_out': total_treasury_out,
                'total_treasury_in': total_treasury_in,
                'invoice_count': invoice_count,
                'net_profit': net_profit,
                'avg_ticket': total_sales / invoice_count if invoice_count > 0 else 0,
                'profit_margin': (net_profit / net_sales * 100) if net_sales > 0 else 0,
                'return_rate': (total_returns / total_sales * 100) if total_sales > 0 else 0
            }
            
        except (mysql.connector.Error, ValueError, TypeError, KeyError) as err:
            print(f"❌ Error calculating net profit: {err}")
            return {'net_profit': 0.0, 'total_returns': 0.0, 'invoice_count': 0}

    def get_hourly_sales_heatmap(self, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """Fetch sales distribution by hour (for heatmap/chart)"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            store_filter = ""
            if store_id:
                store_filter = " AND store_id = %s"
                params.append(store_id)

            query = f"""
            SELECT HOUR(invoice_date) as hour, COUNT(*) as count, SUM(total_amount) as total_sales
            FROM invoices
            WHERE status = 'Completed'{date_filter}{store_filter}
            GROUP BY HOUR(invoice_date)
            ORDER BY hour ASC
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching hourly heatmap: {err}")
            return []

    def get_customer_retention_stats(self, start_date: str = None, end_date: str = None) -> Dict:
        """Calculate retention rate (Repeat vs New Customers)"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " WHERE DATE(invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            query = f"""
            WITH CustomerSales AS (
                SELECT customer_phone, COUNT(*) as order_count
                FROM invoices
                {date_filter}
                AND customer_phone IS NOT NULL AND customer_phone != ''
                GROUP BY customer_phone
            )
            SELECT 
                COUNT(CASE WHEN order_count > 1 THEN 1 END) as repeat_customers,
                COUNT(CASE WHEN order_count = 1 THEN 1 END) as new_customers,
                COUNT(*) as total_customers
            FROM CustomerSales
            """
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            if res and res['total_customers'] and res['total_customers'] > 0:
                res['retention_rate'] = (res['repeat_customers'] / res['total_customers']) * 100
                return res
            return {'repeat_customers': 0, 'new_customers': 0, 'total_customers': 0, 'retention_rate': 0}
        except mysql.connector.Error as err:
            print(f"❌ Error fetching customer retention: {err}")
            return {}
    
    def export_to_log(self, user_id: int, action: str, table_name: str = None,
                     record_id: int = None, old_values: str = None, new_values: str = None):
        """تسجيل العملية في سجل التدقيق"""
        try:
            query = """
            INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (user_id, action, table_name, record_id, old_values, new_values))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في التسجيل: {err}")

    def get_sales_by_store(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch total sales grouped by store"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(i.invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]

            query = f"""
            SELECT s.store_name, COALESCE(SUM(i.total_amount), 0) as total_sales, COUNT(i.id) as invoice_count
            FROM stores s
            LEFT JOIN invoices i ON s.id = i.store_id AND i.status = 'Completed'{date_filter}
            GROUP BY s.id, s.store_name
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching sales by store: {err}")
            return []

    def get_overall_total_sales(self, start_date: str = None, end_date: str = None) -> float:
        """Fetch grand total of all sales"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]

            query = f"SELECT SUM(total_amount) as grand_total FROM invoices WHERE status = 'Completed'{date_filter}"
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            return float(res['grand_total']) if res and res['grand_total'] else 0.0
        except mysql.connector.Error:
            return 0.0

    def get_top_selling_products(self, limit=10, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """Fetch products with highest sales quantity"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(i.invoice_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            store_filter = ""
            if store_id:
                store_filter = " AND i.store_id = %s"
                params.append(store_id)

            params.append(limit)

            query = f"""
            SELECT p.product_name, SUM(ii.quantity) as total_qty, SUM(ii.total_price) as total_revenue
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.status = 'Completed'{date_filter}{store_filter}
            GROUP BY p.id, p.product_name
            ORDER BY total_qty DESC
            LIMIT %s
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching top selling products: {err}")
            return []

    def get_most_returned_products(self, limit=10, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """Fetch products with highest return count"""
        try:
            params = []
            date_filter_inv = "" 
            if start_date and end_date:
                date_filter_inv = " AND DATE(sr.return_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            store_filter = ""
            if store_id:
                store_filter = " AND sr.store_id = %s"
                params.append(store_id)

            params.append(limit)

            query = f"""
            SELECT p.product_name, SUM(ri.quantity) as return_qty
            FROM return_items ri
            JOIN products p ON ri.product_id = p.id
            JOIN sales_returns sr ON ri.return_id = sr.id
            WHERE 1=1{date_filter_inv}{store_filter}
            GROUP BY p.id, p.product_name
            ORDER BY return_qty DESC
            LIMIT %s
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching most returned products: {err}")
            return []

    def get_return_reasons_summary(self, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """Summarize return reasons"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(return_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            store_filter = ""
            if store_id:
                store_filter = " AND store_id = %s"
                params.append(store_id)

            query = f"""
            SELECT 
                CASE WHEN reason IS NULL OR reason = '' THEN 'غير محدد' ELSE reason END as reason, 
                COUNT(*) as count
            FROM sales_returns
            WHERE 1=1 {date_filter}{store_filter}
            GROUP BY CASE WHEN reason IS NULL OR reason = '' THEN 'غير محدد' ELSE reason END
            ORDER BY count DESC
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error:
            return []

    def get_top_customers(self, limit=10, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """
        Fetch top customers by total spending.
        Also finds their most frequently purchased product.
        """
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(i.invoice_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            store_filter = ""
            if store_id:
                store_filter = " AND i.store_id = %s"
                params.append(store_id)

            params.append(limit)

            query = f"""
            SELECT 
                i.customer_name, 
                i.customer_phone, 
                i.customer_address,
                COUNT(DISTINCT i.id) as total_invoices,
                SUM(i.total_amount) as total_spent,
                (
                    SELECT p.product_name 
                    FROM invoice_items ii2 
                    JOIN invoices i2 ON ii2.invoice_id = i2.id
                    JOIN products p ON ii2.product_id = p.id
                    WHERE (i2.customer_phone = i.customer_phone OR i2.customer_name = i.customer_name)
                    GROUP BY p.id
                    ORDER BY SUM(ii2.quantity) DESC
                    LIMIT 1
                ) as favorite_product
            FROM invoices i
            WHERE i.status = 'Completed' 
              AND (i.customer_name IS NOT NULL OR i.customer_phone IS NOT NULL)
              {date_filter}{store_filter}
            GROUP BY i.customer_phone, i.customer_name, i.customer_address
            ORDER BY total_spent DESC
            LIMIT %s
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching top customers: {err}")
            return []



    def get_product_total_stock(self, product_id: int) -> int:
        """احسب إجمالي المخزون لمنتج معين في جميع الفروع"""
        try:
            query = "SELECT SUM(quantity_in_stock) as total FROM product_inventory WHERE product_id = %s"
            self.cursor.execute(query, (product_id,))
            result = self.cursor.fetchone()
            if result and result['total'] is not None:
                return int(result['total'])
            return 0
        except mysql.connector.Error as err:
            print(f"❌ Error getting total stock: {err}")
            return 0

    # ==================== التحويلات المخزون ====================
    
    def get_main_warehouse_id(self) -> Optional[int]:
        """الحصول على معرف المخزون لمنتج معين في جميع الفروع"""
        try:
            # البحث عن المخزن من نوع Main أو Warehouse
            query = "SELECT id FROM stores WHERE store_type IN ('Main', 'Warehouse') ORDER BY id LIMIT 1"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                return result['id']
            # إذا لم يوجد، نأخذ أول متجر
            self.cursor.execute("SELECT id FROM stores ORDER BY id LIMIT 1")
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب المخزون الرئيسي")
            return None

    def transfer_stock(self, product_id: int, from_store_id: int, to_store_id: int, 
                      quantity: int, user_id: int, notes: str = None) -> Tuple[bool, str]:
        """
        نقل مخزون من فرع لآخر (خصم من المصدر وإنشاء سجل معلق)
        Returns: (Success: bool, Message: str)
        """
        try:
            # 1. التحقق من توفر الكمية في المصدر
            query_check = "SELECT quantity_in_stock FROM product_inventory WHERE product_id=%s AND store_id=%s"
            self.cursor.execute(query_check, (product_id, from_store_id))
            source_stock = self.cursor.fetchone()
            
            if not source_stock or source_stock['quantity_in_stock'] < quantity:
                return False, "الكمية في المخزون المصدر غير كافية"
            
            # 2. إنشاء سجل التحويل (Header)
            transfer_code = f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            insert_transfer = """
                INSERT INTO warehouse_transfers (transfer_number, from_store_id, to_store_id, 
                                               created_by, status, notes)
                VALUES (%s, %s, %s, %s, 'Pending', %s)
            """
            self.cursor.execute(insert_transfer, (transfer_code, from_store_id, to_store_id, user_id, notes))
            transfer_id = self.cursor.lastrowid
            
            # 3. إنشاء بند التحويل
            insert_item = """
                INSERT INTO transfer_items (transfer_id, product_id, quantity_sent)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(insert_item, (transfer_id, product_id, quantity))
            
            # 4. خصم الكمية من المصدر فقط
            self.update_inventory(product_id, from_store_id, quantity, operation='subtract')
            
            self.conn.commit()
            return True, f"تم بدء التحويل بنجاح. في انتظار الاستلام. رقم: {transfer_code}"
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"❌ خطأ في عملية التحويل: {err}")
            return False, f"حدث خطأ في قاعدة البيانات: {str(err)}"

    def get_pending_transfers(self, to_store_id: int = None) -> List[Dict]:
        """جلب التحويلات الواردة المعلقة
        If to_store_id is None, fetch ALL pending transfers (for Admin)
        """
        try:
            query = """
            SELECT wt.id, wt.transfer_number, wt.transfer_date, wt.notes,
                   s.store_name as from_store, s2.store_name as to_store_name, 
                   u.name as created_by_name,
                   ti.product_id, ti.quantity_sent, p.product_name,
                   wt.to_store_id
            FROM warehouse_transfers wt
            JOIN stores s ON wt.from_store_id = s.id
            JOIN stores s2 ON wt.to_store_id = s2.id
            JOIN users u ON wt.created_by = u.id
            JOIN transfer_items ti ON wt.id = ti.transfer_id
            JOIN products p ON ti.product_id = p.id
            WHERE wt.status = 'Pending'
            """
            
            params = []
            if to_store_id is not None:
                query += " AND wt.to_store_id = %s"
                params.append(to_store_id)
            
            query += " ORDER BY wt.transfer_date DESC"
            
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب التحويلات الواردة المعلقة: {err}")
            return []

    def receive_transfer(self, transfer_id: int, user_id: int) -> Tuple[bool, str]:
        """استلام التحويل وإضافة الكمية للمخزون المستلم"""
        try:
            # 1. جلب بيانات التحويل
            query = """
                SELECT wt.*, ti.product_id, ti.quantity_sent 
                FROM warehouse_transfers wt
                JOIN transfer_items ti ON wt.id = ti.transfer_id
                WHERE wt.id = %s AND wt.status = 'Pending'
            """
            self.cursor.execute(query, (transfer_id,))
            transfer = self.cursor.fetchone()
            
            if not transfer:
                return False, "التحويل غير موجود أو تم معالجته مسبقاً"
            
            # 2. تحديث المخزن المستلم (إضافة)
            self.update_inventory(transfer['product_id'], transfer['to_store_id'], 
                                transfer['quantity_sent'], operation='add')
            
            # 3. تحديث حالة التحويل
            update_query = """
                UPDATE warehouse_transfers 
                SET status = 'Received', received_by = %s, received_date = NOW()
                WHERE id = %s
            """
            self.cursor.execute(update_query, (user_id, transfer_id))
            
            # 4. تحديث الكمية المستلمة في البيانات للمخزون
            update_item = "UPDATE transfer_items SET quantity_received = %s WHERE transfer_id = %s"
            self.cursor.execute(update_item, (transfer['quantity_sent'], transfer_id))
            
            self.conn.commit()
            return True, "تم استلام التحويل وإضافة الكمية للمخزون بنجاح"
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"❌ خطأ في استلام التحويل: {err}")
            return False, f"خطأ: {str(err)}"
    
    # ==================== نظام التحكم في الوصول ====================
    
    def check_device_authorization(self, device_id: str, user_id: int, store_id: int) -> bool:
        """التحقق من أن الجهاز مصرح به للمستخدم"""
        try:
            query = """
            SELECT id, is_active FROM authorized_devices
            WHERE device_id = %s AND is_active = TRUE
            AND (user_id = %s OR user_id IS NULL)
            AND (store_id = %s OR store_id IS NULL)
            """
            self.cursor.execute(query, (device_id, user_id, store_id))
            result = self.cursor.fetchone()
            
            if result:
                # تحديث آخر استخدام
                update_query = "UPDATE authorized_devices SET last_used = NOW() WHERE id = %s"
                self.cursor.execute(update_query, (result['id'],))
                self.conn.commit()
                return True
            return False
        except mysql.connector.Error as err:
            print(f"❌ خطأ في التحقق من الجهاز مصرح به للمستخدم: {err}")
            return False

    def get_device_store_id(self, device_id: str) -> Optional[int]:
        """معرفة الفرع المرتبط بهذا الجهاز (الأولوية للقيود المرتبطة بفرع)"""
        try:
            # ترتيب النتائج بحيث يظهر السجل الذي يتطلب على store_id أولاً
            query = """
            SELECT store_id FROM authorized_devices 
            WHERE device_id = %s AND is_active = TRUE 
            ORDER BY (store_id IS NULL) ASC, registered_at DESC 
            LIMIT 1
            """
            self.cursor.execute(query, (device_id,))
            res = self.cursor.fetchone()
            return res['store_id'] if res else None
        except mysql.connector.Error as err:
            print(f"❌ Error getting device store ID: {err}")
            return None
    
    def check_ip_in_range(self, ip: str, store_id: int) -> Tuple[bool, str]:
        """التحقق من أن IP ضمن نطاق الفرع"""
        try:
            query = """
            SELECT ip_range_start, ip_range_end, require_ip_check, store_name
            FROM stores WHERE id = %s
            """
            self.cursor.execute(query, (store_id,))
            store = self.cursor.fetchone()
            
            if not store:
                return False, "الفرع غير موجود أو تم معالجته مسبقاً"
            
            # إذا كان الفرع لا يتم تحديد نطاق IP
            if not store.get('require_ip_check', True):
                return True, "معفي من فحص IP"
            
            # إذا لم يتم تحديد نطاق IP
            if not store.get('ip_range_start') or not store.get('ip_range_end'):
                return True, "لم يتم تحديد نطاق IP"
            
            # التحقق من النطاق
            from utils.device_manager import DeviceManager
            if DeviceManager.ip_in_range(ip, store['ip_range_start'], store['ip_range_end']):
                return True, "IP ضمن النطاق المسموح"
            else:
                return False, f"IP خارج نطاق {store['store_name']}"
                
        except mysql.connector.Error as err:
            print(f"❌ خطأ في فحص IP: {err}")
            return False, f"خطأ: {str(err)}"

    def check_device_banned(self, device_id: str) -> bool:
        """التحقق مما إذا كان الجهاز محظوراً (تم تعطيله)"""
        try:
            # نبحث عن أي سجل لهذا الجهاز تكون حالته غير نشطة
            # إذا كان الجهاز مسجلاً ولكن is_active = FALSE، فهذا يعني أنه محظوراً
            query = "SELECT id FROM authorized_devices WHERE device_id = %s AND is_active = FALSE LIMIT 1"
            self.cursor.execute(query, (device_id,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error:
            return False
    
    def register_device(self, device_id: str, device_name: str, mac_address: str,
                       store_id: int = None, user_id: int = None, 
                       registered_by: int = None, notes: str = None) -> bool:
        """تسجيل جهاز جديد"""
        try:
            query = """
            INSERT INTO authorized_devices 
            (device_id, device_name, mac_address, store_id, user_id, registered_by, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            device_name = VALUES(device_name),
            store_id = VALUES(store_id),
            user_id = VALUES(user_id),
            notes = VALUES(notes),
            is_active = TRUE
            """
            self.cursor.execute(query, (device_id, device_name, mac_address, 
                                       store_id, user_id, registered_by, notes))
            self.conn.commit()
            print(f"✅ تم تسجيل/تحديث الجهاز: {device_name}")
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في تسجيل الجهاز: {err}")
            return False
    
    def log_login_attempt(self, email: str, device_id: str, device_name: str,
                         ip_address: str, success: bool, failure_reason: str = None,
                         user_id: int = None) -> bool:
        """تسجيل محاولة تسجيل الدخول"""
        try:
            query = """
            INSERT INTO login_attempts 
            (user_email, user_id, device_id, device_name, ip_address, success, failure_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (email, user_id, device_id, device_name, 
                                       ip_address, success, failure_reason))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في تسجيل محاولة الدخول: {err}")
            return False
    
    def get_authorized_devices(self, store_id: int = None, user_id: int = None) -> List[Dict]:
        """جلب الأجهزة المصرج بها"""
        try:
            query = """
            SELECT ad.*, s.store_name, u.name as user_name, 
                   ru.name as registered_by_name
            FROM authorized_devices ad
            LEFT JOIN stores s ON ad.store_id = s.id
            LEFT JOIN users u ON ad.user_id = u.id
            LEFT JOIN users ru ON ad.registered_by = ru.id
            WHERE 1=1
            """
            params = []
            
            if store_id:
                query += " AND ad.store_id = %s"
                params.append(store_id)
            
            if user_id:
                query += " AND ad.user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY ad.registered_at DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب الأجهزة: {err}")
            return []
    
    def deactivate_device(self, record_id: int) -> bool:
        """تعطيل جهاز باستخدام المعرف الفريد"""
        try:
            query = "UPDATE authorized_devices SET is_active = FALSE WHERE id = %s"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
            print(f"✅ تم تعطيل التصريح رقم: {record_id}")
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في تعطيل التصريح: {err}")
            return False
    
    def activate_device(self, record_id: int) -> bool:
        """تفعيل جهاز باستخدام المعرف الفريد"""
        try:
            query = "UPDATE authorized_devices SET is_active = TRUE WHERE id = %s"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
            print(f"✅ تم تفعيل التصريح رقم: {record_id}")
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في تفعيل التصريح: {err}")
            return False
    
    def delete_device(self, record_id: int) -> bool:
        """حذف جهاز باستخدام المعرف الفريد"""
        try:
            query = "DELETE FROM authorized_devices WHERE id = %s"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
            print(f"✅ تم حذف التصريح رقم: {record_id}")
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في حذف التصريح: {err}")
            return False
    
    def get_login_attempts(self, limit: int = 100, failed_only: bool = False) -> List[Dict]:
        """جلب سجل محاولة تسجيل الدخول"""
        try:
            query = """
            SELECT * FROM login_attempts
            WHERE 1=1
            """
            
            if failed_only:
                query += " AND success = FALSE"
            
            query += " ORDER BY attempt_time DESC LIMIT %s"
            
            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب سجل محاولة تسجيل الدخول: {err}")
            return []
    
    def get_store_info(self, store_id: int) -> Optional[Dict]:
        """جلب معلومات الفرع بما في ذلك نطاق IP"""
        try:
            query = """
            SELECT * FROM stores WHERE id = %s
            """
            self.cursor.execute(query, (store_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب معلومات الفرع: {err}")
            return None

    # ==================== Analytics ====================
    
    def get_daily_sales_trend(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch daily sales totals for the chart"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]
            elif not start_date and not end_date:
                date_filter = " AND invoice_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
            
            query = f"""
            SELECT DATE(invoice_date) as date, SUM(total_amount) as total_sales
            FROM invoices
            WHERE status = 'Completed'{date_filter}
            GROUP BY DATE(invoice_date)
            ORDER BY date ASC
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching daily sales trend: {err}")
            return []

    def get_sales_by_category(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch sales distribution by category"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(i.invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            query = f"""
            SELECT c.category_name as label, SUM(ii.total_price) as value
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.status = 'Completed'{date_filter}
            GROUP BY c.id, c.category_name
            ORDER BY value DESC
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching sales by category: {err}")
            return []

    def get_product_sales_report(self, start_date: str = None, end_date: str = None, store_id: int = None) -> List[Dict]:
        """Fetch daily product sales report per branch"""
        try:
            params = []
            filters = "WHERE i.status = 'Completed'"
            
            if start_date and end_date:
                filters += " AND DATE(i.invoice_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            if store_id:
                filters += " AND i.store_id = %s"
                params.append(store_id)
                
            query = f"""
            SELECT 
                p.product_code, 
                p.product_name, 
                s.store_name, 
                DATE(i.invoice_date) as sale_date,
                SUM(ii.quantity) as total_qty,
                SUM(ii.total_price) as total_revenue,
                SUM(ii.quantity * p.buy_price) as total_cost
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            JOIN stores s ON i.store_id = s.id
            {filters}
            GROUP BY p.id, s.id, DATE(i.invoice_date)
            ORDER BY sale_date DESC, total_qty DESC
            """
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching product sales report: {err}")
            return []

    def get_sales_by_payment_method(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch sales distribution by payment method"""
        try:
            params = []
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(invoice_date) BETWEEN %s AND %s"
                params = [start_date, end_date]

            query = f"""
            SELECT 
                SUM(cash_amount) as Cash,
                SUM(card_amount) as Visa
            FROM invoices
            WHERE status = 'Completed'{date_filter}
            """
            self.cursor.execute(query, params)
            res = self.cursor.fetchone()
            
            result = []
            if res:
                if res['Cash'] and float(res['Cash']) > 0:
                    result.append({'label': 'Cash', 'value': float(res['Cash']), 'color': '#10B981'})
                if res['Visa'] and float(res['Visa']) > 0:
                    result.append({'label': 'Visa', 'value': float(res['Visa']), 'color': '#3B82F6'})
            
            return result
        except mysql.connector.Error as err:
            print(f"❌ Error fetching payment stats: {err}")
            return []

    # ==================== إدارة المصروفات ====================
    
    def add_expense(self, store_id: int, user_id: int, expense_type: str, 
                   amount: float, description: str = None, is_personal: bool = False) -> Optional[int]:
        """إضافة مصروف جديد"""
        try:
            user_id = self._get_valid_user_id(user_id)
            query = """
            INSERT INTO expenses (store_id, user_id, expense_type, amount, description, is_personal)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (store_id, user_id, expense_type, amount, description, is_personal))
            expense_id = self.cursor.lastrowid
            self.conn.commit()

            # Queue for sync
            self._queue_sync('expenses', expense_id, 'INSERT', {
                'store_id': store_id, 'user_id': user_id, 'expense_type': expense_type,
                'amount': amount, 'description': description, 'is_personal': is_personal
            })
            
            # Record Treasury Out
            self.record_treasury_transaction(
                store_id=store_id,
                trans_type='Out',
                amount=amount,
                source='Expense',
                ref_id=expense_id,
                desc=f"مصروف: {expense_type} - {description or ''}",
                user_id=user_id
            )

            # تسجيل المصروف في السجل المالي (للظهور في صفحة الحسابات)
            self.cursor.execute("""
                INSERT INTO financial_ledger 
                    (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                VALUES ('Expense', %s, 'Debit', %s, 'Expense', %s, %s, %s)
            """, (user_id, amount, expense_id,
                  f"مصروف: {expense_type} - {description or ''}",
                  user_id))
            self.conn.commit()
            
            return expense_id
        except mysql.connector.Error as err:
            print(f"❌ خطأ في إضافة المصروف: {err}")
            if self.conn: self.conn.rollback()
            return None

    def get_expenses(self, store_id: int, start_date: str = None, 
                    end_date: str = None, limit: int = 100) -> List[Dict]:
        """جلب المصروفات مع فلاتر التاريخ"""
        try:
            params = [store_id]
            date_filter = ""
            if start_date and end_date:
                date_filter = " AND DATE(e.expense_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            query = f"""
            SELECT e.id, e.expense_type, e.amount, e.description, e.expense_date, e.is_personal,
                   u.name as user_name
            FROM expenses e
            JOIN users u ON e.user_id = u.id
            WHERE e.store_id = %s {date_filter}
            ORDER BY e.expense_date DESC
            LIMIT %s
            """
            params.append(limit)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب المصروفات: {err}")
            return []

    def delete_expense(self, expense_id: int) -> bool:
        """حذف مصروف مع تنظيف السجلات المتعلقة في الخزينة والسجل المالي"""
        try:
            # 1. حذف من الخزينة
            self.cursor.execute("DELETE FROM treasury WHERE source_type = 'Expense' AND reference_id = %s", (expense_id,))
            
            # 2. حذف من السجل المالي
            self.cursor.execute("DELETE FROM financial_ledger WHERE reference_type = 'Expense' AND reference_id = %s", (expense_id,))
            
            # 3. حذف المصروف نفسه
            query = "DELETE FROM expenses WHERE id = %s"
            self.cursor.execute(query, (expense_id,))
            
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ في حذف المصروف: {err}")
            if self.conn: self.conn.rollback()
            return False

    def get_financial_report(self, store_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """
        إنشاء تقرير مالي شامل وحساب صافي الأرباح
        Net Profit = (Total Sales - Total Returns) - (COGS - Cost of Returns) - Expenses
        """
        try:
            report = {
                'total_sales': 0.0,
                'total_returns': 0.0,
                'total_cogs': 0.0,      # Cost of Goods Sold
                'cost_of_returns': 0.0, # Cost of returned items
                'total_expenses': 0.0,
                'net_profit': 0.0,
                'period': 'All Time'
            }
            
            params = [store_id]
            date_filter_inv = ""
            date_filter_ret = ""
            date_filter_exp = ""
            
            if start_date and end_date:
                report['period'] = f"{start_date} to {end_date}"
                date_filter_inv = " AND DATE(invoice_date) BETWEEN %s AND %s"
                date_filter_ret = " AND DATE(return_date) BETWEEN %s AND %s"
                date_filter_exp = " AND DATE(expense_date) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            # 1. Total Sales (Completed Invoices)
            # Separate Header Sales from Itemized COGS to avoid Cartesian Product bug
            query_sales_header = f"SELECT COALESCE(SUM(total_amount), 0) as sales FROM invoices WHERE store_id = %s AND status = 'Completed' {date_filter_inv}"
            query_cogs_items = f"""
            SELECT 
                COALESCE(SUM(ii.quantity * COALESCE(NULLIF(ii.buy_price, 0), p.buy_price, 0)), 0) as cogs
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            JOIN invoices i ON ii.invoice_id = i.id
            WHERE i.store_id = %s AND i.status = 'Completed' {date_filter_inv.replace('invoice_date', 'i.invoice_date')}
            """
            
            # Execute Sales Header Query
            p_sales = [store_id]
            if start_date and end_date:
                p_sales.extend([start_date, end_date])
                
            self.cursor.execute(query_sales_header, p_sales)
            res_header = self.cursor.fetchone()
            if res_header:
                report['total_sales'] = float(res_header['sales'])
                
            # Execute COGS Query
            self.cursor.execute(query_cogs_items, p_sales)
            res_cogs = self.cursor.fetchone()
            if res_cogs:
                report['total_cogs'] = float(res_cogs['cogs'])
                
            # 2. Total Returns (Separate Header and Cost)
            query_returns_header = f"SELECT COALESCE(SUM(total_return_amount), 0) as returns FROM sales_returns WHERE store_id = %s {date_filter_ret}"
            query_returns_cost = f"""
            SELECT 
                COALESCE(SUM(ri.quantity * COALESCE(NULLIF(ri.buy_price, 0), p.buy_price, 0)), 0) as cost_returns
            FROM sales_returns sr
            JOIN return_items ri ON sr.id = ri.return_id
            JOIN products p ON ri.product_id = p.id
            WHERE sr.store_id = %s {date_filter_ret.replace('return_date', 'DATE(sr.return_date)') if 'DATE' in date_filter_ret else date_filter_ret.replace('return_date', 'sr.return_date')}
            """
            
            p_ret = [store_id]
            if start_date and end_date:
                p_ret.extend([start_date, end_date])
                
            self.cursor.execute(query_returns_header, p_ret)
            res_rh = self.cursor.fetchone()
            if res_rh:
                report['total_returns'] = float(res_rh['returns'])
                
            self.cursor.execute(query_returns_cost, p_ret)
            res_rc = self.cursor.fetchone()
            if res_rc:
                report['cost_of_returns'] = float(res_rc['cost_returns'])
                
            # 3. Total Expenses (Separated)
            query_expenses = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN is_personal = 0 THEN amount ELSE 0 END), 0) as operational,
                COALESCE(SUM(CASE WHEN is_personal = 1 THEN amount ELSE 0 END), 0) as personal
            FROM expenses
            WHERE store_id = %s {date_filter_exp}
            """
            p_exp = [store_id]
            if start_date and end_date:
                p_exp.extend([start_date, end_date])
                
            self.cursor.execute(query_expenses, p_exp)
            res_exp = self.cursor.fetchone()
            if res_exp:
                report['total_expenses'] = float(res_exp['operational']) # Operational only
                report['personal_expenses'] = float(res_exp['personal'])
            else:
                report['total_expenses'] = 0.0
                report['personal_expenses'] = 0.0
                
            # 4. Calculate Net Profit (Operational)
            # Net Sales = Sales - Returns
            net_sales = report['total_sales'] - report['total_returns']
            
            # Net Cost = COGS - Cost of Returns
            net_cost = report['total_cogs'] - report['cost_of_returns']
            
            # Gross Profit = Net Sales - Net Cost
            gross_profit = net_sales - net_cost
            
            # Net Operational Profit
            report['net_profit'] = gross_profit - report['total_expenses']
            
            # 5. Net Profit (Cash Flow / Pocket)
            # This is what remains in pocket after personal withdrawals
            report['net_cash'] = report['net_profit'] - report['personal_expenses']
            
            if self._verbose_diagnostics:
                logger.info(
                    "FINANCIAL DIAGNOSTICS | store=%s | period=%s..%s | sales=%.2f | cogs=%.2f | returns=%.2f | expenses=%.2f | net_profit=%.2f | net_cash=%.2f",
                    store_id if store_id is not None else 'ALL',
                    start_date,
                    end_date,
                    float(report.get('total_sales', 0) or 0),
                    float(report.get('total_cogs', 0) or 0),
                    float(report.get('total_returns', 0) or 0),
                    float(report.get('total_expenses', 0) or 0),
                    float(report.get('net_profit', 0) or 0),
                    float(report.get('net_cash', 0) or 0),
                )

            return report
            
        except mysql.connector.Error as err:
            print(f"❌ Error compiling financial report: {err}")
            return {}

    # ==================== إدارة المصروفات ====================
    
    def get_categories(self) -> List[Dict]:
        """جلب كافة فئات المنتجات"""
        try:
            self.cursor.execute("SELECT * FROM categories ORDER BY category_name ASC")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ Error fetching categories: {err}")
            return []

    def add_category(self, name: str) -> bool:
        """إضافة فئة جديدة"""
        try:
            self.cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (name,))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error adding category: {err}")
            return False

    def update_category(self, category_id: int, new_name: str) -> bool:
        """تحديث اسم الفئة"""
        try:
            self.cursor.execute("UPDATE categories SET category_name = %s WHERE id = %s", (new_name, category_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error updating category: {err}")
            return False

    def delete_category(self, category_id: int) -> Tuple[bool, str]:
        """حذف فئة بشرط عدم وجود مبيعات أو مخزون"""
        try:
            # التحقق من وجود مخزون
            self.cursor.execute("SELECT COUNT(*) as count FROM products WHERE category_id = %s AND is_active = TRUE", (category_id,))
            res = self.cursor.fetchone()
            if res and res['count'] > 0:
                return False, f"لا يمكن حذف الفئة لوجود {res['count']} منتج مرتبطة بها. يجب حذف المنتجات أولاً."
            
            self.cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            self.conn.commit()
            return True, "تم حذف الفئة بنجاح"
        except mysql.connector.Error as err:
            print(f"❌ Error deleting category: {err}")
            return False, f"خطأ في قاعدة البيانات: {err}"

    def delete_store(self, store_id: int) -> Tuple[bool, str]:
        """حذف فرع بشرط عدم وجود مبيعات أو مخزون"""
        try:
            # التحقق من وجود مخزون
            self.cursor.execute("SELECT COUNT(*) as count FROM invoices WHERE store_id = %s", (store_id,))
            res = self.cursor.fetchone()
            if res and res['count'] > 0:
                return False, f"لا يمكن حذف الفرع لوجود {res['count']} فاتورة مرتبطة به. قم بتصفية المخزون أولاً."
            
            # التحقق من وجود مخزون
            self.cursor.execute("SELECT COUNT(*) as count FROM product_inventory WHERE store_id = %s AND quantity_in_stock > 0", (store_id,))
            res = self.cursor.fetchone()
            if res and res['count'] > 0:
                return False, f"لا يمكن حذف الفرع لوجود {res['count']} صنف في المخزون. قم بتصفية المخزون أولاً."
            
            # حذف الفرع
            self.cursor.execute("DELETE FROM stores WHERE id = %s", (store_id,))
            self.conn.commit()
            return True, "تم حذف الفرع بنجاح"
        except mysql.connector.Error as err:
            if err.errno == 1451: # Foreign key constraint
                return False, "لا يمكن حذف الفرع لارتباطه بسجلات أخرى (مثل المستخدمين أو الأجهزة)"
            print(f"❌ Error deleting store: {err}")
            return False, f"خطأ في قاعدة البيانات: {err}"


    # ==================== المشتريات (Purchases) ====================

    def create_purchases_tables(self):
        """إنشاء جداول المشتريات والموردين"""
        try:
            # 1. جدول الموردين
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                address TEXT,
                tax_number VARCHAR(50),
                opening_balance DECIMAL(10, 2) DEFAULT 0,
                current_balance DECIMAL(10, 2) DEFAULT 0,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # 2. جدول فواتير الشراء
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_number VARCHAR(50),
                ref_number VARCHAR(50),
                supplier_id INT,
                invoice_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) DEFAULT 0,
                subtotal DECIMAL(10, 2) DEFAULT 0,
                tax_amount DECIMAL(10, 2) DEFAULT 0,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                payment_method VARCHAR(50) DEFAULT 'Cash',
                payment_status VARCHAR(50) DEFAULT 'paid',
                paid_amount DECIMAL(10, 2) DEFAULT 0,
                remaining_amount DECIMAL(10, 2) DEFAULT 0,
                status VARCHAR(50) DEFAULT 'completed',
                notes TEXT,
                created_by INT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # 3. جدول بنود الفاتورة
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_id INT,
                product_id INT,
                quantity INT,
                unit_price DECIMAL(10, 2),
                buy_price DECIMAL(10, 2) DEFAULT 0,
                discount DECIMAL(10, 2) DEFAULT 0,
                total_price DECIMAL(10, 2),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            # Ensure buy_price exists in invoice_items
            try:
                self.cursor.execute("ALTER TABLE invoice_items ADD COLUMN buy_price DECIMAL(10, 2) DEFAULT 0")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            # 3. جدول بنود الشراء
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_id INT,
                product_id INT,
                quantity INT NOT NULL,
                unit_cost DECIMAL(10, 2) NOT NULL,
                total_cost DECIMAL(10, 2) NOT NULL,
                tax_percent DECIMAL(5, 2) DEFAULT 0,
                discount_value DECIMAL(10, 2) DEFAULT 0,
                expiry_date DATE NULL,
                FOREIGN KEY (invoice_id) REFERENCES purchase_invoices(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            # Ensure supplier_id exists in products
            try:
                self.cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INT AFTER category_id")
                self.cursor.execute("ALTER TABLE products ADD CONSTRAINT fk_product_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id)")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            self.conn.commit()
            logger.info("✅ جداول المشتريات جاهزة")
        except mysql.connector.Error as err:
            logger.error(f"❌ خطأ في جداول المشتريات: {err}")

    def add_supplier(self, name: str, phone: str = None, address: str = None, 
                     tax_number: str = None, opening_balance: float = 0.0) -> bool:
        """إضافة مورد جديد"""
        try:
            query = """INSERT INTO suppliers 
                       (name, phone, address, tax_number, opening_balance, current_balance) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (name, phone, address, tax_number, opening_balance, opening_balance))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ خطأ إضافة مورد: {err}")
            return False

    def get_all_suppliers(self) -> List[Dict]:
        """جلب قائمة الموردين النشطين"""
        try:
            self.cursor.execute("SELECT * FROM suppliers WHERE is_active = TRUE ORDER BY id DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ جلب الموردين: {err}")
            return []

    def create_purchase_invoice(self, supplier_id: int, total_amount: float, items: List[Dict], user_id: int, 
                               notes: str = "", ref_number: str = "", payment_method: str = "Cash", 
                               paid_amount: float = 0.0, subtotal: float = 0.0, 
                               tax_amount: float = 0.0, discount_amount: float = 0.0) -> Optional[int]:
        """إنشاء فاتورة شراء وتحديث المخزون ومتوسط التكلفة - يرجع رقم الفاتورة في السجل المالي للمورد والتاريخ"""
        try:
            remaining = total_amount - paid_amount
            status = 'paid' if remaining <= 0 else 'partial' if paid_amount > 0 else 'unpaid'
            user_id = self._get_valid_user_id(user_id)
            
            # 1. إنشاء الفاتورة
            logger.debug("Inserting invoice for supplier %s", supplier_id)
            inv_query = """
                INSERT INTO purchase_invoices (supplier_id, total_amount, paid_amount, remaining_amount, 
                                             subtotal, tax_amount, discount_amount, payment_method, 
                                             payment_status, ref_number, created_by, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(inv_query, (supplier_id, total_amount, paid_amount, remaining,
                                          subtotal, tax_amount, discount_amount, payment_method,
                                          status, ref_number, user_id, notes))
            invoice_id = self.cursor.lastrowid
            
            # Queue for sync (Now including items)
            self._queue_sync('purchase_invoices', invoice_id, 'INSERT', {
                'supplier_id': supplier_id, 'total_amount': total_amount, 'paid_amount': paid_amount, 'remaining_amount': remaining,
                'subtotal': subtotal, 'tax_amount': tax_amount, 'discount_amount': discount_amount, 'payment_method': payment_method,
                'payment_status': status, 'ref_number': ref_number, 'created_by': user_id, 'notes': notes,
                'items': items # Include items for cloud replay
            })
            
            logger.debug("Invoice created with ID: %s", invoice_id)

            # 2. تحديث رصيد الموردين والموردين
            if remaining > 0:
                self.cursor.execute("UPDATE suppliers SET current_balance = current_balance + %s WHERE id = %s", 
                                  (remaining, supplier_id))

            # 3. بنود الفاتورة وتحديث المخزون ومتوسط التكلفة
            item_query = """
                INSERT INTO purchase_items (invoice_id, product_id, quantity, unit_cost, total_cost, 
                                          expiry_date, tax_percent, discount_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # جلب معرف المخزن
            user_store_query = "SELECT store_id FROM users WHERE id = %s"
            self.cursor.execute(user_store_query, (user_id,))
            res = self.cursor.fetchone()
            store_id = res['store_id'] if res and res['store_id'] else 1

            # Fetch supplier name and actual invoice date once
            # Fetch supplier name
            self.cursor.execute("SELECT name FROM suppliers WHERE id = %s", (supplier_id,))
            supplier_res = self.cursor.fetchone()
            supplier_name = supplier_res['name'] if supplier_res else "Unknown Supplier"
            
            # Fetch actual invoice date (as it defaults to CURRENT_TIMESTAMP)
            self.cursor.execute("SELECT invoice_date FROM purchase_invoices WHERE id = %s", (invoice_id,))
            invoice_date_res = self.cursor.fetchone()
            # Extract only the date part
            actual_invoice_date = invoice_date_res['invoice_date'].date() if invoice_date_res and invoice_date_res['invoice_date'] else None
            
            for item in items:
                pid = item['product_id']
                qty = item['quantity']
                cost = item['cost']
                total = item['total']
                expiry = item.get('expiry_date')
                
                # إدراج بند الفاتورة
                self.cursor.execute(item_query, (invoice_id, pid, qty, cost, total, expiry, 0, 0))
                
                # --- WAC Calculation ---
                # Get current stock and cost
                self.cursor.execute("SELECT buy_price FROM products WHERE id = %s", (pid,))
                curr_prod = self.cursor.fetchone()
                old_cost = float(curr_prod['buy_price']) if curr_prod else 0.0
                
                # Get total current quantity across all stores (simplified WAC) OR specific store?
                # Usually WAC is global or per store. Let's do Global WAC for simplicity or Store-based.
                # Assuming Global Price in `products` table:
                stock_res = self.get_product_total_stock(pid) # Need to implement or use query
                old_qty = 0
                if stock_res: # stock_res might be int or dict depending on implementation
                     # Let's do a direct query to be safe
                     self.cursor.execute("SELECT SUM(quantity_in_stock) as qty FROM product_inventory WHERE product_id = %s", (pid,))
                     q_res = self.cursor.fetchone()
                     old_qty = float(q_res['qty']) if q_res and q_res['qty'] else 0.0
                
                new_qty_total = old_qty + qty
                if new_qty_total > 0:
                    new_wac_cost = ((old_qty * old_cost) + (qty * cost)) / new_qty_total
                else:
                    new_wac_cost = cost
                
                # Update Inventory
                self.update_inventory(pid, store_id, qty, operation='add')
                
                # Update Product Cost (Buy Price) & Sell Price if provided
                new_sell_price = item.get('new_sell_price')
                if new_sell_price and float(new_sell_price) > 0:
                    self.update_product_price(pid, new_buy_price=new_wac_cost, new_sell_price=float(new_sell_price), changed_by=user_id, notes="شراء - تحديث تكلفة وسعر بيع")
                else:
                    self.update_product_price(pid, new_buy_price=new_wac_cost, changed_by=user_id, notes="متوسط تكلفة شراء")
                    
                # Update last supplier and purchase date
                self.update_product_purchase_info(pid, supplier_name, actual_invoice_date) 

            self.conn.commit()
            
            # Record Treasury Out if paid
            if paid_amount > 0:
                self.record_treasury_transaction(
                    store_id=store_id,
                    trans_type='Out',
                    amount=paid_amount,
                    source='Purchase',
                    ref_id=invoice_id,
                    desc=f"شراء بضاعة - فاتورة رقم {invoice_number}",
                    user_id=user_id
                )
                # سجل المبلغ المدفوع فوراً في السجل المالي للمورد (Credit = Cash Out)
                self.cursor.execute("""
                    INSERT INTO financial_ledger 
                        (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                    VALUES ('Supplier', %s, 'Credit', %s, 'Payment', %s, %s, %s)
                """, (supplier_id, paid_amount,
                      invoice_id, f"مديونية آجلة - فاتورة شراء #{ref_number or invoice_id}",
                      user_id))
                self.conn.commit()

            # سجل المبلغ المدفوع فوراً في السجل المالي (Debit = Increasing Debt)
            if remaining > 0:
                self.cursor.execute("""
                    INSERT INTO financial_ledger 
                        (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                    VALUES ('Supplier', %s, 'Debit', %s, 'Purchase', %s, %s, %s)
                """, (supplier_id, remaining,
                      invoice_id, f"مديونية آجلة - فاتورة شراء #{ref_number or invoice_id}",
                      user_id))
                self.conn.commit()
            
            return invoice_id
            
        except mysql.connector.Error as err:
            logger.error("Create purchase invoice failed: %s", err, exc_info=True)
            self.conn.rollback()
            return False
        except (TypeError, ValueError) as e:
            logger.error("Unexpected data error while creating purchase invoice: %s", e, exc_info=True)
            self.conn.rollback()
            return False

    def update_product_purchase_info(self, product_id, supplier_name, purchase_date):
        """Updates the product with the last supplier and purchase date."""
        try:
            # Check if columns exist (Quick & Dirty Check, ideally do this in migration/setup)
            # But since we are patching dynamically:
            try:
                self.cursor.execute("SELECT last_supplier FROM products LIMIT 1")
            except mysql.connector.Error:
                # Add columns if not exist
                logger.debug("Adding last_supplier and last_purchase_date columns to products table...")
                self.cursor.execute("ALTER TABLE products ADD COLUMN last_supplier VARCHAR(255) NULL")
                self.cursor.execute("ALTER TABLE products ADD COLUMN last_purchase_date DATE NULL")
                # ALTER TABLE implicitly commits, so no self.conn.commit() needed here for the ALTER.
                # However, the subsequent UPDATE needs to be part of the main transaction.
            
            # Update the record
            query = "UPDATE products SET last_supplier = %s, last_purchase_date = %s WHERE id = %s"
            self.cursor.execute(query, (supplier_name, purchase_date, product_id))
            # No commit here. Transaction is managed by caller (create_purchase_invoice).
            
        except mysql.connector.Error as err:
            print(f"❌ Error updating product purchase info: {err}")
            # Do not rollback here, let the caller handle the transaction.
        except (TypeError, ValueError) as e:
            print(f"❌ Unexpected Error updating product purchase info: {e}")
            raise e

    def update_purchase_invoice_payment(self, invoice_id: int, amount: float, payment_method: str = 'Cash') -> bool:
        """Update purchase invoice payment and supplier balance."""
        try:
            # 1. Get current invoice details
            self.cursor.execute("SELECT supplier_id, total_amount, paid_amount, remaining_amount, payment_status, created_by FROM purchase_invoices WHERE id = %s", (invoice_id,))
            inv = self.cursor.fetchone()
            if not inv:
                return False

            current_paid = float(inv['paid_amount'])
            current_remaining = float(inv['remaining_amount'])
            supplier_id = inv['supplier_id']

            if amount > current_remaining:
                print(f"❌ Payment amount {amount} exceeds remaining {current_remaining}")
                return False

            new_paid = current_paid + amount
            new_remaining = current_remaining - amount

            # Determine new status
            if new_remaining <= 0:
                new_status = 'paid'
                new_remaining = 0 # Ensure no negative float precision issues
            else:
                new_status = 'partial'

            # 2. Update Invoice
            self.cursor.execute("""
                UPDATE purchase_invoices
                SET paid_amount = %s, remaining_amount = %s, payment_status = %s, payment_method = %s
                WHERE id = %s
            """, (new_paid, new_remaining, new_status, payment_method, invoice_id))

            # 3. Update Supplier Balance (Debit the supplier account)
            # If we pay the supplier, our debt (current_balance) decreases.
            if supplier_id:
                self.cursor.execute("UPDATE suppliers SET current_balance = current_balance - %s WHERE id = %s", (amount, supplier_id))
                
                # 4. Record in Financial Ledger for central tracking
                # We fetch the original creator, but fall back to a valid user if needed to avoid FK errors
                creator_id = self._get_valid_user_id(inv.get('created_by'))

                self.cursor.execute("""
                    INSERT INTO financial_ledger (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, ('Supplier', supplier_id, 'Credit', amount, 'Payment', invoice_id, f"Invoice #{invoice_id} Payment", creator_id))
                
                # 5. Sync with Treasury
                self.cursor.execute("SELECT store_id FROM users WHERE id = %s", (creator_id,))
                user_data = self.cursor.fetchone()
                store_id = user_data['store_id'] if user_data else 1
                
                # Using ENUMs: transaction_type('In','Out'), source_type('Sale','Purchase','Expense','Settlement','Adjustment','Return')
                self.record_treasury_transaction(
                    store_id, 'Out', amount, 'Settlement', self.cursor.lastrowid, 
                    f"Invoice #{invoice_id} Payment", creator_id
                )

            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"❌ Error updating purchase payment: {err}")
            print(f"❌ Error updating purchase payment: {err}")
            return False

    def get_purchase_invoices(self) -> List[Dict]:
        """جلب سجل فواتير الشراء"""
        try:
            query = """
                SELECT pi.*, s.name as supplier_name, u.name as user_name,
                       (SELECT COUNT(*) FROM purchase_items WHERE invoice_id = pi.id) as items_count
                FROM purchase_invoices pi
                LEFT JOIN suppliers s ON pi.supplier_id = s.id
                LEFT JOIN users u ON pi.created_by = u.id
                ORDER BY pi.invoice_date DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"❌ خطأ في جلب الفواتير: {err}")
            return []

    def get_product_total_stock(self, product_id: int) -> int:
        """احسب إجمالي المخزون لمنتج معين في جميع الفروع"""
        try:
            query = "SELECT SUM(quantity_in_stock) as total FROM product_inventory WHERE product_id = %s"
            self.cursor.execute(query, (product_id,))
            result = self.cursor.fetchone()
            if result and result['total'] is not None:
                return int(result['total'])
            return 0
        except mysql.connector.Error as err:
            print(f"❌ Error getting total stock: {err}")
            return 0

    # ==================== نظام الحسابات والعملاء ====================

    def setup_accounts_system(self):
        """تهيئة نظام الحسابات والعملاء المتقدم"""
        self.create_customers_table()
        self.create_ledger_table()
        self.create_treasury_table()
        self.migrate_customers_from_transactions()
        self.update_transaction_tables_with_customer_id()
        self.upgrade_accounts_schema()

    def upgrade_accounts_schema(self):
        """إضافة أعمدة ومميزات متقدمة للجداول الحالية"""
        try:
            # إضافة الحد الائتماني للعملاء
            try:
                self.cursor.execute("ALTER TABLE customers ADD COLUMN credit_limit DECIMAL(12, 2) DEFAULT 0 AFTER current_balance")
                self.cursor.execute("ALTER TABLE customers ADD COLUMN notes TEXT")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            # إضافة مسار المرفقات والتسويات للسجل
            try:
                self.cursor.execute("ALTER TABLE financial_ledger ADD COLUMN attachment_path VARCHAR(255) AFTER description")
                self.cursor.execute("ALTER TABLE financial_ledger ADD COLUMN is_settlement BOOLEAN DEFAULT FALSE")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            self.conn.commit()
        except mysql.connector.Error as e:
            logger.error("Upgrade schema failed: %s", e, exc_info=True)

    def create_treasury_table(self):
        """إنشاء جدول حركة الخزينة المركزية"""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS treasury (
                id INT PRIMARY KEY AUTO_INCREMENT,
                store_id INT,
                transaction_type ENUM('In', 'Out') NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                source_type ENUM('Sale', 'Purchase', 'Expense', 'Settlement', 'Adjustment', 'Return') NOT NULL,
                reference_id INT,
                description TEXT,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES stores(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            # Ensure ENUM is up to date for existing databases
            try:
                self.cursor.execute("ALTER TABLE treasury MODIFY COLUMN source_type ENUM('Sale','Purchase','Expense','Settlement','Adjustment','Return') NOT NULL")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            self.conn.commit()
            logger.info("جدول الخزينة جاهز")
        except mysql.connector.Error as err:
            logger.error("خطأ في إنشاء جدول الخزينة: %s", err, exc_info=True)

    def create_customers_table(self):
        """إنشاء جدول العملاء المركزية"""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(150) NOT NULL,
                phone VARCHAR(20) UNIQUE,
                address TEXT,
                email VARCHAR(100),
                current_balance DECIMAL(12, 2) DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            self.conn.commit()
            logger.info("جدول العملاء جاهز")
        except mysql.connector.Error as err:
            logger.error("خطأ في إنشاء جدول العملاء: %s", err, exc_info=True)

    def create_ledger_table(self):
        """إنشاء سجل العمليات المالية (دفتر الأستاذ)"""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_ledger (
                id INT PRIMARY KEY AUTO_INCREMENT,
                account_type ENUM('Customer', 'Supplier', 'System') NOT NULL,
                account_id INT,
                transaction_type ENUM('Credit', 'Debit') NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reference_type ENUM('Invoice', 'Purchase', 'Payment', 'Return', 'Expense') NOT NULL,
                reference_id INT,
                description TEXT,
                created_by INT,
                FOREIGN KEY (created_by) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            self.conn.commit()
            logger.info("سجل العمليات المالية جاهز")
        except mysql.connector.Error as err:
            logger.error("خطأ في إنشاء سجل العمليات المالية: %s", err, exc_info=True)

    def migrate_customers_from_transactions(self):
        """ترحيل بيانات العملاء من الفواتير والطلبات السابقة"""
        try:
            # 1. جلب العملاء من الفواتير
            self.cursor.execute("SELECT DISTINCT customer_name, customer_phone, customer_address FROM invoices WHERE customer_phone IS NOT NULL AND customer_name IS NOT NULL")
            inv_cust = self.cursor.fetchall()
            
            # 2. جلب العملاء من الطلبات
            self.cursor.execute("SELECT DISTINCT customer_name, customer_phone, customer_address FROM orders WHERE customer_phone IS NOT NULL AND customer_name IS NOT NULL")
            ord_cust = self.cursor.fetchall()
            
            all_cust = {}
            for c in inv_cust:
                p = str(c['customer_phone']).strip()
                if p and p not in all_cust: all_cust[p] = c
            for c in ord_cust:
                p = str(c['customer_phone']).strip()
                if p and p not in all_cust: all_cust[p] = c
                
            for phone, data in all_cust.items():
                self.cursor.execute("""
                    INSERT IGNORE INTO customers (name, phone, address)
                    VALUES (%s, %s, %s)
                """, (data['customer_name'], phone, data['customer_address']))
            
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Migration Error: {err}")
            return False

    def update_transaction_tables_with_customer_id(self):
        """ربط الفواتير والطلبات بجدول العملاء"""
        try:
            # إضافة العمود للفواتير
            try:
                self.cursor.execute("ALTER TABLE invoices ADD COLUMN customer_id INT AFTER cashier_id")
                self.cursor.execute("ALTER TABLE invoices ADD CONSTRAINT fk_inv_cust FOREIGN KEY (customer_id) REFERENCES customers(id)")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            # إضافة العمود للطلبات
            try:
                self.cursor.execute("ALTER TABLE orders ADD COLUMN customer_id INT AFTER customer_city")
                self.cursor.execute("ALTER TABLE orders ADD CONSTRAINT fk_ord_cust FOREIGN KEY (customer_id) REFERENCES customers(id)")
            except mysql.connector.Error as e:
                self._handle_non_critical_db_error(e)
            # تحديث الربط
            self.cursor.execute("UPDATE invoices i JOIN customers c ON i.customer_phone = c.phone SET i.customer_id = c.id WHERE i.customer_id IS NULL")
            self.cursor.execute("UPDATE orders o JOIN customers c ON o.customer_phone = c.phone SET o.customer_id = c.id WHERE o.customer_id IS NULL")
            
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"❌ Link Error: {err}")

    def get_customer_accounts(self) -> List[Dict]:
        """جلب ٣رصدة كافة العملاء"""
        try:
            self.cursor.execute("SELECT * FROM customers WHERE is_active = TRUE ORDER BY current_balance DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error("DB query failed: %s", e, exc_info=True)
            return []
    def record_payment(self, account_type: str, account_id: int, amount: float, user_id: int, desc: str = "") -> bool:
        """تسجيل عملية دفع أو تحصيل وتحديث الرصيد"""
        try:
            # 1. تحديث الرصيد
            if account_type == 'Customer':
                # العميل يدفع لنا -> يقل حسابه المدين
                self.cursor.execute("UPDATE customers SET current_balance = current_balance - %s WHERE id = %s", (amount, account_id))
                ref_type = 'Payment'
                trans_type = 'Debit' # Debit our cash, decrease their credit
            elif account_type == 'Supplier':
                # نحن ندفع للمورد -> يقل حسابه الدائن لنا
                self.cursor.execute("UPDATE suppliers SET current_balance = current_balance - %s WHERE id = %s", (amount, account_id))
                ref_type = 'Payment'
                trans_type = 'Credit'
                
                # --- NEW: Allocate payment to individual purchase invoices (FIFO) ---
                remaining_to_allocate = amount
                self.cursor.execute("""
                    SELECT id, remaining_amount, paid_amount 
                    FROM purchase_invoices 
                    WHERE supplier_id = %s AND payment_status != 'paid' 
                    ORDER BY invoice_date ASC, id ASC
                """, (account_id,))
                
                open_invoices = self.cursor.fetchall()
                for inv in open_invoices:
                    if remaining_to_allocate <= 0: break
                    
                    inv_id = inv['id']
                    inv_rem = float(inv['remaining_amount'])
                    inv_paid = float(inv['paid_amount'])
                    
                    allocate = min(remaining_to_allocate, inv_rem)
                    new_inv_paid = inv_paid + allocate
                    new_inv_rem = inv_rem - allocate
                    new_status = 'paid' if new_inv_rem <= 0 else 'partial'
                    
                    self.cursor.execute("""
                        UPDATE purchase_invoices 
                        SET paid_amount = %s, remaining_amount = %s, payment_status = %s 
                        WHERE id = %s
                    """, (new_inv_paid, new_inv_rem, new_status, inv_id))
                    
                    remaining_to_allocate -= allocate

            # 2. التسجيل في السجل المالي كوسيلة تسوية
            user_id = self._get_valid_user_id(user_id)
            self.cursor.execute("""
                INSERT INTO financial_ledger (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                VALUES (%s, %s, %s, %s, %s, NULL, %s, %s)
            """, (account_type, account_id, trans_type, amount, ref_type, desc, user_id))
            ledger_id = self.cursor.lastrowid

            # 3. مزامنة مع الخزينة
            self.cursor.execute("SELECT store_id FROM users WHERE id = %s", (user_id,))
            user_data = self.cursor.fetchone()
            store_id = user_data['store_id'] if user_data else 1
            
            # Using ENUMs: transaction_type('In','Out'), source_type('Sale','Purchase','Expense','Settlement','Adjustment')
            treasury_type = 'In' if trans_type == 'Debit' else 'Out'
            source = 'Settlement'
            
            self.record_treasury_transaction(
                store_id, treasury_type, amount, source, ledger_id, 
                f"{desc} ({account_type} #{account_id})", user_id
            )
            
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            logger.error("Record payment failed: %s", e, exc_info=True)
            self.conn.rollback()
            return False

    def get_account_history(self, account_type: str, account_id: int) -> List[Dict]:
        """جلب كشف حساب لعميل أو مورد"""
        try:
            query = """
                SELECT * FROM financial_ledger 
                WHERE account_type = %s AND account_id = %s 
                ORDER BY transaction_date DESC
            """
            self.cursor.execute(query, (account_type, account_id))
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error("DB query failed: %s", e, exc_info=True)
            return []
    def _get_or_create_customer(self, name, phone, address):
        """Helper to get existing customer ID or create a new one"""
        # If both name and phone are empty, we handle it as a default anonymous customer
        if not phone and (not name or name in ["عميل نقدي", "Cash Customer", "-"]):
            # Try to find a default "Cash Customer" record
            self.cursor.execute("SELECT id FROM customers WHERE name = 'عميل نقدي' LIMIT 1")
            res = self.cursor.fetchone()
            if res: return res['id']
            
            # Create a default "Cash Customer" record if it doesn't exist
            self.cursor.execute("INSERT INTO customers (name, phone) VALUES ('عميل نقدي', '0000000000')")
            self.conn.commit()
            return self.cursor.lastrowid

        try:
            # If phone is provided, it's our primary key for lookup
            if phone:
                self.cursor.execute("SELECT id FROM customers WHERE phone = %s", (phone,))
                res = self.cursor.fetchone()
                if res: return res['id']
            
            # Otherwise, use name as fallback if phone is missing
            elif name:
                self.cursor.execute("SELECT id FROM customers WHERE name = %s AND (phone IS NULL OR phone = '')", (name,))
                res = self.cursor.fetchone()
                if res: return res['id']

            # Create new record if not found
            final_name = name if name else "عميل نقدي"
            self.cursor.execute("INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)", 
                               (final_name, phone if phone else None, address))
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as e:
            logger.error("Get or create customer failed: %s", e, exc_info=True)
            return None

    def finalize_invoice(self, invoice_number: str, user_id: int) -> bool:
        """لحساب الديون على العميل وتسجيلها في السجل المالي"""
        try:
            # 1. جلب بيانات الفاتورة
            self.cursor.execute("""
                SELECT id, customer_id, total_amount, (cash_amount + card_amount) as total_paid 
                FROM invoices WHERE invoice_number = %s
            """, (invoice_number,))
            inv = self.cursor.fetchone()
            if not inv or not inv['customer_id']: return True # لا يوجد عميل أو لم يتم ربطه

            total = float(inv['total_amount'])
            paid = float(inv['total_paid'])
            debt = total - paid

            if debt > 0:
                # تحديث رصيد العميل (زيادة المديونية)
                self.cursor.execute("UPDATE customers SET current_balance = current_balance + %s WHERE id = %s", (debt, inv['customer_id']))
                
                # التسجيل في السجل المالي
                user_id = self._get_valid_user_id(user_id)
                self.cursor.execute("""
                    INSERT INTO financial_ledger (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by)
                    VALUES ('Customer', %s, 'Credit', %s, 'Invoice', %s, %s, %s)
                """, (inv['customer_id'], debt, inv['id'], f"مديونية فاتورة رقم {invoice_number}", user_id))
            
            # Queue for sync
            self._queue_sync('invoices_finalize', inv['id'], 'FINALIZE', {
                'invoice_number': invoice_number, 'user_id': user_id
            })
            
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            logger.error("Finalize invoice failed: %s", e, exc_info=True)
            return False

    def check_credit_limit(self, customer_id: int, additional_amount: float) -> Tuple[bool, str]:
        """التحقق من تجاوز الحد الائتماني للعميل"""
        try:
            self.cursor.execute("SELECT name, current_balance, credit_limit FROM customers WHERE id = %s", (customer_id,))
            res = self.cursor.fetchone()
            if not res or float(res['credit_limit']) <= 0:
                return True, "" # لا يوجد حد ائتماني أو لم يتم ربطه

            new_total = float(res['current_balance']) + additional_amount
            limit = float(res['credit_limit'])
            
            if new_total > limit:
                return False, f"⚠️ العميل '{res['name']}' تجاوز الحد الائتماني المسموح به ({limit:,.2f} ج.م). الرصيد الحالي: {res['current_balance']:,.2f}"
            
            return True, ""
        except (mysql.connector.Error, ValueError, TypeError, KeyError) as e:
            logger.warning("Credit limit check failed, allowing operation by fallback: %s", e)
            return True, ""
    def record_treasury_transaction(self, store_id, trans_type, amount, source, ref_id, desc, user_id):
        """تسجيل حركة في الخزينة"""
        try:
            user_id = self._get_valid_user_id(user_id)
            self.cursor.execute("""
                INSERT INTO treasury (store_id, transaction_type, amount, source_type, reference_id, description, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (store_id, trans_type, amount, source, ref_id, desc, user_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            logger.error("Treasury transaction failed: %s", e, exc_info=True)
            return False

    def get_debt_aging_report(self):
        """تقرير أعمدة الديون (تقادم الديون)"""
        try:
            # تبسيط: جلب العملاء الذين لديهم رصيد مدين وتصنيفهم بناءً على تاريخ آخر فاتورة لم تسدد بالكامل
            query = """
                SELECT c.name, c.current_balance, 
                    DATEDIFF(NOW(), MAX(i.invoice_date)) as days_since_last_sale
                FROM customers c
                JOIN invoices i ON c.id = i.customer_id
                WHERE c.current_balance > 0
                GROUP BY c.id
                ORDER BY days_since_last_sale DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error("DB query failed: %s", e, exc_info=True)
            return []
    def record_settlement(self, account_type, account_id, amount, desc, user_id):
        """تسجيل تسوية ديون (إعدام دين أو خصم تسوية)"""
        try:
            # 1. تحديث رصيد الحساب (تقليل المديونية)
            table = 'customers' if account_type == 'Customer' else 'suppliers'
            self.cursor.execute(f"UPDATE {table} SET current_balance = current_balance - %s WHERE id = %s", (amount, account_id))
            
            # 2. التسجيل في السجل المالي كوسيلة تسوية
            user_id = self._get_valid_user_id(user_id)
            self.cursor.execute("""
                INSERT INTO financial_ledger (account_type, account_id, transaction_type, amount, reference_type, reference_id, description, created_by, is_settlement)
                VALUES (%s, %s, 'Debit', %s, 'Adjustment', NULL, %s, %s, TRUE)
            """, (account_type, account_id, amount, desc, user_id))
            
            # Queue for sync
            self._queue_sync('settlements', account_id, 'INSERT', {
                'account_type': account_type, 'account_id': account_id, 'amount': amount, 'description': desc, 'user_id': user_id
            })
            
            self.conn.commit()
            return True
        except mysql.connector.Error as e:
            self.conn.rollback()
            return False

if __name__ == "__main__":
    db = DatabaseManager()
    db.close()






