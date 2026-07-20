"""
Live Widgets — CW Transportadora
Widgets vivos para o Dashboard: caminhões, caixa, pendências, timeline.
Todos com animação de valor (count-up), refresh via QTimer, visual premium.
"""

from typing import Optional, List, Tuple
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QSizePolicy, QGraphicsDropShadowEffect, QScrollArea,
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QRectF
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QLinearGradient,
    QFont, QPainterPath, QRadialGradient,
)

from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor
from utils.icons import get_icon, get_pixmap


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _card_shadow(widget: QWidget, blur: int = 20, y: int = 4, alpha: int = 40):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setYOffset(y)
    shadow.setXOffset(0)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


# ══════════════════════════════════════════════════════════════════════════════
# LiveValueLabel — anima número de 0 → alvo (count-up)
# ══════════════════════════════════════════════════════════════════════════════
class LiveValueLabel(QLabel):
    """QLabel que anima o valor numérico com count-up suave."""

    def __init__(self, prefix: str = "", suffix: str = "", decimals: int = 0,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._prefix = prefix
        self._suffix = suffix
        self._decimals = decimals
        self._current = 0.0
        self._target = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._step)
        self._update_text()

    def set_value(self, value: float, animate: bool = True):
        self._target = float(value)
        if animate and abs(self._target - self._current) > 0.01:
            self._timer.start()
        else:
            self._current = self._target
            self._update_text()

    def _step(self):
        diff = self._target - self._current
        if abs(diff) < 0.5:
            self._current = self._target
            self._timer.stop()
        else:
            self._current += diff * 0.12
        self._update_text()

    def _update_text(self):
        if self._decimals == 0:
            num = f"{int(self._current):,}".replace(",", ".")
        else:
            num = f"{self._current:,.{self._decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.setText(f"{self._prefix}{num}{self._suffix}")


# ══════════════════════════════════════════════════════════════════════════════
# TrendBadge — ▲ +18% / ▼ -5%
# ══════════════════════════════════════════════════════════════════════════════
class TrendBadge(QFrame):
    def __init__(self, pct: float = 0.0, parent=None):
        super().__init__(parent)
        self._build(pct)

    def _build(self, pct: float):
        c = theme_manager.colors
        t = theme_manager.tokens
        is_up = pct >= 0
        color = c["success"] if is_up else c["error"]
        bg    = c["success_soft"] if is_up else c["error_soft"]
        arrow = "▲" if is_up else "▼"
        sign  = "+" if is_up else ""

        self.setStyleSheet(f"""
        QFrame {{ background: {bg}; border-radius: {t.RADIUS_FULL}px; }}
        """)
        hl = QHBoxLayout()
        hl.setContentsMargins(6, 3, 6, 3)
        hl.setSpacing(2)
        self.setLayout(hl)

        lbl = QLabel(f"{arrow} {sign}{pct:.1f}%")
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
        hl.addWidget(lbl)

    def update_pct(self, pct: float):
        # Limpar e reconstruir
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build(pct)


# ══════════════════════════════════════════════════════════════════════════════
# MiniProgressBar — barra fina de progresso custom
# ══════════════════════════════════════════════════════════════════════════════
class MiniProgressBar(QWidget):
    def __init__(self, color: str = "#6366F1", height: int = 5, parent=None):
        super().__init__(parent)
        self._color = color
        self._pct = 0.0
        self._anim_pct = 0.0
        self.setFixedHeight(height)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._step)

    def set_pct(self, pct: float):
        self._pct = max(0.0, min(1.0, pct))
        self._timer.start()

    def _step(self):
        diff = self._pct - self._anim_pct
        if abs(diff) < 0.002:
            self._anim_pct = self._pct
            self._timer.stop()
        else:
            self._anim_pct += diff * 0.10
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = theme_manager.colors
        r = self.height() // 2
        # Track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c["bg_overlay"]))
        p.drawRoundedRect(0, 0, self.width(), self.height(), r, r)
        # Fill
        fill_w = int(self.width() * self._anim_pct)
        if fill_w > 0:
            grad = QLinearGradient(0, 0, fill_w, 0)
            base = QColor(self._color)
            grad.setColorAt(0, base)
            bright = QColor(base); bright.setAlpha(200)
            grad.setColorAt(1, bright)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, 0, fill_w, self.height(), r, r)
        p.end()


