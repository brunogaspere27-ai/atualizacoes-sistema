"""
CW Transportadora — Dashboard EMU
Gráficos próprios via QPainter (sem dependência de cw_theme ou pyqtgraph).
Substitua o arquivo dashboard_cw.py ou dashboard_pyside6.py por este.
"""
from __future__ import annotations

import math
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSize
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient,
    QPainterPath, QFontMetrics,
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QGraphicsDropShadowEffect,
)

try:
    from services import dashboard_service
except Exception:
    dashboard_service = None

try:
    from utils.helpers import formatar_moeda
    def _brl(v):
        try:
            return formatar_moeda(float(v or 0))
        except Exception:
            return _brl_fallback(v)
except Exception:
    def _brl(v):
        return _brl_fallback(v)

def _brl_fallback(v):
    try:
        v = float(v or 0)
    except Exception:
        v = 0.0
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


# ── paleta ────────────────────────────────────────────────────────────────────

BG       = "#0A0E14"
SURF     = "#11161D"
ELEV     = "#1A202C"
OVER     = "#232D3F"
B1       = "#2D3748"
B2       = "#4A5568"

T1       = "#E2E8F0"
T2       = "#A0AEC0"
T3       = "#718096"

BRAND    = "#DC2626"
BRAND_H  = "#EF4444"
BRAND_BG = "#1F1515"

EMERALD  = "#059669"
SKY      = "#0284C7"
AMBER    = "#D97706"
ROSE     = "#E11D48"
VIOLET   = "#7C3AED"
CYAN     = "#0891B2"


# ── helpers de widget ─────────────────────────────────────────────────────────

def _shadow(w: QWidget, blur=12, dy=2, alpha=0.25):
    # Desabilitado temporariamente para investigar linhas fantasma
    pass


def _lbl(text="", size=11, color=T1, bold=False, mono=False) -> QLabel:
    lb = QLabel(str(text))
    fam = "Cascadia Code" if mono else "Segoe UI"
    f = QFont(fam, size)
    f.setBold(bold)
    lb.setFont(f)
    lb.setStyleSheet(f"color:{color};background:transparent;")
    return lb


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:{B1};border:none;")
    return f


# ── card base ─────────────────────────────────────────────────────────────────

