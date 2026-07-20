"""
Aurora Charts v1.0 - CW Transportadora
Gráficos profissionais estilo Stripe/Power BI com Aurora Design System

Features:
- Gradientes suaves
- Cantos arredondados
- Tooltips modernos
- Animações de entrada
- Paleta harmoniosa
"""

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QFont, QPainterPath
)
from pyqtgraph import PlotWidget, BarGraphItem, PlotCurveItem
import pyqtgraph as pg

from telas.theme_aurora import aurora_theme_manager, AccentColor
import re


def _parse_color(color_str: str) -> QColor:
    """Converte cor (hex ou rgba()) para QColor."""
    if color_str.startswith('#'):
        return QColor(color_str)
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = int(float(m.group(4)) * 255) if m.group(4) else 255
        return QColor(r, g, b, a)
    return QColor(color_str)


class AuroraChartCard(QFrame):
    """Card de gráfico com glassmorphism e glow."""

    def __init__(self, title: str, icon_name: str = None,
                 accent_color: AccentColor = AccentColor.AURORA,
                 parent=None):
        super().__init__(parent)
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens
        self._accent = accent_color

        self.setObjectName("auroraChartCard")
        glow = aurora_theme_manager.get_glow(accent_color)
        accent = aurora_theme_manager.get_accent(accent_color)

        self.setStyleSheet(f"""
        QFrame#auroraChartCard {{
            background: {c['card_bg']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        QFrame#auroraChartCard:hover {{
            border-color: {accent};
            box-shadow: 0 0 30px {glow};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_XL, t.SPACING_XL, t.SPACING_XL, t.SPACING_XL)
        layout.setSpacing(t.SPACING_LG)
        self.setLayout(layout)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(t.SPACING_MD)

        if icon_name:
            from utils.icons import get_pixmap
            ico = QLabel()
            ico.setFixedSize(40, 40)
            ico.setStyleSheet(f"""
            QLabel {{
                background: {aurora_theme_manager.get_color(accent_color.value + '_soft')};
                border-radius: 12px;
            }}
            """)
            ico.setPixmap(get_pixmap(icon_name, (20, 20), accent))
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hdr.addWidget(ico)

        title_lbl = QLabel(title)
        title_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
        title_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        w = QWidget()
        w.setStyleSheet("background: transparent;")
        w.setLayout(hdr)
        layout.addWidget(w)


class AuroraLineChart(QWidget):
    """Gráfico de linha premium estilo Linear com tooltips interativos."""

    def __init__(self, accent_color: AccentColor = AccentColor.AURORA, parent=None):
        super().__init__(parent)
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens
        self._accent = accent_color
        self._hover_data = None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # PlotWidget com tema refinado estilo Linear
        self.plot = PlotWidget()
        self.plot.setBackground(c['chart_bg'])
        self.plot.showGrid(x=True, y=True, alpha=0.1)  # Grid muito sutil
        self.plot.getAxis('left').setPen(pg.mkPen(color=_parse_color(c['border_subtle']), width=1))
        self.plot.getAxis('bottom').setPen(pg.mkPen(color=_parse_color(c['border_subtle']), width=1))
        self.plot.getAxis('left').setTextPen(pg.mkPen(color=c['text_tertiary'], width=1))
        self.plot.getAxis('bottom').setTextPen(pg.mkPen(color=c['text_tertiary'], width=1))

        # Configurar fonte refinada
        font = aurora_theme_manager.get_font(t.FONT_SIZE_XS)
        self.plot.getAxis('left').tickFont = font
        self.plot.getAxis('bottom').tickFont = font

        # Remover bordas
        self.plot.setContentsMargins(0, 0, 0, 0)
        self.plot.plotItem.setContentsMargins(0, 0, 0, 0)

        # Habilitar hover para tooltips
        self.plot.setMouseEnabled(x=True, y=False)
        self.plot.scene().sigMouseMoved.connect(self._on_mouse_move)

        layout.addWidget(self.plot)

        self._curve = None
        self._fill = None
        self._animation_progress = 0.0
        self._x_data = []
        self._y_data = []

    def _on_mouse_move(self, pos):
        """Handle mouse move para tooltip interativo."""
        if not self._x_data or not self._y_data:
            return
        
        # Encontrar ponto mais próximo
        mouse_point = self.plot.plotItem.vb.mapSceneToView(pos)
        x_pos = mouse_point.x()
        
        # Encontrar índice mais próximo
        if len(self._x_data) > 0:
            idx = min(range(len(self._x_data)), key=lambda i: abs(self._x_data[i] - x_pos))
            self._hover_data = (self._x_data[idx], self._y_data[idx])
            self.update()

    def set_data(self, x_data, y_data, label: str = ""):
        """Define os dados do gráfico."""
        c = aurora_theme_manager.colors
        accent = aurora_theme_manager.get_accent(self._accent)
        accent_start = aurora_theme_manager.get_color(self._accent.value + '_start')
        accent_end = aurora_theme_manager.get_color(self._accent.value + '_end')

        # Armazenar dados para hover
        self._x_data = list(x_data)
        self._y_data = list(y_data)

        # Limpar gráfico anterior
        self.plot.clear()

        # Criar curva com stroke refinado estilo Linear
        self._curve = PlotCurveItem(
            x=x_data,
            y=y_data,
            pen=pg.mkPen(color=accent, width=2.5),  # Stroke mais sutil
            name=label
        )
        self.plot.addItem(self._curve)

        # Criar área preenchida com gradient refinado
        path = QPainterPath()
        if len(x_data) > 0:
            path.moveTo(x_data[0], 0)
            for x, y in zip(x_data, y_data):
                path.lineTo(x, y)
            path.lineTo(x_data[-1], 0)
            path.closeSubpath()

        # Gradient fill muito sutil estilo Linear
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0, QColor(accent + "30"))  # 19% opacity
        gradient.setColorAt(1, QColor(accent + "00"))  # 0% opacity
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)

        brush = QBrush(gradient)
        fill_item = pg.PlotCurveItem(
            x=x_data + [x_data[-1], x_data[0]],
            y=y_data + [0, 0],
            pen=pg.mkPen(None),
            brush=brush
        )
        self.plot.addItem(fill_item)

        # Animação de entrada suave (120ms estilo Linear)
        self._animate_curve(x_data, y_data)

    def _animate_curve(self, x_data, y_data):
        """Anima a curva de entrada com easing estilo Linear."""
        self._animation_progress = 0.0
        self._full_x = x_data
        self._full_y = y_data

        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._update_animation)
        self._anim_timer.start(8)  # ~120fps para animação suave

    def _update_animation(self):
        """Atualiza frame da animação com easing."""
        # Easing function estilo Linear (ease-out cubic)
        self._animation_progress += 0.015
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            self._anim_timer.stop()

        # Easing
        eased = 1 - pow(1 - self._animation_progress, 3)
        
        # Mostrar porcentagem dos dados
        n_points = int(len(self._full_y) * eased)
        if n_points > 0:
            x_visible = self._full_x[:n_points]
            y_visible = self._full_y[:n_points]
            self._curve.setData(x=x_visible, y=y_visible)

    def clear(self):
        """Limpa o gráfico."""
        self.plot.clear()


class AuroraBarChart(QWidget):
    """Gráfico de barras premium estilo Linear."""

    def __init__(self, accent_color: AccentColor = AccentColor.AURORA, parent=None):
        super().__init__(parent)
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens
        self._accent = accent_color

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # PlotWidget com tema refinado estilo Linear
        self.plot = PlotWidget()
        self.plot.setBackground(c['chart_bg'])
        self.plot.showGrid(x=True, y=True, alpha=0.1)  # Grid muito sutil
        self.plot.getAxis('left').setPen(pg.mkPen(color=_parse_color(c['border_subtle']), width=1))
        self.plot.getAxis('bottom').setPen(pg.mkPen(color=_parse_color(c['border_subtle']), width=1))
        self.plot.getAxis('left').setTextPen(pg.mkPen(color=c['text_tertiary'], width=1))
        self.plot.getAxis('bottom').setTextPen(pg.mkPen(color=c['text_tertiary'], width=1))

        font = aurora_theme_manager.get_font(t.FONT_SIZE_XS)
        self.plot.getAxis('left').tickFont = font
        self.plot.getAxis('bottom').tickFont = font

        self.plot.setContentsMargins(0, 0, 0, 0)
        self.plot.plotItem.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.plot)

        self._bar_item = None
        self._animation_progress = 0.0

    def set_data(self, x_data, y_data, labels=None):
        """Define os dados do gráfico de barras com gradientes refinados."""
        c = aurora_theme_manager.colors
        accent = aurora_theme_manager.get_accent(self._accent)
        accent_start = aurora_theme_manager.get_color(self._accent.value + '_start')
        accent_end = aurora_theme_manager.get_color(self._accent.value + '_end')

        self.plot.clear()

        # Criar gradiente vertical refinado estilo Linear
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0, QColor(accent_start))
        gradient.setColorAt(1, QColor(accent_end))
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        brush = QBrush(gradient)

        # Criar barras com stroke sutil
        self._bar_item = BarGraphItem(
            x=x_data,
            height=y_data,
            width=0.5,  # Barras mais finas estilo Linear
            brush=brush,
            pen=pg.mkPen(color=accent + "40", width=1)  # Stroke muito sutil
        )
        self.plot.addItem(self._bar_item)

        # Configurar labels do eixo X
        if labels:
            ticks = [(i + 0.5, labels[i]) for i in range(len(labels))]
            self.plot.getAxis('bottom').setTicks([ticks])

        # Animação de entrada suave
        self._animate_bars(y_data)

    def _animate_bars(self, y_data):
        """Anima as barras de entrada com easing estilo Linear."""
        self._animation_progress = 0.0
        self._full_y = y_data

        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._update_animation)
        self._anim_timer.start(8)  # ~120fps para animação suave

    def _update_animation(self):
        """Atualiza frame da animação com easing."""
        # Easing function estilo Linear (ease-out cubic)
        self._animation_progress += 0.015
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            self._anim_timer.stop()

        # Easing
        eased = 1 - pow(1 - self._animation_progress, 3)
        
        # Escalar altura das barras
        scaled_y = [y * eased for y in self._full_y]
        self._bar_item.setOpts(height=scaled_y)

    def clear(self):
        """Limpa o gráfico."""
        self.plot.clear()


class AuroraMultiLineChart(QWidget):
    """Gráfico de múltiplas linhas com gradientes."""

    def __init__(self, accent_colors: list = None, parent=None):
        super().__init__(parent)
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        self._accent_colors = accent_colors or [
            AccentColor.AURORA, AccentColor.OCEAN, AccentColor.FOREST
        ]

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.plot = PlotWidget()
        self.plot.setBackground(c['chart_bg'])
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.getAxis('left').setPen(pg.mkPen(color=_parse_color(c['chart_grid']), width=1))
        self.plot.getAxis('bottom').setPen(pg.mkPen(color=_parse_color(c['chart_grid']), width=1))
        self.plot.getAxis('left').setTextPen(pg.mkPen(color=c['chart_text'], width=1))
        self.plot.getAxis('bottom').setTextPen(pg.mkPen(color=c['chart_text'], width=1))

        font = aurora_theme_manager.get_font(t.FONT_SIZE_XS)
        self.plot.getAxis('left').tickFont = font
        self.plot.getAxis('bottom').tickFont = font

        self.plot.setContentsMargins(0, 0, 0, 0)
        self.plot.plotItem.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.plot)

        self._curves = []

    def set_data(self, series_data: list, labels: list = None):
        """
        series_data: list of (x_data, y_data) tuples
        labels: list of series labels
        """
        self.plot.clear()
        self._curves = []

        for idx, (x_data, y_data) in enumerate(series_data):
            accent = self._accent_colors[idx % len(self._accent_colors)]
            color = aurora_theme_manager.get_accent(accent)

            curve = PlotCurveItem(
                x=x_data,
                y=y_data,
                pen=pg.mkPen(color=color, width=2),
                name=labels[idx] if labels and idx < len(labels) else f"Série {idx+1}"
            )
            self.plot.addItem(curve)
            self._curves.append(curve)

        if labels:
            self.plot.addLegend()

    def clear(self):
        """Limpa o gráfico."""
        self.plot.clear()


class AuroraSparkline(QWidget):
    """Sparkline minimalista para KPI cards."""

    def __init__(self, accent_color: AccentColor = AccentColor.AURORA, parent=None):
        super().__init__(parent)
        self._accent = accent_color
        self._data = []
        self.setFixedHeight(40)

    def set_data(self, data: list):
        """Define os dados do sparkline."""
        self._data = data
        self.update()

    def paintEvent(self, event):
        """Desenha o sparkline."""
        if not self._data or len(self._data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        c = aurora_theme_manager.colors
        accent = aurora_theme_manager.get_accent(self._accent)
        accent_soft = aurora_theme_manager.get_color(self._accent.value + '_soft')

        w = self.width()
        h = self.height()

        # Normalizar dados
        data_min = min(self._data)
        data_max = max(self._data)
        data_range = data_max - data_min if data_max != data_min else 1

        # Criar path
        path = QPainterPath()
        x_step = w / (len(self._data) - 1)

        for i, value in enumerate(self._data):
            x = i * x_step
            y = h - ((value - data_min) / data_range) * h * 0.8 - h * 0.1
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # Desenhar linha
        pen = QPen(_parse_color(accent))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        # Desenhar área preenchida
        fill_path = QPainterPath(path)
        fill_path.lineTo(w, h)
        fill_path.lineTo(0, h)
        fill_path.closeSubpath()

        brush = QBrush(_parse_color(accent_soft))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(fill_path)