# ══════════════════════════════════════════════════════════════════════════════
# BaseWidget — card base com sombra, título e refresh timer
# ══════════════════════════════════════════════════════════════════════════════
class BaseWidget(QFrame):
    """Base para todos os live widgets. Fornece card visual + auto-refresh."""

    refresh_requested = Signal()

    def __init__(self, title: str, icon: str, accent: str,
                 refresh_ms: int = 30_000, parent=None):
        super().__init__(parent)
        self._accent = accent
        self._refresh_ms = refresh_ms
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setObjectName("liveWidget")
        self.setStyleSheet(f"""
        QFrame#liveWidget {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame#liveWidget:hover {{
            border-color: {accent}55;
        }}
        """)
        _card_shadow(self, blur=24, y=4, alpha=30)

        self._root_layout = QVBoxLayout()
        self._root_layout.setContentsMargins(t.SPACING_LG, t.SPACING_LG, t.SPACING_LG, t.SPACING_LG)
        self._root_layout.setSpacing(t.SPACING_SM)
        self.setLayout(self._root_layout)

        # Header
        hdr = QHBoxLayout()
        hdr.setSpacing(t.SPACING_SM)

        ico_wrap = QFrame()
        ico_wrap.setFixedSize(32, 32)
        ico_wrap.setStyleSheet(f"""
        QFrame {{
            background: {accent}22;
            border-radius: {t.RADIUS_SM}px;
            border: 1px solid {accent}44;
        }}
        """)
        il = QVBoxLayout(); il.setContentsMargins(0,0,0,0); ico_wrap.setLayout(il)
        ico_lbl = QLabel()
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico_lbl.setPixmap(get_pixmap(icon, color=accent))
        il.addWidget(ico_lbl)
        hdr.addWidget(ico_wrap)

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        title_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 0.8px;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        # Pulsing dot (indica "live")
        self._live_dot = QLabel()
        self._live_dot.setFixedSize(7, 7)
        self._live_dot.setStyleSheet(f"background: {accent}; border-radius: 3px;")
        hdr.addWidget(self._live_dot)
        self._pulse_state = True
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(1200)
        self._pulse_timer.timeout.connect(self._pulse_dot)
        self._pulse_timer.start()

        hdr_w = QWidget(); hdr_w.setStyleSheet("background: transparent;"); hdr_w.setLayout(hdr)
        self._root_layout.addWidget(hdr_w)

        # Content area (subclasses add here)
        self._content_layout = QVBoxLayout()
        self._content_layout.setSpacing(t.SPACING_SM)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        content_w = QWidget(); content_w.setStyleSheet("background: transparent;")
        content_w.setLayout(self._content_layout)
        self._root_layout.addWidget(content_w)

        # Auto-refresh
        if refresh_ms > 0:
            self._refresh_timer = QTimer(self)
            self._refresh_timer.setInterval(refresh_ms)
            self._refresh_timer.timeout.connect(self.refresh_requested.emit)
            self._refresh_timer.start()

    def _pulse_dot(self):
        self._pulse_state = not self._pulse_state
        alpha = "ff" if self._pulse_state else "40"
        self._live_dot.setStyleSheet(
            f"background: {self._accent}{alpha}; border-radius: 3px;"
        )

    def add_content(self, widget: QWidget):
        self._content_layout.addWidget(widget)

    def add_content_layout(self, layout):
        self._content_layout.addLayout(layout)