class Card(QFrame):
    def __init__(self, accent=None, radius=14):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background:{SURF};
                border:none;
                border-radius:{radius}px;
            }}
        """)
        _shadow(self)


# ── KPI card ──────────────────────────────────────────────────────────────────

class KPICard(Card):
    def __init__(self, titulo: str, acento: str = BRAND):
        super().__init__(accent=acento)
        self._acento = acento

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(3)

        # linha colorida topo
        bar = QFrame()
        bar.setFixedHeight(2)
        bar.setStyleSheet(f"background:{acento};border:none;border-radius:1px;")
        lay.addWidget(bar)
        lay.addSpacing(4)

        self._titulo = _lbl(titulo.upper(), 8, T3)
        lay.addWidget(self._titulo)

        self._valor = QLabel("—")
        f = QFont("Segoe UI", 18)
        f.setBold(True)
        self._valor.setFont(f)
        self._valor.setStyleSheet(f"color:{T1};background:transparent;")
        lay.addWidget(self._valor)

        self._delta = _lbl("", 9, T3, mono=True)
        lay.addWidget(self._delta)

    def set(self, valor: str, delta: str = "", positivo: bool | None = None):
        self._valor.setText(valor)
        if delta:
            if positivo is True:
                cor, seta = EMERALD, "↑ "
            elif positivo is False:
                cor, seta = ROSE, "↓ "
            else:
                cor, seta = T3, ""
            self._delta.setText(seta + delta)
            self._delta.setStyleSheet(f"color:{cor};background:transparent;")
        else:
            self._delta.setText("")


# ── Linha chart (QPainter) ────────────────────────────────────────────────────

class LineChart(QWidget):
    """
    Gráfico de linha com gradiente, desenhado com QPainter.
    series: lista de (nome, [valores], cor_hex)
    labels: lista de strings para o eixo X
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._series: list[tuple[str, list[float], str]] = []
        self._labels: list[str] = []
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background:transparent;")

    def set_data(self, labels: list[str],
                 series: list[tuple[str, list[float], str]]):
        self._labels = labels
        self._series = series
        self.update()

    def paintEvent(self, _):
        if not self._series:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 52, 16, 12, 32
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b

        all_vals = [v for _, vs, _ in self._series for v in vs]
        if not all_vals:
            p.end()
            return
        mn, mx = min(all_vals), max(all_vals)
        span = (mx - mn) or 1
        mn -= span * 0.08
        mx += span * 0.12
        span = mx - mn

        n = max(len(vs) for _, vs, _ in self._series)
        if n < 2:
            p.end()
            return

        def px(i, v):
            x = pad_l + i * cw / (n - 1)
            y = pad_t + ch - (v - mn) / span * ch
            return QPointF(x, y)

        # grid
        grid_pen = QPen(QColor(B1))
        grid_pen.setWidthF(1.0)
        p.setPen(grid_pen)
        for i in range(5):
            y = pad_t + i * ch / 4
            p.drawLine(int(pad_l), int(y), int(W - pad_r), int(y))

        # eixo Y labels
        p.setFont(QFont("Cascadia Code", 8))
        p.setPen(QColor(T3))
        for i in range(5):
            v = mx - i * span / 4
            y = pad_t + i * ch / 4
            txt = f"{v/1000:.0f}k" if abs(v) >= 1000 else f"{v:.0f}"
            p.drawText(0, int(y) - 8, pad_l - 6, 16,
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, txt)

        # eixo X labels
        if self._labels:
            for i, lb in enumerate(self._labels[:n]):
                x = pad_l + i * cw / (n - 1)
                p.drawText(int(x) - 20, H - pad_b + 4, 40, 20,
                           Qt.AlignmentFlag.AlignCenter, lb)

        # série
        for nome, vals, cor_hex in self._series:
            if not vals:
                continue
            cor = QColor(cor_hex)

            # gradiente de preenchimento
            path_fill = QPainterPath()
            path_fill.moveTo(px(0, vals[0]))
            for i in range(1, len(vals)):
                path_fill.lineTo(px(i, vals[i]))
            path_fill.lineTo(QPointF(px(len(vals) - 1, vals[-1]).x(), pad_t + ch))
            path_fill.lineTo(QPointF(px(0, vals[0]).x(), pad_t + ch))
            path_fill.closeSubpath()

            grad = QLinearGradient(0, pad_t, 0, pad_t + ch)
            c1 = QColor(cor_hex)
            c1.setAlphaF(0.18)
            c2 = QColor(cor_hex)
            c2.setAlphaF(0.0)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(grad))
            p.drawPath(path_fill)

            # linha
            path_line = QPainterPath()
            path_line.moveTo(px(0, vals[0]))
            for i in range(1, len(vals)):
                path_line.lineTo(px(i, vals[i]))
            pen = QPen(cor)
            pen.setWidthF(2.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(path_line)

            # pontos
            p.setBrush(QBrush(QColor(SURF)))
            p.setPen(QPen(cor, 2))
            for i, v in enumerate(vals):
                pt = px(i, v)
                p.drawEllipse(pt, 4, 4)

        p.end()


# ── barra de progresso customizada ────────────────────────────────────────────

class ProgressBar(QWidget):
    def __init__(self, pct: float, cor: str, parent=None):
        super().__init__(parent)
        self._pct = max(0.0, min(1.0, pct))
        self._cor = QColor(cor)
        self.setFixedHeight(6)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background:transparent;")

    def set_pct(self, pct: float):
        self._pct = max(0.0, min(1.0, pct))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()

        # trilha
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(ELEV))
        p.drawRoundedRect(0, 0, W, H, 3, 3)

        # preenchimento com gradiente
        fill_w = int(W * self._pct)
        if fill_w > 0:
            grad = QLinearGradient(0, 0, fill_w, 0)
            c1 = QColor(self._cor)
            c2 = QColor(self._cor)
            c2.setAlphaF(0.65)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, 0, fill_w, H, 3, 3)

        p.end()


# ── badge de status ───────────────────────────────────────────────────────────

