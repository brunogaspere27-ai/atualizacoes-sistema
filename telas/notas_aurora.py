"""
Notas Aurora v1.0 - CW Transportadora
Tela de notas importadas com Aurora Design System

Features:
- Split view com lista de manifestos e tabela de notas
- Glassmorphism e gradientes
- Tabela premium estilo Stripe
- Resumo com KPIs
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QFileDialog, QMessageBox, QAbstractItemView,
    QSizePolicy,
)

from services.notas_service import notas_service
from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.components_aurora import (
    AuroraCard, AuroraButton, ButtonStyle, CardVariant,
    AuroraTable, AuroraKPICard, SeparatorLine,
)
from utils.helpers import formatar_moeda, formatar_peso
from utils.logger import get_logger

logger = get_logger(__name__)


# Constantes de coluna
_COL_CTE = 0
_COL_REMETENTE = 1
_COL_DEST = 2
_COL_ORIGEM = 3
_COL_DESTINO = 4
_COL_FRETE = 5
_COL_PESO = 6
_COL_STATUS = 7

_COLUNAS_NOTAS = ["CT-e", "Remetente", "Destinatário", "Origem", "Destino", "Frete", "Peso", "Status"]


class _ImportWorker(QObject):
    """Worker de importação em thread separada."""

    concluido = Signal(dict)
    erro = Signal(str)

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


class NotasAurora(QWidget):
    """Tela de gerenciamento de manifestos com Aurora Design System."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._manifesto_ids: dict[int, int] = {}
        self._setup_ui()
        self._carregar_manifestos()

    def _setup_ui(self) -> None:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        self.setStyleSheet(f"background-color: {c['bg_primary']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(t.SPACING_3XL, t.SPACING_XL, t.SPACING_3XL, t.SPACING_2XL)
        root.setSpacing(t.SPACING_XL)

        # Header
        header = self._create_header()
        root.addWidget(header)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
        QSplitter::handle {{
            background: {c['border_default']};
        }}
        """)

        # Painel esquerdo - lista de manifestos
        left_panel = self._build_manifestos_panel()
        splitter.addWidget(left_panel)

        # Painel direito - tabela de notas
        right_panel = self._build_notas_panel()
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter)

    def _create_header(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(t.SPACING_MD)
        header.setLayout(hl)

        title = QLabel("Notas Importadas")
        title.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hl.addWidget(title)

        hl.addStretch()

        # Botão importar
        self.btn_importar = AuroraButton("Importar Manifesto", ButtonStyle.AURORA, "upload")
        self.btn_importar.setFixedHeight(44)
        self.btn_importar.clicked.connect(self._on_importar)
        hl.addWidget(self.btn_importar)

        # Botão apagar
        self.btn_apagar = AuroraButton("Apagar Selecionado", ButtonStyle.CRIMSON, "trash")
        self.btn_apagar.setFixedHeight(44)
        self.btn_apagar.clicked.connect(self._on_apagar)
        hl.addWidget(self.btn_apagar)

        return header

    def _build_manifestos_panel(self) -> AuroraCard:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        card = AuroraCard(
            "Manifestos",
            "file-text",
            variant=CardVariant.DEFAULT,
            accent_color=AccentColor.COSMOS,
            padding=t.SPACING_LG
        )

        layout = QVBoxLayout()
        layout.setSpacing(t.SPACING_MD)
        layout.setContentsMargins(0, 0, 0, 0)

        # Lista de manifestos
        self.lista_manifestos = QListWidget()
        self.lista_manifestos.setStyleSheet(f"""
        QListWidget {{
            background: {c['bg_tertiary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 8px;
        }}
        QListWidget::item {{
            background: transparent;
            color: {c['text_primary']};
            border-radius: {t.RADIUS_MD}px;
            padding: 12px 16px;
            margin: 2px 0;
        }}
        QListWidget::item:hover {{
            background: {c['bg_overlay']};
        }}
        QListWidget::item:selected {{
            background: {c['aurora_soft']};
            color: {c['aurora']};
            font-weight: 600;
        }}
        QScrollBar:vertical {{ background: transparent; width: 6px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 3px; }}
        """)
        self.lista_manifestos.currentRowChanged.connect(self._on_manifesto_selecionado)
        layout.addWidget(self.lista_manifestos)

        card.add_layout(layout)

        return card

    def _build_notas_panel(self) -> QWidget:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(t.SPACING_LG)
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)

        # Card com tabela
        table_card = AuroraCard(
            "Notas do Manifesto",
            "file",
            variant=CardVariant.DEFAULT,
            accent_color=AccentColor.OCEAN,
            padding=t.SPACING_LG
        )

        self.tabela_notas = AuroraTable()
        self.tabela_notas.setColumnCount(len(_COLUNAS_NOTAS))
        self.tabela_notas.setHorizontalHeaderLabels(_COLUNAS_NOTAS)
        self.tabela_notas.setFixedHeight(400)

        table_card.add_widget(self.tabela_notas)
        layout.addWidget(table_card)

        # Resumo
        resumo_card = AuroraCard(
            "Resumo",
            "calculator",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.FOREST,
            padding=t.SPACING_LG
        )

        resumo_layout = QHBoxLayout()
        resumo_layout.setSpacing(t.SPACING_XL)
        resumo_layout.setContentsMargins(0, 0, 0, 0)

        # KPIs
        self.kpi_total_notas = AuroraKPICard("Total de Notas", "0", "", "file", AccentColor.AURORA)
        resumo_layout.addWidget(self.kpi_total_notas)

        self.kpi_valor_total = AuroraKPICard("Valor Total", "R$ 0,00", "", "dollar", AccentColor.FOREST)
        resumo_layout.addWidget(self.kpi_valor_total)

        self.kpi_peso_total = AuroraKPICard("Peso Total", "0 kg", "", "package", AccentColor.OCEAN)
        resumo_layout.addWidget(self.kpi_peso_total)

        resumo_card.add_layout(resumo_layout)
        layout.addWidget(resumo_card)

        return container

    def _carregar_manifestos(self):
        """Carrega a lista de manifestos."""
        try:
            manifestos = notas_service.listar_manifestos()
            self.lista_manifestos.clear()
            self._manifesto_ids.clear()

            for idx, man in enumerate(manifestos):
                item = QListWidgetItem(
                    f"{man.get('numero', 'N/A')} - {man.get('data', 'N/A')}"
                )
                self.lista_manifestos.addItem(item)
                self._manifesto_ids[idx] = man.get('id')

        except Exception as e:
            logger.error(f"Erro ao carregar manifestos: {e}")

    def _on_manifesto_selecionado(self, row: int):
        """Carrega notas do manifesto selecionado."""
        if row < 0:
            return

        manifesto_id = self._manifesto_ids.get(row)
        if not manifesto_id:
            return

        try:
            notas = notas_service.obter_notas_manifesto(manifesto_id)
            self._carregar_tabela(notas)
            self._atualizar_resumo(notas)
        except Exception as e:
            logger.error(f"Erro ao carregar notas: {e}")

    def _carregar_tabela(self, notas: list):
        """Carrega a tabela de notas."""
        self.tabela_notas.setRowCount(0)

        for idx, nota in enumerate(notas):
            self.tabela_notas.insertRow(idx)
            self.tabela_notas.setItem(idx, _COL_CTE, QTableWidgetItem(nota.get('cte', '')))
            self.tabela_notas.setItem(idx, _COL_REMETENTE, QTableWidgetItem(nota.get('remetente', '')))
            self.tabela_notas.setItem(idx, _COL_DEST, QTableWidgetItem(nota.get('destinatario', '')))
            self.tabela_notas.setItem(idx, _COL_ORIGEM, QTableWidgetItem(nota.get('origem', '')))
            self.tabela_notas.setItem(idx, _COL_DESTINO, QTableWidgetItem(nota.get('destino', '')))
            self.tabela_notas.setItem(idx, _COL_FRETE, QTableWidgetItem(formatar_moeda(nota.get('frete', 0))))
            self.tabela_notas.setItem(idx, _COL_PESO, QTableWidgetItem(formatar_peso(nota.get('peso', 0))))
            self.tabela_notas.setItem(idx, _COL_STATUS, QTableWidgetItem(nota.get('status', 'Pendente')))

    def _atualizar_resumo(self, notas: list):
        """Atualiza os KPIs de resumo."""
        total_notas = len(notas)
        valor_total = sum(n.get('frete', 0) for n in notas)
        peso_total = sum(n.get('peso', 0) for n in notas)

        # Atualizar KPIs
        for child in self.kpi_total_notas.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(str(total_notas))
                break

        for child in self.kpi_valor_total.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(formatar_moeda(valor_total))
                break

        for child in self.kpi_peso_total.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(formatar_peso(peso_total))
                break

    def _on_importar(self):
        """Abre diálogo para importar manifesto."""
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Manifesto", "", "XML (*.xml);;Todos os Arquivos (*)"
        )

        if not caminho:
            return

        self.btn_importar.setEnabled(False)
        self.btn_importar.setText("Importando...")

        worker = _ImportWorker(caminho)
        worker_thread = threading.Thread(target=worker.run, daemon=True)
        worker.concluido.connect(self._on_importacao_concluida)
        worker.erro.connect(self._on_importacao_erro)
        worker_thread.start()

    def _on_importacao_concluida(self, resultado: dict):
        """Callback quando importação conclui."""
        self.btn_importar.setEnabled(True)
        self.btn_importar.setText("Importar Manifesto")

        if resultado.get('sucesso'):
            QMessageBox.information(self, "Sucesso", "Manifesto importado com sucesso!")
            self._carregar_manifestos()
        else:
            QMessageBox.warning(self, "Aviso", resultado.get('mensagem', 'Erro desconhecido'))

    def _on_importacao_erro(self, erro: str):
        """Callback quando importação falha."""
        self.btn_importar.setEnabled(True)
        self.btn_importar.setText("Importar Manifesto")
        QMessageBox.critical(self, "Erro", f"Erro ao importar: {erro}")

    def _on_apagar(self):
        """Apaga o manifesto selecionado."""
        row = self.lista_manifestos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um manifesto para apagar.")
            return

        manifesto_id = self._manifesto_ids.get(row)
        if not manifesto_id:
            return

        reply = QMessageBox.question(
            self, "Confirmar", "Deseja realmente apagar este manifesto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                notas_service.apagar_manifesto(manifesto_id)
                self._carregar_manifestos()
                self.tabela_notas.setRowCount(0)
                QMessageBox.information(self, "Sucesso", "Manifesto apagado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao apagar: {e}")
