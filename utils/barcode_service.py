
import barcode
from barcode.writer import ImageWriter
import os
import tempfile

class BarcodeService:
    @staticmethod
    def generate_barcode(code, name, price=None, output_dir=None, label_size="40x25", write_text=True):
        """
        توليد صورة باركود للمنتج بمقاس محدد.
        """
        try:
            # استخدام Code128 كمعيار افتراضي
            code128 = barcode.get('code128', str(code), writer=ImageWriter())
            
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            filename = f"barcode_{code}_{label_size}"
            filepath = os.path.join(output_dir, filename)

            # إعدادات مخصصة - محسنة للطابعات الحرارية (Professional POS)
            if label_size == "50x30":
                options = {
                    'module_height': 15.0,
                    'module_width': 0.45,
                    'font_size': 10,
                    'text_distance': 3.0,
                    'quiet_zone': 2.0,
                    'center_text': True,
                    'write_text': write_text,
                }
            elif label_size == "30x20":
                options = {
                    'module_height': 10.0,
                    'module_width': 0.4, 
                    'font_size': 7,
                    'text_distance': 1.0,
                    'quiet_zone': 1.0,
                    'center_text': True,
                    'write_text': write_text,
                }
            else:  # الافتراضي 40x25
                options = {
                    'module_height': 12.0,
                    'module_width': 0.45,
                    'font_size': 8,
                    'text_distance': 2.5,
                    'quiet_zone': 1.5,
                    'center_text': True,
                    'write_text': write_text,
                }
            
            # الحفظ كصورة
            full_path = code128.save(filepath, options=options)
            return full_path
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