_STATUS = {
    "Entregue":   (EMERALD, "#0D2818"),
    "Concluído":  (EMERALD, "#0D2818"),
    "Em Rota":    (SKY,     "#0C2D6B"),
    "Trânsito":   (SKY,     "#0C2D6B"),
    "Agendado":   (CYAN,    "#0A2A2E"),
    "Pendente":   (AMBER,   "#2A1F0A"),
    "Manutenção": (ROSE,    "#2E141C"),
    "Atrasado":   (BRAND,   BRAND_BG),
}

def _badge(texto: str) -> QLabel:
    fg, bg = _STATUS.get(texto, (T2, ELEV))
    lb = QLabel(texto)
    lb.setFont(QFont("Cascadia Code", 9))
    lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lb.setFixedHeight(22)
    lb.setStyleSheet(f"""
        QLabel {{
            color:{fg};background:{bg};
            border:none;border-radius:4px;
            padding:0 8px;
        }}
    """)
    return lb


# ── DashboardCW ───────────────────────────────────────────────────────────────

class DashboardCW(QWidget):
    """
    Dashboard principal EMU. Compatível com a chamada DashboardCW() do main_pyside6.py.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")
        self._build()
        QTimer.singleShot(0, self._load_data)

    # ── layout ────────────────────────────────────────────────────────────

    def _build(self):
        self.setStyleSheet(f"""
            background:{BG};
            QLabel {{
                border: none;
                background: transparent;
            }}
            QFrame {{
                border: none;
            }}
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:{BG}; }}
            QScrollBar:vertical {{
                width:6px; background:transparent; margin:0;
            }}
            QScrollBar::handle:vertical {{
                background:{B2}; border-radius:3px; min-height:40px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height:0; }}
        """)

        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        self._root = QVBoxLayout(page)
        self._root.setContentsMargins(24, 20, 24, 32)
        self._root.setSpacing(16)

        scroll.setWidget(page)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._build_header()
        self._build_kpis()
        self._build_charts()
        self._build_operations()
        self._root.addStretch()

    # ── cabeçalho ─────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # identidade
        ident = QVBoxLayout()
        ident.setSpacing(1)
        ident.addWidget(_lbl("CW TRANSPORTADORA", 14, T1, bold=True))
        ident.addWidget(_lbl(
            datetime.now().strftime("Dashboard executivo  ·  %d/%m/%Y"),
            8, T3, mono=True
        ))
        row.addLayout(ident)
        row.addStretch()

        # período
        self._combo = QComboBox()
        self._combo.addItems(["Geral", "Mês", "Ano"])
        self._combo.setMaximumHeight(32)
        self._combo.setMinimumWidth(100)
        self._combo.setStyleSheet(f"""
            QComboBox {{
                background:{SURF}; color:{T1};
                border:none; border-radius:6px;
                padding:0 10px; font-size:10px; font-family:'Segoe UI';
            }}
            QComboBox:hover {{ background:{ELEV}; }}
            QComboBox::drop-down {{ border:none; width:16px; }}
            QComboBox::down-arrow {{
                width:0; height:0;
                border-left:3px solid transparent;
                border-right:3px solid transparent;
                border-top:4px solid {T2};
            }}
            QComboBox QAbstractItemView {{
                background:{ELEV}; color:{T1};
                border:none; border-radius:6px;
                selection-background-color:{BRAND_BG};
            }}
        """)
        self._combo.currentTextChanged.connect(self._change_period)
        row.addWidget(self._combo)

        # botão atualizar
        btn = QPushButton("Atualizar")
        btn.setMaximumHeight(32)
        btn.setMinimumWidth(80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{BRAND}; color:#fff; border:none;
                border-radius:6px; font-size:10px; font-weight:600;
                font-family:'Segoe UI'; padding:0 12px;
            }}
            QPushButton:hover {{ background:{BRAND_H}; }}
            QPushButton:pressed {{ background:#B91C1C; }}
        """)
        btn.clicked.connect(self._load_data)
        row.addWidget(btn)

        self._root.addLayout(row)
        self._root.addWidget(_sep())

    # ── KPIs ──────────────────────────────────────────────────────────────

    def _build_kpis(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        self._kpi_receita   = KPICard("Receita Bruta",      EMERALD)
        self._kpi_lucro     = KPICard("Lucro Estimado",     SKY)
        self._kpi_fretes    = KPICard("Fretes Realizados",  BRAND)
        self._kpi_andamento = KPICard("Em Andamento",       AMBER)
        self._kpi_clientes  = KPICard("Clientes Ativos",    VIOLET)

        for kpi in [self._kpi_receita, self._kpi_lucro, self._kpi_fretes,
                    self._kpi_andamento, self._kpi_clientes]:
            row.addWidget(kpi, 1)

        self._root.addLayout(row)

    # ── gráficos ──────────────────────────────────────────────────────────

    def _build_charts(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # ── gráfico de linha (2/3)
        card_chart = Card()
        cc = QVBoxLayout(card_chart)
        cc.setContentsMargins(16, 14, 16, 14)
        cc.setSpacing(10)

        head = QHBoxLayout()
        ttl = QVBoxLayout()
        ttl.setSpacing(1)
        ttl.addWidget(_lbl("Receita × Despesas", 12, T1, bold=True))
        ttl.addWidget(_lbl("Evolução mensal do período", 8, T3))
        head.addLayout(ttl)
        head.addStretch()

        for nome, cor in [("Receita", EMERALD), ("Despesa", ROSE)]:
            dot = QLabel(f"● {nome}")
            dot.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            dot.setStyleSheet(f"color:{cor};background:transparent;")
            head.addSpacing(10)
            head.addWidget(dot)

        cc.addLayout(head)

        self._chart = LineChart()
        self._chart.setMinimumHeight(200)
        cc.addWidget(self._chart, 1)

        row.addWidget(card_chart, 2)

        # ── painel operacional (1/3)
        card_ops = Card()
        co = QVBoxLayout(card_ops)
        co.setContentsMargins(14, 14, 14, 14)
        co.setSpacing(10)

        co.addWidget(_lbl("Operação atual", 12, T1, bold=True))
        co.addWidget(_lbl("Fretes por status", 8, T3))
        co.addWidget(_sep())

        self._op_rows: dict[str, tuple[QLabel, ProgressBar, QLabel]] = {}
        for nome, cor in [("Entregue", EMERALD), ("Em Rota", SKY), ("Pendente", AMBER)]:
            bloco = QVBoxLayout()
            bloco.setSpacing(4)

            linha = QHBoxLayout()
            dot = QLabel("●")
            dot.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            dot.setStyleSheet(f"color:{cor};background:transparent;")
            linha.addWidget(dot)
            nm = _lbl(nome, 9, T2)
            linha.addWidget(nm)
            linha.addStretch()
            val = _lbl("—", 10, T1, bold=True, mono=True)
            linha.addWidget(val)

            bloco.addLayout(linha)
            bar = ProgressBar(0.0, cor)
            bloco.addWidget(bar)
            co.addLayout(bloco)
            self._op_rows[nome] = (val, bar, nm)

        co.addWidget(_sep())
        co.addWidget(_lbl("Utilização", 10, T1, bold=True))

        self._util_rows: dict[str, tuple[QLabel, ProgressBar]] = {}
        for nome, pct, cor in [
            ("Frota disponível", 0.86, SKY),
            ("Entregas no prazo", 0.92, EMERALD),
            ("Contas em dia",     0.83, VIOLET),
        ]:
            bloco = QVBoxLayout()
            bloco.setSpacing(3)
            ln = QHBoxLayout()
            ln.addWidget(_lbl(nome, 8, T2))
            ln.addStretch()
            vl = _lbl(f"{int(pct*100)}%", 8, T1, bold=True, mono=True)
            ln.addWidget(vl)
            bloco.addLayout(ln)
            bar = ProgressBar(pct, cor)
            bloco.addWidget(bar)
            co.addLayout(bloco)
            self._util_rows[nome] = (vl, bar)

        co.addStretch()
        row.addWidget(card_ops, 1)
        self._root.addLayout(row)

    # ── operações ─────────────────────────────────────────────────────────

    def _build_operations(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        # tabela entregas (2/3)
        card_tbl = Card()
        ct = QVBoxLayout(card_tbl)
        ct.setContentsMargins(16, 14, 16, 14)
        ct.setSpacing(8)
        ct.addWidget(_lbl("Próximas Entregas", 12, T1, bold=True))

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Data", "Documento", "Destino", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setMinimumHeight(180)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background:{SURF}; border:none;
                color:{T1}; font-size:10px; font-family:'Segoe UI';
                outline:0;
            }}
            QHeaderView::section {{
                background:{BG}; color:{T3};
                border:none;
                padding:6px 8px;
                font-size:8px; font-weight:700;
                font-family:'Segoe UI'; letter-spacing:0.5px;
                text-transform:uppercase;
            }}
            QTableWidget::item {{
                border:none;
                padding:8px;
            }}
            QTableWidget::item:selected {{
                background:{BRAND_BG}; color:{T1};
            }}
            QScrollBar:vertical {{
                width:5px; background:transparent;
            }}
            QScrollBar::handle:vertical {{
                background:{B2}; border-radius:3px;
            }}
        """)
        ct.addWidget(self._table)
        row.addWidget(card_tbl, 2)

        # rail financeiro (1/3)
        card_fin = Card()
        cf = QVBoxLayout(card_fin)
        cf.setContentsMargins(14, 14, 14, 14)
        cf.setSpacing(8)
        cf.addWidget(_lbl("Financeiro", 12, T1, bold=True))
        cf.addWidget(_lbl("Posição resumida", 8, T3))
        cf.addWidget(_sep())

        self._fin_items: dict[str, tuple[QLabel, QLabel]] = {}
        for nome, cor in [
            ("A receber",  EMERALD),
            ("A pagar",    ROSE),
            ("Combustível",AMBER),
            ("Manutenção", SKY),
        ]:
            box = QFrame()
            box.setStyleSheet(f"""
                QFrame {{
                    background:{ELEV};
                    border:none;
                    border-left:3px solid {cor};
                    border-radius:6px;
                }}
            """)
            bl = QVBoxLayout(box)
            bl.setContentsMargins(10, 8, 10, 8)
            bl.setSpacing(1)
            bl.addWidget(_lbl(nome.upper(), 7, T3))
            val = _lbl("R$ —", 12, T1, bold=True)
            det = _lbl("—", 8, T3, mono=True)
            bl.addWidget(val)
            bl.addWidget(det)
            cf.addWidget(box)
            self._fin_items[nome] = (val, det)

        cf.addStretch()
        row.addWidget(card_fin, 1)
        self._root.addLayout(row)

    # ── dados ─────────────────────────────────────────────────────────────

    def _load_data(self):
        if dashboard_service is None:
            self._demo()
            return
        try:
            kpis = dashboard_service.calcular_kpis(
                self.tipo_periodo, self.mes, self.ano)
            status = dashboard_service.resumo_fretes_status(
                self.tipo_periodo, self.mes, self.ano)
            contas = dashboard_service.resumo_contas_receber_pagar(
                self.tipo_periodo, self.mes, self.ano)
            comb = dashboard_service.resumo_combustivel_mes()
            manut = dashboard_service.resumo_manutencoes()
            entregas = dashboard_service.proximas_entregas(8)
            graf = dashboard_service.dados_graficos_comparativo_mensal(self.ano)
            self._render(kpis, status, contas, comb, manut, entregas, graf)
        except Exception as e:
            print(f"[DashboardCW] {e}")
            self._demo()

    def _demo(self):
        kpis = {
            "receita_total":    {"valor": 613400, "crescimento": 12.8},
            "lucro_estimado":   {"valor": 142800, "crescimento": 8.4},
            "fretes_realizados":{"valor": 89,     "crescimento": 5.2},
            "fretes_andamento": {"valor": 14,     "crescimento": 0},
            "clientes_ativos":  {"valor": 37,     "crescimento": 3.1},
        }
        status = [("Entregue", 68), ("Em Rota", 21), ("Pendente", 11)]
        contas = {
            "Receber": {"total": 61020, "vencidas": 10200},
            "Pagar":   {"total": 60700, "vencidas": 8300},
        }
        comb  = {"total": 18400, "litros": 5200}
        manut = {"total": 4,     "atrasadas": 1}
        entregas = [
            {"quando": "15/08", "titulo": "NF-00341", "detalhe": "Campinas, SP",       "status": "Em Rota"},
            {"quando": "15/08", "titulo": "NF-00340", "detalhe": "Ribeirão Preto, SP", "status": "Em Rota"},
            {"quando": "16/08", "titulo": "NF-00338", "detalhe": "Santos, SP",         "status": "Agendado"},
            {"quando": "18/08", "titulo": "NF-00331", "detalhe": "Curitiba, PR",       "status": "Agendado"},
            {"quando": "19/08", "titulo": "NF-00329", "detalhe": "Sorocaba, SP",       "status": "Pendente"},
        ]
        graf = {
            "labels":  ["Mar", "Abr", "Mai", "Jun", "Jul", "Ago"],
            "receitas":[142000,168000,155000,189000,204000,231400],
            "despesas":[98000, 112000,109000,126000,139000,151000],
        }
        self._render(kpis, status, contas, comb, manut, entregas, graf)

    def _render(self, kpis, status, contas, comb, manut, entregas, graf):
        def g(k):
            v = kpis.get(k, {})
            return v if isinstance(v, dict) else {}

        rec   = g("receita_total")
        luc   = g("lucro_estimado")
        fre   = g("fretes_realizados")
        and_  = g("fretes_andamento")
        cli   = g("clientes_ativos")

        def _delta(d):
            if d is None:
                return "", None
            return f"{float(d):.1f}% vs. anterior", float(d) >= 0

        self._kpi_receita.set(
            _brl(rec.get("valor", 0)), *_delta(rec.get("crescimento")))
        self._kpi_lucro.set(
            _brl(luc.get("valor", 0)), *_delta(luc.get("crescimento")))
        self._kpi_fretes.set(
            str(int(fre.get("valor", 0))), "fretes no período")
        self._kpi_andamento.set(
            str(int(and_.get("valor", 0))), "em tempo real")
        self._kpi_clientes.set(
            str(int(cli.get("valor", 0))), "cadastrados")

        # gráfico de linha
        labels = graf.get("labels", [])
        receitas = graf.get("receitas", [])
        despesas = graf.get("despesas", [])
        self._chart.set_data(labels, [
            ("Receita", receitas, EMERALD),
            ("Despesa", despesas, ROSE),
        ])

        # status operacional
        total_status = sum(v for _, v in status) or 1
        for nome, val_num in status:
            if nome in self._op_rows:
                vl, bar, _ = self._op_rows[nome]
                vl.setText(str(int(val_num)))
                bar.set_pct(val_num / total_status)

        # tabela entregas
        self._table.setRowCount(0)
        for item in entregas:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setRowHeight(r, 42)
            for c, val in enumerate([
                item.get("quando", ""),
                item.get("titulo", ""),
                item.get("detalhe", ""),
                item.get("status", ""),
            ]):
                if c == 3:
                    # badge centralizado
                    w = QWidget()
                    w.setStyleSheet("background:transparent;")
                    wl = QHBoxLayout(w)
                    wl.setContentsMargins(6, 4, 6, 4)
                    wl.addStretch()
                    wl.addWidget(_badge(val))
                    wl.addStretch()
                    self._table.setCellWidget(r, c, w)
                else:
                    cell = QTableWidgetItem(str(val))
                    cell.setFont(QFont("Segoe UI", 11 if c > 0 else 10))
                    if c == 0:
                        cell.setForeground(QColor(T3))
                    self._table.setItem(r, c, cell)

        # financeiro
        cr = contas.get("Receber", {})
        cp = contas.get("Pagar",   {})
        cb = comb  or {}
        cm = manut or {}

        def _set_fin(nome, val, det):
            if nome in self._fin_items:
                v, d = self._fin_items[nome]
                v.setText(val)
                d.setText(det)

        _set_fin("A receber",  _brl(cr.get("total", 0)),
                               f"{_brl(cr.get('vencidas', 0))} vencidas")
        _set_fin("A pagar",    _brl(cp.get("total", 0)),
                               f"{_brl(cp.get('vencidas', 0))} vencidas")
        _set_fin("Combustível",_brl(cb.get("total", 0)),
                               f"{float(cb.get('litros', 0) or 0):,.0f} litros")
        _set_fin("Manutenção", str(cm.get("total", 0)),
                               f"{cm.get('atrasadas', 0)} atrasadas")

    def _change_period(self, value: str):
        self.tipo_periodo = value
        self._load_data()