# ══════════════════════════════════════════════════════════════════════════════
# TruckStatusWidget — caminhões online / oficina / parado
# ══════════════════════════════════════════════════════════════════════════════
class TruckStatusWidget(BaseWidget):
    """Widget de status da frota com barras de status animadas."""

    def __init__(self, parent=None):
        c = theme_manager.colors
        super().__init__("Frota", "truck", c["sky"], refresh_ms=20_000, parent=parent)
        self._build_content()

    def _build_content(self):
        c = theme_manager.colors
        t = theme_manager.tokens

        # Número grande central
        total_row = QHBoxLayout()
        total_row.setContentsMargins(0, 4, 0, 0)

        self._total_lbl = LiveValueLabel(suffix=" veículos")
        self._total_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_2XL, bold=True))
        self._total_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        total_row.addWidget(self._total_lbl)
        total_row.addStretch()
        self.add_content_layout(total_row)

        # Status rows
        self._status_rows = {}
        status_cfg = [
            ("online",  "🟢 Online",   c["success"]),
            ("oficina", "🔧 Oficina",   c["warning"]),
            ("parado",  "⚫ Parado",    c["text_tertiary"]),
        ]
        for key, label_text, color in status_cfg:
            row = QHBoxLayout()
            row.setSpacing(t.SPACING_SM)

            lbl = QLabel(label_text)
            lbl.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
            lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            lbl.setFixedWidth(90)
            row.addWidget(lbl)

            bar = MiniProgressBar(color=color, height=6)
            bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row.addWidget(bar, 1)

            count_lbl = QLabel("0")
            count_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
            count_lbl.setStyleSheet(f"color: {color}; background: transparent;")
            count_lbl.setFixedWidth(24)
            count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(count_lbl)

            self._status_rows[key] = (bar, count_lbl)
            self.add_content_layout(row)

    def update_data(self, online: int, oficina: int, parado: int):
        total = online + oficina + parado
        if total == 0:
            total = 1
        self._total_lbl.set_value(total)
        for key, count in [("online", online), ("oficina", oficina), ("parado", parado)]:
            bar, lbl = self._status_rows[key]
            bar.set_pct(count / total)
            lbl.setText(str(count))


# ══════════════════════════════════════════════════════════════════════════════
# CashWidget — caixa do dia com trend
# ══════════════════════════════════════════════════════════════════════════════
class CashWidget(BaseWidget):
    """Widget financeiro do dia com valor animado e trend vs ontem."""

    def __init__(self, parent=None):
        c = theme_manager.colors
        super().__init__("Caixa Hoje", "money", c["emerald"], refresh_ms=15_000, parent=parent)
        self._build_content()

    def _build_content(self):
        c = theme_manager.colors
        t = theme_manager.tokens

        self._value_lbl = LiveValueLabel(prefix="R$ ", decimals=2)
        self._value_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_3XL, bold=True))
        self._value_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        self.add_content(self._value_lbl)

        trend_row = QHBoxLayout()
        self._trend_badge = TrendBadge(0.0)
        trend_row.addWidget(self._trend_badge)
        vs_lbl = QLabel("vs. ontem")
        vs_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS))
        vs_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        trend_row.addWidget(vs_lbl)
        trend_row.addStretch()
        self.add_content_layout(trend_row)

        self._bar = MiniProgressBar(color=c["emerald"], height=5)
        self.add_content(self._bar)

    def update_data(self, valor_hoje: float, valor_ontem: float, meta: float = 0):
        self._value_lbl.set_value(valor_hoje)
        pct = ((valor_hoje - valor_ontem) / abs(valor_ontem) * 100) if valor_ontem else 0
        self._trend_badge.update_pct(pct)
        if meta > 0:
            self._bar.set_pct(valor_hoje / meta)
        elif valor_hoje > 0:
            self._bar.set_pct(min(1.0, valor_hoje / max(valor_hoje, valor_ontem or 1)))


