"""
Premium Charts CW Transportadora - PySide6 + pyqtgraph

Componentes de gráficos profissionais inspirados em Power BI, Stripe Dashboard,
Linear Analytics, Grafana.
"""

import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QPainterPath, QConicalGradient
)
from typing import Optional, List, Tuple

from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor

try:
    import pyqtgraph as pg
    import numpy as np
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False


# ===================================================================== ChartCard (Premium Style)
class ChartCard(QFrame):
    """Card wrapper premium para gráficos com título e filtro de período."""

    PERIODS = ["Este mês", "Semana", "Ano", "Geral"]

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setObjectName("chartCard")
        self.setStyleSheet(f"""
        QFrame#chartCard {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['card_bg']}, stop:1 {c['card_hover']});
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame#chartCard:hover {{
            border-color: {c['border_strong']};
        }}
        """)

        # Sombra suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 6))
        self.setGraphicsEffect(shadow)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(t.SPACING_XL, t.SPACING_LG, t.SPACING_XL, t.SPACING_LG)
        self._layout.setSpacing(t.SPACING_MD)
        self.setLayout(self._layout)

        # Header elegante
        hdr = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
        title_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        # Period filter buttons modernos
        self._period_btns: List[QPushButton] = []
        self._active_period = "Este mês"
        for p in self.PERIODS:
            btn = QPushButton(p)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(26)
            btn.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
            self._style_period_btn(btn, p == self._active_period)
            btn.clicked.connect(lambda _, b=btn, period=p: self._set_period(period))
            hdr.addWidget(btn)
            self._period_btns.append(btn)

        self._layout.addLayout(hdr)
        self._chart_area = QVBoxLayout()
        self._layout.addLayout(self._chart_area)

    def _style_period_btn(self, btn: QPushButton, active: bool):
        c = theme_manager.colors
        t = theme_manager.tokens
        if active:
            btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['brand']}; color: #FFF;
                border: none; border-radius: {t.RADIUS_SM}px;
                padding: 3px 12px; font-weight: 700;
            }}
            """)
        else:
            btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {c['text_secondary']};
                border: 1px solid {c['border_subtle']}; border-radius: {t.RADIUS_SM}px;
                padding: 3px 12px; font-weight: 600;
            }}
            QPushButton:hover {{ color: {c['text_primary']}; border-color: {c['border_strong']}; }}
            """)

    def _set_period(self, period: str):
        self._active_period = period
        for btn in self._period_btns:
            self._style_period_btn(btn, btn.text() == period)

    def set_chart_widget(self, widget: QWidget):
        """Adiciona o widget de gráfico na área do card."""
        # Clear existing
        while self._chart_area.count():
            item = self._chart_area.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._chart_area.addWidget(widget)


