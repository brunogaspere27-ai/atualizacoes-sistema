"""
Tela Criar Viagem - CW Transportadora - PySide6
Reescrita completa: design premium, bugs corrigidos, tema consistente.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView, QComboBox, QDialog,
    QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor

from services.viagem_service import viagem_service
from services.rascunho_viagem_service import (
    atualizar_marcacao_nota,
    salvar_rascunho_viagem,
    carregar_rascunho_viagem,
    limpar_rascunho_viagem,
    adicionar_historico_viagem,
    listar_historico_viagem,
)
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWTable, CWBadge, BadgeVariant
from utils.helpers import formatar_moeda, formatar_peso, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Paleta fixa (independente do tema para garantir consistência visual) ──────
_BG       = "#080d1a"
_SURFACE  = "#0e1525"
_CARD     = "#131c2e"
_BORDER   = "#1d2d47"
_BORDER2  = "#1a2540"
_TXT1     = "#e2e8f0"
_TXT2     = "#94a3b8"
_TXT3     = "#64748b"
_BLUE     = "#3b82f6"
_BLUE_DIM = "#1d4ed8"
_GREEN    = "#10b981"
_GREEN_DK = "#15803d"
_RED      = "#ef4444"
_AMBER    = "#f59e0b"
_VIOLET   = "#8b5cf6"
_MONO     = "Consolas, 'Courier New', monospace"


def _label(text: str, color: str = _TXT1, bold: bool = False,
           mono: bool = False, size: int = 13) -> QLabel:
    lbl = QLabel(text)
    font = QFont("Consolas" if mono else "Segoe UI", size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


def _input_style(focus_color: str = _BLUE) -> str:
    return f"""
        QLineEdit {{
            background-color: {_CARD};
            border: 1px solid {_BORDER};
            border-radius: 3px;
            padding: 0 10px;
            font-size: 13px;
            color: {_TXT1};
            min-height: 36px;
        }}
        QLineEdit:focus {{ border: 1px solid {focus_color}; }}
        QLineEdit::placeholder {{ color: {_TXT3}; }}
    """


def _btn(text: str, bg: str, fg: str, hover: str, border: str = "") -> QPushButton:
    b = border or bg
    btn = QPushButton(text)
    btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {b};
            border-radius: 3px;
            padding: 7px 16px;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
    """)
    return btn


def _section_header(title: str) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = _label(title.upper(), _BLUE, bold=True, mono=True, size=10)
    lbl.setStyleSheet(f"color: {_BLUE}; background: transparent; letter-spacing: 2px;")
    row.addWidget(lbl)
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {_BORDER}; background: {_BORDER}; max-height: 1px;")
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    row.addWidget(line)
    return row


