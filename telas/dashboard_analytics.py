"""
CW TRANSPORTADORA — ANALYTICS TEMPLATE
Redesign baseado em padrões modernos de dashboards analytics:
- navegação HORIZONTAL, sem sidebar
- header compacto
- faixa de filtros
- hero financeiro grande
- gráfico principal ocupando a maior área
- "health rail" de operação à direita
- tabela operacional em largura total
- cards pequenos apenas onde fazem sentido

A lógica de dados preserva o dashboard_service existente.
"""

from __future__ import annotations
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)

try:
    from services import dashboard_service
except Exception:
    dashboard_service = None

try:
    from utils.helpers import formatar_moeda
except Exception:
    formatar_moeda = None

# Charts não importados para evitar dependência de cw_theme
BarChart = DonutChart = MultiLineChart = None


# ---------------------------- theme ----------------------------

BG = "#F7F8FA"
WHITE = "#FFFFFF"
INK = "#171A1F"
SUB = "#667085"
FAINT = "#98A2B3"
LINE = "#EAECF0"

RED = "#C9343D"
RED_LIGHT = "#FFF1F2"
GREEN = "#15803D"
GREEN_LIGHT = "#ECFDF3"
BLUE = "#2563EB"
BLUE_LIGHT = "#EFF6FF"
ORANGE = "#C66A16"
ORANGE_LIGHT = "#FFF7ED"
PURPLE = "#6941C6"
PURPLE_LIGHT = "#F4F3FF"


def font(size, bold=False):
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    return f


def label(value="", size=10, color=INK, bold=False):
    w = QLabel(str(value))
    w.setFont(font(size, bold))
    w.setStyleSheet(f"background:transparent;color:{color};")
    return w


def money(v):
    try:
        v = float(v or 0)
    except Exception:
        v = 0
    if formatar_moeda:
        try:
            return formatar_moeda(v)
        except Exception:
            pass
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Surface(QFrame):
    def __init__(self, radius=12):
        super().__init__()
        self.setStyleSheet(
            f"""
            QFrame {{
                background:{WHITE};
                border:1px solid {LINE};
                border-radius:{radius}px;
            }}
            """
        )


class StatusDot(QLabel):
    def __init__(self, text_value, color):
        super().__init__(f"●  {text_value}")
        self.setFont(font(9, True))
        self.setStyleSheet(f"background:transparent;color:{color};")


