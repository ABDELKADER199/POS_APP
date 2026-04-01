import logging
import os
import tempfile

import barcode

try:
    # ImageWriter يعتمد على Pillow. إذا Pillow غير متوفر ستكون القيمة None.
    from barcode.writer import ImageWriter
except Exception:  # pragma: no cover
    ImageWriter = None

logger = logging.getLogger(__name__)


class BarcodeService:
    _missing_writer_reported = False

    @staticmethod
    def generate_barcode(code, name, price=None, output_dir=None, label_size="40x25", write_text=True):
        """توليد صورة باركود للمنتج بمقاس محدد."""
        try:
            if ImageWriter is None:
                if not BarcodeService._missing_writer_reported:
                    message = (
                        "Barcode image generation requires Pillow. "
                        "Install it with: pip install Pillow"
                    )
                    logger.error(message)
                    print(f"Error generating barcode: {message}")
                    BarcodeService._missing_writer_reported = True
                return None

            code128 = barcode.get("code128", str(code), writer=ImageWriter())

            if output_dir is None:
                output_dir = tempfile.gettempdir()

            filename = f"barcode_{code}_{label_size}"
            filepath = os.path.join(output_dir, filename)

            if label_size == "50x30":
                options = {
                    "module_height": 15.0,
                    "module_width": 0.45,
                    "font_size": 10,
                    "text_distance": 3.0,
                    "quiet_zone": 2.0,
                    "center_text": True,
                    "write_text": write_text,
                }
            elif label_size == "30x20":
                options = {
                    "module_height": 10.0,
                    "module_width": 0.4,
                    "font_size": 7,
                    "text_distance": 1.0,
                    "quiet_zone": 1.0,
                    "center_text": True,
                    "write_text": write_text,
                }
            else:  # default 40x25
                options = {
                    "module_height": 12.0,
                    "module_width": 0.45,
                    "font_size": 8,
                    "text_distance": 2.5,
                    "quiet_zone": 1.5,
                    "center_text": True,
                    "write_text": write_text,
                }

            return code128.save(filepath, options=options)
        except Exception as exc:
            logger.exception("Error generating barcode")
            print(f"Error generating barcode: {exc}")
            return None
