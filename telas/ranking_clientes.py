"""
CW Transportadora — Ranking de Clientes EMU
Versão simplificada sem threading
"""
from __future__ import annotations

import csv
from datetime import datetime

from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox, QPushButton, QLineEdit,
    QTableView, QHeaderView, QAbstractItemView,
    QSizePolicy, QGraphicsDropShadowEffect, QFileDialog, QMessageBox,
)

try:
    from services.ranking_service import ranking_service
except Exception:
    ranking_service = None

def _brl(v):
    try:
        v = float(v or 0)
    except Exception:
        v = 0.0
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def _peso(kg: float) -> str:
    if kg >= 1000:
        return f"{kg/1000:,.2f} t".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{kg:,.0f} kg".replace(",", ".")

# Paleta
BG = "#080B11"
SURF = "#0D1117"
ELEV = "#161B22"
B1 = "#21262D"
B2 = "#30363D"
T1 = "#F0F6FC"
T2 = "#8B949E"
T3 = "#484F58"
BRAND = "#E5484D"
BRAND_H = "#FF6369"
BRAND_BG = "#2D1215"
EMERALD = "#3FB950"
SKY = "#58A6FF"
AMBER = "#D29922"
ROSE = "#FB7185"
VIOLET = "#A78BFA"
CYAN = "#39C5CF"

_MEDALHAS = ["🥇", "🥈", "🥉"]
_RANK_CORES = [AMBER, T2, "#CD7F32", T3, T3]

def _lbl(text="", size=11, color=T1, bold=False, mono=False) -> QLabel:
    lb = QLabel(str(text))
    f = QFont("Cascadia Code" if mono else "Segoe UI", size)
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