class TelaCriarViagem(QWidget):
    """Tela de criação de viagens — design premium, PySide6."""

    _notas_carregadas = Signal(list)
    _clientes_encontrados = Signal(list)

    def __init__(self, parent=None, cliente_pre_selecionado: tuple = None):
        super().__init__(parent)

        self.cliente_selecionado = None
        self.cliente_selecionado_id = None
        self.notas_selecionadas: set = set()
        self.caminhoes_map: dict = {}
        self.caminhoes_catalogo: list = []
        self.notas_ids: dict = {}
        self.notas_catalogo: dict = {}
        self.notas_selecionadas_row_ids: dict = {}
        self._resumo_labels: dict[str, QLabel] = {}
        self._cliente_pre_selecionado = cliente_pre_selecionado

        self._notas_carregadas.connect(self._preencher_tabela_notas)
        self._clientes_encontrados.connect(self._mostrar_dialogo_clientes)
        self._setup_ui()
        self._carregar_caminhoes()

        if self._cliente_pre_selecionado:
            QTimer.singleShot(100, self._selecionar_cliente_com_delay)
        else:
            QTimer.singleShot(200, self._carregar_rascunho)

    # ──────────────────────────────────────────────────── UI ──────────────────

    def _setup_ui(self):
        self.setStyleSheet(f"""
            background-color: {_BG};
            QMessageBox {{
                background-color: {_SURFACE};
                color: {_TXT1};
            }}
            QMessageBox QLabel {{
                color: {_TXT1};
                background: transparent;
            }}
            QMessageBox QPushButton {{
                background-color: {_BLUE};
                color: #fff;
                border: none;
                border-radius: 3px;
                padding: 6px 16px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {_BLUE_DIM};
            }}
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {_BG}; border: none; }}"
                             "QScrollBar:vertical { width: 4px; background: transparent; }"
                             f"QScrollBar::handle:vertical {{ background: {_BORDER}; border-radius: 2px; }}")
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {_BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 24, 28, 28)
        cl.setSpacing(14)
        scroll.setWidget(content)

        cl.addWidget(self._build_page_header())
        cl.addWidget(self._build_busca_cliente())

        notes_row = QHBoxLayout()
        notes_row.setSpacing(14)
        notes_row.addWidget(self._build_tabela_notas(), stretch=3)
        notes_row.addWidget(self._build_panel_selecionadas(), stretch=1)
        cl.addLayout(notes_row)

        cl.addWidget(self._build_kpi_bar())
        cl.addWidget(self._build_criacao_viagem())

        self.label_validacao = _label(
            "Selecione notas e um caminhão para validar.", _TXT3, size=12)
        self.label_validacao.setWordWrap(True)
        cl.addWidget(self.label_validacao)

        self.label_historico = _label("", _TXT3, size=11)
        self.label_historico.setWordWrap(True)
        cl.addWidget(self.label_historico)

        cl.addStretch()

    def _build_page_header(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        row = QHBoxLayout(frame)
        row.setContentsMargins(0, 0, 0, 4)

        left = QVBoxLayout()
        title = _label("Criar Nova Viagem", _TXT1, bold=True, size=20)
        title.setStyleSheet(
            f"color: {_TXT1}; background: transparent; letter-spacing: -0.5px;")
        sub = _label("Associe notas fiscais, defina veículo e motorista.", _TXT3, size=12)
        left.addWidget(title)
        left.addWidget(sub)
        row.addLayout(left)
        row.addStretch()

        now = datetime.now().strftime("%d/%m/%Y · %H:%M")
        ts = _label(now, _TXT3, mono=True, size=11)
        row.addWidget(ts)
        return frame

    def _build_busca_cliente(self) -> QFrame:
        frame = self._card_frame()
        cl = QVBoxLayout(frame)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(10)

        cl.addLayout(_section_header("Cliente"))

        row = QHBoxLayout()
        row.setSpacing(10)

        self.entrada_busca = QLineEdit()
        self.entrada_busca.setPlaceholderText("Nome do cliente ou CNPJ...")
        self.entrada_busca.setStyleSheet(_input_style())
        self.entrada_busca.returnPressed.connect(self._buscar_cliente)
        row.addWidget(self.entrada_busca, stretch=1)

        btn = _btn("Buscar", _BLUE, "#fff", _BLUE_DIM)
        btn.clicked.connect(self._buscar_cliente)
        row.addWidget(btn)

        self.btn_limpar_cliente = _btn("✕ Limpar", "transparent", _TXT3, _CARD, _BORDER)
        self.btn_limpar_cliente.clicked.connect(self._limpar_cliente)
        self.btn_limpar_cliente.setVisible(False)
        row.addWidget(self.btn_limpar_cliente)

        cl.addLayout(row)

        self.label_cliente = _label("Nenhum cliente selecionado.", _TXT3, size=12)
        cl.addWidget(self.label_cliente)
        return frame

    def _build_tabela_notas(self) -> QFrame:
        frame = self._card_frame()
        cl = QVBoxLayout(frame)
        cl.setContentsMargins(18, 14, 18, 14)
        cl.setSpacing(10)

        # Header row
        hrow = QHBoxLayout()
        hrow.addLayout(_section_header("Notas Fiscais"))

        self.lbl_notas_count = _label("0 disponíveis", _TXT3, mono=True, size=10)
        hrow.addWidget(self.lbl_notas_count)
        hrow.addStretch()

        self.entrada_filtro = QLineEdit()
        self.entrada_filtro.setPlaceholderText("Filtrar...")
        self.entrada_filtro.setFixedWidth(140)
        self.entrada_filtro.setStyleSheet(_input_style())
        self.entrada_filtro.textChanged.connect(self._filtrar_notas)
        hrow.addWidget(self.entrada_filtro)

        self.btn_todas = _btn("Selecionar todas", _CARD, _TXT2, _BORDER2, _BORDER)
        self.btn_todas.clicked.connect(self._selecionar_todas)
        hrow.addWidget(self.btn_todas)

        cl.addLayout(hrow)

        # Table
        colunas = ["", "Nota / CT-e", "Cidade", "Status", "Peso", "Vol.", "Frete"]
        self.tabela_notas = QTableWidget(0, len(colunas))
        self.tabela_notas.setHorizontalHeaderLabels(colunas)
        self.tabela_notas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_notas.verticalHeader().setVisible(False)
        self.tabela_notas.setShowGrid(False)
        self.tabela_notas.setAlternatingRowColors(True)
        self.tabela_notas.setMinimumHeight(320)
        self.tabela_notas.verticalHeader().setDefaultSectionSize(36)
        self.tabela_notas.setStyleSheet(self._table_style())

        h = self.tabela_notas.horizontalHeader()
        h.resizeSection(0, 32)
        h.resizeSection(1, 160)
        h.resizeSection(2, 160)
        h.resizeSection(3, 90)
        h.resizeSection(4, 100)
        h.resizeSection(5, 50)
        h.setStretchLastSection(True)

        self.tabela_notas.cellClicked.connect(self._clicar_na_nota)
        cl.addWidget(self.tabela_notas)
        return frame

    def _build_panel_selecionadas(self) -> QFrame:
        frame = self._card_frame()
        cl = QVBoxLayout(frame)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(10)

        hrow = QHBoxLayout()
        hrow.addLayout(_section_header("Selecionadas"))
        self.btn_limpar_sel = _btn("Limpar", "transparent", _TXT3, _CARD, _BORDER)
        self.btn_limpar_sel.setFixedHeight(26)
        self.btn_limpar_sel.clicked.connect(self._limpar_selecao)
        hrow.addWidget(self.btn_limpar_sel)
        cl.addLayout(hrow)

        colunas = ["Nota", "Peso"]
        self.tabela_selecionadas = QTableWidget(0, 2)
        self.tabela_selecionadas.setHorizontalHeaderLabels(colunas)
        self.tabela_selecionadas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_selecionadas.verticalHeader().setVisible(False)
        self.tabela_selecionadas.setShowGrid(False)
        self.tabela_selecionadas.setAlternatingRowColors(True)
        self.tabela_selecionadas.setMinimumHeight(240)
        self.tabela_selecionadas.setStyleSheet(self._table_style())
        self.tabela_selecionadas.horizontalHeader().setStretchLastSection(True)
        self.tabela_selecionadas.horizontalHeader().resizeSection(0, 110)

        cl.addWidget(self.tabela_selecionadas)

        btn_remover = _btn("✕ Remover", "transparent", _RED, "#1c0a0a", _RED)
        btn_remover.clicked.connect(self._remover_nota_selecionada)
        cl.addWidget(btn_remover)
        return frame

    def _build_kpi_bar(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"background: transparent;")
        row = QHBoxLayout(frame)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        for titulo, chave, cor in [
            ("Qtd Notas", "qtd", "#93c5fd"),
            ("Volumes",   "vol", "#c4b5fd"),
            ("Peso Total", "peso", _TXT2),
            ("Frete Total", "frete", "#4ade80"),
        ]:
            kpi = self._card_frame()
            kl = QVBoxLayout(kpi)
            kl.setContentsMargins(14, 10, 14, 10)
            kl.setSpacing(2)

            lbl_t = _label(titulo.upper(), _TXT3, mono=True, size=9)
            lbl_t.setStyleSheet(
                f"color: {_TXT3}; background: transparent; letter-spacing: 2px;")
            v = _label("0", cor, bold=True, mono=True, size=16)
            kl.addWidget(lbl_t)
            kl.addWidget(v)
            self._resumo_labels[chave] = v
            row.addWidget(kpi)

        self.lbl_cap_aviso = _label("", _RED, size=11)
        self.lbl_cap_aviso.setWordWrap(True)
        self.lbl_cap_aviso.setVisible(False)
        row.addWidget(self.lbl_cap_aviso, stretch=1)
        return frame

    def _build_criacao_viagem(self) -> QFrame:
        frame = self._card_frame()
        row = QHBoxLayout(frame)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(12)

        row.addWidget(_label("Caminhão", _TXT3, bold=True, size=11))

        self.combo_caminhoes = QComboBox()
        self.combo_caminhoes.setMinimumWidth(260)
        self.combo_caminhoes.setFixedHeight(36)
        self.combo_caminhoes.setStyleSheet(f"""
            QComboBox {{
                background: {_CARD}; color: {_TXT1};
                border: 1px solid {_BORDER}; border-radius: 3px;
                padding: 0 10px; font-size: 12px;
            }}
            QComboBox:focus {{ border-color: {_BLUE}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {_CARD}; color: {_TXT1};
                selection-background-color: {_BORDER2};
                border: 1px solid {_BORDER};
            }}
        """)
        self.combo_caminhoes.currentTextChanged.connect(self._atualizar_validacao)
        row.addWidget(self.combo_caminhoes)

        row.addWidget(_label("Motorista", _TXT3, bold=True, size=11))

        self.entrada_motorista = QLineEdit()
        self.entrada_motorista.setPlaceholderText("Nome do motorista...")
        self.entrada_motorista.setFixedWidth(200)
        self.entrada_motorista.setStyleSheet(_input_style())
        row.addWidget(self.entrada_motorista)

        row.addStretch()

        btn_limpar = _btn("Limpar", "transparent", _TXT3, _CARD, _BORDER)
        btn_limpar.clicked.connect(self._limpar_formulario)
        row.addWidget(btn_limpar)

        btn_rasc = _btn("Rascunho", "#1a1333", _VIOLET, "#1e1a3a", _VIOLET)
        btn_rasc.clicked.connect(self._salvar_rascunho_atual)
        row.addWidget(btn_rasc)

        btn_carregar = _btn("Carregar", _CARD, _TXT2, _BORDER2, _BORDER)
        btn_carregar.clicked.connect(self._carregar_rascunho)
        row.addWidget(btn_carregar)

        btn_criar = _btn("  ＋  CRIAR VIAGEM", _GREEN_DK, "#f0fdf4", "#166534")
        btn_criar.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn_criar.clicked.connect(self._criar_viagem)
        row.addWidget(btn_criar)

        return frame

    # ──────────────────────────────────────────── Helpers de estilo ───────────

    @staticmethod
    def _card_frame() -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"QFrame {{ background: {_SURFACE}; border: 1px solid {_BORDER}; border-radius: 3px; }}")
        return f

    @staticmethod
    def _table_style() -> str:
        return """
            QTableWidget {
                background: #0e1525;
                alternate-background-color: #0b111f;
                color: #e2e8f0;
                border: none;
                gridline-color: transparent;
                font-size: 12px;
            }
            QTableWidget::item {
                color: #e2e8f0;
                background: transparent;
                padding: 8px 10px;
                border: none;
            }
            QHeaderView::section {
                background: #0e1525;
                color: #e2e8f0;
                border: none;
                border-bottom: 1px solid #1d2d47;
                padding: 8px 10px;
                font-size: 10px;
                font-family: Consolas;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
            QTableWidget::item:selected {
                background: #0d1e35;
                color: #e2e8f0;
            }
        """

    # ────────────────────────────────────────────────── Lógica ───────────────

    def _selecionar_cliente_com_delay(self):
        if self._cliente_pre_selecionado:
            cid, nome = self._cliente_pre_selecionado
            self._selecionar_cliente(cid, nome)

    def _carregar_caminhoes(self):
        self.caminhoes_map.clear()
        self.caminhoes_catalogo.clear()
        self.combo_caminhoes.clear()
        try:
            caminhoes = viagem_service.listar_caminhoes_disponiveis()
        except Exception as e:
            logger.error(f"Erro ao carregar caminhões: {e}")
            caminhoes = []
        for row in caminhoes:
            cid, placa, modelo, motorista, capacidade = row
            texto = f"{placa}  —  {modelo}  ({capacidade:,.0f} kg)"
            self.caminhoes_map[texto] = cid
            self.caminhoes_catalogo.append(
                {"id": cid, "texto": texto, "capacidade": capacidade or 0})
            self.combo_caminhoes.addItem(texto)
        if not caminhoes:
            self.combo_caminhoes.addItem("Nenhum caminhão disponível")

    def _buscar_cliente(self):
        termo = self.entrada_busca.text().strip()
        if len(termo) < 2:
            QMessageBox.warning(self, "Atenção", "Digite ao menos 2 caracteres.")
            return

        print(f"[CriarViagem] Buscando cliente com termo: {termo}")

        def tarefa():
            try:
                print(f"[CriarViagem] Chamando viagem_service.buscar_clientes...")
                clientes = viagem_service.buscar_clientes(termo)
                print(f"[CriarViagem] Clientes encontrados: {len(clientes) if clientes else 0}")
                self._clientes_encontrados.emit(clientes)
            except Exception as e:
                print(f"[CriarViagem] Erro ao buscar clientes: {e}")
                import traceback
                traceback.print_exc()
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(e)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _mostrar_dialogo_clientes(self, clientes: list):
        print(f"[CriarViagem] _mostrar_dialogo_clientes chamado com {len(clientes)} clientes")
        
        if not clientes:
            QMessageBox.information(self, "Busca", "Nenhum cliente encontrado.")
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Selecionar Cliente")
        dlg.resize(520, 380)
        dlg.setStyleSheet(f"background: {_SURFACE}; color: {_TXT1};")
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)

        lbl = _label("Selecione o cliente", _TXT1, bold=True, size=14)
        lay.addWidget(lbl)

        tabela = QTableWidget(len(clientes), 3)
        tabela.setHorizontalHeaderLabels(["Nome", "CNPJ", "Cidade"])
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.verticalHeader().setVisible(False)
        tabela.setShowGrid(False)
        tabela.setAlternatingRowColors(True)
        tabela.setStyleSheet(self._table_style())

        for i, c in enumerate(clientes):
            cid, nome, cnpj, cidade, uf = c
            print(f"[CriarViagem] Cliente {i}: {nome}")
            tabela.setItem(i, 0, QTableWidgetItem(nome or "-"))
            tabela.setItem(i, 1, QTableWidgetItem(cnpj or "-"))
            tabela.setItem(i, 2, QTableWidgetItem(
                f"{cidade or '-'} / {uf or '-'}"))

        tabela.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(tabela)

        def on_ok():
            row = tabela.currentRow()
            print(f"[CriarViagem] Cliente selecionado na linha {row}")
            if row < 0:
                QMessageBox.warning(dlg, "Atenção", "Selecione um cliente.")
                return
            cid, nome = clientes[row][0], clientes[row][1]
            print(f"[CriarViagem] Selecionando cliente: {nome} (ID: {cid})")
            self._selecionar_cliente(cid, nome)
            # Não fecha o diálogo - permite selecionar mais clientes
            # dlg.accept()

        btn_selecionar = _btn("Selecionar", _BLUE, "#fff", _BLUE_DIM)
        btn_selecionar.clicked.connect(on_ok)
        lay.addWidget(btn_selecionar)
        
        btn_fechar = _btn("Fechar", "#1a2540", _TXT2, "#1d2d47", "#1d2d47")
        btn_fechar.clicked.connect(dlg.accept)
        lay.addWidget(btn_fechar)
        
        tabela.cellDoubleClicked.connect(lambda r, c: on_ok())
        print(f"[CriarViagem] Executando dialogo...")
        dlg.exec()
        print(f"[CriarViagem] Dialogo fechado")

    def _selecionar_cliente(self, cliente_id, nome: str):
        self.cliente_selecionado_id = cliente_id
        self.cliente_selecionado = nome
        # Not limpar notas selecionadas - permite acumular notas de diferentes buscas
        # self.notas_selecionadas.clear()
        self.notas_ids.clear()
        self.notas_catalogo.clear()

        self.label_cliente.setText(f"✓  {nome}")
        self.label_cliente.setStyleSheet(
            f"color: {_GREEN}; background: transparent; font-size: 12px;")
        self.btn_limpar_cliente.setVisible(True)
        self._carregar_notas_cliente()

    def _limpar_cliente(self):
        self.cliente_selecionado = None
        self.cliente_selecionado_id = None
        self.entrada_busca.clear()
        self.label_cliente.setText("Nenhum cliente selecionado.")
        self.label_cliente.setStyleSheet(f"color: {_TXT3}; background: transparent;")
        self.btn_limpar_cliente.setVisible(False)
        self.tabela_notas.setRowCount(0)
        self.notas_selecionadas.clear()
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()

    def _carregar_notas_cliente(self):
        if not self.cliente_selecionado_id:
            return
        cid = self.cliente_selecionado_id
        print(f"[CriarViagem] Carregando notas para cliente ID: {cid}")

        def tarefa():
            try:
                print(f"[CriarViagem] Chamando viagem_service.listar_notas_cliente...")
                notas = viagem_service.listar_notas_cliente(
                    cid, apenas_disponiveis=True, excluir_vinculadas=True)
                print(f"[CriarViagem] Notas encontradas: {len(notas) if notas else 0}")
                self._notas_carregadas.emit(notas)
            except Exception as e:
                print(f"[CriarViagem] Erro ao carregar notas: {e}")
                import traceback
                traceback.print_exc()
                logger.error(f"Erro ao carregar notas: {e}")
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(e)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _preencher_tabela_notas(self, notas: list):
        print(f"[CriarViagem] _preencher_tabela_notas chamado com {len(notas)} notas")
        self.tabela_notas.setRowCount(0)
        self.notas_ids.clear()
        self.notas_catalogo.clear()

        STATUS_COLORS = {
            "Disponível": _GREEN,
            "Coletado":   "#6ee7b7",
            "Triagem":    _VIOLET,
            "Pendente":   _AMBER,
        }

        for nota in notas:
            nota_id, numero_cte, chave_nfe, _cli, cidade, peso, frete, data, status = nota
            numero = numero_cte or (chave_nfe[:20] if chave_nfe else "-")
            peso = peso or 0
            frete = frete or 0
            data_fmt = data[:10] if data else "-"
            marcador = "☑" if nota_id in self.notas_selecionadas else "☐"
            
            print(f"[CriarViagem] Nota: {numero}, cidade: {cidade}, peso: {peso}, frete: {frete}, status: {status}")

            self.notas_catalogo[nota_id] = {
                "numero": numero, "cidade": cidade or "-",
                "peso": peso, "frete": frete, "data": data_fmt, "status": status,
            }

            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            self.notas_ids[row] = nota_id

            valores = [
                (marcador, Qt.AlignmentFlag.AlignCenter),
                (numero, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                (cidade or "-", Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                (status or "-", Qt.AlignmentFlag.AlignCenter),
                (f"{peso:,.0f} kg", Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
                ("-", Qt.AlignmentFlag.AlignCenter),
                (f"R$ {frete:,.2f}", Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
            ]

            for col, (txt, align) in enumerate(valores):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(align)
                self.tabela_notas.setItem(row, col, item)

        count = self.tabela_notas.rowCount()
        print(f"[CriarViagem] Tabela preenchida com {count} linhas")
        self.lbl_notas_count.setText(f"{count} disponíve{'is' if count != 1 else 'l'}")
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _filtrar_notas(self, texto: str):
        termo = texto.lower()
        for row in range(self.tabela_notas.rowCount()):
            visible = any(
                termo in (self.tabela_notas.item(row, col).text().lower() if self.tabela_notas.item(row, col) else "")
                for col in range(1, 4)
            )
            self.tabela_notas.setRowHidden(row, not visible)

    def _clicar_na_nota(self, row: int, _col: int):
        nota_id = self.notas_ids.get(row)
        if nota_id is None:
            return
        selecionando = nota_id not in self.notas_selecionadas
        atualizar_marcacao_nota(self.notas_selecionadas, nota_id, selecionando)
        item = self.tabela_notas.item(row, 0)
        if item:
            item.setText("☑" if selecionando else "☐")
            item.setForeground(QColor(_BLUE if selecionando else _TXT3))
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _selecionar_todas(self):
        for row in range(self.tabela_notas.rowCount()):
            if self.tabela_notas.isRowHidden(row):
                continue
            nota_id = self.notas_ids.get(row)
            if nota_id and nota_id not in self.notas_selecionadas:
                atualizar_marcacao_nota(self.notas_selecionadas, nota_id, True)
                item = self.tabela_notas.item(row, 0)
                if item:
                    item.setText("☑")
                    item.setForeground(QColor(_BLUE))
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _limpar_selecao(self):
        self.notas_selecionadas.clear()
        for row in range(self.tabela_notas.rowCount()):
            item = self.tabela_notas.item(row, 0)
            if item:
                item.setText("☐")
                item.setForeground(QColor(_TXT3))
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _atualizar_lista_selecionadas(self):
        self.tabela_selecionadas.setRowCount(0)
        self.notas_selecionadas_row_ids.clear()
        for nota_id in sorted(self.notas_selecionadas):
            d = self.notas_catalogo.get(nota_id, {})
            row = self.tabela_selecionadas.rowCount()
            self.tabela_selecionadas.insertRow(row)

            it_num = QTableWidgetItem(d.get("numero", "-"))
            it_num.setForeground(QColor("#93c5fd"))
            self.tabela_selecionadas.setItem(row, 0, it_num)

            peso = d.get("peso", 0) or 0
            it_p = QTableWidgetItem(f"{peso:,.0f} kg")
            it_p.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_p.setForeground(QColor(_TXT2))
            self.tabela_selecionadas.setItem(row, 1, it_p)

            self.notas_selecionadas_row_ids[row] = nota_id

    def _remover_nota_selecionada(self):
        row = self.tabela_selecionadas.currentRow()
        nota_id = self.notas_selecionadas_row_ids.get(row)
        if nota_id is None:
            return
        self.notas_selecionadas.discard(nota_id)
        for r in range(self.tabela_notas.rowCount()):
            if self.notas_ids.get(r) == nota_id:
                item = self.tabela_notas.item(r, 0)
                if item:
                    item.setText("☐")
                    item.setForeground(QColor(_TXT3))
                break
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _atualizar_resumo(self):
        try:
            resumo = viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas))
        except Exception:
            resumo = {"quantidade": 0, "peso_total": 0, "frete_total": 0, "volumes": 0}

        self._resumo_labels["qtd"].setText(str(resumo.get("quantidade", 0)))
        self._resumo_labels["vol"].setText(str(resumo.get("volumes", 0)))

        peso = resumo.get("peso_total", 0) or 0
        caminhao_texto = self.combo_caminhoes.currentText()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        cap = next((c["capacidade"] for c in self.caminhoes_catalogo
                    if c["id"] == caminhao_id), 0)

        peso_color = _RED if (cap and peso > cap) else _TXT2
        self._resumo_labels["peso"].setText(f"{peso:,.0f} kg")
        self._resumo_labels["peso"].setStyleSheet(
            f"color: {peso_color}; background: transparent;")

        frete = resumo.get("frete_total", 0) or 0
        self._resumo_labels["frete"].setText(f"R$ {frete:,.2f}")

    def _atualizar_validacao(self):
        if not self.notas_selecionadas:
            self.label_validacao.setText("Selecione notas e um caminhão para validar.")
            self.label_validacao.setStyleSheet(f"color: {_TXT3}; background: transparent;")
            self.lbl_cap_aviso.setVisible(False)
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        if not caminhao_texto or "Nenhum" in caminhao_texto:
            self.label_validacao.setText("Selecione um caminhão para validar a capacidade.")
            self.label_validacao.setStyleSheet(f"color: {_AMBER}; background: transparent;")
            self.lbl_cap_aviso.setVisible(False)
            return

        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        if not caminhao_id:
            return

        try:
            valido, mensagem, _ = viagem_service.validar_capacidade(
                caminhao_id, list(self.notas_selecionadas))
        except Exception as e:
            logger.error(f"Erro ao validar capacidade: {e}")
            return

        if valido:
            self.label_validacao.setText(f"✓  Capacidade OK — {caminhao_texto}")
            self.label_validacao.setStyleSheet(f"color: {_GREEN}; background: transparent;")
            self.lbl_cap_aviso.setVisible(False)
        else:
            sugestao = self._sugerir_caminhao_ideal()
            self.label_validacao.setText(mensagem or "Capacidade excedida.")
            self.label_validacao.setStyleSheet(f"color: {_RED}; background: transparent;")
            if sugestao:
                self.lbl_cap_aviso.setText(f"Sugestão: {sugestao}")
                self.lbl_cap_aviso.setVisible(True)
            else:
                self.lbl_cap_aviso.setVisible(False)

        self._atualizar_resumo()

    def _sugerir_caminhao_ideal(self) -> str:
        if not self.notas_selecionadas:
            return ""
        try:
            resumo = viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas))
            peso = resumo.get("peso_total", 0) or 0
        except Exception:
            return ""
        for item in self.caminhoes_catalogo:
            if item.get("capacidade", 0) >= peso:
                return item.get("texto", "")
        return ""

    def _criar_viagem(self):
        if not self.cliente_selecionado_id:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente primeiro.")
            return
        if not self.notas_selecionadas:
            QMessageBox.warning(self, "Atenção", "Selecione pelo menos uma nota.")
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        if not caminhao_id or "Nenhum" in caminhao_texto:
            QMessageBox.warning(self, "Atenção", "Selecione um caminhão válido.")
            return

        motorista = self.entrada_motorista.text().strip()
        if not motorista:
            QMessageBox.warning(self, "Atenção", "Informe o motorista da viagem.")
            return

        try:
            valido, mensagem, _ = viagem_service.validar_capacidade(
                caminhao_id, list(self.notas_selecionadas))
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        if not valido:
            resp = QMessageBox.question(
                self, "Aviso de Capacidade",
                f"{mensagem}\n\nDeseja continuar mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if resp != QMessageBox.StandardButton.Yes:
                return

        notas_ids_snap = list(self.notas_selecionadas)

        def tarefa():
            try:
                viagem_id = viagem_service.criar_viagem_com_notas(
                    caminhao_id, notas_ids_snap, motorista)
                resumo = viagem_service.calcular_resumo_selecao(notas_ids_snap)
                adicionar_historico_viagem({
                    "viagem_id": viagem_id,
                    "motorista": motorista,
                    "caminhao": caminhao_texto,
                    "quantidade": len(notas_ids_snap),
                    "peso_total": round(resumo.get("peso_total", 0), 2),
                    "frete_total": round(resumo.get("frete_total", 0), 2),
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }, None)
                QTimer.singleShot(0, lambda: QMessageBox.information(
                    self, "Sucesso",
                    f"Viagem #{viagem_id} criada!\n{len(notas_ids_snap)} nota(s) vinculadas."))
                QTimer.singleShot(0, self._limpar_formulario)
                QTimer.singleShot(0, self._atualizar_historico)
                QTimer.singleShot(0, self._carregar_notas_cliente)
            except Exception as e:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(e)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _limpar_formulario(self):
        self._limpar_selecao()
        self.entrada_motorista.clear()

    def _salvar_rascunho_atual(self):
        dados = {
            "cliente_id":   self.cliente_selecionado_id,
            "cliente_nome": self.cliente_selecionado,
            "notas":        sorted(self.notas_selecionadas),
            "motorista":    self.entrada_motorista.text().strip(),
            "caminhao":     self.combo_caminhoes.currentText(),
            "timestamp":    datetime.now().strftime("%d/%m/%Y %H:%M"),
            "quantidade":   len(self.notas_selecionadas),
        }
        salvar_rascunho_viagem(dados, None)
        QMessageBox.information(self, "Rascunho", "Estado atual salvo com sucesso.")

    def _carregar_rascunho(self):
        dados = carregar_rascunho_viagem(None)
        if not dados:
            return
        if dados.get("cliente_id") and dados.get("cliente_nome"):
            self._selecionar_cliente(dados["cliente_id"], dados["cliente_nome"])
        self.notas_selecionadas = set(dados.get("notas", []))
        self.entrada_motorista.setText(dados.get("motorista", ""))
        caminhao = dados.get("caminhao", "")
        if caminhao:
            idx = self.combo_caminhoes.findText(caminhao)
            if idx >= 0:
                self.combo_caminhoes.setCurrentIndex(idx)
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()
        self._atualizar_historico()

    def _limpar_rascunho(self):
        limpar_rascunho_viagem(None)
        QMessageBox.information(self, "Rascunho", "Rascunho removido.")

    def _atualizar_historico(self):
        historico = listar_historico_viagem(None)
        if not historico:
            self.label_historico.setText("")
            return
        linhas = []
        for item in historico[:3]:
            linhas.append(
                f"• Viagem #{item.get('viagem_id')} · "
                f"{item.get('motorista', '-')} · "
                f"{item.get('caminhao', '-')} · "
                f"{item.get('quantidade', 0)} nota(s) · "
                f"{item.get('timestamp', '')}"
            )
        self.label_historico.setText("Últimas viagens:\n" + "\n".join(linhas))
