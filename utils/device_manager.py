"""
Device Manager - إدارة معرّفات الأجهزة والتحقق من الموقع
"""

import socket
import uuid
import platform
from typing import Optional, Dict

class DeviceManager:
    """فئة لإدارة معرّفات الأجهزة والتحقق من الموقع"""
    
    @staticmethod
    def get_mac_address() -> str:
        """الحصول على MAC Address للجهاز"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])
            return mac
        except:
            return "00:00:00:00:00:00"
    
    @staticmethod
    def get_device_name() -> str:
        """الحصول على اسم الجهاز"""
        try:
            return platform.node()
        except:
            return "Unknown"
    
    @staticmethod
    def get_stable_id() -> str:
        """الحصول على معرّف عتادي ثابت (Serial Number/UUID)"""
        import subprocess
        try:
            if platform.system() == "Windows":
                # المحاولة الأولى: رقم اللوحة الأم / BIOS
                try:
                    cmd = "wmic bios get serialnumber"
                    res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().split()
                    if len(res) >= 2 and res[1] and res[1].strip() and res[1].lower() != "to be filled by o.e.m.":
                        return f"HW_{res[1].strip()}"
                except:
                    pass
                
                # المحاولة الثانية: UUID النظام
                try:
                    cmd = "wmic csproduct get uuid"
                    res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().split()
                    if len(res) >= 2 and res[1] and res[1].strip():
                        return f"UUID_{res[1].strip()}"
                except:
                    pass
            
            # المحاولة الثالثة: MAC Address كحل أخير
            return f"MAC_{DeviceManager.get_mac_address()}"
        except:
            return f"NODE_{uuid.getnode()}"

    @staticmethod
    def get_device_id() -> str:
        """الحصول على معرّف فريد وثابت للجهاز"""
        stable_id = DeviceManager.get_stable_id()
        name = DeviceManager.get_device_name()
        return f"{stable_id}_{name}"
    
    @staticmethod
    def get_local_ip() -> str:
        """الحصول على عنوان IP المحلي للجهاز"""
        try:
            # Create a socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_device_info() -> Dict[str, str]:
        """الحصول على معلومات كاملة عن الجهاز"""
        return {
            'device_id': DeviceManager.get_device_id(),
            'mac_address': DeviceManager.get_mac_address(),
            'device_name': DeviceManager.get_device_name(),
            'ip_address': DeviceManager.get_local_ip(),
            'os': platform.system(),
            'os_version': platform.version()
        }
    
    @staticmethod
    def ip_in_range(ip: str, range_start: str, range_end: str) -> bool:
        """التحقق من أن IP ضمن نطاق معين"""
        try:
            # Convert IP addresses to integers for comparison
            def ip_to_int(ip_str):
                parts = ip_str.split('.')
                return (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
                       (int(parts[2]) << 8) + int(parts[3])
            
            ip_int = ip_to_int(ip)
            start_int = ip_to_int(range_start)
            end_int = ip_to_int(range_end)
            
            return start_int <= ip_int <= end_int
        except:
            return False
    
    @staticmethod
    def is_local_network(ip: str) -> bool:
        """التحقق من أن IP ضمن الشبكة المحلية"""
        try:
            parts = ip.split('.')
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            # Check for private IP ranges
            # 10.0.0.0 - 10.255.255.255
            if first_octet == 10:
                return True
            # 172.16.0.0 - 172.31.255.255
            if first_octet == 172 and 16 <= second_octet <= 31:
                return True
            # 192.168.0.0 - 192.168.255.255
            if first_octet == 192 and second_octet == 168:
                return True
            
            return False
        except:
            return False
