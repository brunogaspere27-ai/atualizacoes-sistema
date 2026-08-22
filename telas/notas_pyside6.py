from __future__ import annotations

import threading
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QFrame,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QComboBox, QLineEdit, QAbstractItemView,
    QPushButton, QDialog, QInputDialog,
)

from services.notas_service import notas_service
from services.viagem_service import viagem_service
from ui.theme.cw_theme import cw_theme
from utils.helpers import formatar_moeda, formatar_peso
from utils.logger import get_logger

logger = get_logger(__name__)


_R = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
_C = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter


def _item(text: str, align=_C if False else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) -> QTableWidgetItem:
    c = cw_theme.colors
    item = QTableWidgetItem(str(text) if text not in (None, "") else "—")
    item.setTextAlignment(align)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    item.setForeground(QColor(c['text_primary']))
    return item


class _KpiTile(QFrame):
    def __init__(self, label: str, accent: str, parent=None):
        super().__init__(parent)
        self._accent = accent
        c = cw_theme.colors
        self.setMinimumHeight(84)
        self.setStyleSheet(f"""
            QFrame {{
                background: {c['bg_elevated']};
                border: 1px solid {c['border_subtle']};
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(3)
        label_widget = QLabel(label.upper())
        label_widget.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        label_widget.setStyleSheet(f"color:{c['text_tertiary']};background:transparent;letter-spacing:1.2px;")
        lay.addWidget(label_widget)
        self._value = QLabel("—")
        self._value.setFont(QFont("Cascadia Code", 20, QFont.Weight.Bold))
        self._value.setStyleSheet(f"color:{accent};background:transparent;")
        lay.addWidget(self._value)

    def set_value(self, value: str):
        self._value.setText(value)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self._accent))
        p.drawRoundedRect(0, 18, 3, max(0, self.height() - 36), 2, 2)


class _ManifestoCard(QFrame):
    clicked = Signal(int)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self._data = data
        self._selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(88)
        self._build()
        self._update_appearance()

    def _build(self):
        c = cw_theme.colors
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 14, 12)
        lay.setSpacing(5)

        top = QHBoxLayout()
        nome_txt = self._data.get("nome_arquivo", "Manifesto") or f"Manifesto {self._data.get('id', '')}"
        nome = QLabel(nome_txt)
        nome.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        nome.setStyleSheet(f"color:{c['text_primary']};background:transparent;")
        nome.setWordWrap(True)
        nome.setMinimumWidth(150)
        top.addWidget(nome, 1)

        badge = QLabel(f" {self._data.get('total_notas', 0)} ")
        badge.setFont(QFont("Cascadia Code", 9, QFont.Weight.Bold))
        badge.setAlignment(_C)
        badge.setStyleSheet(f"color:{c['sky']};background:{c['sky_soft']};border-radius:9px;padding:1px 7px;")
        top.addWidget(badge)
        lay.addLayout(top)

        mid = QHBoxLayout()
        date = QLabel(self._data.get("data_importacao", "") or "—")
        date.setFont(QFont("Segoe UI", 9))
        date.setStyleSheet(f"color:{c['text_tertiary']};background:transparent;")
        mid.addWidget(date)
        mid.addStretch()
        freight = float(self._data.get("frete_total", 0) or 0)
        if freight:
            f = QLabel(formatar_moeda(freight))
            f.setFont(QFont("Cascadia Code", 9, QFont.Weight.Bold))
            f.setStyleSheet(f"color:{c['emerald']};background:transparent;")
            mid.addWidget(f)
        lay.addLayout(mid)

        bottom = QHBoxLayout()
        weight = float(self._data.get("peso_total", 0) or 0)
        w = QLabel(formatar_peso(weight))
        w.setFont(QFont("Cascadia Code", 9, QFont.Weight.Bold))
        w.setStyleSheet(f"color:{c['text_secondary']};background:transparent;")
        bottom.addWidget(w)
        bottom.addStretch()
        lay.addLayout(bottom)

    def _update_appearance(self):
        c = cw_theme.colors
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['brand_soft']};
                    border: 1.5px solid {c['brand']};
                    border-radius: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['bg_elevated']};
                    border: 1px solid {c['border_subtle']};
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    background-color: {c['bg_overlay']};
                    border-color: {c['border_strong']};
                }}
            """)

    def set_selected(self, value: bool):
        self._selected = value
        self._update_appearance()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._data["id"])
        super().mousePressEvent(event)

    def refresh_data(self, data: dict):
        self._data = data
        self._rebuild_safely()

    def _rebuild_safely(self):
        while self.layout() and self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        self._build()
        self._update_appearance()


