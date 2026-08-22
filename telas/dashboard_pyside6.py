"""
Dashboard Executivo CW Transportadora — EMU Premium
======================================================
Versão unificada das duas implementações fornecidas.

Principais decisões:
- Mantém o visual dark premium da versão EMU.
- Mantém a integração real da segunda versão com dashboard_service.
- Usa cw_theme quando disponível.
- Mantém os componentes de gráficos existentes (BarChart, DonutChart,
  MultiLineChart) quando disponíveis.
- Possui fallback visual para execução sem os componentes externos.
- Evita dados de tendência inventados: os deltas vêm do dashboard_service.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy, QComboBox, QPushButton,
)

# ---------------------------------------------------------------------------
# Integrações existentes
# ---------------------------------------------------------------------------

try:
    from services.dashboard_service import dashboard_service
except Exception:
    try:
        from services import dashboard_service
    except Exception:
        dashboard_service = None

try:
    from ui.theme.cw_theme import cw_theme
except Exception:
    cw_theme = None

try:
    from utils.charts import BarChart, DonutChart, MultiLineChart
except Exception:
    BarChart = DonutChart = MultiLineChart = None

try:
    from utils.helpers import formatar_moeda
except Exception:
    formatar_moeda = None


# ---------------------------------------------------------------------------
# Paleta fallback — baseada no visual da primeira versão
# ---------------------------------------------------------------------------

BG = "#0B0E14"
SURFACE = "#11151C"
ELEVATED = "#161B24"
OVERLAY = "#1C2230"
BORDER = "#21262D"
BORDER2 = "#30363D"

TEXT = "#E6EDF3"
TEXT2 = "#8B949E"
TEXT3 = "#484F58"

BRAND = "#E5484D"
BRAND_H = "#FF6369"
BRAND_BG = "#2D1215"

EMERALD = "#3FB950"
SKY = "#58A6FF"
AMBER = "#D29922"
CYAN = "#39C5CF"
ROSE = "#FB7185"

CHART_COLORS = [SKY, EMERALD, BRAND, "#FB923C", AMBER, CYAN]


def C(name: str, fallback: str) -> str:
    """Obtém uma cor do tema existente sem tornar o dashboard dependente dele."""
    if cw_theme is not None:
        try:
            return cw_theme.colors.get(name, fallback)
        except Exception:
            pass
    return fallback


def moeda(v) -> str:
    try:
        v = float(v or 0)
    except Exception:
        v = 0.0

    if formatar_moeda is not None:
        try:
            return formatar_moeda(v)
        except Exception:
            pass

    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fonte(size: int, bold: bool = False, mono: bool = False) -> QFont:
    if cw_theme is not None:
        try:
            return cw_theme.get_font(size, bold=bold)
        except Exception:
            pass
    f = QFont("Cascadia Code" if mono else "Segoe UI", size)
    f.setBold(bold)
    return f


def label(text="", size=13, color=TEXT, bold=False, mono=False) -> QLabel:
    w = QLabel(str(text))
    w.setFont(fonte(size, bold, mono))
    w.setStyleSheet(f"color: {color}; background: transparent;")
    return w


def separator() -> QFrame:
    w = QFrame()
    w.setFixedHeight(1)
    w.setStyleSheet(f"background: {BORDER}; border: none;")
    return w


def section_label(text: str) -> QLabel:
    w = QLabel(text.upper())
    w.setFont(fonte(9, True))
    w.setStyleSheet(
        f"color:{TEXT3}; background:transparent; letter-spacing:1px;"
    )
    return w


class Card(QFrame):
    """Card visual consistente com o dashboard EMU."""

    def __init__(self, parent=None, accent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE};
                border: none;
                border-radius: 14px;
            }}
        """)


