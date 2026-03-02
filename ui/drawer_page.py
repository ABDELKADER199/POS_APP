from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QFrame, QInputDialog, QDialog,
                             QFormLayout, QDialogButtonBox, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QShortcut, QKeySequence
from database_manager import DatabaseManager
from ui.styles import GLOBAL_STYLE, COLORS

class ClosedDrawersDialog(QDialog):
    """Dialog to show history of closed drawers with print option"""
    def __init__(self, store_id, parent=None):
        super().__init__(parent)
        self.store_id = store_id
        self.db = DatabaseManager()
        self.setWindowTitle("سجل الأدراج المغلقة")
        self.setMinimumSize(900, 600)
        # Apply global style to dialog
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: #1F2937;
            }
            QLabel {
                color: white;
            }
        """)
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header Container
        header_layout = QHBoxLayout()
        
        icon_lbl = QLabel("🗄️")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 24))
        header_layout.addWidget(icon_lbl)
        
        # Title
        title = QLabel("سجل إغلاق الأدراج")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #F3F4F6;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # --- Filter Section ---
        filter_layout = QHBoxLayout()
        
        # Date Filters
        from PyQt6.QtWidgets import QDateEdit
        from PyQt6.QtCore import QDate
        
        filter_layout.addWidget(QLabel("📅 من:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("📅 إلى:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.date_to)
        
        # Search Box
        filter_layout.addSpacing(20)
        filter_layout.addWidget(QLabel("🔍 بحث:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اسم الكاشير...")
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        # Load Button
        reload_btn = QPushButton("🔄 تحديث البيانات")
        reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        reload_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(reload_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "الكاشير", "وقت الإغلاق", "الرصيد الفعلي", "الرصيد المتوقع", "العجز/الزيادة", "إجراءات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        # Premium Table Style
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #374151;
                border: 1px solid #4B5563;
                border-radius: 12px;
                gridline-color: transparent;
                color: white;
                selection-background-color: #3B82F6;
                selection-color: white;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #111827;
                color: #D1D5DB;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #4B5563;
            }
            QTableWidget::item:selected {
                background-color: #3B82F6;
                color: white;
            }
        """)
        layout.addWidget(self.table)
        
        # Close Button
        btn_close = QPushButton("إغلاق")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.setLayout(layout)
        
    def load_data(self):
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        
        # If the DB manager supports date filtering, we should use it.
        # For now, let's assume it fetches based on store_id and we can filter if needed,
        # but usually history needs date bounds.
        # Checking if get_closed_drawers_history supports dates
        try:
            drawers = self.db.get_closed_drawers_history(self.store_id, start_date, end_date)
        except TypeError:
            # Fallback if DB method doesn't support dates yet
            drawers = self.db.get_closed_drawers_history(self.store_id)
            
        self.table.setRowCount(len(drawers))
        
        for row, drawer in enumerate(drawers):
            # 0. ID
            item_id = QTableWidgetItem(str(drawer['id']))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_id)
            
            # 1. Cashier
            item_cashier = QTableWidgetItem(drawer['cashier_name'])
            item_cashier.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_cashier)
            
            # 2. Close Date
            close_date = str(drawer['closing_date'])
            # Format nicely if needed (e.g. drop seconds)
            item_close = QTableWidgetItem(close_date)
            item_close.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_close)
            
            # Calculations
            opening = float(drawer.get('opening_balance', 0))
            closing = float(drawer.get('closing_balance', 0))
            cash_sales = float(drawer.get('cash_sales', 0)) # From query
            returns = float(drawer.get('total_returns', 0)) # From query
            
            expected = opening + cash_sales - returns
            difference = closing - expected
            
            # 3. Actual Balance (Closing)
            item_actual = QTableWidgetItem(f"{closing:,.2f}")
            item_actual.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_actual.setForeground(QColor("#10B981")) # Green text for money
            self.table.setItem(row, 3, item_actual)
            
            # 4. Expected Balance
            item_expected = QTableWidgetItem(f"{expected:,.2f}")
            item_expected.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item_expected)
            
            # 5. Difference
            diff_text = f"{difference:,.2f}"
            if difference > 0:
                diff_text = f"+{difference:,.2f}"
            
            item_diff = QTableWidgetItem(diff_text)
            item_diff.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if difference < -0.01:
                item_diff.setForeground(QColor("#EF4444")) # Red for shortage
            elif difference > 0.01:
                item_diff.setForeground(QColor("#10B981")) # Green for overage
            else:
                item_diff.setForeground(QColor("#9CA3AF")) # Gray for exact
            
            self.table.setItem(row, 5, item_diff)
            
            # 6. Print Button Container
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_print = QPushButton("🖨️ طباعة")
            btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
            # Add explicit min-width and ensure color is white
            btn_print.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                    min-height: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            btn_print.clicked.connect(lambda checked, d_id=drawer['id']: self.print_drawer(d_id))
            
            btn_layout.addWidget(btn_print)
            self.table.setCellWidget(row, 6, btn_container)
            
    def filter_table(self):
        """تصفية الجدول محلياً حسب اسم الكاشير"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            cashier_item = self.table.item(row, 1) # Column 1 is Cashier
            if cashier_item:
                match = search_text in cashier_item.text().lower()
                self.table.setRowHidden(row, not match)

    def print_drawer(self, drawer_id):
        try:
            from utils.printer_service import PrinterService
            summary = self.db.get_drawer_summary(drawer_id)
            if summary:
                PrinterService.print_drawer_report(summary)
                QMessageBox.information(self, "نجاح", "تم إرسال أمر الطباعة بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "تعذر جلب بيانات الدرج")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")


class DrawerPage(QWidget):
    """صفحة إدارة الدرج النقدي (مبسطة)"""
    
    drawer_opened = pyqtSignal()
    drawer_closed = pyqtSignal()
    
    def __init__(self, user_info=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(GLOBAL_STYLE)
        self.db = DatabaseManager()
        self.user_info = user_info or {}
        self.init_ui()
        self.check_drawer_status()
        
        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_F2), self).activated.connect(self.open_drawer_click)
        QShortcut(QKeySequence(Qt.Key.Key_F12), self).activated.connect(self.close_drawer_click)
    
    def set_user(self, user_info):
        self.user_info = user_info or {}
        self.check_drawer_status()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("💰 إدارة الدرج النقدي")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status Card
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        status_layout = QVBoxLayout(self.status_card)
        
        lbl_status = QLabel("حالة الدرج الحالي")
        lbl_status.setStyleSheet("color: white; font-size: 14px;")
        status_layout.addWidget(lbl_status)
        
        self.status_label = QLabel("---")
        self.status_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(self.status_card)
        
        # Control Buttons Container
        buttons_layout = QHBoxLayout()
        
        # Open Drawer Button
        self.btn_open = QPushButton("🔓 فتح الدرج")
        self.btn_open.setStyleSheet(f"""
            QPushButton {{
                background-color: #10B981;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.clicked.connect(self.open_drawer_click)
        buttons_layout.addWidget(self.btn_open)
        
        # Close Drawer Button
        self.btn_close = QPushButton("🔒 إغلاق الدرج")
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: #EF4444;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close_drawer_click)
        buttons_layout.addWidget(self.btn_close)
        
        layout.addLayout(buttons_layout)
        
        # History Button (Replaces "Print Last")
        self.btn_history = QPushButton("🗄️ سجل الأدراج المغلقة")
        self.btn_history.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_history.clicked.connect(self.show_history_dialog)
        layout.addWidget(self.btn_history)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Initially hide buttons until status checked
        self.btn_open.hide()
        self.btn_close.hide()
        self.btn_history.hide() # Default hidden until permission checked
    
    def check_drawer_status(self):
        try:
            store_id = self.user_info.get('store_id')
            user_id = self.user_info.get('id')
            role_name = self.user_info.get('role_name', '').lower()
            
            # Check permissions for history button
            # Roles allowed: admin, manager, branch manager (English or Arabic)
            allowed_roles = ['admin', 'manager', 'branch manager', 'مدير', 'مدير عام', 'مدير فرع', 'system admin', 'developer']
            
            if any(role in role_name for role in allowed_roles) or (self.user_info.get('role_id') == 99):
                self.btn_history.show()
            else:
                self.btn_history.hide()
            
            # Check store-wide status
            store_status = self.db.get_store_open_drawer(store_id)
            
            if store_status:
                # There is an open drawer in the store
                opener_name = store_status.get('cashier_name', 'Unknown')
                opened_at = store_status.get('opened_at')
                
                if store_status.get('cashier_id') == user_id:
                    # It's MY drawer
                    self.status_label.setText(f"مفتوح لديك منذ {opened_at}")
                    self.status_card.setStyleSheet(self.status_card.styleSheet().replace(COLORS['secondary'], "#10B981")) # Green
                    self.btn_open.hide()
                    self.btn_close.show()
                else:
                    # It's SOMEONE ELSE'S drawer
                    self.status_label.setText(f"مفتوح بواسطة: {opener_name}")
                    self.status_card.setStyleSheet(self.status_card.styleSheet().replace("#10B981", "#F59E0B")) # Orange/Amber check logic
                    # Ensure base color is replaced correctly if it was green or default
                    # Let's just reset the style string to be safe
                    base_style = f"""
                        QFrame {{
                            background-color: #F59E0B;
                            border-radius: 12px;
                            padding: 15px;
                        }}
                    """
                    self.status_card.setStyleSheet(base_style)
                    
                    self.btn_open.hide()
                    self.btn_close.hide() # Cannot close others' drawer from here (usually)
            else:
                # No drawer open in the store
                self.status_label.setText("مغلق")
                # Reset to default
                default_style = f"""
                    QFrame {{
                        background-color: {COLORS['secondary']};
                        border-radius: 12px;
                        padding: 15px;
                    }}
                """
                self.status_card.setStyleSheet(default_style)
                self.btn_open.show()
                self.btn_close.hide()
                
        except Exception as e:
            print(f"Error checking status: {e}")

    def show_history_dialog(self):
        """Show the closed drawers history dialog"""
        store_id = self.user_info.get('store_id')
        if not store_id:
            return
            
        dialog = ClosedDrawersDialog(store_id, self)
        dialog.exec()

    def open_drawer_click(self):
        """Open the drawer with optional starting balance"""
        store_id = self.user_info.get('store_id')
        user_id = self.user_info.get('id')
        
        # Double check before opening logic
        store_status = self.db.get_store_open_drawer(store_id)
        if store_status:
            QMessageBox.warning(self, "تنبيه", f"عذراً، يوجد درج مفتوح بالفعل بواسطة {store_status.get('cashier_name')}.\nلا يمكن فتح درج جديد.")
            self.check_drawer_status() # Refresh UI
            return

        # Ask for opening balance (Optional)
        balance, ok = QInputDialog.getDouble(
            self, "فتح الدرج", 
            "أدخل رصيد البداية (اختياري):", 
            0, 0, 1000000, 2
        )
        
        if ok:
            if self.db.open_drawer(store_id, user_id, balance):
                QMessageBox.information(self, "نجاح", "تم فتح الدرج بنجاح")
                self.check_drawer_status()
                self.drawer_opened.emit()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في فتح الدرج")

    def close_drawer_click(self):
        """Close the drawer with cash and card details"""
        status = self.db.get_drawer_status(self.user_info.get('id'))
        if not status or not status.get('is_open'):
            return

        # Custom dialog for closing
        dialog = QDialog(self)
        dialog.setWindowTitle("إغلاق الدرج - جرد النقدية والفيزا")
        dialog.setFixedWidth(350)
        dialog.setStyleSheet(GLOBAL_STYLE)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        form.setSpacing(15)
        
        cash_input = QLineEdit()
        cash_input.setPlaceholderText("0.00")
        cash_input.setStyleSheet(f"min-height: 40px; font-size: 16px; background-color: {COLORS['bg_input']}; color: white; border: 1px solid {COLORS['border']}; border-radius: 8px;")
        
        card_input = QLineEdit()
        card_input.setPlaceholderText("0.00")
        card_input.setStyleSheet(f"min-height: 40px; font-size: 16px; background-color: {COLORS['bg_input']}; color: white; border: 1px solid {COLORS['border']}; border-radius: 8px;")
        
        form.addRow("💰 إجمالي الكاش:", cash_input)
        form.addRow("💳 إجمالي الفيزا:", card_input)
        
        layout.addLayout(form)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        
        if dialog.exec():
            try:
                cash_total = float(cash_input.text()) if cash_input.text() else 0.0
                card_total = float(card_input.text()) if card_input.text() else 0.0
                
                drawer_id = status['id']
                # We store both in denomination_details with special keys
                details = {
                    "1ج": int(cash_total), # Current logic quirk: uses denom names as ints
                    "Visa": card_total # We will handle this in DB manager
                }
                
                if self.db.close_drawer(drawer_id, cash_total, details):
                     QMessageBox.information(self, "نجاح", "تم إغلاق الدرج بنجاح")
                     self.check_drawer_status()
                     self.drawer_closed.emit()
                     
                     # Print report
                     try:
                         from utils.printer_service import PrinterService
                         summary = self.db.get_drawer_summary(drawer_id)
                         if summary:
                             PrinterService.print_drawer_report(summary)
                     except Exception as e:
                         print(f"Printing error: {e}")
                else:
                     QMessageBox.critical(self, "خطأ", "فشل في إغلاق الدرج")
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال أرقام صحيحة")

    def print_last_closing(self):
        """Print the receipt for the last closed drawer"""
        try:
            store_id = self.user_info.get('store_id')
            user_id = self.user_info.get('id')
            
            if not store_id or not user_id:
                return

            last_drawer_id = self.db.get_last_closed_drawer_id(store_id, user_id)
            
            if not last_drawer_id:
                QMessageBox.warning(self, "تنبيه", "لا يوجد سجل درج مغلق سابق لهذا المستخدم في هذا الفرع.")
                return
            
            # Print
            from utils.printer_service import PrinterService
            summary = self.db.get_drawer_summary(last_drawer_id)
            if summary:
                PrinterService.print_drawer_report(summary)
                QMessageBox.information(self, "نجاح", "تم إرسال أمر الطباعة بنجاح")
            else:
                QMessageBox.warning(self, "خطأ", "تعذر جلب بيانات الدرج")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")