class DashboardCW(QWidget):
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

        self._build()
        QTimer.singleShot(0, self._load_data)

    # ============================================================
    # LAYOUT — NÃO É O LAYOUT ANTERIOR
    # ============================================================

    def _build(self):
        self.setStyleSheet(f"background:{BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"""
            QScrollArea{{border:none;background:{BG};}}
            QScrollBar:vertical{{width:7px;background:transparent;}}
            QScrollBar::handle:vertical{{background:#D0D5DD;border-radius:4px;}}
            """
        )

        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        self.root = QVBoxLayout(page)
        self.root.setContentsMargins(34, 26, 34, 40)
        self.root.setSpacing(16)

        scroll.setWidget(page)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)

        self._topbar()
        self._filters()
        self._hero()
        self._analytics()
        self._operations()

    # ---------- top bar horizontal ----------
    def _topbar(self):
        row = QHBoxLayout()
        row.setSpacing(24)

        # Brand
        brand = QVBoxLayout()
        brand.setSpacing(0)
        brand.addWidget(label("CW TRANSPORTADORA", 15, INK, True))
        brand.addWidget(label("Executive Analytics", 8, FAINT))
        row.addLayout(brand)
        row.addSpacing(25)

        for item in ["Dashboard", "Operação", "Financeiro", "Frota", "Relatórios"]:
            b = QPushButton(item)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                f"""
                QPushButton {{
                    background:transparent;border:none;
                    color:{SUB};font-size:10px;font-weight:600;
                    padding:8px 2px;
                }}
                QPushButton:hover{{color:{INK};}}
                """
            )
            row.addWidget(b)

        row.addStretch()

        today = label(datetime.now().strftime("%d/%m/%Y"), 9, SUB, True)
        row.addWidget(today)

        self.root.addLayout(row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{LINE};border:none;")
        self.root.addWidget(sep)

    # ---------- filter strip ----------
    def _filters(self):
        p = QFrame()
        p.setStyleSheet("background:transparent;border:none;")
        l = QHBoxLayout(p)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(8)

        l.addWidget(label("VISÃO", 8, FAINT, True))

        self.combo = QComboBox()
        self.combo.addItems(["Geral", "Mês", "Ano"])
        self.combo.setFixedSize(100, 34)
        self.combo.setStyleSheet(
            f"""
            QComboBox {{
                background:{WHITE};color:{INK};
                border:1px solid {LINE};border-radius:8px;
                padding:0 9px;font-size:10px;font-weight:600;
            }}
            QComboBox::drop-down{{border:none;}}
            """
        )
        self.combo.currentTextChanged.connect(self._change_period)
        l.addWidget(self.combo)

        self.refresh = QPushButton("↻ Atualizar")
        self.refresh.setFixedSize(100,34)
        self.refresh.setStyleSheet(
            f"""
            QPushButton {{
                background:{WHITE};color:{SUB};
                border:1px solid {LINE};border-radius:8px;
                font-size:9px;font-weight:600;
            }}
            QPushButton:hover{{border-color:{RED};color:{RED};}}
            """
        )
        self.refresh.clicked.connect(self._load_data)
        l.addWidget(self.refresh)

        l.addStretch()

        l.addWidget(label("ATUALIZADO AGORA",8,FAINT,True))
        self.root.addWidget(p)

    # ---------- hero ----------
    def _hero(self):
        p = Surface(16)
        l = QHBoxLayout(p)
        l.setContentsMargins(24, 21, 24, 21)

        left = QVBoxLayout()
        left.setSpacing(3)
        left.addWidget(label("RECEITA BRUTA", 9, FAINT, True))
        self.hero_value = label("R$ —", 31, INK, True)
        left.addWidget(self.hero_value)
        self.hero_delta = label("—", 9, GREEN)
        left.addWidget(self.hero_delta)
        l.addLayout(left, 2)

        l.addWidget(self._vline())

        self.hero_lucro = self._metric("Lucro estimado", "R$ —", GREEN)
        self.hero_fretes = self._metric("Fretes realizados", "—", BLUE)
        self.hero_andamento = self._metric("Em andamento", "—", ORANGE)
        self.hero_clientes = self._metric("Clientes ativos", "—", PURPLE)

        for x in [
            self.hero_lucro,
            self.hero_fretes,
            self.hero_andamento,
            self.hero_clientes
        ]:
            l.addLayout(x, 1)

        self.root.addWidget(p)

    def _vline(self):
        x = QFrame()
        x.setFixedWidth(1)
        x.setStyleSheet(f"background:{LINE};border:none;")
        return x

    def _metric(self, title, value, color):
        box = QVBoxLayout()
        box.setContentsMargins(15,0,15,0)
        box.setSpacing(4)
        box.addWidget(label(title.upper(), 8, FAINT, True))
        val = label(value, 18, INK, True)
        box.addWidget(val)
        dot = label("●", 8, color)
        box.addWidget(dot)
        box.value = val
        return box

    # ---------- analytics ----------
    def _analytics(self):
        row = QHBoxLayout()
        row.setSpacing(14)

        chart = Surface(14)
        cl = QVBoxLayout(chart)
        cl.setContentsMargins(20,18,20,16)
        cl.setSpacing(8)

        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title_box.addWidget(label("Receita x despesas", 14, INK, True))
        title_box.addWidget(label("Acompanhe a margem ao longo do período", 9, SUB))
        head.addLayout(title_box)
        head.addStretch()
        head.addWidget(StatusDot("Receita", GREEN))
        head.addSpacing(10)
        head.addWidget(StatusDot("Despesa", RED))
        cl.addLayout(head)

        self.chart = MultiLineChart() if MultiLineChart else QWidget()
        self.chart.setMinimumHeight(300)
        cl.addWidget(self.chart, 1)

        row.addWidget(chart, 3)

        # right panel: operational snapshot, not donut/card stack
        side = Surface(14)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(18,18,18,18)
        sl.setSpacing(12)

        sl.addWidget(label("Resumo operacional", 14, INK, True))
        sl.addWidget(label("Onde a operação está agora", 9, SUB))

        self._status_row(sl, "Entregues", GREEN)
        self._status_row(sl, "Em trânsito", BLUE)
        self._status_row(sl, "Pendentes", ORANGE)

        sl.addSpacing(5)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{LINE};border:none;")
        sl.addWidget(sep)

        sl.addWidget(label("Utilização", 11, INK, True))
        self.util_frota = self._util_row("Frota disponível", 86, BLUE)
        self.util_prazo = self._util_row("Entregas no prazo", 92, GREEN)
        self.util_fin = self._util_row("Contas em dia", 83, PURPLE)
        sl.addWidget(self.util_frota)
        sl.addWidget(self.util_prazo)
        sl.addWidget(self.util_fin)
        sl.addStretch()

        row.addWidget(side, 1)
        self.root.addLayout(row)

    def _status_row(self, parent, name, color):
        r = QHBoxLayout()
        r.addWidget(StatusDot(name, color))
        r.addStretch()
        value = label("—", 11, INK, True)
        r.addWidget(value)
        parent.addLayout(r)
        return value

    def _util_row(self, name, pct, color):
        box = QVBoxLayout()
        box.setSpacing(4)
        top = QHBoxLayout()
        top.addWidget(label(name, 9, SUB))
        top.addStretch()
        val = label(f"{pct}%", 9, INK, True)
        top.addWidget(val)
        box.addLayout(top)

        bar = QFrame()
        bar.setFixedHeight(6)
        bar.setStyleSheet(
            f"""
            QFrame {{
                background:#F0F2F5;border:none;border-radius:3px;
            }}
            """
        )
        # fixed child fill
        fill = QFrame(bar)
        fill.setGeometry(0,0,int(180*pct/100),6)
        fill.setStyleSheet(f"background:{color};border-radius:3px;")
        box.addWidget(bar)
        return QWidgetProxy(box)

    # ---------- operations ----------
    def _operations(self):
        title = QHBoxLayout()
        title.addWidget(label("Operação", 16, INK, True))
        title.addWidget(label("  /  visão de campo", 9, FAINT))
        title.addStretch()
        self.root.addLayout(title)

        row = QHBoxLayout()
        row.setSpacing(14)

        # full-width operational table
        table_panel = Surface(14)
        tl = QVBoxLayout(table_panel)
        tl.setContentsMargins(18,16,18,18)
        tl.setSpacing(8)

        tl.addWidget(label("Próximas entregas", 13, INK, True))
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["Data","Documento","Destino","Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setMinimumHeight(205)
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background:{WHITE};border:none;
                color:{INK};font-size:10px;
            }}
            QHeaderView::section {{
                background:#F8F9FB;color:{FAINT};
                border:none;border-bottom:1px solid {LINE};
                padding:8px;font-size:8px;font-weight:700;
            }}
            QTableWidget::item {{
                border-bottom:1px solid #F1F2F4;
                padding:8px;
            }}
            """
        )
        tl.addWidget(self.table)
        row.addWidget(table_panel, 3)

        # compact finance rail
        rail = Surface(14)
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(18,16,18,18)
        rl.setSpacing(10)
        rl.addWidget(label("Financeiro", 13, INK, True))
        rl.addWidget(label("posição resumida", 9, SUB))

        self.fin_receive = self._finance_item(rl,"A receber",GREEN)
        self.fin_pay = self._finance_item(rl,"A pagar",RED)
        self.fin_fuel = self._finance_item(rl,"Combustível",ORANGE)
        self.fin_maint = self._finance_item(rl,"Manutenção",BLUE)

        rl.addStretch()
        row.addWidget(rail, 1)

        self.root.addLayout(row)

    def _finance_item(self, parent, title, color):
        box = QFrame()
        box.setStyleSheet(
            f"""
            QFrame {{
                background:{BG};
                border:1px solid {LINE};
                border-left:3px solid {color};
                border-radius:8px;
            }}
            """
        )
        l = QVBoxLayout(box)
        l.setContentsMargins(10,8,10,8)
        l.setSpacing(1)
        l.addWidget(label(title,8,SUB,True))
        val = label("R$ —",13,INK,True)
        det = label("—",8,FAINT)
        l.addWidget(val)
        l.addWidget(det)
        parent.addWidget(box)
        box.value = val
        box.detail = det
        return box

    # ============================================================
    # DATA
    # ============================================================

    def _load_data(self):
        if dashboard_service is None:
            self._demo()
            return

        try:
            self.kpis = dashboard_service.calcular_kpis(
                self.tipo_periodo, self.mes, self.ano
            )
            self.fretes_status = dashboard_service.resumo_fretes_status(
                self.tipo_periodo, self.mes, self.ano
            )
            self.contas_resumo = dashboard_service.resumo_contas_receber_pagar(
                self.tipo_periodo, self.mes, self.ano
            )
            self.combustivel_resumo = dashboard_service.resumo_combustivel_mes()
            self.manutencoes_resumo = dashboard_service.resumo_manutencoes()
            self.entregas = dashboard_service.proximas_entregas(8)
            self.grafico_comparativo = dashboard_service.dados_graficos_comparativo_mensal(self.ano)
            self._refresh()
        except Exception as e:
            print("[EMU TEMPLATE]", e)
            self._demo()

    def _demo(self):
        self.kpis = {
            "receita_total":{"valor":613400,"crescimento":12.8},
            "lucro_estimado":{"valor":142800,"crescimento":8.4},
            "fretes_realizados":{"valor":89,"crescimento":5.2},
            "fretes_andamento":{"valor":14,"crescimento":0},
            "clientes_ativos":{"valor":37,"crescimento":3.1},
        }
        self.fretes_status = [("Entregue",68),("Em Rota",21),("Pendente",11)]
        self.contas_resumo = {
            "Receber":{"total":61020,"vencidas":10200},
            "Pagar":{"total":60700,"vencidas":8300},
        }
        self.combustivel_resumo = {"total":18400,"litros":5200}
        self.manutencoes_resumo = {"total":4,"atrasadas":1}
        self.entregas = [
            {"quando":"15/08","titulo":"NF-00341","detalhe":"Campinas, SP","status":"Em Rota"},
            {"quando":"15/08","titulo":"NF-00340","detalhe":"Ribeirão Preto, SP","status":"Em Rota"},
            {"quando":"16/08","titulo":"NF-00338","detalhe":"Santos, SP","status":"Agendado"},
            {"quando":"18/08","titulo":"NF-00331","detalhe":"Curitiba, PR","status":"Agendado"},
        ]
        self.grafico_comparativo = {
            "labels":["Mar","Abr","Mai","Jun","Jul","Ago"],
            "receitas":[142000,168000,155000,189000,204000,231400],
            "despesas":[98000,112000,109000,126000,139000,151000],
        }
        self._refresh()

    def _refresh(self):
        def get(k):
            v = self.kpis.get(k,{})
            return v if isinstance(v,dict) else {}

        rec=get("receita_total")
        luc=get("lucro_estimado")
        fre=get("fretes_realizados")
        andam=get("fretes_andamento")
        cli=get("clientes_ativos")

        self.hero_value.setText(money(rec.get("valor",0)))
        g=rec.get("crescimento")
        self.hero_delta.setText(
            f"↑ {float(g):.1f}% vs. período anterior" if g is not None else "Sem comparação"
        )

        self.hero_lucro.value.setText(money(luc.get("valor",0)))
        self.hero_fretes.value.setText(str(int(fre.get("valor",0))))
        self.hero_andamento.value.setText(str(int(andam.get("valor",0))))
        self.hero_clientes.value.setText(str(int(cli.get("valor",0))))

        d=self.grafico_comparativo or {}
        if hasattr(self.chart,"set_series"):
            self.chart.set_series(
                d.get("labels",[]),
                [
                    ("Receita",d.get("receitas",[]),GREEN),
                    ("Despesa",d.get("despesas",[]),RED)
                ]
            )

        if hasattr(self, "table"):
            self.table.setRowCount(0)
            for item in self.entregas:
                r=self.table.rowCount()
                self.table.insertRow(r)
                vals=[
                    item.get("quando",""),
                    item.get("titulo",""),
                    item.get("detalhe",""),
                    item.get("status",""),
                ]
                for c,v in enumerate(vals):
                    cell=QTableWidgetItem(str(v))
                    if c==3:
                        cell.setForeground(QColor(BLUE if v=="Em Rota" else ORANGE))
                    self.table.setItem(r,c,cell)

        cr=self.contas_resumo.get("Receber",{})
        cp=self.contas_resumo.get("Pagar",{})
        cb=self.combustivel_resumo or {}
        cm=self.manutencoes_resumo or {}

        self.fin_receive.value.setText(money(cr.get("total",0)))
        self.fin_receive.detail.setText(f"{money(cr.get('vencidas',0))} vencidas")

        self.fin_pay.value.setText(money(cp.get("total",0)))
        self.fin_pay.detail.setText(f"{money(cp.get('vencidas',0))} vencidas")

        self.fin_fuel.value.setText(money(cb.get("total",0)))
        self.fin_fuel.detail.setText(f"{float(cb.get('litros',0) or 0):,.0f} litros")

        self.fin_maint.value.setText(str(cm.get("total",0)))
        self.fin_maint.detail.setText(f"{cm.get('atrasadas',0)} atrasadas")

    def _change_period(self, value):
        self.tipo_periodo=value
        self._load_data()


class QWidgetProxy(QWidget):
    """Pequeno adaptador para aceitar QLayout como widget em uma coluna."""
    def __init__(self, layout):
        super().__init__()
        self.setLayout(layout)
        self.setMinimumHeight(38)