class BarrasHorizontais(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: list[dict] = []
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background:transparent;")

    def set_dados(self, dados: list[dict]):
        self._dados = dados[:8]
        self.update()

    def paintEvent(self, _):
        if not self._dados:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        n = len(self._dados)
        if n == 0:
            p.end()
            return
        pad_l, pad_r, pad_t, pad_b = 8, 120, 8, 8
        row_h = (H - pad_t - pad_b) / n
        max_val = max(d.get("frete", 0) for d in self._dados) or 1
        nome_w = 160
        bar_x = pad_l + nome_w + 12
        bar_max_w = W - bar_x - pad_r - 8
        for i, d in enumerate(self._dados):
            y = pad_t + i * row_h
            cy = y + row_h / 2
            rank_txt = _MEDALHAS[i] if i < 3 else f"#{i+1}"
            p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            p.setPen(QColor(_RANK_CORES[min(i, len(_RANK_CORES)-1)]))
            p.drawText(pad_l, int(y), nome_w - 4, int(row_h), Qt.AlignmentFlag.AlignVCenter, rank_txt)
            nome = d.get("cliente", "")
            p.setFont(QFont("Segoe UI", 10))
            p.setPen(QColor(T2 if i >= 3 else T1))
            metrics = p.fontMetrics()
            nome_px = nome_w - 32
            nome_elidido = metrics.elidedText(nome, Qt.TextElideMode.ElideRight, nome_px)
            p.drawText(pad_l + 28, int(y), nome_px, int(row_h), Qt.AlignmentFlag.AlignVCenter, nome_elidido)
            val = d.get("frete", 0)
            bw = int(bar_max_w * val / max_val)
            bh = max(int(row_h * 0.38), 6)
            by = int(cy - bh / 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(ELEV))
            p.drawRoundedRect(bar_x, by, int(bar_max_w), bh, 3, 3)
            if bw > 0:
                c1 = QColor(BRAND if i == 0 else SKY if i == 1 else EMERALD if i == 2 else T3)
                c2 = QColor(c1)
                c2.setAlphaF(0.4)
                grad = QLinearGradient(bar_x, 0, bar_x + bw, 0)
                grad.setColorAt(0, c1)
                grad.setColorAt(1, c2)
                p.setBrush(QBrush(grad))
                p.drawRoundedRect(bar_x, by, bw, bh, 3, 3)
            p.setFont(QFont("Cascadia Code", 9, QFont.Weight.Bold))
            p.setPen(QColor(T2))
            p.drawText(W - pad_r, int(y), pad_r - 4, int(row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, _brl(val))
        p.end()

_COLUNAS = ["#", "Cliente", "Fretes", "Frete Total", "Peso", "% Médio"]

class RankingModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados: list[dict] = []

    def carregar(self, dados: list[dict]):
        self.beginResetModel()
        self._dados = dados
        self.endResetModel()

    def rowCount(self, _=QModelIndex()):
        return len(self._dados)

    def columnCount(self, _=QModelIndex()):
        return len(_COLUNAS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return _COLUNAS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        d = self._dados[row]
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return _MEDALHAS[row] if row < 3 else str(row + 1)
            if col == 1:
                return d.get("cliente", "")
            if col == 2:
                return str(int(d.get("total_notas", 0)))
            if col == 3:
                return _brl(d.get("frete", 0))
            if col == 4:
                return _peso(float(d.get("peso", 0)))
            if col == 5:
                pct = d.get("percentual_medio", 0)
                return f"{float(pct or 0):.2f}%"
        if role == Qt.ItemDataRole.ForegroundRole:
            if col == 0:
                cores = [QColor(AMBER), QColor(T2), QColor("#CD7F32")]
                return cores[row] if row < 3 else QColor(T3)
            if col == 3:
                return QColor(EMERALD)
            return QColor(T1 if col == 1 else T2)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col == 0:
                return Qt.AlignmentFlag.AlignCenter
            if col in (2, 3, 4, 5):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.FontRole:
            f = QFont("Cascadia Code" if col in (2, 3, 4, 5) else "Segoe UI", 10 if col != 0 else 13)
            f.setBold(col in (0, 1) and row < 3)
            return f
        if role == Qt.ItemDataRole.BackgroundRole:
            return QColor(SURF if row % 2 == 0 else ELEV)
        return None

    def dados_raw(self) -> list[dict]:
        return self._dados

def _dados_demo() -> list[dict]:
    return [
        {"cliente": "Atacadão Central Ltda", "total_notas": 28, "frete": 218400, "peso": 512400, "percentual_medio": 3.2, "valor_notas": 6825000},
        {"cliente": "Supermercados Norte S.A.", "total_notas": 19, "frete": 164700, "peso": 387200, "percentual_medio": 2.9, "valor_notas": 5680000},
        {"cliente": "Distribuidora Sul Atacado", "total_notas": 14, "frete": 98200, "peso": 241000, "percentual_medio": 3.5, "valor_notas": 2805700},
        {"cliente": "JV Alimentos EIRELI", "total_notas": 11, "frete": 74300, "peso": 189800, "percentual_medio": 3.1, "valor_notas": 2396800},
        {"cliente": "Comércio Leste Exportações", "total_notas": 8, "frete": 57800, "peso": 142600, "percentual_medio": 4.0, "valor_notas": 1445000},
        {"cliente": "Frigorífico Planalto", "total_notas": 7, "frete": 51200, "peso": 198300, "percentual_medio": 2.6, "valor_notas": 1969200},
        {"cliente": "Cerealista Boa Vista", "total_notas": 5, "frete": 33600, "peso": 98100, "percentual_medio": 3.8, "valor_notas": 884200},
        {"cliente": "Trans Sudeste Ltda", "total_notas": 4, "frete": 21900, "peso": 67400, "percentual_medio": 3.3, "valor_notas": 663600},
    ]

class TelaRankingClientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tipo = "Geral"
        self._mes = datetime.now().strftime("%m")
        self._ano = datetime.now().strftime("%Y")
        self._model = RankingModel()
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(1)
        self._setup_ui()
        self._carregar()

    def _setup_ui(self):
        self.setStyleSheet(f"background:{BG};")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:{BG}; }}
            QScrollBar:vertical {{ width:6px; background:transparent; }}
            QScrollBar::handle:vertical {{ background:{B2}; border-radius:3px; min-height:40px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        page = QWidget()
        page.setStyleSheet(f"background:{BG};")
        self._root = QVBoxLayout(page)
        self._root.setContentsMargins(32, 24, 32, 36)
        self._root.setSpacing(20)
        scroll.setWidget(page)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self._build_header()
        self._build_kpis()
        self._build_chart_card()
        self._build_table_card()
        self._root.addStretch()

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(_lbl("Ranking de Clientes", 18, T1, bold=True))
        col.addWidget(_lbl("Desempenho por volume de frete e receita", 9, T3))
        row.addLayout(col)
        row.addStretch()
        self._busca = QLineEdit()
        self._busca.setPlaceholderText("Buscar cliente...")
        self._busca.setFixedSize(200, 36)
        self._busca.setStyleSheet(f"""
            QLineEdit {{ background:{SURF}; color:{T1}; border:none; border-radius:8px; padding:0 12px; font-size:11px; }}
            QLineEdit:focus {{ background:{ELEV}; }}
        """)
        self._busca.textChanged.connect(lambda t: self._proxy.setFilterFixedString(t))
        row.addWidget(self._busca)
        self._combo = QComboBox()
        self._combo.addItems(["Geral", "Mês", "Ano"])
        self._combo.setFixedSize(110, 36)
        self._combo.setStyleSheet(f"""
            QComboBox {{ background:{SURF}; color:{T1}; border:none; border-radius:8px; padding:0 12px; font-size:11px; }}
            QComboBox:hover {{ background:{ELEV}; }}
            QComboBox::drop-down {{ border:none; width:20px; }}
            QComboBox::down-arrow {{ width:0; height:0; border-left:4px solid transparent; border-right:4px solid transparent; border-top:5px solid {T2}; }}
            QComboBox QAbstractItemView {{ background:{ELEV}; color:{T1}; border:none; border-radius:8px; selection-background-color:{BRAND_BG}; }}
        """)
        self._combo.currentTextChanged.connect(self._mudar_periodo)
        row.addWidget(self._combo)
        btn_csv = QPushButton("↓  Exportar CSV")
        btn_csv.setFixedSize(130, 36)
        btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_csv.setStyleSheet(f"""
            QPushButton {{ background:{ELEV}; color:{T2}; border:none; border-radius:8px; font-size:11px; font-weight:600; }}
            QPushButton:hover {{ background:{B1}; color:{T1}; }}
        """)
        btn_csv.clicked.connect(self._exportar_csv)
        row.addWidget(btn_csv)
        self._btn_refresh = QPushButton("↻  Atualizar")
        self._btn_refresh.setFixedSize(120, 36)
        self._btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_refresh.setStyleSheet(f"""
            QPushButton {{ background:{BRAND}; color:#fff; border:none; border-radius:8px; font-size:11px; font-weight:700; }}
            QPushButton:hover {{ background:{BRAND_H}; }}
            QPushButton:pressed {{ background:#CC3D42; }}
        """)
        self._btn_refresh.clicked.connect(self._carregar)
        row.addWidget(self._btn_refresh)
        self._root.addLayout(row)
        self._root.addWidget(_sep())

    def _build_kpis(self):
        self._kpi_widgets: list[tuple[QLabel, QLabel]] = []
        row = QHBoxLayout()
        row.setSpacing(12)
        cores = [BRAND, EMERALD, SKY, AMBER]
        titulos = ["Clientes Ativos", "Frete Total", "Notas Fiscais", "Peso Transportado"]
        for i, (titulo, cor) in enumerate(zip(titulos, cores)):
            card = Card(accent=cor)
            lay = QVBoxLayout(card)
            lay.setContentsMargins(18, 14, 18, 14)
            lay.setSpacing(4)
            bar = QFrame()
            bar.setFixedHeight(3)
            bar.setStyleSheet(f"background:{cor};border:none;border-radius:2px;")
            lay.addWidget(bar)
            lay.addSpacing(4)
            lay.addWidget(_lbl(titulo.upper(), 9, T3))
            val = _lbl("—", 20, T1, bold=True)
            sub = _lbl("", 9, T3, mono=True)
            lay.addWidget(val)
            lay.addWidget(sub)
            row.addWidget(card)
            self._kpi_widgets.append((val, sub))
        self._root.addLayout(row)

    def _build_chart_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(10)
        head = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(_lbl("Top Clientes por Frete", 13, T1, bold=True))
        col.addWidget(_lbl("Volume de frete por cliente (R$)", 9, T3))
        head.addLayout(col)
        head.addStretch()
        lay.addLayout(head)
        self._barras = BarrasHorizontais()
        self._barras.setMinimumHeight(260)
        lay.addWidget(self._barras)
        self._root.addWidget(card)

    def _build_table_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)
        head = QHBoxLayout()
        head.addWidget(_lbl("Tabela Completa", 13, T1, bold=True))
        head.addStretch()
        self._lbl_total = _lbl("", 9, T3, mono=True)
        head.addWidget(self._lbl_total)
        lay.addLayout(head)
        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.setSortingEnabled(True)
        self._table.setMinimumHeight(280)
        self._table.verticalHeader().setDefaultSectionSize(44)
        self._table.setStyleSheet(f"""
            QTableView {{ background:{SURF}; border:none; color:{T1}; font-size:11px; font-family:'Segoe UI'; outline:0; }}
            QHeaderView::section {{ background:{BG}; color:{T3}; border:none; padding:10px; font-size:9px; font-weight:700; font-family:'Segoe UI'; letter-spacing:0.5px; }}
            QHeaderView::section:hover {{ color:{T1}; }}
            QTableView::item {{ border:none; padding:0 10px; }}
            QTableView::item:selected {{ background:{BRAND_BG}; color:{T1}; }}
            QScrollBar:vertical {{ width:6px; background:transparent; }}
            QScrollBar::handle:vertical {{ background:{B2}; border-radius:3px; min-height:40px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        lay.addWidget(self._table)
        self._root.addWidget(card)

    def _carregar(self):
        self._btn_refresh.setText("Carregando...")
        self._btn_refresh.setEnabled(False)
        try:
            if ranking_service:
                dados = ranking_service.carregar_ranking(self._tipo, self._mes, self._ano)
            else:
                dados = _dados_demo()
        except Exception as e:
            print(f"[Ranking] Erro: {e}")
            dados = _dados_demo()
        self._render(dados)
        self._btn_refresh.setText("↻  Atualizar")
        self._btn_refresh.setEnabled(True)

    def _render(self, dados: list[dict]):
        self._model.carregar(dados)
        self._barras.set_dados(dados)
        n = len(dados)
        total_frete = sum(d.get("frete", 0) for d in dados)
        total_notas = sum(d.get("total_notas", 0) for d in dados)
        total_peso = sum(d.get("peso", 0) for d in dados)
        vals = [
            (_brl(n), ""),
            (_brl(total_frete), "no período"),
            (str(int(total_notas)), "emitidas"),
            (_peso(total_peso), "transportados"),
        ]
        for (v, s), (val_lb, sub_lb) in zip(vals, self._kpi_widgets):
            val_lb.setText(v)
            sub_lb.setText(s)
        self._lbl_total.setText(f"{n} cliente{'s' if n != 1 else ''} encontrado{'s' if n != 1 else ''}")

    def _mudar_periodo(self, valor: str):
        self._tipo = valor
        self._carregar()

    def _exportar_csv(self):
        dados = self._model.dados_raw()
        if not dados:
            QMessageBox.information(self, "Exportar", "Nenhum dado para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", f"ranking_clientes_{self._tipo.lower()}.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["posicao", "cliente", "total_notas", "frete", "peso", "percentual_medio", "valor_notas"])
                writer.writeheader()
                for i, d in enumerate(dados, 1):
                    writer.writerow({
                        "posicao": i, "cliente": d.get("cliente", ""), "total_notas": d.get("total_notas", 0),
                        "frete": d.get("frete", 0), "peso": d.get("peso", 0), "percentual_medio": d.get("percentual_medio", 0), "valor_notas": d.get("valor_notas", 0),
                    })
            QMessageBox.information(self, "Exportar", f"Arquivo salvo:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao exportar", str(e))
