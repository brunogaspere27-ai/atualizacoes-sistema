"""
Dashboard Premium — CW Transportadora
Criado do zero por um UX/UI Designer Sênior especializado em logística.

Filosofia de design:
 - Data-first: cada pixel serve a um dado real, nenhum placeholder
 - Information hierarchy: KPIs → tendências → detalhamento
 - Dark mode profissional: #0A0A0A canvas, #141414 cards, #DC2626 brand
 - Gráficos nativos via QPainter (sem dependência externa)
 - Tipografia clara com hierarquia de 4 níveis
 - Sem herança de componentes legados
"""

from __future__ import annotations

import math
import threading
from datetime import datetime
from typing import Dict, Any, List

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSizeF, Signal
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QPen, QBrush,
    QLinearGradient, QFontMetrics,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
)

from config.settings import settings
from services.dashboard_service import dashboard_service
from services.auth_service import auth_service
from utils.helpers import formatar_moeda

# ─── Paleta ────────────────────────────────────────────────────────────────────

BG       = "#0A0A0A"   # canvas — profundidade máxima
CARD     = "#141414"   # superfície elevada
BORDER   = "#222222"   # bordas sutis
HOVER    = "#1C1C1C"   # hover de cards
BRAND    = "#DC2626"   # vermelho CW
BRAND_DIM= "#3D0A0A"   # vermelho atenuado (fundo badge)
SUCCESS  = "#10B981"   # verde lucro
SUCCESS_DIM = "#052E1E"
WARNING  = "#F59E0B"   # âmbar atenção
WARNING_DIM = "#3D2500"
NEUTRAL  = "#6B7280"   # cinza neutro
TEXT1    = "#F9FAFB"   # título
TEXT2    = "#9CA3AF"   # subtítulo / rótulo
TEXT3    = "#4B5563"   # placeholder / grid

# Paleta de gráficos — 6 cores distintas e harmoniosas no fundo escuro
CHART_PALETTE = ["#DC2626", "#10B981", "#3B82F6", "#F59E0B", "#8B5CF6", "#06B6D4"]

FONT_QT = "Segoe UI"


def _font(size: int, bold: bool = False) -> QFont:
    f = QFont(FONT_QT, size)
    if bold:
        f.setBold(True)
    return f


def _shadow(blur: int = 24, y: int = 4, alpha: int = 80) -> QGraphicsDropShadowEffect:
    eff = QGraphicsDropShadowEffect()
    eff.setBlurRadius(blur)
    eff.setOffset(0, y)
    eff.setColor(QColor(0, 0, 0, alpha))
    return eff


# ─── Gráfico de Linhas (Área) ──────────────────────────────────────────────────