class _DialogVeiculo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Veículo")
        self.setMinimumWidth(380)
        self.setModal(True)
        c = cw_theme.colors
        self.setStyleSheet(f"background:{c['bg_elevated']};color:{c['text_primary']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)
        title = QLabel("Novo Veículo")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{c['text_primary']};background:transparent;")
        lay.addWidget(title)

        def inp(ph):
            e = QLineEdit()
            e.setPlaceholderText(ph)
            e.setStyleSheet(f"""
                QLineEdit {{ background:{c['bg_tertiary']};color:{c['text_primary']};border:1px solid {c['border_default']};border-radius:8px;padding:9px 13px;font-size:12px; }}
                QLineEdit:focus {{ border-color:{c['brand']}; }}
            """)
            return e

        self.e_placa = inp("Placa ou nome")
        self.e_modelo = inp("Modelo")
        self.e_motorista = inp("Motorista padrão")
        self.e_capacidade = inp("Capacidade em kg")
        self.e_media = inp("Média km/L")
        for w in (self.e_placa, self.e_modelo, self.e_motorista, self.e_capacidade, self.e_media):
            lay.addWidget(w)

        btn = QPushButton("Salvar Veículo")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn.setStyleSheet(f"QPushButton{{background:{c['emerald']};color:#fff;border:none;border-radius:8px;}}QPushButton:hover{{background:#2da842;}}")
        btn.clicked.connect(self._salvar)
        lay.addWidget(btn)

    def _salvar(self):
        try:
            placa = self.e_placa.text().strip()
            modelo = self.e_modelo.text().strip()
            if not placa or not modelo:
                QMessageBox.warning(self, "Atenção", "Informe placa/nome e modelo.")
                return
            capacidade = float(self.e_capacidade.text().replace(",", ".") or 0)
            media = float(self.e_media.text().replace(",", ".") or 0)
            notas_service.cadastrar_caminhao(placa, modelo, self.e_motorista.text().strip(), capacidade, media)
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Dados inválidos", "Capacidade e média devem ser números.")
        except Exception as exc:
            logger.error(f"Erro ao cadastrar veículo: {exc}")
            QMessageBox.critical(self, "Erro", "Não foi possível cadastrar o veículo.")


class _ImportWorker(QObject):
    concluido = Signal(dict)
    erro = Signal(str)

    def __init__(self, caminho: str):
        super().__init__()
        self._caminho = caminho

    def run(self):
        try:
            self.concluido.emit(notas_service.importar_manifesto(self._caminho))
        except Exception as exc:
            logger.exception("Erro ao importar manifesto")
            self.erro.emit(str(exc))


_COL_SEL, _COL_CTE, _COL_REM, _COL_DEST, _COL_ORIG, _COL_DEST2, _COL_FRETE, _COL_PESO, _COL_STAT = range(9)
_COLS = ["✓", "CT-e", "Remetente", "Destinatário", "Origem", "Destino", "Frete", "Peso", "Status"]
_WIDTHS = [38, 155, 230, 230, 120, 130, 115, 105, 115]


class TelaNotas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._manifesto_cards: dict[int, _ManifestoCard] = {}
        self._selected_manifesto_id: Optional[int] = None
        self._notas_ids: dict[int, int] = {}
        self._notas_marcadas: set[int] = set()
        self._caminhoes_map: dict[str, int] = {}
        self._import_thread = None
        self._worker = None
        self._setup_ui()
        self._carregar_caminhoes()
        self._carregar_manifestos()

    def _setup_ui(self):
        c = cw_theme.colors
        self.setStyleSheet(f"background:{c['bg_primary']};")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())
        root.addWidget(self._build_kpi_strip())
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"QSplitter::handle{{background:{c['border_subtle']};}}")
        splitter.addWidget(self._build_left())
        splitter.addWidget(self._build_right())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([310, 900])
        root.addWidget(splitter, 1)

    def _build_header(self):
        c = cw_theme.colors
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"QFrame{{background:{c['bg_secondary']};border-bottom:1px solid {c['border_subtle']};}}")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(22, 0, 22, 0)
        col = QVBoxLayout()
        col.setSpacing(1)
        title = QLabel("Notas Fiscais")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{c['text_primary']};background:transparent;")
        sub = QLabel("Manifestos, notas fiscais e criação de viagens")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color:{c['text_tertiary']};background:transparent;")
        col.addWidget(title); col.addWidget(sub); lay.addLayout(col); lay.addStretch()

        self._combo_periodo = self._mk_combo(["Geral", "Mês", "Ano"])
        self._combo_periodo.currentTextChanged.connect(self._on_periodo_change)
        lay.addWidget(self._combo_periodo)
        self._combo_mes = self._mk_combo([f"{i:02d}" for i in range(1, 13)])
        self._combo_mes.setCurrentText(datetime.now().strftime("%m"))
        self._combo_mes.currentTextChanged.connect(lambda _: self._carregar_manifestos())
        self._combo_mes.hide(); lay.addWidget(self._combo_mes)
        year = datetime.now().year
        self._combo_ano = self._mk_combo([str(a) for a in range(year - 5, year + 2)])
        self._combo_ano.setCurrentText(str(year))
        self._combo_ano.currentTextChanged.connect(lambda _: self._carregar_manifestos())
        self._combo_ano.hide(); lay.addWidget(self._combo_ano)
        return bar

    def _build_kpi_strip(self):
        c = cw_theme.colors
        strip = QFrame(); strip.setFixedHeight(106)
        strip.setStyleSheet(f"QFrame{{background:{c['bg_secondary']};border-bottom:1px solid {c['border_subtle']};}}")
        lay = QHBoxLayout(strip); lay.setContentsMargins(18, 11, 18, 11); lay.setSpacing(10)
        self._kpi_mfst = _KpiTile("Manifestos", c['sky'])
        self._kpi_nts = _KpiTile("Notas", c['violet'])
        self._kpi_frt = _KpiTile("Frete Total", c['emerald'])
        self._kpi_pso = _KpiTile("Peso Total", c['amber'])
        self._kpi_sel = _KpiTile("Selecionadas", c['brand'])
        for w in (self._kpi_mfst, self._kpi_nts, self._kpi_frt, self._kpi_pso, self._kpi_sel): lay.addWidget(w, 1)
        return strip

    def _build_left(self):
        c = cw_theme.colors
        panel = QWidget(); panel.setMinimumWidth(275); panel.setMaximumWidth(350); panel.setStyleSheet(f"background:{c['bg_secondary']};")
        lay = QVBoxLayout(panel); lay.setContentsMargins(12, 14, 12, 14); lay.setSpacing(10)
        tb = QHBoxLayout()
        title = QLabel("Manifestos"); title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold)); title.setStyleSheet(f"color:{c['text_primary']};background:transparent;")
        tb.addWidget(title); tb.addStretch()
        self._btn_importar = self._mk_btn("+ Importar", c['sky']); self._btn_importar.clicked.connect(self._importar_manifesto)
        self._btn_apagar = self._mk_btn("Apagar", c['error']); self._btn_apagar.clicked.connect(self._apagar_manifesto)
        tb.addWidget(self._btn_importar); tb.addWidget(self._btn_apagar); lay.addLayout(tb)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea{{background:transparent;border:none;}}QScrollBar:vertical{{background:transparent;width:5px;}}QScrollBar::handle:vertical{{background:{c['border_default']};border-radius:2px;min-height:28px;}}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}")
        self._cards_container = QWidget(); self._cards_container.setStyleSheet("background:transparent;")
        self._cards_layout = QVBoxLayout(self._cards_container); self._cards_layout.setContentsMargins(0,0,0,0); self._cards_layout.setSpacing(8); self._cards_layout.addStretch()
        scroll.setWidget(self._cards_container); lay.addWidget(scroll, 1)
        return panel

    def _build_right(self):
        c = cw_theme.colors
        panel = QWidget(); panel.setStyleSheet(f"background:{c['bg_primary']};")
        lay = QVBoxLayout(panel); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        bar = QFrame(); bar.setFixedHeight(42); bar.setStyleSheet(f"QFrame{{background:{c['bg_secondary']};border-bottom:1px solid {c['border_subtle']};}}")
        bl = QHBoxLayout(bar); bl.setContentsMargins(20,0,20,0)
        self._lbl_resumo = QLabel("Selecione um manifesto para visualizar as notas."); self._lbl_resumo.setFont(QFont("Segoe UI",10)); self._lbl_resumo.setStyleSheet(f"color:{c['text_secondary']};background:transparent;")
        bl.addWidget(self._lbl_resumo); lay.addWidget(bar)
        self._tabela = QTableWidget(0, len(_COLS)); self._tabela.setHorizontalHeaderLabels(_COLS)
        self._tabela.verticalHeader().setVisible(False); self._tabela.verticalHeader().setDefaultSectionSize(42)
        self._tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection); self._tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tabela.setSortingEnabled(True); self._tabela.setShowGrid(False); self._tabela.setAlternatingRowColors(True)
        hdr = self._tabela.horizontalHeader(); hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive); hdr.setStretchLastSection(False)
        for i,w in enumerate(_WIDTHS): self._tabela.setColumnWidth(i,w)
        self._tabela.cellClicked.connect(self._on_cell_click)
        self._tabela.setStyleSheet(self._table_style()); lay.addWidget(self._tabela,1)
        lay.addWidget(self._build_trip_panel())
        return panel

    def _build_trip_panel(self):
        c = cw_theme.colors
        panel = QFrame(); panel.setStyleSheet(f"QFrame{{background:{c['bg_elevated']};border-top:2px solid {c['brand']};}}")
        lay = QVBoxLayout(panel); lay.setContentsMargins(20,12,20,12); lay.setSpacing(10)
        tr = QHBoxLayout(); title = QLabel("🚚  Criar Viagem com Notas Selecionadas"); title.setFont(QFont("Segoe UI",12,QFont.Weight.Bold)); title.setStyleSheet(f"color:{c['text_primary']};background:transparent;"); tr.addWidget(title); tr.addStretch()
        self._lbl_sel = QLabel("0 selecionadas"); self._lbl_sel.setFont(QFont("Cascadia Code",11,QFont.Weight.Bold)); self._lbl_sel.setStyleSheet(f"color:{c['amber']};background:transparent;"); tr.addWidget(self._lbl_sel); lay.addLayout(tr)
        cr = QHBoxLayout(); cr.setSpacing(10)
        self._combo_caminhoes = QComboBox(); self._combo_caminhoes.setMinimumWidth(270); self._combo_caminhoes.setStyleSheet(self._combo_style()); cr.addWidget(self._combo_caminhoes)
        self._entry_motorista = QLineEdit(); self._entry_motorista.setPlaceholderText("Motorista"); self._entry_motorista.setMinimumWidth(170); self._entry_motorista.setStyleSheet(self._input_style()); cr.addWidget(self._entry_motorista)
        btn_v = self._mk_btn("+ Veículo", c['text_secondary']); btn_v.clicked.connect(self._abrir_novo_veiculo)
        btn_c = self._mk_btn("✓ Criar Viagem", c['emerald']); btn_c.clicked.connect(self._criar_viagem)
        btn_a = self._mk_btn("✕ Apagar Viagem", c['error']); btn_a.clicked.connect(self._apagar_viagem)
        cr.addWidget(btn_v); cr.addWidget(btn_c); cr.addWidget(btn_a); cr.addStretch(); lay.addLayout(cr)
        return panel

    def _table_style(self):
        c = cw_theme.colors
        return f"""QTableWidget{{background:{c['bg_primary']};alternate-background-color:{c['bg_secondary']};border:none;outline:none;gridline-color:transparent;selection-background-color:{c['brand_soft']};selection-color:{c['text_primary']};color:{c['text_primary']};font-size:12px;}}QTableWidget::item{{padding:0 12px;border-bottom:1px solid {c['border_subtle']};color:{c['text_primary']};}}QTableWidget::item:hover{{background:{c['bg_overlay']};}}QHeaderView::section{{background:{c['bg_secondary']};color:{c['text_tertiary']};padding:8px 12px;border:none;border-bottom:2px solid {c['border_default']};font-size:9px;font-weight:700;letter-spacing:.9px;}}QScrollBar:vertical{{background:transparent;width:6px;}}QScrollBar::handle:vertical{{background:{c['border_default']};border-radius:3px;min-height:36px;}}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}QScrollBar:horizontal{{background:transparent;height:6px;}}QScrollBar::handle:horizontal{{background:{c['border_default']};border-radius:3px;min-width:36px;}}QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{{width:0;}}"""

    def _mk_combo(self, values):
        cb = QComboBox(); cb.addItems(values); cb.setStyleSheet(self._combo_style()); return cb

    def _combo_style(self):
        c = cw_theme.colors
        return f"""QComboBox{{background:{c['bg_tertiary']};color:{c['text_primary']};border:1px solid {c['border_default']};border-radius:8px;padding:6px 12px;font-size:12px;min-height:28px;}}QComboBox:focus{{border-color:{c['brand']};}}QComboBox::drop-down{{border:none;width:22px;}}QComboBox QAbstractItemView{{background:{c['bg_elevated']};color:{c['text_primary']};border:1px solid {c['border_default']};selection-background-color:{c['brand_soft']};selection-color:{c['text_primary']};padding:4px;}}"""

    def _input_style(self):
        c = cw_theme.colors
        return f"QLineEdit{{background:{c['bg_tertiary']};color:{c['text_primary']};border:1px solid {c['border_default']};border-radius:8px;padding:7px 12px;font-size:12px;}}QLineEdit:focus{{border-color:{c['brand']};}}"

    def _mk_btn(self, text, color):
        c = cw_theme.colors
        btn = QPushButton(text); btn.setFont(QFont("Segoe UI",10,QFont.Weight.Bold)); btn.setFixedHeight(32); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton{{background:{color}20;color:{color};border:1px solid {color}50;border-radius:8px;padding:0 14px;}}QPushButton:hover{{background:{color}40;border-color:{color};}}QPushButton:pressed{{background:{color}60;}}QPushButton:disabled{{background:transparent;color:{c['text_disabled']};border-color:{c['border_subtle']};}}")
        return btn

    def _on_periodo_change(self, value):
        self._combo_mes.setVisible(value == "Mês")
        self._combo_ano.setVisible(value in ("Mês", "Ano"))
        self._carregar_manifestos()

    def _obter_filtro(self):
        value = self._combo_periodo.currentText()
        return value, self._combo_mes.currentText() if value == "Mês" else None, self._combo_ano.currentText() if value in ("Mês", "Ano") else None

    def _carregar_caminhoes(self):
        self._caminhoes_map.clear()
        try: rows = viagem_service.listar_caminhoes_disponiveis()
        except Exception as exc:
            logger.error(f"Erro ao listar caminhões: {exc}"); rows = []
        self._combo_caminhoes.clear()
        for cam in rows:
            try:
                cam_id, placa, modelo, motorista, cap = cam
                text = f"{modelo} | {placa} | {float(cap or 0):,.0f} kg"
                self._caminhoes_map[text] = cam_id
                self._combo_caminhoes.addItem(text)
            except Exception:
                logger.exception("Registro de caminhão inválido")
        if not rows: self._combo_caminhoes.addItem("Nenhum caminhão cadastrado")

    def _clear_cards(self):
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._manifesto_cards.clear()

    def _carregar_manifestos(self):
        self._clear_cards()
        self._selected_manifesto_id = None
        self._notas_marcadas.clear()
        self._atualizar_selecao()
        tipo, mes, ano = self._obter_filtro()
        try: manifestos = notas_service.listar_manifestos(tipo, mes, ano)
        except Exception as exc:
            logger.error(f"Erro ao listar manifestos: {exc}"); manifestos = []
        total_notes = total_freight = total_weight = 0
        for row in manifestos:
            mid, nome, data, total_notas, *rest = row
            freight = float(rest[1] or 0) if len(rest) > 1 else 0
            weight = float(rest[2] or 0) if len(rest) > 2 else 0
            total_notes += int(total_notas or 0); total_freight += freight; total_weight += weight
            data_dict = {"id":mid,"nome_arquivo":nome,"data_importacao":data,"total_notas":int(total_notas or 0),"frete_total":freight,"peso_total":weight}
            card = _ManifestoCard(data_dict, self._cards_container); card.clicked.connect(self._selecionar_manifesto)
            self._cards_layout.insertWidget(self._cards_layout.count()-1, card); self._manifesto_cards[mid] = card
        self._kpi_mfst.set_value(str(len(manifestos))); self._kpi_nts.set_value(str(total_notes)); self._kpi_frt.set_value(formatar_moeda(total_freight)); self._kpi_pso.set_value(formatar_peso(total_weight))
        if self._manifesto_cards: self._selecionar_manifesto(next(iter(self._manifesto_cards)))
        else: self._tabela.setRowCount(0); self._lbl_resumo.setText("Nenhum manifesto encontrado.")

    def _selecionar_manifesto(self, manifesto_id):
        if manifesto_id == self._selected_manifesto_id: return
        self._notas_marcadas.clear(); self._atualizar_selecao()
        for mid, card in self._manifesto_cards.items(): card.set_selected(mid == manifesto_id)
        self._selected_manifesto_id = manifesto_id
        card = self._manifesto_cards.get(manifesto_id)
        self._carregar_notas(manifesto_id, card._data.get("nome_arquivo", "") if card else "")

    def _reload_notas(self):
        if self._selected_manifesto_id is None: return
        card = self._manifesto_cards.get(self._selected_manifesto_id)
        self._carregar_notas(self._selected_manifesto_id, card._data.get("nome_arquivo", "") if card else "")

    def _carregar_notas(self, manifesto_id, nome):
        self._notas_ids.clear(); self._tabela.setSortingEnabled(False); self._tabela.setRowCount(0)
        try: dados = notas_service.listar_notas_por_manifesto(manifesto_id)
        except Exception as exc:
            logger.error(f"Erro ao listar notas: {exc}"); dados = []
        c = cw_theme.colors; total_freight = total_weight = 0
        status_colors = {"Disponível":(c['emerald'],c['emerald_soft']),"Em viagem":(c['amber'],c['amber_soft']),"Entregue":(c['sky'],c['sky_soft'])}
        for line in dados:
            id_nota, chave, cte_num, remetente, dest, origem, destino, val_merc, freight, weight, status = line
            freight=float(freight or 0); weight=float(weight or 0); total_freight += freight; total_weight += weight
            row=self._tabela.rowCount(); self._tabela.insertRow(row); self._notas_ids[row]=id_nota
            available=status == "Disponível"; marked=id_nota in self._notas_marcadas
            sel=_item("●" if available and marked else ("○" if available else "—"), _C); sel.setForeground(QColor(c['brand'] if marked and available else c['border_strong'] if available else c['text_disabled']))
            self._tabela.setItem(row,_COL_SEL,sel); self._tabela.setItem(row,_COL_CTE,_item(cte_num or chave or "")); self._tabela.setItem(row,_COL_REM,_item(remetente)); self._tabela.setItem(row,_COL_DEST,_item(dest)); self._tabela.setItem(row,_COL_ORIG,_item(origem)); self._tabela.setItem(row,_COL_DEST2,_item(destino)); self._tabela.setItem(row,_COL_FRETE,_item(formatar_moeda(freight),_R)); self._tabela.setItem(row,_COL_PESO,_item(formatar_peso(weight),_R))
            fg,bg=status_colors.get(status,(c['text_tertiary'],c['bg_tertiary'])); st=_item(status or "—",_C); st.setForeground(QColor(fg)); st.setBackground(QColor(bg)); self._tabela.setItem(row,_COL_STAT,st)
        self._tabela.setSortingEnabled(True)
        qtd=len(dados); self._lbl_resumo.setText(f"{nome}  ·  {qtd} nota{'s' if qtd != 1 else ''}  ·  Frete {formatar_moeda(total_freight)}  ·  Peso {formatar_peso(total_weight)}" if qtd else f"{nome}  ·  Sem notas")
        self._kpi_nts.set_value(str(qtd)); self._kpi_frt.set_value(formatar_moeda(total_freight)); self._kpi_pso.set_value(formatar_peso(total_weight))
        card=self._manifesto_cards.get(manifesto_id)
        if card:
            card._data.update({"frete_total":total_freight,"peso_total":total_weight,"total_notas":qtd})
            card.set_selected(True)

    def _on_cell_click(self, row, col):
        id_nota=self._notas_ids.get(row)
        if id_nota is None: return
        status_item=self._tabela.item(row,_COL_STAT); status=status_item.text() if status_item else ""
        if status != "Disponível":
            QMessageBox.warning(self,"Não disponível",f"Nota com status '{status}' não pode ser selecionada.")
            return
        c=cw_theme.colors; item=self._tabela.item(row,_COL_SEL)
        if id_nota in self._notas_marcadas:
            self._notas_marcadas.remove(id_nota); text="○"; color=c['border_strong']
        else:
            self._notas_marcadas.add(id_nota); text="●"; color=c['brand']
        if item: item.setText(text); item.setForeground(QColor(color))
        self._atualizar_selecao()

    def _atualizar_selecao(self):
        n=len(self._notas_marcadas); self._lbl_sel.setText(f"{n} selecionada{'s' if n != 1 else ''}"); self._kpi_sel.set_value(str(n))

    def _importar_manifesto(self):
        path,_=QFileDialog.getOpenFileName(self,"Selecionar Manifesto TXT","","Arquivos TXT (*.txt);;Todos (*.*)")
        if not path:return
        self._btn_importar.setEnabled(False); self._btn_importar.setText("Importando…")
        self._worker=_ImportWorker(path); self._worker.concluido.connect(self._on_import_ok); self._worker.erro.connect(self._on_import_err)
        self._import_thread=threading.Thread(target=self._worker.run,daemon=True); self._import_thread.start()

    def _finish_import(self):
        self._btn_importar.setEnabled(True); self._btn_importar.setText("+ Importar"); self._worker=None; self._import_thread=None

    def _on_import_ok(self, result):
        self._finish_import()
        QMessageBox.information(self,"Importação Concluída",f"Arquivo: {result.get('arquivo','—')}\n\nNotas encontradas: {result.get('encontradas',0)}\nNotas salvas: {result.get('salvas',0)}\nNotas duplicadas: {result.get('duplicadas',0)}")
        self._carregar_manifestos()

    def _on_import_err(self, msg):
        self._finish_import(); QMessageBox.critical(self,"Erro ao Importar",msg)

    def _apagar_manifesto(self):
        mid=self._selected_manifesto_id
        if mid is None: QMessageBox.warning(self,"Atenção","Selecione um manifesto para apagar."); return
        card=self._manifesto_cards.get(mid); name=card._data.get("nome_arquivo",f"Manifesto {mid}") if card else f"Manifesto {mid}"
        if QMessageBox.question(self,"Apagar Manifesto",f"Apagar '{name}'?\n\nTodas as notas também serão apagadas.",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:return
        try: notas_service.apagar_manifesto(mid)
        except Exception as exc: QMessageBox.critical(self,"Erro ao Apagar",str(exc)); return
        self._notas_marcadas.clear(); self._atualizar_selecao(); self._carregar_manifestos()

    def _criar_viagem(self):
        if not self._notas_marcadas: QMessageBox.warning(self,"Atenção","Selecione pelo menos uma nota."); return
        cam_txt=self._combo_caminhoes.currentText(); cam_id=self._caminhoes_map.get(cam_txt)
        if not cam_id: QMessageBox.warning(self,"Atenção","Selecione um caminhão válido."); return
        driver=self._entry_motorista.text().strip()
        if not driver: QMessageBox.warning(self,"Atenção","Informe o motorista da viagem."); return
        ids=list(self._notas_marcadas)
        try:
            valid,msg,_=viagem_service.validar_capacidade(cam_id,ids)
            if not valid and QMessageBox.question(self,"Aviso de Capacidade",f"{msg}\n\nDeseja continuar mesmo assim?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:return
            viagem_id=viagem_service.criar_viagem_com_notas(cam_id,ids,driver)
        except Exception as exc: QMessageBox.critical(self,"Erro ao Criar Viagem",str(exc)); self._reload_notas(); return
        QMessageBox.information(self,"Viagem Criada",f"Viagem #{viagem_id} criada com sucesso!\n{len(ids)} nota(s) adicionada(s).")
        self._entry_motorista.clear(); self._notas_marcadas.clear(); self._atualizar_selecao(); self._reload_notas()

    def _apagar_viagem(self):
        viagem_id,ok=QInputDialog.getInt(self,"Apagar Viagem","Número da viagem:",1,1,999999)
        if not ok:return
        if QMessageBox.question(self,"Confirmar Exclusão",f"Apagar viagem #{viagem_id}?\n\nAs notas voltarão a ficar disponíveis.",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:return
        try:
            total=notas_service.apagar_viagem(viagem_id)
            QMessageBox.information(self,"Viagem Apagada",f"Viagem #{viagem_id} apagada!\n{total} nota(s) liberada(s).")
            self._notas_marcadas.clear(); self._atualizar_selecao(); self._reload_notas()
        except Exception as exc: QMessageBox.critical(self,"Erro ao Apagar Viagem",str(exc))

    def _abrir_novo_veiculo(self):
        dlg=_DialogVeiculo(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:self._carregar_caminhoes()
