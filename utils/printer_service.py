
import os
import tempfile
import sys
from datetime import datetime

class PrinterService:
    """Service to handle printing receipts using HTML for better formatting."""
    
    @staticmethod
    def _get_common_styles():
        """Returns CSS styles common to all receipt types."""
        return """
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'Amiri', serif; 
                font-size: 12px; 
                margin: 0; 
                padding: 0; 
                width: 100%; 
                color: #1a202c; 
            }
            body { 
                font-family: 'Tahoma', 'Segoe UI', Geneva, Verdana, sans-serif; 
                font-size: 13px; 
                margin: 0; 
                padding: 0; 
                width: 100%; 
                background-color: #fff;
            }
            .receipt { 
                width: 100%;
                max-width: 72mm; 
                height:auto;
                margin: 0 auto; 
                padding: 5px;
            }
            .header { 
                text-align: center; 
                margin-bottom: 10px; 
                padding-bottom: 8px; 
                border-bottom: 2px dashed #000; 
            }
            .store-name { 
                font-size: 18px; 
                font-weight: 900; 
                color: #000; 
                text-transform: uppercase; 
                margin-bottom: 5px;
            }
            .branch-info { font-size: 12px; font-weight: bold; margin-bottom: 5px; }
            
            .meta-info { 
                width: 100%;
                font-size: 11px; 
                font-weight: bold;
                border-collapse: collapse;
                margin-top: 5px;
            }
            .meta-info td { padding: 2px 0; border: none; }
            .meta-info .label { text-align: right; width: 40%; color: #333; }
            .meta-info .value { text-align: left; width: 60%; color: #000; }

            .customer-section { 
                margin: 10px 0; 
                padding: 5px; 
                border: 1px solid #000; 
                border-radius: 4px;
                text-align: center;
                background-color: #fce7f3; /* Very light pink/warm background for distinction, grayscale safe */
            }
            .customer-title { font-weight: bold; font-size: 12px; margin-bottom: 2px; text-decoration: underline; }
            
            table.items-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
            table.items-table th { 
                border-top: 2px solid #000; 
                border-bottom: 2px solid #000; 
                padding: 5px 0; 
                font-size: 12px; 
                font-weight: 900; 
                text-align: right; 
            }
            table.items-table td { 
                padding: 6px 0; 
                font-size: 12px; 
                vertical-align: top; 
                border-bottom: 1px dotted #ccc; 
            }
            
            .item-name { font-weight: bold; font-size: 13px; margin-bottom: 2px; display: block; color: #000; }
            .item-details { font-size: 11px; color: #4a5568; }
            .item-total { text-align: left; font-weight: bold; font-size: 13px; vertical-align: middle; }

            .totals-section { 
                margin-top: 15px; 
                padding-top: 10px;
                border-top: 2px dashed #000;
            }
            .total-table { width: 100%; border-collapse: collapse; }
            .total-table td { padding: 4px 0; border: none; }
            .total-label { text-align: right; font-weight: bold; font-size: 13px; color: #334155; }
            .total-value { text-align: left; font-weight: 800; font-size: 14px; color: #000; }
            
            .grand-total { 
                background-color: #f8fafc;
                border-top: 2px solid #000; 
                border-bottom: 2px solid #000;
                margin-top: 8px;
            }
            .grand-total td { padding: 10px 0; }

            .footer { 
                text-align: center; 
                margin-top: 20px; 
                font-size: 11px; 
                font-weight: bold; 
                border-top: 1px dotted #000; 
                padding-top: 12px; 
                line-height: 1.5;
            }
            .divider { border-top: 1px dashed #000; margin: 10px 0; height: 0; }
            .barcode-container {
                text-align: center;
                margin-top: 12px;
                padding-top: 8px;
                border-top: 1px dotted #ccc;
                width: 100%;
            }
            .barcode-img {
                max-width: 130px;
                height: auto;
            }
        """

    @staticmethod
    def _get_barcode_html(code):
        """Generates a small barcode HTML fragment."""
        if not code:
            return ""
        try:
            from utils.barcode_service import BarcodeService
            import base64
            barcode_path = BarcodeService.generate_barcode(str(code), "", label_size="40x25")
            if barcode_path and os.path.exists(barcode_path):
                with open(barcode_path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                return f"""
                <div class="barcode-container">
                    <img src="data:image/png;base64,{b64_string}" class="barcode-img">
                    <div style="font-size: 8px; margin-top: 2px;">{code}</div>
                </div>
                """
        except Exception as e:
            print(f"Barcode helper error: {e}")
        return ""

    @staticmethod
    def _generate_receipt_html(invoice_data, items, user_name, settings, is_order=False):
        """Generates modern HTML for sales receipts and orders."""
        rows = ""
        for item in items:
            name = item.get('product_name', 'Unknown')
            qty = item.get('quantity', 0)
            price = item.get('price', 0)
            total = item.get('total', qty * price)
            rows += f"""
            <tr>
                <td>
                    <span class="item-name">{name}</span>
                    <span class="item-details">{qty} x {price:.2f}</span>
                </td>
                <td class="item-total">{total:.2f}</td>
            </tr>
            """

        customer_html = ""
        if invoice_data.get('customer_name'):
            customer_html = f"""
            <div class="customer-section">
                <div class="customer-title">العميل {"/ توصيل" if is_order else ""}</div>
                <div class="customer-info">
                    <strong>{invoice_data.get('customer_name')}</strong><br>
                    {invoice_data.get('customer_phone', '')}<br>
                    {invoice_data.get('customer_address', '')}
                </div>
            </div>
            """

        payment_details = ""
        method = invoice_data.get('payment_method', 'Cash')
        if method == 'Mixed':
            payment_details = f"""
            <tr><td class="total-label">نقداً:</td><td class="total-value">{invoice_data.get('cash_amount', 0):.2f}</td></tr>
            <tr><td class="total-label">فيزا:</td><td class="total-value">{invoice_data.get('card_amount', 0):.2f}</td></tr>
            """
        else:
            payment_details = f"""<tr><td class="total-label">طريقة الدفع:</td><td class="total-value">{method}</td></tr>"""

        store_name = settings.get('store_name', 'نظام POS')
        store_address = settings.get('store_address', '')
        store_phone = settings.get('store_phone', '')
        receipt_footer = settings.get('receipt_footer', 'شكراً لزيارتكم')

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>{PrinterService._get_common_styles()}</style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">{store_name}</div>
                    <div class="branch-info">{store_address}<br>{store_phone}</div>
                    <div class="divider"></div>
                    <table class="meta-info">
                        <tr>
                            <td class="label">رقم الفاتورة:</td>
                            <td class="value">#{invoice_data.get('invoice_number')}</td>
                        </tr>
                        <tr>
                            <td class="label">التاريخ:</td>
                            <td class="value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                        <tr>
                            <td class="label">الكاشير:</td>
                            <td class="value">{user_name} (د-{invoice_data.get('drawer_id', '-')})</td>
                        </tr>
                    </table>
                </div>

                {customer_html}

                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="width: 65%; text-align: right; padding-right: 5px;">الصنف</th>
                            <th style="width: 35%; text-align: left; padding-left: 5px;">السعر</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>

                <div class="totals-section">
                    <table class="total-table">
                        <tr><td class="total-label">المجموع:</td><td class="total-value">{invoice_data.get('subtotal', 0):.2f}</td></tr>
                        <tr><td class="total-label">الخصم:</td><td class="total-value">-{invoice_data.get('discount', 0):.2f}</td></tr>
                        {payment_details}
                        <tr class="grand-total">
                            <td class="total-label">الإجمالي:</td>
                            <td class="total-value">{invoice_data.get('total_amount', 0):.2f} ج.م</td>
                        </tr>
                        {f'<tr><td class="total-label">المدفوع:</td><td class="total-value">{invoice_data.get("tendered", 0):.2f}</td></tr><tr><td class="total-label">الباقي:</td><td class="total-value">{invoice_data.get("change", 0):.2f}</td></tr>' if invoice_data.get('tendered', 0) > 0 else ''}
                    </table>
                </div>

                <div class="footer">
                    {receipt_footer}<br>
                    يرجى الاحتفاظ بالفاتورة في حال الاستبدال أو الاسترجاع (14 يوماً)
                </div>

                {PrinterService._get_barcode_html(invoice_data.get('invoice_number', '000'))}
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _generate_return_receipt_html(return_data, items, user_name, settings):
        """Generates modern HTML for return receipts."""
        rows = ""
        for item in items:
            name = item.get('product_name', 'Unknown')
            qty = item.get('quantity', 0)
            price = item.get('unit_price', 0)
            total = item.get('total_price', qty * price)
            rows += f"""
            <tr>
                <td>
                    <span class="item-name">{name}</span>
                    <span class="item-details">{qty} x {price:.2f}</span>
                </td>
                <td class="item-total">{total:.2f}</td>
            </tr>
            """

        store_name = settings.get('store_name', 'نظام POS')
        store_address = settings.get('store_address', '')
        store_phone = settings.get('store_phone', '')
        receipt_footer = settings.get('receipt_footer', 'شكراً لزيارتكم')

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>{PrinterService._get_common_styles()}</style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">{store_name}</div>
                    <div class="branch-info">{store_address}<br>{store_phone}</div>
                    <div class="return-badge">*** إيصال مرتجع ***</div>
                    <table class="meta-info">
                        <tr>
                            <td class="label">رقم المرتجع: {return_data.get('return_number')}</td>
                            <td class="value" style="text-align:left">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                        <tr>
                            <td class="label">فاتورة الأصل: #{return_data.get('invoice_number')}</td>
                            <td class="value" style="text-align:left">الموظف: {user_name}</td>
                        </tr>
                    </table>
                </div>

                <table class="items-table">
                    <thead>
                         <tr>
                            <th style="width: 65%; text-align: right; padding-right: 5px;">الصنف</th>
                            <th style="width: 35%; text-align: left; padding-left: 5px;">السعر</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>

                <div class="totals-section">
                    <table class="total-table">
                        <tr class="grand-total" style="color: #c53030;">
                            <td class="total-label">إجمالي المرتجع:</td> 
                            <td class="total-value">{return_data.get('total_amount', 0):.2f} ج.م</td>
                        </tr>
                    </table>
                </div>

                <div style="margin-top: 10px; font-size: 11px; color: #4a5568;">
                    <strong>السبب:</strong> {return_data.get('reason', '-')}
                </div>

                <div class="footer">
                    {receipt_footer}<br>
                    تم استرداد المبلغ نقداً
                </div>

                {PrinterService._get_barcode_html(return_data.get('return_number', '000'))}
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _save_as_pdf(html_content, width_pts, filename_prefix="Document", category="الفواتير", auto_open=True):
        """Saves HTML content to a PDF file and opens it. Category can be 'invoices', 'returns', etc."""
        try:
            from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize
            from PyQt6.QtPrintSupport import QPrinter
            from PyQt6.QtCore import QSizeF, QMarginsF
            import os
            import subprocess

            # 1. Arabic Month Names
            arabic_months = {
                1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
                5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
                9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
            }
            
            now = datetime.now()
            month_name = arabic_months.get(now.month, str(now.month))
            year_name = str(now.year)

            # 2. Create nested directory structure (Root: الفواتير)
            root_pdf_dir = os.path.join(os.getcwd(), "الفواتير")
            base_category_dir = os.path.join(root_pdf_dir, category)
            final_month_dir = os.path.join(base_category_dir, year_name, month_name)
            
            if not os.path.exists(final_month_dir):
                os.makedirs(final_month_dir)

            # 3. Generate filename
            filename = f"{filename_prefix}.pdf"
            pdf_path = os.path.join(final_month_dir, filename)

            # 4. Setup Printer for PDF
            printer = QPrinter() 
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(pdf_path)

            # 5. Content setup
            doc = QTextDocument()
            doc.setMetaInformation(QTextDocument.MetaInformation.DocumentTitle, filename_prefix)
            doc.setDocumentMargin(0)
            doc.setHtml(html_content)
            doc.setTextWidth(width_pts)
            
            is_small_label = width_pts < 150 
            real_height = doc.size().height() + (0 if is_small_label else 20)

            custom_size = QPageSize(QSizeF(width_pts, real_height), QPageSize.Unit.Point)
            layout = QPageLayout(custom_size, QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0))
            printer.setPageLayout(layout)
            printer.setFullPage(True)
            
            doc.setPageSize(QSizeF(width_pts, real_height))
            doc.print(printer)

            # 6. Open PDF if requested
            if os.path.exists(pdf_path):
                if auto_open:
                    if os.name == 'nt':  # Windows
                        os.startfile(pdf_path)
                    elif os.name == 'posix':  # macOS/Linux
                        subprocess.run(['open', pdf_path] if sys.platform == 'darwin' else ['xdg-open', pdf_path])
                return True, pdf_path
            return False, None

        except Exception as e:
            print(f"PDF Save Error: {e}")
            return False, None

    @staticmethod
    def _is_virtual_printer(printer_info):
        """Helper to detect virtual printers (Fax, XPS, etc.)"""
        if not printer_info or printer_info.isNull():
            return True
        
        name = printer_info.printerName().lower()
        # Common virtual/system-only printers on Windows
        virtual_names = [
            'fax', 'xps', 'one note', 'onenote', 'print to pdf', 
            'microsoft pdf', 'send to', 'virtual', 'writer', 'redirected',
            'pdf', 'fax', 'cute-pdf', 'do-pdf'
        ]
        return any(vn in name for vn in virtual_names)

    @staticmethod
    def _print_html_document(html_content, receipt_height_est=600, width_pts=None, printer_name=None, filename_prefix="Document", category="الفواتير"):
        """Unified method to print HTML content, fallback to PDF if no physical printer."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize
            from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo
            from PyQt6.QtCore import QSizeF, QMarginsF
            import os

            # Determine width
            thermal_width_pts = 226 # ~80mm
            p_width = width_pts or thermal_width_pts

            # 1. Setup Printer
            printer_info = None
            if printer_name:
                available_printers = QPrinterInfo.availablePrinters()
                for p in available_printers:
                    if p.printerName() == printer_name:
                        printer_info = p
                        break
            
            if not printer_info:
                printer_info = QPrinterInfo.defaultPrinter()

            # 2. Always save a silent copy in the organized folders (Silent Archive)
            success_save, pdf_path = PrinterService._save_as_pdf(html_content, p_width, filename_prefix, category=category, auto_open=False)

            # 3. Robust Fallback Logic for actual printing
            if not printer_info or printer_info.isNull() or PrinterService._is_virtual_printer(printer_info):
                # We already saved the PDF in step 2.
                # If we don't have a real printer, we just return the success of the save.
                return success_save

            # 4. Physical Printing Attempt
            try:
                printer = QPrinter(printer_info)
                printer.setPrinterName(printer_info.printerName())
                
                doc = QTextDocument()
                doc.setMetaInformation(QTextDocument.MetaInformation.DocumentTitle, filename_prefix)
                doc.setDocumentMargin(0) 
                doc.setHtml(html_content)
                doc.setTextWidth(p_width)
                
                is_small_label = p_width < 150
                real_height = doc.size().height() + (0 if is_small_label else 20)
                
                custom_size = QPageSize(QSizeF(p_width, real_height), QPageSize.Unit.Point)
                layout = QPageLayout(custom_size, QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0))
                
                printer.setPageLayout(layout)
                doc.setPageSize(QSizeF(p_width, real_height))
                doc.print(printer)
                return True
            except Exception as e:
                print(f"❌ Physical printing failed: {e}")
                return success_save

        except Exception as e:
            print(f"Printing Service Error: {e}")
            return False

    @staticmethod
    def print_barcode_direct(name, code, printer_name, label_size="40x25", price=None, store_name=None):
        """Prints a single barcode label directly to a specified printer."""
        try:
            from utils.barcode_service import BarcodeService
            import base64
            
            # Use write_text=False to allow manual HTML layout control
            path = BarcodeService.generate_barcode(code, name, label_size=label_size, write_text=False)
            if not path or not os.path.exists(path):
                return False
            
            with open(path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode()
            
            # Format price string
            price_str = f"{float(price):.2f} ج.م" if price else ""
            
            # === QTextDocument-compatible layouts (table-based, NO flex) ===
            common_style = "margin:0; padding:0; font-family:'Arial', sans-serif; background-color:white; color:black;"
            if label_size == "50x30":
                w_pts = 141.7  # 50mm
                h_pts = 85.0   # 30mm
                img_w_pts = w_pts - 20
                
                html = f"""
                <html>
                <body style="{common_style}">
                    <table width="{w_pts}pt" height="{h_pts}pt" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; table-layout:fixed;">
                        <tr height="20pt">
                            <td align="center" valign="middle" style="padding:2pt 4pt 0 4pt;">
                                <div style="font-size:10pt; font-weight:bold; line-height:1.1; white-space:nowrap; overflow:hidden;">{name}</div>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" valign="middle" style="padding:2pt 4pt;">
                                <img src="data:image/png;base64,{b64_img}" style="width:{img_w_pts}pt; height:40pt; object-fit:contain;">
                            </td>
                        </tr>
                        <tr height="18pt">
                            <td align="center" valign="top" style="padding:0 4pt 2pt 4pt;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="right" style="font-size:9pt; font-weight:bold; width:50%;">{code}</td>
                                        <td align="left" style="font-size:9pt; font-weight:bold; width:50%; direction:rtl;">{price_str}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            elif label_size == "30x20":
                w_pts = 85.0   # 30mm
                h_pts = 56.7   # 20mm
                img_w_pts = w_pts - 10

                html = f"""
                <html>
                <body style="{common_style}">
                    <table width="{w_pts}pt" height="{h_pts}pt" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; table-layout:fixed;">
                        <tr height="12pt">
                            <td align="center" valign="middle" style="padding:1pt 2pt 0 2pt;">
                                <div style="font-size:7pt; font-weight:bold; line-height:1; white-space:nowrap; overflow:hidden;">{name}</div>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" valign="middle" style="padding:1pt 2pt;">
                                <img src="data:image/png;base64,{b64_img}" style="width:{img_w_pts}pt; height:28pt; object-fit:contain;">
                            </td>
                        </tr>
                        <tr height="10pt">
                            <td align="center" valign="top" style="padding:0 2pt;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="right" style="font-size:6pt; width:50%;">{code}</td>
                                        <td align="left" style="font-size:6pt; font-weight:bold; width:50%;">{price_str}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            else:  # 40x25 (Classic compact layout)
                w_pts = 110  # 40mm
                h_pts = 70   # 25mm
                img_w_pts = w_pts - 14

                html = f"""
                <html>
                <body style="{common_style}">
                    <table width="{w_pts}pt" height="{h_pts}pt" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; table-layout:fixed;">
                        <tr height="15pt">
                            <td align="center" valign="middle" style="padding:2pt 4pt 0 4pt;">
                                <div style="font-size:7pt; font-weight:bold; line-height:1.1; overflow:hidden; white-space:nowrap;">{name}</div>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" valign="middle" style="padding:2pt 4pt;">
                                <img src="data:image/png;base64,{b64_img}" style="width:{img_w_pts}pt; height:30pt; object-fit:contain;">
                            </td>
                        </tr>
                        <tr height="12pt">
                            <td align="center" valign="top" style="padding:0 4pt 2pt 4pt;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="right" style="font-size:5pt; width:50%;">{code}</td>
                                        <td align="left" style="font-size:5pt; font-weight:bold; width:50%;">{price_str}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            
            # === Check for real physical printer ===
            from PyQt6.QtPrintSupport import QPrinterInfo
            
            has_real_printer = False
            if printer_name:
                for p in QPrinterInfo.availablePrinters():
                    if p.printerName() == printer_name and not PrinterService._is_virtual_printer(p):
                        has_real_printer = True
                        break
            
            if not has_real_printer:
                # Check default printer
                default = QPrinterInfo.defaultPrinter()
                if default and not default.isNull() and not PrinterService._is_virtual_printer(default):
                    has_real_printer = True
            
            if has_real_printer:
                # Physical printer found → print normally
                return PrinterService._print_html_document(html, receipt_height_est=h_pts, width_pts=w_pts, printer_name=printer_name, filename_prefix="Barcode")
            else:
                # No physical printer → save as high-DPI PNG image
                return PrinterService._save_barcode_as_image(html, w_pts, h_pts, code, name=name, price_str=price_str, label_size=label_size)
                
        except Exception as e:
            print(f"Barcode Print Error: {e}")
            return False
    
    @staticmethod
    def _save_barcode_as_image(html_content, w_pts, h_pts, code, name="", price_str="", label_size="40x25"):
        """Saves barcode label as a high-DPI PNG image using direct QPainter drawing."""
        try:
            from PyQt6.QtGui import QImage, QPainter, QFont, QColor, QPixmap
            from PyQt6.QtCore import Qt, QRect
            import subprocess

            from utils.barcode_service import BarcodeService
            barcode_path = BarcodeService.generate_barcode(code, name, label_size=label_size, write_text=False)
            if not barcode_path or not os.path.exists(barcode_path):
                print("❌ Barcode file not found")
                return False

            # 300 DPI — professional print quality
            dpi = 300
            scale = dpi / 72.0  # 1 pt = 1/72 inch

            # Convert pt to pixels
            img_w = int(w_pts * scale)
            img_h = int(h_pts * scale)

            # Create white canvas at target pixel size
            image = QImage(img_w, img_h, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            image.setDotsPerMeterX(int(dpi / 0.0254))
            image.setDotsPerMeterY(int(dpi / 0.0254))

            # Load barcode raw image
            barcode_pix = QPixmap(barcode_path)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # === Layout zones in pixels (proportional to image size) ===
            margin    = int(img_w * 0.04)      # ~4% margin
            name_h    = int(img_h * 0.17)      # 17% for name
            code_h    = int(img_h * 0.16)      # 16% for code+price
            barcode_h = img_h - margin * 2 - name_h - code_h - int(img_h * 0.04)
            barcode_y = margin + name_h + int(img_h * 0.02)
            bottom_y  = barcode_y + barcode_h + int(img_h * 0.02)

            name_px  = max(int(img_h * 0.10), 18)   # ~10% of label height
            text_px  = max(int(img_h * 0.09), 14)   # ~9% of label height

            # --- Product name (top center, bold) ---
            name_font = QFont("Arial")
            name_font.setPixelSize(name_px)
            name_font.setBold(True)
            painter.setFont(name_font)
            painter.setPen(QColor(0, 0, 0))
            name_rect = QRect(margin, margin, img_w - margin * 2, name_h)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, str(name))

            # --- Barcode image (center) ---
            if not barcode_pix.isNull():
                barcode_target = QRect(margin, barcode_y, img_w - margin * 2, barcode_h)
                painter.drawPixmap(barcode_target, barcode_pix.scaled(
                    barcode_target.width(), barcode_target.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))

            # --- Code (left) and price (right) at bottom ---
            half_w   = (img_w - margin * 2) // 2
            code_rect  = QRect(margin,             bottom_y, half_w, code_h)
            price_rect = QRect(margin + half_w,    bottom_y, half_w, code_h)

            code_font = QFont("Arial")
            code_font.setPixelSize(text_px)

            price_font = QFont("Arial")
            price_font.setPixelSize(text_px)
            price_font.setBold(True)

            painter.setFont(code_font)
            painter.drawText(code_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(code))

            painter.setFont(price_font)
            painter.drawText(price_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, price_str)

            painter.end()

            # Save
            save_dir = os.path.join(os.getcwd(), "الباركود")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            safe_code = str(code).replace('/', '_').replace('\\', '_')
            img_path = os.path.join(save_dir, f"barcode_{safe_code}.png")
            image.save(img_path, "PNG")

            if os.path.exists(img_path):
                if os.name == 'nt':
                    os.startfile(img_path)
                print(f"✅ Barcode saved as image: {img_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ Image save error: {e}")
            import traceback; traceback.print_exc()
            return False

    @staticmethod
    def print_receipt(invoice_data, items, user_name, store_name_unused=None, is_order=False):
        """Prints a modern sales receipt or order."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        est_height = 400 + (len(items) * 45) + (100 if invoice_data.get('customer_name') else 0)
        html = PrinterService._generate_receipt_html(invoice_data, items, user_name, settings, is_order)
        prefix = invoice_data.get('invoice_number', 'Invoice')
        return PrinterService._print_html_document(html, est_height, filename_prefix=prefix, category="فواتير البيع")

    @staticmethod
    def print_return_receipt(return_data, items, user_name, store_name_unused=None):
        """Prints a modern return receipt."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        est_height = 350 + (len(items) * 45)
        html = PrinterService._generate_return_receipt_html(return_data, items, user_name, settings)
        prefix = return_data.get('return_number', 'Return')
        return PrinterService._print_html_document(html, est_height, filename_prefix=prefix, category="فواتير المرتجعات")

    @staticmethod
    def print_drawer_report(summary_data):
        """Prints a modern drawer report."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        html = PrinterService._generate_drawer_report_html(summary_data, settings)
        return PrinterService._print_html_document(html, 800, filename_prefix="Report")

    @staticmethod
    def save_receipt_as_pdf(invoice_data, items, user_name, store_name_unused=None, is_order=False):
        """Explicitly saves a receipt as PDF without trying to print."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        html = PrinterService._generate_receipt_html(invoice_data, items, user_name, settings, is_order)
        prefix = invoice_data.get('invoice_number', 'Invoice')
        thermal_width_pts = 226
        success, _ = PrinterService._save_as_pdf(html, thermal_width_pts, filename_prefix=prefix, category="فواتير البيع", auto_open=True)
        return success

    @staticmethod
    def _generate_purchase_invoice_html(invoice_data, items, user_name, settings):
        """Generates modern HTML for purchase invoices."""
        rows = ""
        for item in items:
            name = item.get('product_name', 'Unknown')
            qty = item.get('quantity', 0)
            cost = item.get('cost', 0)
            total = item.get('total', qty * cost)
            rows += f"""
            <tr>
                <td>
                    <span class="item-name">{name}</span>
                    <span class="item-details">{qty} x {cost:.2f}</span>
                </td>
                <td class="item-total">{total:.2f}</td>
            </tr>
            """

        supplier_html = ""
        if invoice_data.get('supplier_name'):
            supplier_html = f"""
            <div class="customer-section">
                <div class="customer-title">المورد</div>
                <div class="customer-info">
                    <strong>{invoice_data.get('supplier_name')}</strong>
                </div>
            </div>
            """

        store_name = settings.get('store_name', 'نظام POS')
        store_address = settings.get('store_address', '')
        store_phone = settings.get('store_phone', '')

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>{PrinterService._get_common_styles()}</style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">{store_name}</div>
                    <div class="branch-info">{store_address}<br>{store_phone}</div>
                    <div class="return-badge" style="border: 2px solid #000; padding: 2px; margin: 5px 0;">*** فاتورة مشتريات ***</div>
                    <table class="meta-info">
                        <tr>
                            <td class="label">رقم الفاتورة:</td>
                            <td class="value">#{invoice_data.get('invoice_number', '-')}</td>
                        </tr>
                        <tr>
                            <td class="label">مرجع المورد:</td>
                            <td class="value">{invoice_data.get('ref_number', '-')}</td>
                        </tr>
                        <tr>
                            <td class="label">التاريخ:</td>
                            <td class="value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                        <tr>
                            <td class="label">المستخدم:</td>
                            <td class="value">{user_name}</td>
                        </tr>
                    </table>
                </div>

                {supplier_html}

                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="width: 65%; text-align: right; padding-right: 5px;">الصنف</th>
                            <th style="width: 35%; text-align: left; padding-left: 5px;">التكلفة</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>

                <div class="totals-section">
                    <table class="total-table">
                        <tr><td class="total-label">المجموع:</td><td class="total-value">{invoice_data.get('subtotal', 0):.2f}</td></tr>
                        <tr><td class="total-label">الخصم:</td><td class="total-value">-{invoice_data.get('discount', 0):.2f}</td></tr>
                        <tr><td class="total-label">الضريبة:</td><td class="total-value">+{invoice_data.get('tax', 0):.2f}</td></tr>
                        <tr class="grand-total">
                            <td class="total-label">الإجمالي:</td>
                            <td class="total-value">{invoice_data.get('total_amount', 0):.2f} ج.م</td>
                        </tr>
                        <tr><td class="total-label">طريقة الدفع:</td><td class="total-value">{invoice_data.get('payment_method', '-')}</td></tr>
                        <tr><td class="total-label">المدفوع:</td><td class="total-value">{invoice_data.get('paid_amount', 0):.2f}</td></tr>
                        <tr><td class="total-label">المتبقي:</td><td class="total-value">{invoice_data.get('remaining_amount', 0):.2f}</td></tr>
                    </table>
                </div>

                <div class="footer">
                    تم حفظ الفاتورة بنجاح
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def save_purchase_invoice_as_pdf(invoice_data, items, user_name):
        """Saves a purchase invoice as PDF."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        html = PrinterService._generate_purchase_invoice_html(invoice_data, items, user_name, settings)
        prefix = f"Purchase_{invoice_data.get('invoice_number', 'New')}"
        thermal_width_pts = 226
        # Save to specific folder for purchases if needed, for now sticking to category='مشتريات'
        success, _ = PrinterService._save_as_pdf(html, thermal_width_pts, filename_prefix=prefix, category="المشتريات", auto_open=True)
        return success

    @staticmethod
    def save_return_as_pdf(return_data, items, user_name, store_name_unused=None):
        """Explicitly saves a return receipt as PDF without trying to print."""
        from database_manager import DatabaseManager
        db = DatabaseManager()
        settings = db.get_settings()
        
        html = PrinterService._generate_return_receipt_html(return_data, items, user_name, settings)
        prefix = return_data.get('return_number', 'Return')
        thermal_width_pts = 226
        success, _ = PrinterService._save_as_pdf(html, thermal_width_pts, filename_prefix=prefix, category="فواتير المرتجعات", auto_open=True)
        return success

    @staticmethod
    def _generate_drawer_report_html(summary, settings):
        """Format the drawer report with premium HTML."""
        den_html = ""
        if summary.get('denominations'):
            den_html = "<div class='divider'></div><div class='customer-title'>تفاصيل الفئات</div><table>"
            for den in summary['denominations']:
                den_html += f"<tr><td>{den['denomination']} x {den['quantity']}</td><td style='text-align:left'>{den['total_amount']:.2f}</td></tr>"
            den_html += "</table>"

        store_name = settings.get('store_name', 'نظمة POS')
        store_address = settings.get('store_address', '')
        store_phone = settings.get('store_phone', '')

        diff = summary['difference']
        diff_style = "color: #38a169;" if diff >= 0 else "color: #e53e3e;"
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>{PrinterService._get_common_styles()}</style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <div class="store-name">{store_name}</div>
                    <div class="branch-info">{store_address}<br>{store_phone}</div>
                    <div class="customer-title" style="font-size: 14px; margin-top:5px;">*** تقرير إغلاق الدرج ***</div>
                    <div class="divider"></div>
                    <table class="meta-info">
                        <tr>
                            <td class="label">رقم الدرج: {summary['drawer_id']}</td>
                            <td class="value" style="text-align:left">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td>
                        </tr>
                        <tr>
                            <td class="label" colspan="2" style="text-align:center">الكاشير: {summary['cashier_name']}</td>
                        </tr>
                    </table>
                </div>

                <table class="items-table">
                    <tr><td>الرصيد الافتتاحي:</td><td style="text-align:left">{summary['opening_balance']:.2f}</td></tr>
                    <tr><td>إجمالي المبيعات ({summary['sales_count']}):</td><td style="text-align:left">{summary['total_sales']:.2f}</td></tr>
                    <tr style="font-size: 10px; color: #555"><td>&nbsp;&nbsp; - نقداً:</td><td style="text-align:left">{summary['total_cash_sales']:.2f}</td></tr>
                    <tr style="font-size: 10px; color: #555"><td>&nbsp;&nbsp; - فيزا (نظام):</td><td style="text-align:left">{summary['total_card_sales']:.2f}</td></tr>
                    <tr style="font-size: 10px; color: #555"><td>&nbsp;&nbsp; - آجل:</td><td style="text-align:left">{summary.get('total_deferred', 0):.2f}</td></tr>
                    <tr><td>المرتجعات ({summary['returns_count']}):</td><td style="text-align:left">-{summary['total_returns']:.2f}</td></tr>
                    <tr style="font-size: 10px; color: #555"><td>&nbsp;&nbsp; - مرتجعات نقدية:</td><td style="text-align:left">-{summary.get('total_cash_returns', summary['total_returns']):.2f}</td></tr>
                </table>

                <div class="divider"></div>
                <div class="customer-title" style="font-size: 13px;">مطابقة الفيزا (الماكينة)</div>
                <table class="items-table">
                    <tr><td>المتوقع (النظام):</td><td style="text-align:left">{summary['total_card_sales']:.2f}</td></tr>
                    <tr><td>الفعلي (الماكينة):</td><td style="text-align:left">{summary['actual_visa']:.2f}</td></tr>
                    <tr style="font-weight: bold; color: {'#38a169' if summary['visa_difference'] >= 0 else '#e53e3e'};">
                        <td>فرق الفيزا:</td>
                        <td style="text-align:left">{summary['visa_difference']:+.2f}</td>
                    </tr>
                </table>

                <div class="totals-section">
                    <table class="total-table">
                        <tr><td class="total-label">المتوقع نقداً:</td> <td class="total-value">{summary['expected_cash']:.2f}</td></tr>
                        <tr><td class="total-label">الفعلي نقداً:</td> <td class="total-value">{summary['actual_cash']:.2f}</td></tr>
                        <tr class="grand-total" style="{diff_style}">
                            <td class="total-label">العجز / الزيادة:</td> 
                            <td class="total-value">{diff:+.2f} ج.م</td>
                        </tr>
                    </table>
                </div>

                {den_html}

                <table style="margin-top: 30px; font-size: 10px;">
                    <tr>
                        <td style="text-align: center; width: 50%;">توقيع الكاشير<br><br>__________</td>
                        <td style="text-align: center; width: 50%;">توقيع المدير<br><br>__________</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        return html