# ══════════════════════════════════════════════════════════════════════════════
# PendingWidget — pendências CT-e / notas / contas
# ══════════════════════════════════════════════════════════════════════════════
class PendingWidget(BaseWidget):
    """Widget de pendências com contador e botão de ação."""

    item_clicked = Signal(str)   # emite a chave do item clicado

    def __init__(self, parent=None):
        c = theme_manager.colors
        super().__init__("Pendências", "warning", c["amber"], refresh_ms=25_000, parent=parent)
        self._items: List[dict] = []
        self._item_rows: List[QWidget] = []

    def update_data(self, items: List[dict]):
        """items: [{'key': str, 'label': str, 'count': int, 'color': str}]"""
        # Limpar
        for w in self._item_rows:
            w.deleteLater()
        self._item_rows.clear()
        self._items = items

        c = theme_manager.colors
        t = theme_manager.tokens

        for item in items[:5]:
            row = QPushButton()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            color = item.get("color", c["amber"])
            row.setStyleSheet(f"""
            QPushButton {{
                background: {c['bg_tertiary']}; border-radius: {t.RADIUS_MD}px;
                border: 1px solid {c['border_subtle']}; padding: 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{ background: {c['bg_overlay']}; border-color: {color}44; }}
            """)
            rl = QHBoxLayout()
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(t.SPACING_SM)

            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background: {color}; border-radius: 4px;")
            rl.addWidget(dot)

            label_lbl = QLabel(item["label"])
            label_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
            label_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            rl.addWidget(label_lbl, 1)

            count_lbl = QLabel(str(item["count"]))
            count_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
            count_lbl.setStyleSheet(f"color: {color}; background: transparent;")
            rl.addWidget(count_lbl)

            # Container
            inner_w = QWidget(); inner_w.setStyleSheet("background: transparent;"); inner_w.setLayout(rl)
            row.setLayout(QHBoxLayout())  # dummy, we overlay
            row_actual = QFrame()
            row_actual.setStyleSheet(f"""
            QFrame {{
                background: {c['bg_tertiary']}; border-radius: {t.RADIUS_MD}px;
                border: 1px solid {c['border_subtle']};
            }}
            QFrame:hover {{ background: {c['bg_overlay']}; border-color: {color}44; }}
            """)
            row_actual.setCursor(Qt.CursorShape.PointingHandCursor)
            rll = QHBoxLayout()
            rll.setContentsMargins(10, 8, 10, 8)
            rll.setSpacing(t.SPACING_SM)
            row_actual.setLayout(rll)

            d2 = QLabel(); d2.setFixedSize(8, 8); d2.setStyleSheet(f"background: {color}; border-radius: 4px;")
            rll.addWidget(d2)
            l2 = QLabel(item["label"]); l2.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
            l2.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            rll.addWidget(l2, 1)
            c2 = QLabel(str(item["count"])); c2.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
            c2.setStyleSheet(f"color: {color}; background: transparent;")
            rll.addWidget(c2)

            key = item["key"]
            row_actual.mousePressEvent = lambda e, k=key: self.item_clicked.emit(k)

            self.add_content(row_actual)
            self._item_rows.append(row_actual)