# ===================================================================== LineChart (ApexCharts Style)
class LineChart(QWidget):
    """Gráfico de linhas premium estilo ApexCharts com gradientes e eixos minimalistas."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        if not HAS_PYQTGRAPH:
            self._fallback_label = QLabel("pyqtgraph não instalado")
            self._fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return

        self.setMinimumHeight(280)
        c = theme_manager.colors

        # pyqtgraph config
        pg.setConfigOptions(antialias=True, background=c['chart_bg'], foreground=c['chart_text'])

        self._plot = pg.PlotWidget()
        self._plot.setBackground(c['chart_bg'])
        self._plot.showGrid(x=True, y=True, alpha=0.08)
        self._plot.getAxis('left').setPen(QColor(c['chart_grid']))
        self._plot.getAxis('left').setTextPen(QColor(c['chart_text']))
        self._plot.getAxis('bottom').setPen(QColor(c['chart_grid']))
        self._plot.getAxis('bottom').setTextPen(QColor(c['chart_text']))
        self._plot.getAxis('left').setStyle(tickLength=0, tickFont=QFont("Arial", 8))
        self._plot.getAxis('bottom').setStyle(tickLength=0, tickFont=QFont("Arial", 8))
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.setMenuEnabled(False)
        self._plot.enableAutoRange(False, False)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        self.setLayout(layout)

    def set_data(self, x: list, y: list, color: str = None, fill: bool = True):
        if not HAS_PYQTGRAPH:
            return
        c = theme_manager.colors
        line_color = color or c['chart_1']

        self._plot.clear()

        # Line suave com curva
        pen = pg.mkPen(color=line_color, width=3, style=Qt.PenStyle.SolidLine)
        curve = self._plot.plot(x, y, pen=pen, connect='finite')

        # Fill com gradiente
        if fill:
            fill_color = QColor(line_color)
            fill_color.setAlpha(25)
            fill_curve = pg.FillBetweenItem(
                pg.PlotDataItem(x, y),
                pg.PlotDataItem(x, [0] * len(y)),
                brush=QBrush(fill_color)
            )
            self._plot.addItem(fill_curve)

        # Pontos discretos
        for i, (xi, yi) in enumerate(zip(x, y)):
            scatter = pg.ScatterPlotItem([xi], [yi], size=8, pen=pg.mkPen(None), brush=pg.mkBrush(line_color))
            self._plot.addItem(scatter)

        # Auto range minimalista
        if len(y) > 0:
            y_min = min(y) * 0.95 if min(y) > 0 else min(y) * 1.05
            y_max = max(y) * 1.08
            self._plot.setXRange(0, len(x) - 1, padding=0.05)
            self._plot.setYRange(y_min, y_max, padding=0.05)


# ===================================================================== BarChart (pyqtgraph)
class BarChart(QWidget):
    """Gráfico de barras premium."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        if not HAS_PYQTGRAPH:
            return
        self.setMinimumHeight(250)
        c = theme_manager.colors
        pg.setConfigOptions(antialias=True, background=c['chart_bg'], foreground=c['chart_text'])

        self._plot = pg.PlotWidget()
        self._plot.setBackground(c['chart_bg'])
        self._plot.showGrid(x=False, y=True, alpha=0.15)
        self._plot.getAxis('left').setPen(QColor(c['chart_grid']))
        self._plot.getAxis('left').setTextPen(QColor(c['chart_text']))
        self._plot.hideAxis('bottom')
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.setMenuEnabled(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot)
        self.setLayout(layout)

    def set_data(self, labels: list, values: list, color: str = None):
        if not HAS_PYQTGRAPH:
            return
        c = theme_manager.colors
        bar_color = color or c['chart_1']

        self._plot.clear()
        x = list(range(len(values)))
        bg = pg.BarGraphItem(x=x, height=values, width=0.6, brush=QColor(bar_color))
        self._plot.addItem(bg)

        if len(values) > 0:
            y_max = max(values) * 1.15
            self._plot.setXRange(-0.5, len(values) - 0.5, padding=0)
            self._plot.setYRange(0, y_max, padding=0)


