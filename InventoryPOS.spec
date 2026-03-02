import mysql.connector
import barcode
import os

block_cipher = None
mysql_connector_path = os.path.dirname(mysql.connector.__file__)
barcode_path = os.path.dirname(barcode.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui', 'ui'), 
        ('utils', 'utils'), 
        ('icon.png', '.'),
        (os.path.join(mysql_connector_path, 'locales'), 'mysql/connector/locales'),
        (os.path.join(barcode_path, 'fonts'), 'barcode/fonts')
    ],
    hiddenimports=['barcode', 'barcode.writer', 'barcode.errors', 'PyQt6.QtPrintSupport',
                   'mysql.connector.plugins.mysql_native_password',
                   'mysql.connector.plugins.caching_sha2_password',
                   'mysql.connector.locales.eng.client_error'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InventoryPOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.png'],
)
