"""
Ranking Aurora v1.0 - CW Transportadora
Tela de ranking de clientes com Aurora Design System

Features:
- Tabela premium estilo Stripe
- Filtros por período
- KPIs de resumo
- Exportação CSV
"""

import csv
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QBrush, QFont

from services.ranking_service import ranking_service
from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.components_aurora import (
    AuroraCard, AuroraButton, ButtonStyle, CardVariant,
    AuroraTable, AuroraKPICard, SeparatorLine,
)
from utils.helpers import formatar_moeda
from utils.logger import get_logger

logger = get_logger(__name__)


class _RankingWorker(QObject):
    """Worker para carregar ranking em background."""

    concluido = Signal(list, int)
    erro = Signal(int)

    def __init__(self, tipo: str, mes: str, ano: str, geracao: int):
        super().__init__()
        self._tipo = tipo
        self._mes = mes
        self._ano = ano
        self._geracao = geracao

    def executar(self):
        try:
            dados = ranking_service.carregar_ranking(self._tipo, self._mes, self._ano)
            self.concluido.emit(dados, self._geracao)
        except Exception as e:
            logger.error(f"Erro ao carregar ranking: {e}")
            self.erro.emit(self._geracao)


class RankingAurora(QWidget):
    """Tela de Ranking de Clientes com Aurora Design System."""

    _dados_prontos = Signal(list, int)
    _dados_erro = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.tipo_periodo: str = "Geral"
        self.mes: str = datetime.now().strftime("%m")
        self.ano: str = datetime.now().strftime("%Y")
        self.dados: list = []
        self._geracao: int = 0

        self._dados_prontos.connect(self._aplicar_dados)
        self._dados_erro.connect(self._aplicar_erro)

        self._setup_ui()
        self.carregar_ranking()

    def _setup_ui(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background-color: {c['bg_primary']}; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 3px; }}
        """)
        root_layout.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(t.SPACING_3XL, t.SPACING_XL, t.SPACING_3XL, t.SPACING_2XL)
        content_layout.setSpacing(t.SPACING_XL)
        content.setLayout(content_layout)
        scroll.setWidget(content)

        # Header
        header = self._create_header()
        content_layout.addWidget(header)

        # Filtros
        filters = self._create_filters()
        content_layout.addLayout(filters)

        # KPIs
        kpi_row = self._create_kpis()
        content_layout.addWidget(kpi_row)

        # Tabela
        table_card = AuroraCard(
            "Ranking de Clientes",
            "trophy",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.EMBER,
            padding=t.SPACING_LG
        )

        self.tabela_ranking = AuroraTable()
        self.tabela_ranking.setColumnCount(6)
        self.tabela_ranking.setHorizontalHeaderLabels([
            "Posição", "Cliente", "Viagens", "Receita", "Carga", "Margem"
        ])
        self.tabela_ranking.setFixedHeight(400)

        table_card.add_widget(self.tabela_ranking)
        content_layout.addWidget(table_card)

    def _create_header(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(t.SPACING_MD)
        header.setLayout(hl)

        title = QLabel("Ranking de Clientes")
        title.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hl.addWidget(title)

        hl.addStretch()

        # Botão exportar
        self.btn_exportar = AuroraButton("Exportar CSV", ButtonStyle.OCEAN, "download")
        self.btn_exportar.setFixedHeight(44)
        self.btn_exportar.clicked.connect(self._exportar_csv)
        hl.addWidget(self.btn_exportar)

        return header

    def _create_filters(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        filter_row = QHBoxLayout()
        filter_row.setSpacing(t.SPACING_MD)

        # Período
        periodo_lbl = QLabel("Período:")
        periodo_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        periodo_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        filter_row.addWidget(periodo_lbl)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Este Mês", "Mês Anterior", "Este Ano"])
        self.combo_periodo.setCurrentText(self.tipo_periodo)
        self.combo_periodo.setFixedHeight(40)
        self.combo_periodo.setStyleSheet(f"""
        QComboBox {{
            background: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 8px 16px;
        }}
        QComboBox:hover {{ border-color: {c['border_strong']}; }}
        QComboBox:focus {{ border: 1px solid {c['aurora']}; }}
        """)
        self.combo_periodo.currentTextChanged.connect(self._on_periodo_changed)
        filter_row.addWidget(self.combo_periodo)

        filter_row.addStretch()

        # Botão atualizar
        btn_atualizar = AuroraButton("Atualizar", ButtonStyle.AURORA, "refresh")
        btn_atualizar.setFixedHeight(40)
        btn_atualizar.clicked.connect(self.carregar_ranking)
        filter_row.addWidget(btn_atualizar)

        return filter_row

    def _create_kpis(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(t.SPACING_LG)

        self.kpi_total_clientes = AuroraKPICard(
            "Total de Clientes",
            "0",
            "",
            "users",
            AccentColor.AURORA
        )
        kpi_row.addWidget(self.kpi_total_clientes)

        self.kpi_receita_total = AuroraKPICard(
            "Receita Total",
            "R$ 0,00",
            "",
            "dollar",
            AccentColor.FOREST
        )
        kpi_row.addWidget(self.kpi_receita_total)

        self.kpi_viagens_total = AuroraKPICard(
            "Total de Viagens",
            "0",
            "",
            "truck",
            AccentColor.OCEAN
        )
        kpi_row.addWidget(self.kpi_viagens_total)

        container = QWidget()
        container.setLayout(kpi_row)
        return container

    def _on_periodo_changed(self, texto):
        self.tipo_periodo = texto
        self.carregar_ranking()

    def carregar_ranking(self):
        """Carrega o ranking em background."""
        self._geracao += 1
        worker = _RankingWorker(self.tipo_periodo, self.mes, self.ano, self._geracao)
        thread = threading.Thread(target=worker.executar, daemon=True)
        thread.start()

    def _aplicar_dados(self, dados: list, geracao: int):
        """Aplica os dados recebidos do worker."""
        if geracao != self._geracao:
            return  # Ignora resultados antigos

        self.dados = dados
        self._carregar_tabela(dados)
        self._atualizar_kpis(dados)

    def _aplicar_erro(self, geracao: int):
        """Trata erro no carregamento."""
        if geracao != self._geracao:
            return
        QMessageBox.critical(self, "Erro", "Erro ao carregar ranking.")

    def _carregar_tabela(self, dados: list):
        """Carrega a tabela com os dados."""
        self.tabela_ranking.setRowCount(0)

        for idx, cliente in enumerate(dados):
            self.tabela_ranking.insertRow(idx)
            self.tabela_ranking.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.tabela_ranking.setItem(idx, 1, QTableWidgetItem(cliente.get('nome', '')))
            self.tabela_ranking.setItem(idx, 2, QTableWidgetItem(str(cliente.get('viagens', 0))))
            self.tabela_ranking.setItem(idx, 3, QTableWidgetItem(formatar_moeda(cliente.get('receita', 0))))
            self.tabela_ranking.setItem(idx, 4, QTableWidgetItem(f"{cliente.get('carga', 0):.0f} kg"))
            self.tabela_ranking.setItem(idx, 5, QTableWidgetItem(f"{cliente.get('margem', 0):.1f}%"))

    def _atualizar_kpis(self, dados: list):
        """Atualiza os KPIs."""
        total_clientes = len(dados)
        receita_total = sum(c.get('receita', 0) for c in dados)
        viagens_total = sum(c.get('viagens', 0) for c in dados)

        # Atualizar KPIs
        for child in self.kpi_total_clientes.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(str(total_clientes))
                break

        for child in self.kpi_receita_total.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(formatar_moeda(receita_total))
                break

        for child in self.kpi_viagens_total.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(str(viagens_total))
                break

    def _exportar_csv(self):
        """Exporta o ranking para CSV."""
        if not self.dados:
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar CSV", "", "CSV (*.csv);;Todos os Arquivos (*)"
        )

        if not caminho:
            return

        try:
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Posição', 'Cliente', 'Viagens', 'Receita', 'Carga', 'Margem'])

                for idx, cliente in enumerate(self.dados):
                    writer.writerow([
                        idx + 1,
                        cliente.get('nome', ''),
                        cliente.get('viagens', 0),
                        cliente.get('receita', 0),
                        cliente.get('carga', 0),
                        cliente.get('margem', 0),
                    ])

            QMessageBox.information(self, "Sucesso", "Arquivo exportado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")