class LineAreaChart(QWidget):
    """
    Gráfico de área com gradiente para séries de receita/lucro ao longo do ano.
    Renderiza até 2 séries simultâneas.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Dados: lista de (labels, [(cor, [valores])])
        self._labels: List[str] = []
        self._series: List[tuple[str, List[float]]] = []  # (color, values)

    def set_data(
        self,
        labels: List[str],
        series: List[tuple[str, List[float]]],
    ) -> None:
        self._labels = labels
        self._series = series
        self.update()

    def paintEvent(self, _) -> None:  # noqa: N802
        if not self._labels or not self._series:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 48, 16, 12, 32

        plot_w = W - pad_l - pad_r
        plot_h = H - pad_t - pad_b

        # Coletar todos os valores para escala
        all_vals = [v for _, vals in self._series for v in vals]
        max_v = max(all_vals) if all_vals else 1
        min_v = 0
        if max_v == 0:
            max_v = 1

        n = len(self._labels)
        if n < 2:
            return

        def x_pos(i: int) -> float:
            return pad_l + (i / (n - 1)) * plot_w

        def y_pos(v: float) -> float:
            return pad_t + plot_h - ((v - min_v) / (max_v - min_v)) * plot_h

        # Grid horizontal — 4 linhas
        p.setPen(QPen(QColor(TEXT3), 0.5, Qt.PenStyle.DotLine))
        for k in range(1, 5):
            gy = pad_t + plot_h * (1 - k / 4)
            p.drawLine(QPointF(pad_l, gy), QPointF(pad_l + plot_w, gy))
            val_at = (k / 4) * max_v
            label = f"R${val_at/1_000:.0f}k" if val_at >= 1_000 else f"R${val_at:.0f}"
            p.setFont(_font(8))
            p.setPen(QColor(TEXT3))
            p.drawText(QRectF(0, gy - 8, pad_l - 4, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, label)
            p.setPen(QPen(QColor(TEXT3), 0.5, Qt.PenStyle.DotLine))

        # Séries
        for color_hex, vals in self._series:
            if len(vals) != n:
                continue

            # Área com gradiente
            path_area = QPainterPath()
            path_area.moveTo(QPointF(x_pos(0), y_pos(0) + plot_h + pad_t))  # base esquerda
            for i, v in enumerate(vals):
                if i == 0:
                    path_area.lineTo(QPointF(x_pos(i), y_pos(v)))
                else:
                    # curva bezier suave
                    prev_x = x_pos(i - 1)
                    cur_x = x_pos(i)
                    cp_x = (prev_x + cur_x) / 2
                    path_area.cubicTo(
                        QPointF(cp_x, y_pos(vals[i - 1])),
                        QPointF(cp_x, y_pos(v)),
                        QPointF(cur_x, y_pos(v)),
                    )
            path_area.lineTo(QPointF(x_pos(n - 1), y_pos(0) + plot_h + pad_t))
            path_area.closeSubpath()

            grad = QLinearGradient(0, pad_t, 0, pad_t + plot_h)
            c = QColor(color_hex)
            c.setAlpha(55)
            grad.setColorAt(0, c)
            c2 = QColor(color_hex)
            c2.setAlpha(0)
            grad.setColorAt(1, c2)
            p.fillPath(path_area, QBrush(grad))

            # Linha
            path_line = QPainterPath()
            for i, v in enumerate(vals):
                pt = QPointF(x_pos(i), y_pos(v))
                if i == 0:
                    path_line.moveTo(pt)
                else:
                    prev_x = x_pos(i - 1)
                    cp_x = (prev_x + pt.x()) / 2
                    path_line.cubicTo(
                        QPointF(cp_x, y_pos(vals[i - 1])),
                        QPointF(cp_x, pt.y()),
                        pt,
                    )
            p.setPen(QPen(QColor(color_hex), 2))
            p.drawPath(path_line)

        # Rótulos do eixo X
        p.setFont(_font(8))
        p.setPen(QColor(TEXT3))
        for i, label in enumerate(self._labels):
            lx = x_pos(i)
            p.drawText(
                QRectF(lx - 16, H - pad_b + 4, 32, 16),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        p.end()


# ─── Gráfico de Barras ─────────────────────────────────────────────────────────

class BarChart(QWidget):
    """
    Gráfico de barras verticais para volumes mensais (fretes, litros, etc.).
    """

    def __init__(self, color: str = BRAND, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._color = color
        self._labels: List[str] = []
        self._values: List[float] = []

    def set_data(self, labels: List[str], values: List[float]) -> None:
        self._labels = labels
        self._values = values
        self.update()

    def paintEvent(self, _) -> None:  # noqa: N802
        if not self._labels or not self._values:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 8, 8, 8, 24

        plot_w = W - pad_l - pad_r
        plot_h = H - pad_t - pad_b

        n = len(self._labels)
        max_v = max(self._values) if self._values else 1
        if max_v == 0:
            max_v = 1

        bar_w = plot_w / n
        inner_w = max(bar_w * 0.55, 4)
        gap = (bar_w - inner_w) / 2

        for i, (lbl, val) in enumerate(zip(self._labels, self._values)):
            ratio = val / max_v
            bar_h = plot_h * ratio
            bx = pad_l + i * bar_w + gap
            by = pad_t + plot_h - bar_h

            # Gradiente na barra
            grad = QLinearGradient(bx, by, bx, by + bar_h)
            grad.setColorAt(0, QColor(self._color))
            c_dim = QColor(self._color)
            c_dim.setAlpha(120)
            grad.setColorAt(1, c_dim)

            radius = min(inner_w / 2, 4)
            rect = QRectF(bx, by, inner_w, bar_h)
            path = QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            p.fillPath(path, QBrush(grad))

            # Label eixo X
            p.setFont(_font(8))
            p.setPen(QColor(TEXT3))
            p.drawText(
                QRectF(pad_l + i * bar_w, H - pad_b + 4, bar_w, 16),
                Qt.AlignmentFlag.AlignCenter,
                lbl,
            )

        p.end()


# ─── Barras horizontais de ranking ────────────────────────────────────────────

class HorizontalRankBars(QWidget):
    """
    Lista de ranking com barra de progresso horizontal inline.
    Usado para top clientes e top motoristas.
    """

    def __init__(self, color: str = BRAND, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self._items: List[tuple[str, float]] = []  # (label, value)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, items: List[tuple[str, float]]) -> None:
        self._items = items
        self.update()

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(300, max(len(self._items) * 44, 100))

    def paintEvent(self, _) -> None:  # noqa: N802
        if not self._items:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W = self.width()
        row_h = 44
        max_v = max(v for _, v in self._items) if self._items else 1
        if max_v == 0:
            max_v = 1

        label_w = min(int(W * 0.38), 180)
        val_w = 72
        bar_area = W - label_w - val_w - 32

        for i, (lbl, val) in enumerate(self._items):
            y = i * row_h
            cy = y + row_h / 2

            # Índice
            p.setFont(_font(9, bold=True))
            rank_color = QColor(BRAND) if i == 0 else QColor(TEXT3)
            p.setPen(rank_color)
            p.drawText(QRectF(0, cy - 8, 20, 16), Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # Rótulo
            p.setFont(_font(11))
            p.setPen(QColor(TEXT1 if i == 0 else TEXT2))
            fm = QFontMetrics(p.font())
            name = fm.elidedText(lbl, Qt.TextElideMode.ElideRight, label_w - 4)
            p.drawText(QRectF(24, cy - 9, label_w, 18), Qt.AlignmentFlag.AlignVCenter, name)

            # Trilho
            tx = 24 + label_w + 8
            th = 6
            ty = cy - th / 2
            track_rect = QRectF(tx, ty, bar_area, th)
            p.fillRect(track_rect, QColor(BORDER))

            # Barra de progresso
            ratio = val / max_v
            fill_w = bar_area * ratio
            if fill_w > 0:
                fill_rect = QRectF(tx, ty, fill_w, th)
                path = QPainterPath()
                path.addRoundedRect(fill_rect, 3, 3)
                grad = QLinearGradient(tx, 0, tx + fill_w, 0)
                grad.setColorAt(0, QColor(self._color))
                c2 = QColor(self._color)
                c2.setAlpha(160)
                grad.setColorAt(1, c2)
                p.fillPath(path, QBrush(grad))

            # Valor
            p.setFont(_font(10, bold=True))
            p.setPen(QColor(TEXT1))
            val_str = formatar_moeda(val) if val >= 100 else str(int(val))
            p.drawText(QRectF(tx + bar_area + 8, cy - 9, val_w, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, val_str)

        self.setMinimumHeight(len(self._items) * row_h)
        p.end()


# ─── KPI Card ──────────────────────────────────────────────────────────────────

class KPICard(QFrame):
    """
    Card de KPI com:
     - Rótulo superior (ex: "Receita Total")
     - Valor principal em destaque (ex: "R$ 284.500")
     - Badge de variação percentual com cor semântica (verde/vermelho)
     - Linha de contexto (ex: "vs mês anterior")
    """

    def __init__(
        self,
        label: str,
        icon_char: str = "◆",
        icon_color: str = BRAND,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_color = icon_color

        self.setObjectName("kpiCard")
        self.setStyleSheet(f"""
        QFrame#kpiCard {{
            background-color: {CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
        }}
        QFrame#kpiCard:hover {{
            border-color: #333333;
            background-color: {HOVER};
        }}
        """)
        self.setGraphicsEffect(_shadow(20, 3, 60))

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(6)

        # Linha superior: ícone + rótulo
        top = QHBoxLayout()
        top.setSpacing(8)
        top.setContentsMargins(0, 0, 0, 0)

        self._icon_lbl = QLabel(icon_char)
        self._icon_lbl.setFont(_font(10))
        self._icon_lbl.setStyleSheet(f"color: {icon_color}; background: transparent;")
        self._icon_lbl.setFixedWidth(14)
        top.addWidget(self._icon_lbl)

        self._label = QLabel(label)
        self._label.setFont(_font(11))
        self._label.setStyleSheet(f"color: {TEXT2}; background: transparent;")
        top.addWidget(self._label)
        top.addStretch()

        # Badge de tendência (preenchido depois)
        self._badge = QLabel()
        self._badge.setFont(_font(9, bold=True))
        self._badge.setStyleSheet(f"""
            color: {TEXT3};
            background: {BORDER};
            border-radius: 5px;
            padding: 2px 7px;
        """)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setVisible(False)
        top.addWidget(self._badge)

        root.addLayout(top)

        # Valor principal
        self._value = QLabel("—")
        self._value.setFont(_font(26, bold=True))
        self._value.setStyleSheet(f"color: {TEXT1}; background: transparent;")
        self._value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        root.addWidget(self._value)

        # Contexto
        self._context = QLabel()
        self._context.setFont(_font(10))
        self._context.setStyleSheet(f"color: {TEXT3}; background: transparent;")
        root.addWidget(self._context)

    def update_value(
        self,
        value: str,
        growth: float | None = None,
        context: str = "vs. período anterior",
    ) -> None:
        self._value.setText(value)

        if growth is not None:
            sign = "▲" if growth >= 0 else "▼"
            color = SUCCESS if growth >= 0 else BRAND
            bg = SUCCESS_DIM if growth >= 0 else BRAND_DIM
            self._badge.setText(f"{sign} {abs(growth):.1f}%")
            self._badge.setStyleSheet(f"""
                color: {color};
                background: {bg};
                border-radius: 5px;
                padding: 2px 7px;
            """)
            self._badge.setVisible(True)

        self._context.setText(context)


# ─── Card container genérico ───────────────────────────────────────────────────

class Section(QFrame):
    """
    Container de seção com título, subtítulo opcional e área de conteúdo.
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("section")
        self.setStyleSheet(f"""
        QFrame#section {{
            background-color: {CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
        }}
        """)
        self.setGraphicsEffect(_shadow(24, 4, 60))

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 20)
        root.setSpacing(14)

        # Cabeçalho
        if title:
            hdr = QHBoxLayout()
            hdr.setSpacing(0)
            hdr.setContentsMargins(0, 0, 0, 0)

            col = QVBoxLayout()
            col.setSpacing(3)

            title_lbl = QLabel(title)
            title_lbl.setFont(_font(13, bold=True))
            title_lbl.setStyleSheet(f"color: {TEXT1}; background: transparent;")
            col.addWidget(title_lbl)

            if subtitle:
                sub_lbl = QLabel(subtitle)
                sub_lbl.setFont(_font(10))
                sub_lbl.setStyleSheet(f"color: {TEXT3}; background: transparent;")
                col.addWidget(sub_lbl)

            hdr.addLayout(col)
            hdr.addStretch()
            root.addLayout(hdr)

            # Divisor
            div = QFrame()
            div.setMinimumHeight(1)
            div.setStyleSheet(f"background: {BORDER};")
            root.addWidget(div)

        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        self.body.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self.body)

    def add(self, widget: QWidget) -> None:
        self.body.addWidget(widget)

    def add_stretch(self) -> None:
        self.body.addStretch()


