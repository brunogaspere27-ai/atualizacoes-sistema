"""
Tela de Notas Importadas - CW Transportadora v8
Migrado de Tkinter/CustomTkinter para PySide6.

Layout dividido em dois painéis:
  • Esquerda  – lista de manifestos + botões Importar / Apagar
  • Direita   – tabela de notas do manifesto selecionado + resumo
A importação roda em thread de fundo e retorna via Signal.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QFileDialog, QMessageBox, QAbstractItemView,
    QSizePolicy, QScrollArea, QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QPainter, QColor, QFont

from services.notas_service import notas_service
from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ButtonSize, ModernCard
from utils.helpers import formatar_moeda, formatar_peso
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Componente de Card de Manifesto (CRM style)
# ---------------------------------------------------------------------------
class ManifestoCard(QFrame):
    """Card moderno estilo CRM para exibir informações do manifesto."""

    clicked = Signal(int)  # manifesto_id

    def __init__(self, manifesto_data: dict, parent: QWidget = None):
        super().__init__(parent)
        self._manifesto_data = manifesto_data
        self._selected = False
        self._setup_ui()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Base style moderno
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['bg_surface']};
            border: 1px solid {colors['border_subtle']};
            border-radius: {tokens.RADIUS_XL}px;
        }}
        QFrame:hover {{
            border-color: {colors['border_default']};
            background-color: {colors['card_hover']};
        }}
        QFrame[selected="true"] {{
            border-color: {colors['aurora']};
            background-color: {colors['aurora_soft']};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_LG, tokens.SPACING_LG, tokens.SPACING_LG, tokens.SPACING_LG)
        layout.setSpacing(tokens.SPACING_SM)
        self.setLayout(layout)

        # Header: nome + status
        header = QHBoxLayout()
        header.setSpacing(tokens.SPACING_SM)

        # Nome do manifesto
        nome = self._manifesto_data.get('nome_arquivo', 'Manifesto')
        nome_label = QLabel(nome)
        nome_label.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD, bold=True))
        nome_label.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        nome_label.setWordWrap(True)
        header.addWidget(nome_label, 1)

        # Status badge elegante
        status = self._manifesto_data.get('status', 'Importado')
        status_colors = {
            'Importado': (colors['success'], colors['success_soft']),
            'Em uso': (colors['warning'], colors['warning_soft']),
            'Concluído': (colors['info'], colors['info_soft']),
        }
        status_bg, status_fg = status_colors.get(status, (colors['text_secondary'], colors['bg_tertiary']))

        status_badge = QLabel(status)
        status_badge.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS, bold=True))
        status_badge.setStyleSheet(f"""
        QLabel {{
            background-color: {status_bg}20;
            color: {status_bg};
            border: 1px solid {status_bg}40;
            border-radius: {tokens.RADIUS_SM}px;
            padding: 4px 10px;
        }}
        """)
        header.addWidget(status_badge)

        layout.addLayout(header)

        # Info row: quantidade de notas + data
        info_row = QHBoxLayout()
        info_row.setSpacing(tokens.SPACING_MD)

        notas_count = self._manifesto_data.get('total_notas', 0)
        notas_label = QLabel(f"{notas_count} nota(s)")
        notas_label.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        notas_label.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        info_row.addWidget(notas_label)

        data = self._manifesto_data.get('data_importacao', '')
        if data:
            data_label = QLabel(f"• {data}")
            data_label.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
            data_label.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            info_row.addWidget(data_label)

        info_row.addStretch()
        layout.addLayout(info_row)

        # Footer: peso + frete resumidos
        footer = QHBoxLayout()
        footer.setSpacing(tokens.SPACING_MD)

        peso = self._manifesto_data.get('peso_total', 0)
        peso_label = QLabel(f"⚖ {formatar_peso(peso)}")
        peso_label.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        peso_label.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        footer.addWidget(peso_label)

        frete = self._manifesto_data.get('frete_total', 0)
        frete_label = QLabel(f"💰 {formatar_moeda(frete)}")
        frete_label.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        frete_label.setStyleSheet(f"color: {colors['success']}; background: transparent;")
        footer.addWidget(frete_label)

        footer.addStretch()
        layout.addLayout(footer)

    def mousePressEvent(self, event):
        self.clicked.emit(self._manifesto_data['id'])
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        """Define estado selecionado com destaque vermelho."""
        self._selected = selected
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        if selected:
            self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['error_soft']};
                border: 2px solid {colors['error']};
                border-radius: {tokens.RADIUS_LG}px;
            }}
            """)
        else:
            self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['card_bg']};
                border: 1px solid {colors['card_border']};
                border-radius: {tokens.RADIUS_LG}px;
            }}
            QFrame:hover {{
                border-color: {colors['border_strong']};
                background-color: {colors['card_hover']};
            }}
            """)


# ---------------------------------------------------------------------------
# Constantes de coluna da tabela de notas
# ---------------------------------------------------------------------------
_COL_CTE       = 0
_COL_REMETENTE = 1
_COL_DEST      = 2
_COL_ORIGEM    = 3
_COL_DESTINO   = 4
_COL_FRETE     = 5
_COL_PESO      = 6
_COL_STATUS    = 7

_COLUNAS_NOTAS = ["CT-e", "Remetente", "Destinatário", "Origem", "Destino", "Frete", "Peso", "Status"]


# ---------------------------------------------------------------------------
# Worker de importação – emite sinal quando concluída
# ---------------------------------------------------------------------------
class _ImportWorker(QObject):
    """Executa a importação em thread separada e emite sinais thread-safe."""

    concluido = Signal(dict)       # resultado da importação
    erro      = Signal(str)        # mensagem de erro

    def __init__(self, caminho: str):
        super().__init__()
        self._caminho = caminho

    def run(self):
        try:
            resultado = notas_service.importar_manifesto(self._caminho)
            self.concluido.emit(resultado)
        except Exception as exc:
            logger.error(f"Erro ao importar manifesto: {exc}")
            self.erro.emit(str(exc))


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------
class TelaNotas(QWidget):
    """Tela de gerenciamento de manifestos e notas importadas (PySide6)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Mapeamento item-da-lista → manifesto_id
        self._manifesto_ids: dict[int, int] = {}   # row → manifesto_id
        self._manifesto_cards: dict[int, ManifestoCard] = {}  # manifesto_id → card
        self._selected_manifesto_id: Optional[int] = None

        self._setup_ui()
        self._carregar_manifestos()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        colors  = theme_manager.colors
        tokens  = theme_manager.tokens

        self.setStyleSheet(f"background-color: {colors['bg_primary']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(
            tokens.SPACING_2XL, tokens.SPACING_2XL,
            tokens.SPACING_2XL, tokens.SPACING_2XL,
        )
        root.setSpacing(tokens.SPACING_LG)

        # ── Resumo / totais ─────────────────────────────────────────
        self._lbl_resumo = QLabel("Selecione um manifesto para visualizar as notas.")
        self._lbl_resumo.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD, bold=True))
        self._lbl_resumo.setStyleSheet(
            f"color: {colors['text_secondary']}; background-color: transparent;"
        )
        self._lbl_resumo.setWordWrap(True)
        root.addWidget(self._lbl_resumo)

        # ── Splitter: esquerda=manifestos / direita=notas ────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet(f"""
        QSplitter::handle {{
            background-color: {colors['border_subtle']};
        }}
        """)

        splitter.addWidget(self._criar_painel_manifestos())
        splitter.addWidget(self._criar_painel_notas())
        splitter.setStretchFactor(0, 0)   # esquerda – tamanho fixo preferido
        splitter.setStretchFactor(1, 1)   # direita  – cresce com a janela
        splitter.setSizes([340, 900])

        root.addWidget(splitter, stretch=1)

    # ── Painel esquerdo – Manifestos (Cards CRM style) ─────────────────────

    def _criar_painel_manifestos(self) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        container = QWidget()
        container.setMinimumWidth(320)
        container.setMaximumWidth(400)
        container.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(tokens.SPACING_MD)

        # Header com título
        header = QHBoxLayout()
        header.setSpacing(tokens.SPACING_SM)

        title = QLabel("Manifestos")
        title.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG, bold=True))
        title.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        header.addWidget(title)

        header.addStretch()

        # Botões de ação
        self._btn_importar = ModernButton("＋ Importar", ButtonStyle.SUCCESS, size=ButtonSize.SM)
        self._btn_importar.clicked.connect(self._importar_manifesto)
        header.addWidget(self._btn_importar)

        self._btn_apagar = ModernButton("Apagar", ButtonStyle.DANGER, size=ButtonSize.SM)
        self._btn_apagar.clicked.connect(self._apagar_manifesto)
        header.addWidget(self._btn_apagar)

        layout.addLayout(header)

        # Scroll area para cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 1px; }}
        QScrollBar::handle:vertical {{ background: {colors['border_default']}; border-radius: 3px; min-height: 30px; }}
        QScrollBar::handle:vertical:hover {{ background: {colors['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ height: 0px; }}
        """)

        # Container para cards
        self._cards_container = QWidget()
        self._cards_container.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout()
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(tokens.SPACING_MD)
        self._cards_container.setLayout(self._cards_layout)

        scroll.setWidget(self._cards_container)
        layout.addWidget(scroll, 1)

        return container

    # ── Painel direito – Notas ───────────────────────────────────────────

    def _criar_painel_notas(self) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard("📄 Notas do Manifesto Selecionado", parent=self)

        # Tabela de notas
        self._tabela_notas = QTableWidget(0, len(_COLUNAS_NOTAS))
        self._tabela_notas.setHorizontalHeaderLabels(_COLUNAS_NOTAS)
        self._tabela_notas.setAlternatingRowColors(True)
        self._tabela_notas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tabela_notas.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tabela_notas.verticalHeader().setVisible(False)
        self._tabela_notas.setSortingEnabled(True)
        self._tabela_notas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        hdr = self._tabela_notas.horizontalHeader()
        # CT-e: stretch; demais: ajuste ao conteúdo ou dimensão mínima fixa
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(False)
        # Larguras iniciais
        larguras = [160, 220, 220, 130, 130, 110, 110, 110]
        for col, w in enumerate(larguras):
            self._tabela_notas.setColumnWidth(col, w)

        self._tabela_notas.setStyleSheet(f"""
        QTableWidget {{
            background-color: {colors['bg_secondary']};
            alternate-background-color: {colors['table_row_odd']};
            gridline-color: {colors['border_subtle']};
            border: 1px solid {colors['border_subtle']};
            border-radius: {tokens.RADIUS_LG}px;
            selection-background-color: {colors['table_row_selected']};
            selection-color: {colors['text_primary']};
            outline: none;
            font-size: {tokens.FONT_SIZE_MD}px;
            color: {colors['text_primary']};
        }}
        QTableWidget::item {{
            padding: 8px 12px;
            border-bottom: 1px solid {colors['border_subtle']};
        }}
        QTableWidget::item:hover {{
            background-color: {colors['table_row_hover']};
        }}
        QHeaderView::section {{
            background-color: {colors['table_header_bg']};
            color: {colors['table_header_text']};
            padding: 10px 12px;
            border: none;
            border-bottom: 2px solid {colors['border_default']};
            border-right: 1px solid {colors['border_subtle']};
            font-weight: 700;
            font-size: {tokens.FONT_SIZE_SM}px;
        }}
        """)

        card.add_widget(self._tabela_notas)
        return card

    # ------------------------------------------------------------------
    # Carregar manifestos (Cards CRM style)
    # ------------------------------------------------------------------

    def _carregar_manifestos(self) -> None:
        # Limpar cards existentes
        for card in self._manifesto_cards.values():
            card.deleteLater()
        self._manifesto_cards.clear()
        self._manifesto_ids.clear()
        self._selected_manifesto_id = None

        try:
            manifestos = notas_service.listar_manifestos("Geral", None, None)
        except Exception as exc:
            logger.error(f"Erro ao listar manifestos: {exc}")
            manifestos = []

        for manifesto in manifestos:
            manifesto_id, nome_arquivo, data_importacao, total_notas, *_rest = manifesto

            # Criar dados do card
            manifesto_data = {
                'id': manifesto_id,
                'nome_arquivo': nome_arquivo,
                'data_importacao': data_importacao,
                'total_notas': total_notas,
                'status': 'Importado',
                'peso_total': 0,  # Será calculado depois
                'frete_total': 0,  # Será calculado depois
            }

            # Criar card
            card = ManifestoCard(manifesto_data, parent=self._cards_container)
            card.clicked.connect(self._ao_selecionar_manifesto)
            self._cards_layout.addWidget(card)
            self._manifesto_cards[manifesto_id] = card

        # Selecionar primeiro manifesto se houver
        if self._manifesto_cards:
            first_id = list(self._manifesto_cards.keys())[0]
            self._selecionar_manifesto(first_id)
        else:
            self._tabela_notas.setRowCount(0)
            self._lbl_resumo.setText("Nenhum manifesto encontrado.")

    # ------------------------------------------------------------------
    # Selecionar manifesto → carregar notas
    # ------------------------------------------------------------------

    def _ao_selecionar_manifesto(self, manifesto_id: int) -> None:
        self._selecionar_manifesto(manifesto_id)

    def _selecionar_manifesto(self, manifesto_id: int) -> None:
        """Seleciona um manifesto e carrega suas notas."""
        if manifesto_id == self._selected_manifesto_id:
            return

        # Atualizar seleção visual dos cards
        for mid, card in self._manifesto_cards.items():
            card.set_selected(mid == manifesto_id)

        self._selected_manifesto_id = manifesto_id

        # Obter nome do manifesto
        card = self._manifesto_cards.get(manifesto_id)
        nome_arquivo = card._manifesto_data.get('nome_arquivo', f'Manifesto {manifesto_id}') if card else f'Manifesto {manifesto_id}'

        self._carregar_notas(manifesto_id, nome_arquivo)

    def _carregar_notas(self, manifesto_id: int, nome_exibido: str) -> None:
        self._tabela_notas.setSortingEnabled(False)
        self._tabela_notas.setRowCount(0)

        try:
            dados = notas_service.listar_notas_por_manifesto(manifesto_id)
        except Exception as exc:
            logger.error(f"Erro ao listar notas do manifesto {manifesto_id}: {exc}")
            dados = []

        total_frete = 0.0
        total_peso  = 0.0

        colors = theme_manager.colors

        for linha in dados:
            (
                _id_nota,
                chave_nfe,
                numero_cte,
                remetente,
                destinatario,
                origem,
                destino,
                valor_mercadoria,
                frete,
                peso,
                status,
            ) = linha

            frete = float(frete or 0)
            peso  = float(peso  or 0)
            total_frete += frete
            total_peso  += peso

            cte = numero_cte if numero_cte else (chave_nfe or "")

            row_idx = self._tabela_notas.rowCount()
            self._tabela_notas.insertRow(row_idx)

            def _item(text: str, align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) -> QTableWidgetItem:
                it = QTableWidgetItem(str(text) if text else "-")
                it.setTextAlignment(align)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                return it

            _right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

            self._tabela_notas.setItem(row_idx, _COL_CTE,       _item(cte))
            self._tabela_notas.setItem(row_idx, _COL_REMETENTE,  _item(remetente or "-"))
            self._tabela_notas.setItem(row_idx, _COL_DEST,       _item(destinatario or "-"))
            self._tabela_notas.setItem(row_idx, _COL_ORIGEM,     _item(origem or "-"))
            self._tabela_notas.setItem(row_idx, _COL_DESTINO,    _item(destino or "-"))
            self._tabela_notas.setItem(row_idx, _COL_FRETE,      _item(formatar_moeda(frete),  _right))
            self._tabela_notas.setItem(row_idx, _COL_PESO,       _item(formatar_peso(peso),    _right))

            # Status com cor
            status_item = _item(status or "-", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            cor_status = {
                "Disponível": colors.get("success", "#22C55E"),
                "Em viagem":  colors.get("warning", "#F59E0B"),
                "Entregue":   colors.get("info",    "#3B82F6"),
            }.get(status, colors.get("text_tertiary", "#94A3B8"))
            status_item.setForeground(
                __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(cor_status)
            )
            self._tabela_notas.setItem(row_idx, _COL_STATUS, status_item)

        self._tabela_notas.setSortingEnabled(True)

        # Atualizar card do manifesto com totais calculados
        card = self._manifesto_cards.get(manifesto_id)
        if card:
            card._manifesto_data['peso_total'] = total_peso
            card._manifesto_data['frete_total'] = total_frete
            # Recriar o card para atualizar os valores
            card.deleteLater()
            new_card = ManifestoCard(card._manifesto_data, parent=self._cards_container)
            new_card.clicked.connect(self._ao_selecionar_manifesto)
            new_card.set_selected(True)
            self._cards_layout.replaceWidget(card, new_card)
            self._manifesto_cards[manifesto_id] = new_card

        qtd = len(dados)
        resumo = (
            f"{nome_exibido}   •   "
            f"Notas: {qtd}   •   "
            f"Frete Total: {formatar_moeda(total_frete)}   •   "
            f"Peso Total: {formatar_peso(total_peso)}"
        )
        self._lbl_resumo.setText(resumo)

    # ------------------------------------------------------------------
    # Importar manifesto
    # ------------------------------------------------------------------

    def _importar_manifesto(self) -> None:
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Manifesto TXT",
            "",
            "Arquivos TXT (*.txt);;Todos os arquivos (*.*)",
        )
        if not caminho:
            return

        self._btn_importar.setEnabled(False)
        self._btn_importar.setText("Importando…")

        self._worker = _ImportWorker(caminho)
        self._worker.concluido.connect(self._ao_importar_concluido)
        self._worker.erro.connect(self._ao_importar_erro)

        t = threading.Thread(target=self._worker.run, daemon=True)
        t.start()

    def _ao_importar_concluido(self, resultado: dict) -> None:
        self._btn_importar.setEnabled(True)
        self._btn_importar.setText("＋ Importar Manifesto")

        QMessageBox.information(
            self,
            "Importação Concluída",
            (
                f"Arquivo: {resultado.get('arquivo', '-')}\n\n"
                f"Notas encontradas:  {resultado.get('encontradas', 0)}\n"
                f"Notas salvas:       {resultado.get('salvas', 0)}\n"
                f"Notas duplicadas:   {resultado.get('duplicadas', 0)}"
            ),
        )
        self._carregar_manifestos()

    def _ao_importar_erro(self, mensagem: str) -> None:
        self._btn_importar.setEnabled(True)
        self._btn_importar.setText("＋ Importar Manifesto")

        QMessageBox.critical(self, "Erro ao Importar Manifesto", mensagem)

    # ------------------------------------------------------------------
    # Apagar manifesto
    # ------------------------------------------------------------------

    def _apagar_manifesto(self) -> None:
        if self._selected_manifesto_id is None:
            QMessageBox.warning(self, "Atenção", "Selecione um manifesto para apagar.")
            return

        manifesto_id = self._selected_manifesto_id
        card = self._manifesto_cards.get(manifesto_id)
        nome_exibido = card._manifesto_data.get('nome_arquivo', f'Manifesto {manifesto_id}') if card else f'Manifesto {manifesto_id}'

        resposta = QMessageBox.question(
            self,
            "Apagar Manifesto",
            (
                f"Deseja apagar este manifesto?\n\n{nome_exibido}\n\n"
                "Todas as notas desse manifesto também serão apagadas."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            notas_service.apagar_manifesto(manifesto_id)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao Apagar Manifesto", str(exc))
            return

        QMessageBox.information(self, "Sucesso", "Manifesto apagado com sucesso!")
        self._tabela_notas.setRowCount(0)
        self._lbl_resumo.setText("Selecione um manifesto para visualizar as notas.")
        self._carregar_manifestos()