# ══════════════════════════════════════════════════════════════════════════════
# TimelineWidget — timeline horizontal de eventos do dia
# ══════════════════════════════════════════════════════════════════════════════
class TimelineWidget(QFrame):
    """Timeline horizontal de eventos: saída, abastecimento, entrega, chegada."""

    def __init__(self, parent=None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setObjectName("timelineCard")
        self.setStyleSheet(f"""
        QFrame#timelineCard {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
        }}
        """)
        _card_shadow(self, blur=20, y=3, alpha=25)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_LG, t.SPACING_LG, t.SPACING_LG, t.SPACING_LG)
        layout.setSpacing(t.SPACING_MD)
        self.setLayout(layout)

        # Header
        hdr = QHBoxLayout()
        ttl = QLabel("TIMELINE DO DIA")
        ttl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        ttl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 0.8px;")
        hdr.addWidget(ttl)
        hdr.addStretch()
        hdr_w = QWidget(); hdr_w.setStyleSheet("background: transparent;"); hdr_w.setLayout(hdr)
        layout.addWidget(hdr_w)

        # Scroll area horizontal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:horizontal {{ background: transparent; height: 4px; }}
        QScrollBar::handle:horizontal {{ background: {c['border_default']}; border-radius: 2px; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)

        self._timeline_w = _TimelineCanvas()
        scroll.setWidget(self._timeline_w)
        layout.addWidget(scroll)

    def update_events(self, events: List[dict]):
        """events: [{'time': 'HH:MM', 'icon': str, 'label': str, 'color': str, 'done': bool}]"""
        self._timeline_w.set_events(events)


class _TimelineCanvas(QWidget):
    """Canvas que desenha a timeline horizontal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._events: List[dict] = []
        self.setMinimumHeight(90)

    def set_events(self, events: List[dict]):
        self._events = events
        n = max(len(events), 1)
        self.setMinimumWidth(max(500, n * 110))
        self.update()

    def paintEvent(self, event):
        if not self._events:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = theme_manager.colors
        t = theme_manager.tokens

        n = len(self._events)
        w = self.width()
        h = self.height()
        step = w / max(n, 1)
        cy = h // 2 - 8

        # Track line
        p.setPen(QPen(QColor(c["border_default"]), 2))
        margin = int(step * 0.5)
        p.drawLine(margin, cy, w - margin, cy)

        for i, ev in enumerate(self._events):
            x = int(step * i + step * 0.5)
            done = ev.get("done", False)
            color = QColor(ev.get("color", c["indigo"]))

            # Node circle
            r = 14
            p.setPen(Qt.PenStyle.NoPen)
            if done:
                p.setBrush(color)
            else:
                p.setBrush(QColor(c["bg_overlay"]))
                p.setPen(QPen(color, 2))
            p.drawEllipse(x - r, cy - r, r * 2, r * 2)

            # Icon text (emoji)
            icon = ev.get("icon", "")
            if icon:
                p.setFont(QFont("Segoe UI Emoji", 10))
                p.setPen(QColor("#FFFFFF" if done else c["text_tertiary"]))
                p.drawText(x - r, cy - r, r * 2, r * 2, Qt.AlignmentFlag.AlignCenter, icon)

            # Time label (above)
            time_str = ev.get("time", "")
            if time_str:
                p.setFont(theme_manager.get_font(9, bold=True))
                p.setPen(QColor(c["text_secondary"]))
                p.drawText(x - 30, cy - r - 22, 60, 18, Qt.AlignmentFlag.AlignCenter, time_str)

            # Label (below)
            label = ev.get("label", "")
            if label:
                p.setFont(theme_manager.get_font(9))
                p.setPen(QColor(c["text_tertiary"]))
                p.drawText(x - 40, cy + r + 4, 80, 18, Qt.AlignmentFlag.AlignCenter, label)

        p.end()


# ══════════════════════════════════════════════════════════════════════════════
# KPITile — KPI card grande e limpo (estilo "item 3")
# ══════════════════════════════════════════════════════════════════════════════
class KPITile(QFrame):
    """KPI tile com número grande, label, trend badge e mini sparkline."""

    def __init__(self, label: str, prefix: str = "", suffix: str = "",
                 decimals: int = 0, accent: str = "#6366F1",
                 icon: str = "trending_up", parent=None):
        super().__init__(parent)
        self._accent = accent
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setObjectName("kpiTile")
        self.setStyleSheet(f"""
        QFrame#kpiTile {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-left: 3px solid {accent};
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame#kpiTile:hover {{
            border-color: {accent};
            background: {c['card_hover']};
        }}
        """)
        _card_shadow(self, blur=16, y=3, alpha=25)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_LG, t.SPACING_LG, t.SPACING_LG, t.SPACING_LG)
        layout.setSpacing(6)
        self.setLayout(layout)

        # Icon + label row
        top = QHBoxLayout()
        ico = QLabel()
        ico.setPixmap(get_pixmap(icon, color=accent))
        top.addWidget(ico)
        top.addSpacing(6)
        lbl_w = QLabel(label.upper())
        lbl_w.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl_w.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 0.8px;")
        top.addWidget(lbl_w)
        top.addStretch()
        top_w = QWidget(); top_w.setStyleSheet("background: transparent;"); top_w.setLayout(top)
        layout.addWidget(top_w)

        # Value
        self._value_lbl = LiveValueLabel(prefix=prefix, suffix=suffix, decimals=decimals)
        self._value_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_3XL, bold=True))
        self._value_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        layout.addWidget(self._value_lbl)

        # Trend
        trend_row = QHBoxLayout()
        self._trend = TrendBadge(0.0)
        trend_row.addWidget(self._trend)
        self._vs_lbl = QLabel("vs. período anterior")
        self._vs_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS))
        self._vs_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        trend_row.addWidget(self._vs_lbl)
        trend_row.addStretch()
        trend_w = QWidget(); trend_w.setStyleSheet("background: transparent;"); trend_w.setLayout(trend_row)
        layout.addWidget(trend_w)

        # Mini bar
        self._bar = MiniProgressBar(color=accent, height=4)
        layout.addWidget(self._bar)

    def set_data(self, value: float, growth_pct: float = 0, bar_pct: float = 0.6):
        self._value_lbl.set_value(value)
        self._trend.update_pct(growth_pct)
        self._bar.set_pct(bar_pct)