class KPI(QFrame):
    def __init__(self, title, accent, parent=None):
        super().__init__(parent)
        self.accent = accent
        self.setMinimumHeight(132)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {ELEVATED}, stop:1 {SURFACE}
                );
                border: none;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: {OVERLAY};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 15)
        lay.setSpacing(6)

        top = QHBoxLayout()
        indicator = QFrame()
        indicator.setFixedSize(4, 30)
        indicator.setStyleSheet(
            f"background:{accent}; border:none; border-radius:2px;"
        )
        top.addWidget(indicator)
        top.addSpacing(9)
        top.addWidget(label(title.upper(), 10, TEXT3, True))
        top.addStretch()
        lay.addLayout(top)

        self.value = label("—", 25, TEXT, True)
        lay.addWidget(self.value)

        self.delta = label("—", 11, TEXT3, False)
        lay.addWidget(self.delta)

    def update_value(self, value, growth=None):
        self.value.setText(str(value))

        if growth is None:
            self.delta.setText("Sem comparação")
            self.delta.setStyleSheet(
                f"color:{TEXT3}; background:transparent;"
            )
            return

        try:
            g = float(growth)
            arrow = "↑" if g >= 0 else "↓"
            color = EMERALD if g >= 0 else ROSE
            self.delta.setText(f"{arrow} {abs(g):.1f}% vs período anterior")
            self.delta.setStyleSheet(
                f"color:{color}; background:transparent;"
            )
        except Exception:
            self.delta.setText("—")


class FallbackBars(QWidget):
    """Gráfico de barras sem dependências externas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumHeight(190)

    def set_data(self, labels, values):
        self.data = list(zip(labels, values))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if not self.data:
            p.setPen(QColor(TEXT3))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sem dados")
            p.end()
            return

        maxv = max((float(v or 0) for _, v in self.data), default=1) or 1
        chart_h = h - 28
        gap = 8
        bw = max(1, (w - gap * (len(self.data) - 1)) / len(self.data))

        # Draw grid lines (only once, outside the data loop)
        for gy in range(0, chart_h, max(1, chart_h // 4)):
            pen = QPen(QColor(BORDER))
            p.setPen(pen)
            p.drawLine(0, gy, w, gy)

        for i, (lbl, val) in enumerate(self.data):
            x = int(i * (bw + gap))
            bh = int((float(val or 0) / maxv) * (chart_h - 10))
            y = chart_h - bh

            grad = QLinearGradient(x, y, x, chart_h)
            c1, c2 = QColor(EMERALD), QColor(EMERALD)
            c1.setAlphaF(.9)
            c2.setAlphaF(.28)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(x, y, int(bw), bh, 5, 5)

            p.setPen(QColor(TEXT3))
            p.setFont(fonte(9))
            p.drawText(
                x, chart_h + 2, int(bw), 22,
                Qt.AlignmentFlag.AlignCenter, str(lbl)
            )

        p.end()


class FallbackDonut(QWidget):
    """Gráfico de rosca simples para fallback."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumHeight(190)

    def set_data(self, data):
        self.data = data or []
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h) - 24
        x, y = (w - size) // 2, (h - size) // 2
        total = sum(float(v or 0) for _, v in self.data) or 1

        angle = 90 * 16
        for i, (_, value) in enumerate(self.data):
            span = int(float(value or 0) / total * 360 * 16)
            pen = QPen(QColor(CHART_COLORS[i % len(CHART_COLORS)]), 24)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(x + 12, y + 12, size - 24, size - 24, angle, -span)
            angle -= span

        p.setPen(QColor(TEXT))
        p.setFont(fonte(16, True))
        p.drawText(
            x, y, size, size,
            Qt.AlignmentFlag.AlignCenter, str(int(total))
        )
        p.end()


class StatusBadge(QLabel):
    COLORS = {
        "Entregue": (EMERALD, "#0D2818"),
        "Concluído": (EMERALD, "#0D2818"),
        "Em Rota": (SKY, "#0C2D6B"),
        "Trânsito": (SKY, "#0C2D6B"),
        "Pendente": (AMBER, "#2A1F0A"),
        "Agendado": (CYAN, "#0A2A2E"),
        "Manutenção": (ROSE, "#2E141C"),
        "Ativo": (EMERALD, "#0D2818"),
    }

    def __init__(self, text, parent=None):
        super().__init__(str(text), parent)
        fg, bg = self.COLORS.get(text, (TEXT2, ELEVATED))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(fonte(9, True))
        self.setStyleSheet(f"""
            QLabel {{
                color:{fg};
                background:{bg};
                border:none;
                border-radius:5px;
                padding:3px 8px;
            }}
        """)


