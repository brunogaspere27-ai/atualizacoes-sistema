"""
CW Chart - Componentes de gráficos profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Gráficos de linha, barra, donut
- Cores consistentes com tema CW
- Responsivo
- Aparência profissional
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from typing import List, Optional, Dict
from enum import Enum

from ui.theme.cw_theme import cw_theme, CWSpacing, CWRadius


class ChartType(Enum):
    """Tipos de gráfico"""
    LINE = "line"
    BAR = "bar"
    DONUT = "donut"


class CWChartWidget(QWidget):
    """Widget de gráfico base CW Transportadora"""
    
    def __init__(
        self,
        chart_type: ChartType,
        data: Dict,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._chart_type = chart_type
        self._data = data
        
        self.setMinimumHeight(200)
        self._apply_style()
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            CWChartWidget {{
                background-color: {c['bg_primary']};
                border: none;
            }}
        """)
    
    def paintEvent(self, event):
        """Desenha o gráfico"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._chart_type == ChartType.LINE:
            self._draw_line_chart(painter)
        elif self._chart_type == ChartType.BAR:
            self._draw_bar_chart(painter)
        elif self._chart_type == ChartType.DONUT:
            self._draw_donut_chart(painter)
    
    def _draw_line_chart(self, painter: QPainter):
        """Desenha gráfico de linha"""
        c = cw_theme.colors
        
        labels = self._data.get('labels', [])
        values = self._data.get('valores', [])
        
        if not values:
            return
        
        width = self.width() - 40
        height = self.height() - 60
        x_start = 30
        y_start = 30
        y_bottom = height + 20
        
        max_value = max(values) if values else 1
        if max_value == 0:
            max_value = 1
        
        # Draw grid lines
        painter.setPen(QPen(QColor(c['border_subtle']), 1))
        for i in range(5):
            y = y_start + (height / 4) * i
            painter.drawLine(x_start, int(y), x_start + int(width), int(y))
        
        # Draw line
        painter.setPen(QPen(QColor(c['primary']), 2))
        points = []
        
        step_x = width / (len(values) - 1) if len(values) > 1 else width
        
        for i, value in enumerate(values):
            x = x_start + (i * step_x)
            y = y_bottom - ((value / max_value) * height)
            points.append((x, y))
        
        for i in range(len(points) - 1):
            painter.drawLine(
                int(points[i][0]), int(points[i][1]),
                int(points[i+1][0]), int(points[i+1][1])
            )
        
        # Draw points
        painter.setBrush(QBrush(QColor(c['primary'])))
        for x, y in points:
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)
        
        # Draw labels
        painter.setPen(QColor(c['text_tertiary']))
        painter.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS))
        
        for i, label in enumerate(labels):
            if i < len(points):
                x = points[i][0]
                painter.drawText(int(x - 20), int(y_bottom + 20), label[:3])
    
    def _draw_bar_chart(self, painter: QPainter):
        """Desenha gráfico de barras"""
        c = cw_theme.colors
        
        labels = self._data.get('labels', [])
        values = self._data.get('valores', [])
        
        if not values:
            return
        
        width = self.width() - 40
        height = self.height() - 60
        x_start = 30
        y_start = 30
        y_bottom = height + 20
        
        max_value = max(values) if values else 1
        if max_value == 0:
            max_value = 1
        
        # Draw grid lines
        painter.setPen(QPen(QColor(c['border_subtle']), 1))
        for i in range(5):
            y = y_start + (height / 4) * i
            painter.drawLine(x_start, int(y), x_start + int(width), int(y))
        
        # Draw bars
        bar_width = (width / len(values)) * 0.6
        bar_spacing = (width / len(values)) * 0.4
        
        painter.setBrush(QBrush(QColor(c['primary'])))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i, value in enumerate(values):
            x = x_start + (i * (bar_width + bar_spacing)) + bar_spacing / 2
            bar_height = (value / max_value) * height
            y = y_bottom - bar_height
            
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
        
        # Draw labels
        painter.setPen(QColor(c['text_tertiary']))
        painter.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS))
        
        for i, label in enumerate(labels):
            x = x_start + (i * (bar_width + bar_spacing)) + bar_spacing / 2
            painter.drawText(int(x), int(y_bottom + 20), label[:3])
    
    def _draw_donut_chart(self, painter: QPainter):
        """Desenha gráfico de donut"""
        c = cw_theme.colors
        
        labels = self._data.get('labels', [])
        values = self._data.get('valores', [])
        
        if not values:
            return
        
        total = sum(values)
        if total == 0:
            return
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 40
        inner_radius = radius * 0.6
        
        colors = [c['primary'], c['success'], c['warning'], c['info'], c['error']]
        
        start_angle = 0
        
        for i, value in enumerate(values):
            if value == 0:
                continue
            
            span_angle = (value / total) * 360 * 16  # Qt usa 1/16 de grau
            
            painter.setBrush(QBrush(QColor(colors[i % len(colors)])))
            painter.setPen(Qt.PenStyle.NoPen)
            
            painter.drawPie(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2,
                int(start_angle), int(span_angle)
            )
            
            start_angle += span_angle
        
        # Draw inner circle (donut hole)
        painter.setBrush(QBrush(QColor(c['bg_primary'])))
        painter.drawEllipse(
            center_x - inner_radius, center_y - inner_radius,
            inner_radius * 2, inner_radius * 2
        )
        
        # Draw legend
        painter.setPen(QColor(c['text_secondary']))
        painter.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS))
        
        legend_x = 20
        legend_y = 20
        
        for i, (label, value) in enumerate(zip(labels, values)):
            color = colors[i % len(colors)]
            
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x, legend_y, 12, 12)
            
            painter.setPen(QColor(c['text_secondary']))
            painter.drawText(legend_x + 20, legend_y + 10, f"{label}: {value}")
            
            legend_y += 20


class CWChartCard(QWidget):
    """Card com gráfico CW Transportadora"""
    
    def __init__(
        self,
        title: str,
        chart_type: ChartType,
        data: Dict,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._title = title
        self._chart_type = chart_type
        self._data = data
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do card"""
        c = cw_theme.colors
        t = cw_theme.spacing
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(t.XL, t.XL, t.XL, t.XL)
        self.layout.setSpacing(t.MD)
        self.setLayout(self.layout)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_LG,
            bold=True
        ))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
            }}
        """)
        self.layout.addWidget(title_label)
        
        # Chart
        self.chart = CWChartWidget(self._chart_type, self._data)
        self.layout.addWidget(self.chart, 1)
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        r = cw_theme.radius
        
        self.setStyleSheet(f"""
            CWChartCard {{
                background-color: {c['bg_elevated']};
                border: 1px solid {c['border_subtle']};
                border-radius: {r.LG}px;
            }}
        """)
    
    def update_data(self, data: Dict):
        """Atualiza dados do gráfico"""
        self._data = data
        self.chart._data = data
        self.chart.update()
