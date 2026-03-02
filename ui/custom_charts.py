
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFontMetrics, QLinearGradient

class SimpleBarChart(QWidget):
    """
    A simple, lightweight Bar Chart using QPainter.
    Input data format: [{'date': '2023-10-01', 'total_sales': 1200.0}, ...]
    """
    def __init__(self, title="Sales Trend"):
        super().__init__()
        self.setMinimumHeight(250)
        self.data = []
        self.title = title
        self.bar_color = QColor("#10B981") # Neon Green
        self.hover_index = -1
        self.setMouseTracking(True)

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        # painter.fillRect(self.rect(), QColor("#1E293B")) # Transparent/inherited is better

        # Drawing Area Margins
        margin_left = 50
        margin_bottom = 30
        margin_top = 40
        margin_right = 20
        
        w = self.width() - margin_left - margin_right
        h = self.height() - margin_top - margin_bottom
        
        if not self.data:
            painter.setPen(QColor("#94A3B8"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "لا توجد بيانات للعرض")
            return

        # Calculate Scales
        max_val = max([float(d.get('total_sales', 0)) for d in self.data] + [100]) # Avoid div/0
        vals = [float(d.get('total_sales', 0)) for d in self.data]
        n_bars = len(vals)
        bar_width = w / n_bars * 0.6
        spacing = w / n_bars * 0.4
        
        # Draw Title
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(self.font())
        painter.drawText(QRectF(0, 5, self.width(), 30), Qt.AlignmentFlag.AlignCenter, self.title)

        # Draw Grid & Y-Axis Labels
        painter.setPen(QPen(QColor("#334155"), 1, Qt.PenStyle.DashLine))
        steps = 5
        for i in range(steps + 1):
            y = margin_top + h - (i * (h / steps))
            val = i * (max_val / steps)
            
            # Grid line
            painter.drawLine(int(margin_left), int(y), int(margin_left + w), int(y))
            
            # Label
            painter.setPen(QColor("#94A3B8"))
            painter.drawText(QRectF(0, y - 10, margin_left - 5, 20), 
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 
                           f"{int(val/1000)}k" if val >= 1000 else str(int(val)))
            painter.setPen(QPen(QColor("#334155"), 1, Qt.PenStyle.DashLine))

        # Draw Bars
        step_x = w / n_bars
        
        for i, item in enumerate(self.data):
            val = float(item.get('total_sales', 0))
            bar_h = (val / max_val) * h
            
            x = margin_left + (i * step_x) + (step_x - bar_width) / 2
            y = margin_top + h - bar_h
            
            rect = QRectF(x, y, bar_width, bar_h)
            
            # Gradient
            if i == self.hover_index:
                color = self.bar_color.lighter(130)
            else:
                color = self.bar_color
                
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0, color)
            grad.setColorAt(1, color.darker(150))
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw rounded rect bar
            painter.drawRoundedRect(rect, 4, 4)
            
            # Draw X-Axis Label (Show every nth label if too many)
            label_bloat = max(1, n_bars // 10)
            if i % label_bloat == 0:
                date_str = str(item.get('date', ''))[-5:] # Show MM-DD
                painter.setPen(QColor("#94A3B8"))
                painter.drawText(QRectF(x - 10, margin_top + h + 5, bar_width + 20, 20),
                               Qt.AlignmentFlag.AlignCenter, date_str)

    def mouseMoveEvent(self, event):
        # Calculate which bar acts as hover
        pass # To be implemented for tooltips if needed

class DonutChart(QWidget):
    """
    A simple Donut/Pie Chart.
    Input data format: [{'label': 'Food', 'value': 500, 'color': '#FF0000'}, ...]
    """
    def __init__(self, title="Distribution"):
        super().__init__()
        self.setMinimumHeight(250)
        self.data = []
        self.title = title
        self.default_colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        if not self.data:
            painter.setPen(QColor("#94A3B8"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Data")
            return

        # Title
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(self.font())
        painter.drawText(QRectF(0, 0, w, 30), Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Legend Area (Right side)
        legend_width = 120
        chart_size = min(w - legend_width, h - 40)
        
        # Center of donut
        cx = (w - legend_width) / 2
        cy = (h + 30) / 2
        
        outer_radius = chart_size / 2 * 0.8
        inner_radius = outer_radius * 0.6
        
        total = sum([float(d.get('total', d.get('value', 0))) for d in self.data])
        if total == 0:
            return

        start_angle = 90 * 16 # Start from top
        
        # Draw Arcs
        for i, item in enumerate(self.data):
            val = float(item.get('total', item.get('value', 0)))
            if val == 0: continue
            
            span_angle = -(val / total) * 360 * 16
            
            color_code = item.get('color', self.default_colors[i % len(self.default_colors)])
            color = QColor(color_code)
            
            painter.setBrush(QColor(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw Pie Slice
            painter.drawPie(int(cx - outer_radius), int(cy - outer_radius), 
                          int(outer_radius * 2), int(outer_radius * 2), 
                          int(start_angle), int(span_angle))
            
            start_angle += span_angle
            
        # Draw Inner Circle (to make it a Donut)
        painter.setBrush(QColor("#1E293B")) # Background color
        painter.drawEllipse(int(cx - inner_radius), int(cy - inner_radius), 
                          int(inner_radius * 2), int(inner_radius * 2))
        
        # Draw Legend
        lx = w - legend_width + 10
        ly = 50
        
        for i, item in enumerate(self.data):
            val = float(item.get('total', item.get('value', 0)))
            pct = (val / total) * 100
            label = item.get('label', item.get('method', 'Unknown'))
             # Shorten label if needed
            if len(label) > 15: label = label[:12] + "..."
            
            color_code = item.get('color', self.default_colors[i % len(self.default_colors)])
            
            # Rect
            painter.setBrush(QColor(color_code))
            painter.drawRect(int(lx), int(ly), 12, 12)
            
            # Text
            painter.setPen(QColor("#E2E8F0"))
            painter.drawText(int(lx + 20), int(ly + 11), f"{label} ({int(pct)}%)")
            
            ly += 25