# ===================================================================== DonutChart (Custom QPainter)
class DonutChart(QWidget):
    """Gráfico de rosca custom-painted com animação."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data: List[Tuple[str, float, str]] = []  # (label, value, color)
        self._center_text = ""
        self._anim_progress = 0.0
        self.setMinimumSize(200, 200)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_step)

    def set_data(self, data: List[Tuple[str, float]], center_text: str = ""):
        """data: [(label, value), ...]"""
        colors = theme_manager.get_chart_colors()
        self._data = [(label, value, colors[i % len(colors)]) for i, (label, value) in enumerate(data)]
        self._center_text = center_text
        self._anim_progress = 0.0
        self._timer.start(16)

    def _animate_step(self):
        self._anim_progress = min(1.0, self._anim_progress + 0.04)
        self.update()
        if self._anim_progress >= 1.0:
            self._timer.stop()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h)
        cx, cy = w / 2, h / 2
        outer_r = size / 2 - 8
        inner_r = outer_r * 0.62

        total = sum(v for _, v, _ in self._data)
        if total == 0:
            p.end()
            return

        start_angle = -90 * 16  # Start from top
        gap = 2 * 16  # 2 degree gap between segments

        for label, value, color in self._data:
            span = int((value / total) * 360 * 16 * self._anim_progress) - gap
            if span <= 0:
                continue
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(color))
            p.drawPie(
                int(cx - outer_r), int(cy - outer_r),
                int(outer_r * 2), int(outer_r * 2),
                start_angle, span
            )
            start_angle += span + gap

        # Inner circle (donut hole)
        c = theme_manager.colors
        p.setBrush(QColor(c['card_bg']))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - inner_r), int(cy - inner_r), int(inner_r * 2), int(inner_r * 2))

        # Center text
        if self._center_text:
            t = theme_manager.tokens
            p.setFont(theme_manager.get_font(t.FONT_SIZE_2XL, bold=True))
            p.setPen(QColor(c['text_primary']))
            p.drawText(
                int(cx - outer_r), int(cy - inner_r), int(outer_r * 2), int(inner_r * 2),
                Qt.AlignmentFlag.AlignCenter, self._center_text
            )
        p.end()


# ===================================================================== GaugeChart (Custom QPainter)
class GaugeChart(QWidget):
    """Gauge circular para KPIs e metas."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._value = 0.0  # 0.0 to 1.0
        self._label = ""
        self._anim_value = 0.0
        self.setMinimumSize(160, 120)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_step)

    def set_value(self, value: float, label: str = ""):
        self._value = max(0.0, min(1.0, value))
        self._label = label
        self._anim_value = 0.0
        self._timer.start(16)

    def _animate_step(self):
        diff = self._value - self._anim_value
        if abs(diff) < 0.005:
            self._anim_value = self._value
            self._timer.stop()
        else:
            self._anim_value += diff * 0.1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = theme_manager.colors
        t = theme_manager.tokens

        w, h = self.width(), self.height()
        size = min(w, h * 1.8)
        cx = w / 2
        cy = h * 0.65
        r = size / 2 - 10

        # Background arc (180 degrees)
        pen = QPen(QColor(c['bg_tertiary']))
        pen.setWidthF(r * 0.18)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        rect_x = int(cx - r)
        rect_y = int(cy - r)
        rect_s = int(r * 2)
        p.drawArc(rect_x, rect_y, rect_s, rect_s, 0, 180 * 16)

        # Value arc
        color = c['success'] if self._anim_value >= 0.7 else c['warning'] if self._anim_value >= 0.4 else c['error']
        pen = QPen(QColor(color))
        pen.setWidthF(r * 0.18)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        span = int(self._anim_value * 180 * 16)
        p.drawArc(rect_x, rect_y, rect_s, rect_s, 180 * 16, span)

        # Value text
        pct_text = f"{int(self._anim_value * 100)}%"
        p.setFont(theme_manager.get_font(t.FONT_SIZE_2XL, bold=True))
        p.setPen(QColor(c['text_primary']))
        p.drawText(int(cx - r), int(cy - r), int(r * 2), int(r * 2),
                   Qt.AlignmentFlag.AlignCenter, pct_text)

        # Label
        if self._label:
            p.setFont(theme_manager.get_font(t.FONT_SIZE_XS))
            p.setPen(QColor(c['text_secondary']))
            p.drawText(int(cx - r), int(cy + 4), int(r * 2), 24,
                       Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()


# ===================================================================== SparklineChart (Custom QPainter)
class SparklineChart(QWidget):
    """Mini gráfico inline para KPICards."""

    def __init__(self, width: int = 80, height: int = 28, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._data: List[float] = []
        self._color: Optional[str] = None

    def set_data(self, data: List[float], color: str = None):
        self._data = data
        self._color = color
        self.update()

    def paintEvent(self, event):
        if not self._data or len(self._data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = theme_manager.colors
        color = QColor(self._color or c['chart_1'])

        w, h = self.width(), self.height()
        mn, mx = min(self._data), max(self._data)
        rng = mx - mn if mx != mn else 1.0

        # Line
        pen = QPen(color)
        pen.setWidthF(1.5)
        p.setPen(pen)

        points = []
        for i, v in enumerate(self._data):
            x = (i / (len(self._data) - 1)) * w
            y = h - ((v - mn) / rng) * (h - 4) - 2
            points.append(QPointF(x, y))

        for i in range(len(points) - 1):
            p.drawLine(points[i], points[i + 1])

        # Fill below
        fill_color = QColor(color)
        fill_color.setAlpha(25)
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)
        path.lineTo(QPointF(w, h))
        path.lineTo(QPointF(0, h))
        path.closeSubpath()
        p.fillPath(path, QBrush(fill_color))
        p.end()


# ===================================================================== MultiLineChart (pyqtgraph)
class MultiLineChart(QWidget):
    """Gráfico de múltiplas linhas (ex.: Receita x Despesa) com legenda superior."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._legend_layout: Optional[QHBoxLayout] = None
        self._legend_widget: Optional[QWidget] = None

        if not HAS_PYQTGRAPH:
            self._fallback_label = QLabel("pyqtgraph não instalado")
            self._fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout = QVBoxLayout()
            layout.addWidget(self._fallback_label)
            self.setLayout(layout)
            return

        self.setMinimumHeight(260)
        c = theme_manager.colors
        pg.setConfigOptions(antialias=True, background=c['chart_bg'], foreground=c['chart_text'])

        self._plot = pg.PlotWidget()
        self._plot.setBackground(c['chart_bg'])
        self._plot.showGrid(x=False, y=True, alpha=0.15)
        self._plot.getAxis('left').setPen(QColor(c['chart_grid']))
        self._plot.getAxis('left').setTextPen(QColor(c['chart_text']))
        self._plot.getAxis('bottom').setPen(QColor(c['chart_grid']))
        self._plot.getAxis('bottom').setTextPen(QColor(c['chart_text']))
        self._plot.hideAxis('bottom')
        self._plot.setMouseEnabled(x=False, y=False)
        self._plot.setMenuEnabled(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._legend_widget = QWidget()
        self._legend_widget.setStyleSheet("background: transparent;")
        self._legend_layout = QHBoxLayout()
        self._legend_layout.setContentsMargins(0, 0, 0, 0)
        self._legend_layout.setSpacing(16)
        self._legend_layout.addStretch()
        self._legend_widget.setLayout(self._legend_layout)

        layout.addWidget(self._legend_widget)
        layout.addWidget(self._plot)
        self.setLayout(layout)

    def _add_legend_item(self, label: str, color: str):
        t = theme_manager.tokens
        c = theme_manager.colors
        item = QWidget()
        item.setStyleSheet("background: transparent;")
        il = QHBoxLayout()
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(6)
        item.setLayout(il)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
        il.addWidget(dot)

        lbl = QLabel(label)
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        il.addWidget(lbl)

        self._legend_layout.insertWidget(self._legend_layout.count() - 1, item)

    def set_series(self, x_labels: list, series: List[Tuple[str, list, str]]):
        """series: [(nome, valores, cor), ...]"""
        if not HAS_PYQTGRAPH:
            return

        # Limpar legenda anterior
        while self._legend_layout.count() > 1:
            item = self._legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._plot.clear()
        y_all = []
        for nome, valores, cor in series:
            self._add_legend_item(nome, cor)
            pen = pg.mkPen(color=cor, width=2.5)
            self._plot.plot(list(range(len(valores))), valores, pen=pen)

            fill_color = QColor(cor)
            fill_color.setAlpha(22)
            fill_curve = pg.FillBetweenItem(
                pg.PlotDataItem(list(range(len(valores))), valores),
                pg.PlotDataItem(list(range(len(valores))), [0] * len(valores)),
                brush=QBrush(fill_color)
            )
            self._plot.addItem(fill_curve)
            y_all.extend(valores)

        n = len(x_labels)
        if n > 1:
            self._plot.setXRange(0, n - 1, padding=0)
        if y_all:
            y_max = max(y_all) * 1.15 if max(y_all) > 0 else 1
            y_min = min(0, min(y_all))
            self._plot.setYRange(y_min, y_max, padding=0)