# ─── Dashboard Premium ─────────────────────────────────────────────────────────

class DashboardPremium(QWidget):
    """
    Dashboard premium CW Transportadora — criado do zero.

    Layout:
        ┌─────────────────────────────────────────────┐
        │  HEADER  (saudação + data + status sync)    │
        ├───────────────────────────────────────────── │
        │  KPI  KPI  KPI  KPI  KPI  KPI              │  ← 6 KPIs em 2 linhas
        ├──────────────────────┬──────────────────────┤
        │  Gráfico de área     │  Fretes por mês      │  ← linha de gráficos
        │  (Receita vs Lucro)  │  (barras verticais)  │
        ├──────────────────────┼──────────────────────┤
        │  Top Clientes        │  Top Motoristas      │  ← ranking horizontal
        └──────────────────────┴──────────────────────┘
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._ano = datetime.now().strftime("%Y")
        self._mes = datetime.now().strftime("%m")

        # Referências para atualização incremental
        self._kpi_cards: Dict[str, KPICard] = {}
        self._chart_revenue: LineAreaChart | None = None
        self._chart_fretes: BarChart | None = None
        self._rank_clientes: HorizontalRankBars | None = None
        self._rank_motoristas: HorizontalRankBars | None = None
        self._status_lbl: QLabel | None = None

        self._build_ui()

        # Carregar dados em background para não travar a UI
        QTimer.singleShot(80, self._load_async)

        # Auto-refresh a cada 90s
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(90_000)
        self._refresh_timer.timeout.connect(self._load_async)
        self._refresh_timer.start()

    # ── Construção da UI ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet(f"background: {BG};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: {BG}; border: none; }}
        QScrollBar:vertical {{ background: {BG}; width: 6px; border-radius: 3px; }}
        QScrollBar::handle:vertical {{ background: #2A2A2A; border-radius: 3px; min-height: 32px; }}
        QScrollBar::handle:vertical:hover {{ background: #3A3A3A; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ height: 0; background: none; }}
        """)

        self.canvas = QWidget()
        self.canvas.setStyleSheet(f"background: {BG};")
        self._canvas_layout = QVBoxLayout(self.canvas)
        self._canvas_layout.setContentsMargins(32, 24, 32, 32)
        self._canvas_layout.setSpacing(20)
        scroll.setWidget(self.canvas)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._build_header()
        self._build_kpi_grid()
        self._build_charts_row()
        self._build_rankings_row()
        self._canvas_layout.addStretch()

    def _build_header(self) -> None:
        usuario = auth_service.usuario_atual or {}
        hora = datetime.now().hour
        if hora < 12:
            saudacao = "Bom dia"
        elif hora < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"

        nome_completo = usuario.get("nome_completo", "")
        primeiro_nome = nome_completo.split()[0] if nome_completo else "Usuário"

        dias_pt = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
        meses_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        now = datetime.now()
        data_str = f"{dias_pt[now.weekday()]}, {now.day} de {meses_pt[now.month - 1]}"

        row = QHBoxLayout()
        row.setSpacing(0)
        row.setContentsMargins(0, 0, 0, 0)

        # Bloco esquerdo: saudação
        left = QVBoxLayout()
        left.setSpacing(4)

        greet = QLabel(f"{saudacao}, {primeiro_nome}")
        greet.setFont(_font(22, bold=True))
        greet.setStyleSheet(f"color: {TEXT1}; background: transparent;")
        left.addWidget(greet)

        date_lbl = QLabel(data_str)
        date_lbl.setFont(_font(12))
        date_lbl.setStyleSheet(f"color: {TEXT3}; background: transparent;")
        left.addWidget(date_lbl)

        row.addLayout(left)
        row.addStretch()

        # Bloco direito: status sync
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right.setSpacing(4)

        self._status_lbl = QLabel("● Carregando...")
        self._status_lbl.setFont(_font(10))
        self._status_lbl.setStyleSheet(f"color: {TEXT3}; background: transparent;")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self._status_lbl)

        year_lbl = QLabel(f"Exercício {self._ano}")
        year_lbl.setFont(_font(10))
        year_lbl.setStyleSheet(f"color: {TEXT3}; background: transparent;")
        year_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(year_lbl)

        row.addLayout(right)

        self._canvas_layout.addLayout(row)

        # Linha divisora abaixo do header
        div = QFrame()
        div.setMinimumHeight(1)
        div.setStyleSheet(f"background: {BORDER};")
        self._canvas_layout.addWidget(div)

    def _build_kpi_grid(self) -> None:
        """6 KPIs em 2 linhas de 3 colunas."""
        configs = [
            ("receita_total",    "Receita Total",       "◈", BRAND),
            ("lucro_estimado",   "Lucro Estimado",      "◈", SUCCESS),
            ("fretes_realizados","Fretes Realizados",   "◈", "#3B82F6"),
            ("fretes_andamento", "Em Andamento",        "◈", WARNING),
            ("valor_recebido",   "Valor Recebido",      "◈", SUCCESS),
            ("valor_pendente",   "Pendente de Receber", "◈", WARNING),
        ]

        for row_start in range(0, 6, 3):
            row = QHBoxLayout()
            row.setSpacing(16)
            row.setContentsMargins(0, 0, 0, 0)
            for key, lbl, icon, color in configs[row_start:row_start + 3]:
                card = KPICard(lbl, icon, color)
                card.setMinimumHeight(110)
                self._kpi_cards[key] = card
                row.addWidget(card)
            self._canvas_layout.addLayout(row)

    def _build_charts_row(self) -> None:
        """Linha de gráficos: área (receita vs lucro) + barras (fretes)."""
        row = QHBoxLayout()
        row.setSpacing(16)
        row.setContentsMargins(0, 0, 0, 0)

        # ─ Seção esquerda: Receita vs Lucro (linha de área)
        sec_revenue = Section(
            "Receita vs. Lucro",
            f"Evolução mensal — {self._ano}",
        )
        sec_revenue.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Legenda inline
        legend_row = QHBoxLayout()
        legend_row.setSpacing(16)
        legend_row.setContentsMargins(0, 0, 0, 0)
        for label, color in [("Receita", BRAND), ("Lucro", SUCCESS)]:
            leg = QLabel(f"━  {label}")
            leg.setFont(_font(10))
            leg.setStyleSheet(f"color: {color}; background: transparent;")
            legend_row.addWidget(leg)
        legend_row.addStretch()
        sec_revenue.body.addLayout(legend_row)

        self._chart_revenue = LineAreaChart()
        self._chart_revenue.setMinimumHeight(210)
        sec_revenue.add(self._chart_revenue)

        row.addWidget(sec_revenue, 3)

        # ─ Seção direita: Fretes por mês (barras)
        sec_fretes = Section(
            "Fretes por Mês",
            "Viagens finalizadas",
        )
        sec_fretes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._chart_fretes = BarChart(color=BRAND)
        self._chart_fretes.setMinimumHeight(210)
        sec_fretes.add(self._chart_fretes)

        row.addWidget(sec_fretes, 2)

        self._canvas_layout.addLayout(row)

    def _build_rankings_row(self) -> None:
        """Linha de rankings: top clientes + top motoristas."""
        row = QHBoxLayout()
        row.setSpacing(16)
        row.setContentsMargins(0, 0, 0, 0)

        sec_clientes = Section(
            "Top Clientes",
            f"Por frete transportado — {self._ano}",
        )
        sec_clientes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._rank_clientes = HorizontalRankBars(color=BRAND)
        sec_clientes.add(self._rank_clientes)
        sec_clientes.add_stretch()
        row.addWidget(sec_clientes, 1)

        sec_motoristas = Section(
            "Top Motoristas",
            f"Por faturamento — {self._ano}",
        )
        sec_motoristas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._rank_motoristas = HorizontalRankBars(color="#3B82F6")
        sec_motoristas.add(self._rank_motoristas)
        sec_motoristas.add_stretch()
        row.addWidget(sec_motoristas, 1)

        self._canvas_layout.addLayout(row)

    # ── Carregamento de dados ─────────────────────────────────────────────────

    def _load_async(self) -> None:
        """Dispara carregamento em thread de background."""
        threading.Thread(target=self._fetch_data, daemon=True, name="dashboard-fetch").start()

    def _fetch_data(self) -> None:
        """Busca todos os dados necessários (roda em thread de background)."""
        try:
            kpis = dashboard_service.calcular_kpis("Geral")
            receita = dashboard_service.dados_graficos_receita_mensal(self._ano)
            lucro = dashboard_service.dados_graficos_comparativo_mensal(self._ano)
            fretes = dashboard_service.dados_graficos_fretes_mensal(self._ano)
            clientes = dashboard_service.dados_graficos_clientes_lucrativos(self._ano, top_n=7)
            motoristas = dashboard_service.dados_graficos_motoristas_faturamento(self._ano, top_n=7)

            # Despacha atualização de volta para a UI thread
            QTimer.singleShot(0, lambda: self._apply_data(kpis, receita, lucro, fretes, clientes, motoristas))
        except Exception as exc:
            QTimer.singleShot(0, lambda: self._on_error(str(exc)))

    def _apply_data(
        self,
        kpis: Dict[str, Any],
        receita: Dict[str, Any],
        lucro: Dict[str, Any],
        fretes: Dict[str, Any],
        clientes: Dict[str, Any],
        motoristas: Dict[str, Any],
    ) -> None:
        """Aplica os dados carregados nos widgets — roda na UI thread."""

        # ── KPIs ─────────────────────────────────────────────────────────────
        def _fmt_moeda(key: str) -> str:
            return formatar_moeda(kpis.get(key, {}).get("valor", 0))

        def _fmt_int(key: str) -> str:
            return str(int(kpis.get(key, {}).get("valor", 0)))

        def _growth(key: str) -> float | None:
            d = kpis.get(key)
            return d.get("crescimento") if d else None

        self._kpi_cards["receita_total"].update_value(_fmt_moeda("receita_total"), _growth("receita_total"))
        self._kpi_cards["lucro_estimado"].update_value(_fmt_moeda("lucro_estimado"), _growth("lucro_estimado"))
        self._kpi_cards["fretes_realizados"].update_value(_fmt_int("fretes_realizados"), _growth("fretes_realizados"), "viagens finalizadas")
        self._kpi_cards["fretes_andamento"].update_value(_fmt_int("fretes_andamento"), None, "em trânsito agora")
        self._kpi_cards["valor_recebido"].update_value(_fmt_moeda("valor_recebido"), _growth("valor_recebido"))
        self._kpi_cards["valor_pendente"].update_value(_fmt_moeda("valor_pendente"), None, "aguardando recebimento")

        # ── Gráfico de linha: Receita vs Lucro ──────────────────────────────
        labels = receita.get("labels", [])
        receita_vals = receita.get("valores", [])
        lucro_vals = lucro.get("lucros", [])

        if labels and receita_vals:
            series: List[tuple[str, List[float]]] = [(BRAND, receita_vals)]
            if lucro_vals and len(lucro_vals) == len(labels):
                series.append((SUCCESS, lucro_vals))
            self._chart_revenue.set_data(labels, series)

        # ── Gráfico de barras: Fretes por mês ───────────────────────────────
        f_labels = fretes.get("labels", [])
        f_vals = fretes.get("valores", [])
        if f_labels and f_vals:
            self._chart_fretes.set_data(f_labels, f_vals)

        # ── Ranking clientes ─────────────────────────────────────────────────
        c_labels = clientes.get("labels", [])
        c_vals = clientes.get("valores", [])
        if c_labels:
            self._rank_clientes.set_data(list(zip(c_labels, c_vals)))

        # ── Ranking motoristas ───────────────────────────────────────────────
        m_labels = motoristas.get("labels", [])
        m_vals = motoristas.get("valores", [])
        if m_labels:
            self._rank_motoristas.set_data(list(zip(m_labels, m_vals)))

        # ── Status ───────────────────────────────────────────────────────────
        now = datetime.now().strftime("%H:%M:%S")
        self._status_lbl.setText(f"● Atualizado às {now}")
        self._status_lbl.setStyleSheet(f"color: {SUCCESS}; background: transparent;")

    def _on_error(self, msg: str) -> None:
        if self._status_lbl:
            self._status_lbl.setText(f"⚠ Erro ao carregar dados")
            self._status_lbl.setStyleSheet(f"color: {WARNING}; background: transparent;")