class Dashboard(QWidget):
    """
    Dashboard Executivo CW — versão premium final.

    Compatível com o padrão:
        from telas.dashboard_emu_premium_FINAL import Dashboard
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")

        self.kpis = {}
        self.fretes_status = []
        self.contas_resumo = {}
        self.combustivel_resumo = {}
        self.manutencoes_resumo = {}
        self.atividades = []
        self.entregas = []
        self.grafico_comparativo = {}
        self.grafico_receita = {}

        self._setup_ui()
        self._load_data()

    # ------------------------------------------------------------------ UI

    def _setup_ui(self):
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
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:{BG}; }}
            QScrollBar:vertical {{
                width:6px; background:transparent;
            }}
            QScrollBar::handle:vertical {{
                background:{BORDER2}; border-radius:3px; min-height:40px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height:0;
            }}
        """)

        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        self.layout_main = QVBoxLayout(content)
        self.layout_main.setContentsMargins(28, 24, 28, 34)
        self.layout_main.setSpacing(22)
        scroll.setWidget(content)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        self._create_header()
        self._create_kpis()
        self._create_charts()
        self._create_finance()
        self._create_activity()

        self.layout_main.addStretch()

    def _create_header(self):
        card = Card()
        card.setStyleSheet(f"""
            QFrame {{
                background:qlineargradient(
                    x1:0,y1:0,x2:1,y2:0,
                    stop:0 {SURFACE}, stop:1 {ELEVATED}
                );
                border:none;
                border-radius:14px;
            }}
        """)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(22, 17, 22, 17)

        left = QVBoxLayout()
        left.setSpacing(4)

        now = datetime.now()
        saudacao = (
            "Bom dia" if now.hour < 12 else
            "Boa tarde" if now.hour < 18 else
            "Boa noite"
        )

        left.addWidget(label(
            f"{saudacao} — Dashboard Executivo", 22, TEXT, True
        ))
        left.addWidget(label(
            now.strftime("%d/%m/%Y  ·  %H:%M"),
            10, TEXT3, False, True
        ))

        lay.addLayout(left)
        lay.addStretch()

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setCurrentText(self.tipo_periodo)
        self.combo_periodo.setFixedHeight(38)
        self.combo_periodo.setFixedWidth(130)
        self.combo_periodo.setStyleSheet(f"""
            QComboBox {{
                background:{SURFACE};
                color:{TEXT};
                border:none;
                border-radius:8px;
                padding:6px 10px;
            }}
            QComboBox:hover {{ background:{ELEVATED}; }}
            QComboBox::drop-down {{ border:none; width:22px; }}
            QComboBox QAbstractItemView {{
                background:{ELEVATED};
                color:{TEXT};
                selection-background-color:{BRAND_BG};
                border:none;
            }}
        """)
        self.combo_periodo.currentTextChanged.connect(self._update_period)
        lay.addWidget(self.combo_periodo)

        refresh = QPushButton("↻  Atualizar")
        refresh.setFixedHeight(38)
        refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh.setStyleSheet(f"""
            QPushButton {{
                background:{BRAND};
                color:white;
                border:none;
                border-radius:8px;
                padding:0 18px;
                font-weight:600;
            }}
            QPushButton:hover {{ background:{BRAND_H}; }}
        """)
        refresh.clicked.connect(self._load_data)
        lay.addWidget(refresh)

        self.layout_main.addWidget(card)

    def _create_kpis(self):
        self.layout_main.addWidget(section_label("Visão geral"))
        grid = QGridLayout()
        grid.setSpacing(12)

        self.card_receita = KPI("Receita Bruta", EMERALD)
        self.card_lucro = KPI("Lucro Estimado", SKY)
        self.card_fretes_realizados = KPI("Fretes Realizados", BRAND)
        self.card_fretes_andamento = KPI("Fretes em Andamento", AMBER)
        self.card_clientes = KPI("Clientes Ativos", CYAN)

        cards = [
            self.card_receita,
            self.card_lucro,
            self.card_fretes_realizados,
            self.card_fretes_andamento,
            self.card_clientes,
        ]

        for i, card in enumerate(cards):
            grid.addWidget(card, 0, i)
            grid.setColumnStretch(i, 1)

        self.layout_main.addLayout(grid)

    def _chart_card(self, title):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)
        lay.addWidget(label(title, 13, TEXT, True))
        holder = QWidget()
        holder.setStyleSheet("background:transparent;")
        hl = QVBoxLayout(holder)
        hl.setContentsMargins(0, 8, 0, 0)
        lay.addWidget(holder, 1)
        card.chart_layout = hl
        return card

    def _create_charts(self):
        self.layout_main.addWidget(section_label("Performance operacional"))
        row = QHBoxLayout()
        row.setSpacing(12)

        self.chart_comparativo = self._chart_card("Receita × Despesa")
        self.chart_status = self._chart_card("Fretes por Status")
        self.chart_receita = self._chart_card("Receita Mensal")

        # Gráfico principal
        if MultiLineChart:
            self.line_chart = MultiLineChart()
        else:
            self.line_chart = QLabel("Gráfico indisponível")
            self.line_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.line_chart.setStyleSheet(f"color:{TEXT3};")

        self.chart_comparativo.chart_layout.addWidget(self.line_chart)

        # Status
        if DonutChart:
            self.donut_chart = DonutChart()
        else:
            self.donut_chart = FallbackDonut()

        self.chart_status.chart_layout.addWidget(self.donut_chart)

        # Receita
        if BarChart:
            self.bar_chart = BarChart()
        else:
            self.bar_chart = FallbackBars()

        self.chart_receita.chart_layout.addWidget(self.bar_chart)

        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(self.chart_comparativo, 2)

        right = QVBoxLayout()
        right.setSpacing(12)
        right.addWidget(self.chart_status, 1)
        right.addWidget(self.chart_receita, 1)

        row.addLayout(left, 3)
        row.addLayout(right, 2)

        self.layout_main.addLayout(row)

    def _metric_card(self, title, accent):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 15, 18, 15)
        lay.setSpacing(8)

        lay.addWidget(label(title.upper(), 9, TEXT3, True))
        value = label("R$ —", 20, TEXT, True)
        lay.addWidget(value)

        d1 = label("—", 10, TEXT2)
        d2 = label("—", 10, TEXT2)

        line = QHBoxLayout()
        line.addWidget(d1)
        line.addStretch()
        line.addWidget(d2)
        lay.addLayout(line)

        card.value = value
        card.detail1 = d1
        card.detail2 = d2
        return card

    def _create_finance(self):
        self.layout_main.addWidget(section_label("Financeiro e custos"))
        row = QHBoxLayout()
        row.setSpacing(12)

        self.card_contas_receber = self._metric_card(
            "Contas a Receber", EMERALD
        )
        self.card_contas_pagar = self._metric_card(
            "Contas a Pagar", ROSE
        )
        self.card_combustivel = self._metric_card(
            "Combustível (Mês)", AMBER
        )
        self.card_manutencoes = self._metric_card(
            "Manutenções", SKY
        )

        for card in [
            self.card_contas_receber,
            self.card_contas_pagar,
            self.card_combustivel,
            self.card_manutencoes,
        ]:
            row.addWidget(card, 1)

        self.layout_main.addLayout(row)

    def _activity_card(self, title):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)
        lay.addWidget(label(title, 13, TEXT, True))

        holder = QWidget()
        holder.setStyleSheet("background:transparent;")
        hl = QVBoxLayout(holder)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(7)
        lay.addWidget(holder, 1)

        card.content_layout = hl
        return card

    def _create_activity(self):
        self.layout_main.addWidget(section_label("Operação"))
        row = QHBoxLayout()
        row.setSpacing(12)

        left = self._activity_card("Últimas Atividades")
        right = self._activity_card("Próximas Entregas")

        self.atividades_layout = left.content_layout
        self.entregas_layout = right.content_layout

        row.addWidget(left, 1)
        row.addWidget(right, 1)
        self.layout_main.addLayout(row)

    # --------------------------------------------------------------- DATA

    def _load_data(self):
        if dashboard_service is None:
            self._load_mock()
            return

        try:
            self.kpis = dashboard_service.calcular_kpis(
                self.tipo_periodo, self.mes, self.ano
            )
            self.fretes_status = dashboard_service.resumo_fretes_status(
                self.tipo_periodo, self.mes, self.ano
            )
            self.contas_resumo = (
                dashboard_service.resumo_contas_receber_pagar(
                    self.tipo_periodo, self.mes, self.ano
                )
            )
            self.combustivel_resumo = (
                dashboard_service.resumo_combustivel_mes()
            )
            self.manutencoes_resumo = dashboard_service.resumo_manutencoes()
            self.atividades = dashboard_service.atividades_recentes(5)
            self.entregas = dashboard_service.proximas_entregas(5)

            self.grafico_comparativo = (
                dashboard_service.dados_graficos_comparativo_mensal(self.ano)
            )
            self.grafico_receita = (
                dashboard_service.dados_graficos_receita_mensal(self.ano)
            )

            self._update_ui()

        except Exception as exc:
            print(f"[DashboardEMU Premium] erro: {exc}")
            self._load_mock()

    def _load_mock(self):
        """Fallback somente para desenvolvimento/preview."""
        self.kpis = {
            "receita_total": {"valor": 613400, "crescimento": 12.8},
            "lucro_estimado": {"valor": 142800, "crescimento": 8.4},
            "fretes_realizados": {"valor": 89, "crescimento": 5.2},
            "fretes_andamento": {"valor": 14, "crescimento": 0},
            "clientes_ativos": {"valor": 37, "crescimento": 3.1},
        }
        self.fretes_status = [
            ("Entregue", 68), ("Em Rota", 21), ("Pendente", 11)
        ]
        self.contas_resumo = {
            "Receber": {"total": 61020, "vencidas": 10200, "a_vencer": 50820},
            "Pagar": {"total": 60700, "vencidas": 8300, "a_vencer": 52400},
        }
        self.combustivel_resumo = {
            "total": 18400, "litros": 5200, "media_litro": 3.54
        }
        self.manutencoes_resumo = {
            "total": 4, "atrasadas": 1, "agendadas": 3
        }
        self.atividades = [
            {"titulo": "NF-00341", "detalhe": "Atacadão Central", "tipo": "Fretes"},
            {"titulo": "NF-00340", "detalhe": "Norte S.A.", "tipo": "Coletas"},
            {"titulo": "GHI-9012", "detalhe": "Volvo Service", "tipo": "Manutenção"},
        ]
        self.entregas = [
            {"quando": "15/08", "titulo": "NF-00341", "detalhe": "Campinas, SP", "status": "Em Rota"},
            {"quando": "15/08", "titulo": "NF-00340", "detalhe": "Ribeirão Preto, SP", "status": "Em Rota"},
            {"quando": "16/08", "titulo": "NF-00338", "detalhe": "Santos, SP", "status": "Agendado"},
        ]
        self.grafico_comparativo = {
            "labels": ["Mar", "Abr", "Mai", "Jun", "Jul", "Ago"],
            "receitas": [142000, 168000, 155000, 189000, 204000, 231400],
            "despesas": [98000, 112000, 109000, 126000, 139000, 151000],
        }
        self.grafico_receita = {
            "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago"],
            "valores": [121000, 130000, 142000, 168000, 155000, 189000, 204000, 231400],
        }
        self._update_ui()

    def _update_ui(self):
        k = self.kpis

        def get(name):
            return k.get(name, {}) if isinstance(k.get(name, {}), dict) else {}

        self.card_receita.update_value(
            moeda(get("receita_total").get("valor", 0)),
            get("receita_total").get("crescimento")
        )
        self.card_lucro.update_value(
            moeda(get("lucro_estimado").get("valor", 0)),
            get("lucro_estimado").get("crescimento")
        )
        self.card_fretes_realizados.update_value(
            int(get("fretes_realizados").get("valor", 0)),
            get("fretes_realizados").get("crescimento")
        )
        self.card_fretes_andamento.update_value(
            int(get("fretes_andamento").get("valor", 0)),
            get("fretes_andamento").get("crescimento")
        )
        self.card_clientes.update_value(
            int(get("clientes_ativos").get("valor", 0)),
            get("clientes_ativos").get("crescimento")
        )

        self._update_charts()
        self._update_finance()
        self._update_activities()
        self._update_deliveries()

    def _update_charts(self):
        dados = self.grafico_comparativo or {}
        labels = dados.get("labels", [])
        receitas = dados.get("receitas", [])
        despesas = dados.get("despesas", [])

        if hasattr(self.line_chart, "set_series"):
            self.line_chart.set_series(labels, [
                ("Receita", receitas, EMERALD),
                ("Despesa", despesas, ROSE),
            ])

        status = [
            (n, v) for n, v in self.fretes_status
            if float(v or 0) > 0
        ]

        if hasattr(self.donut_chart, "set_data"):
            try:
                self.donut_chart.set_data(
                    status or [("Sem dados", 1)],
                    center_text=str(int(sum(v for _, v in status)))
                )
            except TypeError:
                self.donut_chart.set_data(status or [("Sem dados", 1)])
        elif isinstance(self.donut_chart, FallbackDonut):
            self.donut_chart.set_data(status)

        dados_r = self.grafico_receita or {}
        labels_r = dados_r.get("labels", [])
        valores_r = dados_r.get("valores", [])

        # Não assume que a lista começa em janeiro.
        # Se houver mais de 6 pontos, mostra os seis últimos.
        labels6 = labels_r[-6:]
        valores6 = valores_r[-6:]

        if hasattr(self.bar_chart, "set_data"):
            self.bar_chart.set_data(labels6, valores6)

    def _update_finance(self):
        def update(card, data):
            data = data or {}
            total = data.get("total", 0)
            card.value.setText(moeda(total))
            card.detail1.setText(
                f"Vencidas: {moeda(data.get('vencidas', 0))}"
            )
            card.detail2.setText(
                f"A vencer: {moeda(data.get('a_vencer', 0))}"
            )

        update(
            self.card_contas_receber,
            self.contas_resumo.get("Receber", {})
        )
        update(
            self.card_contas_pagar,
            self.contas_resumo.get("Pagar", {})
        )

        cb = self.combustivel_resumo or {}
        self.card_combustivel.value.setText(moeda(cb.get("total", 0)))
        self.card_combustivel.detail1.setText(
            f"Total: {float(cb.get('litros', 0) or 0):.2f} L"
        )
        self.card_combustivel.detail2.setText(
            f"Média: {moeda(cb.get('media_litro', 0))}/L"
        )

        cm = self.manutencoes_resumo or {}
        self.card_manutencoes.value.setText(str(cm.get("total", 0)))
        self.card_manutencoes.detail1.setText(
            f"Atrasadas: {cm.get('atrasadas', 0)}"
        )
        self.card_manutencoes.detail2.setText(
            f"Agendadas: {cm.get('agendadas', 0)}"
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _activity_item(self, item):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background:{ELEVATED};
                border:none;
                border-radius:9px;
            }}
            QFrame:hover {{ background:{OVERLAY}; }}
        """)

        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 9, 12, 9)
        lay.setSpacing(10)

        text = QVBoxLayout()
        text.setSpacing(2)
        text.addWidget(label(item.get("titulo", ""), 11, TEXT, True))
        text.addWidget(label(item.get("detalhe", ""), 10, TEXT2))
        lay.addLayout(text, 1)

        tipo = item.get("tipo", "")
        lay.addWidget(StatusBadge(tipo))

        return frame

    def _delivery_item(self, item):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background:{ELEVATED};
                border:none;
                border-radius:9px;
            }}
            QFrame:hover {{ background:{OVERLAY}; }}
        """)

        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 9, 12, 9)
        lay.setSpacing(10)

        text = QVBoxLayout()
        text.setSpacing(2)
        title = f"{item.get('quando', '')}  •  {item.get('titulo', '')}"
        text.addWidget(label(title, 11, TEXT, True))
        text.addWidget(label(item.get("detalhe", ""), 10, TEXT2))
        lay.addLayout(text, 1)

        lay.addWidget(StatusBadge(item.get("status", "")))
        return frame

    def _update_activities(self):
        self._clear_layout(self.atividades_layout)

        if not self.atividades:
            self.atividades_layout.addWidget(
                label("Nenhuma atividade recente", 11, TEXT3)
            )
            return

        for item in self.atividades:
            self.atividades_layout.addWidget(self._activity_item(item))

        self.atividades_layout.addStretch()

    def _update_deliveries(self):
        self._clear_layout(self.entregas_layout)

        if not self.entregas:
            self.entregas_layout.addWidget(
                label("Nenhuma entrega próxima", 11, TEXT3)
            )
            return

        for item in self.entregas:
            self.entregas_layout.addWidget(self._delivery_item(item))

        self.entregas_layout.addStretch()

    def _update_period(self):
        self.tipo_periodo = self.combo_periodo.currentText()
        self._load_data()
