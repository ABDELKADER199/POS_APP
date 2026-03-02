"""
UI Package
واجهة التطبيق الرسومية
"""

from .login_page import LoginPage
from .dashboard_page import DashboardPage
from .admin_panel import AdminPanel
from .cashier_page import CashierPage
from .products_page import ProductsPage
from .call_center_page import CallCenterPage
from .drawer_page import DrawerPage

__all__ = [
    'LoginPage',
    'DashboardPage',
    'AdminPanel',
    'CashierPage',
    'ProductsPage',
    'CallCenterPage',
    'DrawerPage'
]
