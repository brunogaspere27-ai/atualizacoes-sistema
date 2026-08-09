"""
Tela de Ranking de Clientes - PySide6
Migrado de telas/ranking_clientes.py (CustomTkinter) para PySide6.
"""

import csv
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QAbstractItemView, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QBrush, QFont

from services.ranking_service import ranking_service
from ui.theme.cw_theme import cw_theme
from utils.components import KPICard, ModernButton, ButtonStyle
from utils.helpers import formatar_moeda
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Trabalhador de thread para carregar o ranking sem bloquear a UI
# ---------------------------------------------------------------------------

class _RankingWorker(QObject):
    """Emite os dados do ranking de dentro de uma thread de background."""

    concluido = Signal(list, int)   # (dados, geracao)
    erro = Signal(int)              # (geracao)

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


# ---------------------------------------------------------------------------
# Tela principal
# ---------------------------------------------------------------------------

class TelaRankingClientes(QWidget):
    """Tela de Ranking de Clientes - PySide6."""

    # Sinal interno para aplicar resultados vindos da thread worker de volta ao
    # thread principal de forma segura (sem QTimer.singleShot entre threads).
    _dados_prontos = Signal(list, int)
    _dados_erro = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.tipo_periodo: str = "Geral"
        self.mes: str = datetime.now().strftime("%m")
        self.ano: str = datetime.now().strftime("%Y")
        self.dados: list = []
        self._geracao: int = 0

        # Conecta os sinais internos ao slot do thread principal
        self._dados_prontos.connect(self._aplicar_dados)
        self._dados_erro.connect(self._aplicar_erro)

        self._setup_ui()
        self.carregar_ranking()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _setup_ui(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Área scrollável principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {colors['bg_primary']}; border: none; }}")
        root_layout.addWidget(scroll)

        # Container interno
        content = QWidget()
        content.setStyleSheet(f"background-color: {colors['bg_primary']};")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(
            tokens._2XL, tokens._2XL,
            tokens._2XL, tokens._2XL,
        )
        self._content_layout.setSpacing(tokens.LG)
        scroll.setWidget(content)

        self._criar_filtros()
        self._criar_kpi_cards()
        self._criar_tabela()

    def _criar_filtros(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing
        radius = cw_theme.radius

        frame = QFrame()
        frame.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: {radius.LG}px;
        }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(tokens.LG, tokens.MD, tokens.LG, tokens.MD)
        layout.setSpacing(tokens.MD)

        # Combo período
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setCurrentText(self.tipo_periodo)
        self.combo_periodo.setMinimumHeight(40)
        self.combo_periodo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD))
        layout.addWidget(self.combo_periodo)

        # Combo mês
        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentText(self.mes)
        self.combo_mes.setMinimumHeight(40)
        self.combo_mes.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD))
        layout.addWidget(self.combo_mes)

        # Input ano
        self.entry_ano = QLineEdit(self.ano)
        self.entry_ano.setPlaceholderText("Ano")
        self.entry_ano.setMinimumHeight(40)
        self.entry_ano.setMaximumWidth(100)
        self.entry_ano.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD))
        layout.addWidget(self.entry_ano)

        layout.addStretch()

        titulo = QLabel("Ranking de clientes por frete")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        layout.insertWidget(0, titulo)

        # Botão Atualizar
        self.btn_atualizar = ModernButton("Atualizar", ButtonStyle.SUCCESS)
        self.btn_atualizar.clicked.connect(self.carregar_ranking)
        layout.addWidget(self.btn_atualizar)

        # Botão Exportar CSV
        self.btn_exportar = ModernButton("Exportar CSV", ButtonStyle.PRIMARY)
        self.btn_exportar.clicked.connect(self.exportar_csv)
        layout.addWidget(self.btn_exportar)

        self._content_layout.addWidget(frame)

    def _criar_kpi_cards(self):
        tokens = cw_theme.spacing

        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(cards_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(tokens.MD)
        for col in range(4):
            grid.setColumnStretch(col, 1)

        self.card_clientes = KPICard(
            "CLIENTES", "0", "Clientes no período", "employees"
        )
        grid.addWidget(self.card_clientes, 0, 0)

        self.card_notas = KPICard(
            "NOTAS", "0", "Total de notas", "package"
        )
        grid.addWidget(self.card_notas, 0, 1)

        self.card_frete = KPICard(
            "FRETE GERADO", "R$ 0,00", "Frete total do período", "money"
        )
        grid.addWidget(self.card_frete, 0, 2)

        self.card_peso = KPICard(
            "PESO TOTAL", "0,00 kg", "Peso transportado", "box"
        )
        grid.addWidget(self.card_peso, 0, 3)

        self._content_layout.addWidget(cards_widget)

    def _criar_tabela(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing
        radius = cw_theme.radius

        container = QFrame()
        container.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: {radius.LG}px;
        }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(tokens.LG, tokens.LG, tokens.LG, tokens.LG)
        container_layout.setSpacing(tokens.MD)

        # Cabeçalho do container da tabela
        topo = QHBoxLayout()
        self.lbl_titulo_tabela = QLabel("Ranking de Clientes")
        self.lbl_titulo_tabela.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        self.lbl_titulo_tabela.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        topo.addWidget(self.lbl_titulo_tabela)

        topo.addStretch()

        lbl_ordem = QLabel("Mais área útil, mais posições e leitura por impacto")
        lbl_ordem.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        lbl_ordem.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        topo.addWidget(lbl_ordem)
        container_layout.addLayout(topo)

        # QTableWidget
        colunas = ["#", "Cliente / Destinatário", "Notas", "Frete Gerado", "Peso", "% Médio", "Impacto"]
        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(False)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(True)
        self.tabela.setMinimumHeight(640)
        self.tabela.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabela.setSortingEnabled(False)

        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)   # #
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)            # cliente
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)   # notas
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)   # frete
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)   # peso
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)   # % médio
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)            # impacto

        container_layout.addWidget(self.tabela)
        self._content_layout.addWidget(container)
        self._content_layout.addStretch()

    # ------------------------------------------------------------------
    # Carregamento de dados com thread de background
    # ------------------------------------------------------------------

    def carregar_ranking(self):
        """Lê os filtros e dispara o carregamento em background."""
        self.tipo_periodo = self.combo_periodo.currentText()
        self.mes = self.combo_mes.currentText()
        self.ano = self.entry_ano.text().strip()

        self._geracao += 1
        geracao_atual = self._geracao

        self.btn_atualizar.setEnabled(False)
        self._mostrar_carregando()

        worker = _RankingWorker(self.tipo_periodo, self.mes, self.ano, geracao_atual)
        # Conecta os sinais do worker aos sinais internos ANTES de iniciar a thread.
        # Como os sinais internos são do objeto TelaRankingClientes (que vive no Qt
        # main thread), a entrega é automaticamente cross-thread segura.
        worker.concluido.connect(self._dados_prontos)
        worker.erro.connect(self._dados_erro)

        t = threading.Thread(target=worker.executar, daemon=True)
        t.start()

    def _mostrar_carregando(self):
        self.tabela.setRowCount(0)
        self.tabela.setRowCount(1)
        item = QTableWidgetItem("Carregando…")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        colors = cw_theme.colors
        item.setForeground(QBrush(QColor(colors["text_tertiary"])))
        self.tabela.setItem(0, 0, item)
        self.tabela.setSpan(0, 0, 1, self.tabela.columnCount())

    def _aplicar_dados(self, dados: list, geracao: int):
        """Recebido no thread principal via sinal; descarta resultados obsoletos."""
        if geracao != self._geracao:
            return
        self.dados = dados
        self.btn_atualizar.setEnabled(True)
        self._atualizar_kpi_cards()
        self._atualizar_tabela()

    def _aplicar_erro(self, geracao: int):
        if geracao != self._geracao:
            return
        self.dados = []
        self.btn_atualizar.setEnabled(True)
        self._atualizar_kpi_cards()
        self._atualizar_tabela()

    # ------------------------------------------------------------------
    # Atualização dos KPI cards
    # ------------------------------------------------------------------

    def _atualizar_kpi_cards(self):
        total_clientes = len(self.dados)
        total_notas = sum(item.get("total_notas", 0) for item in self.dados)
        total_frete = sum(item.get("frete", 0) for item in self.dados)
        total_peso = sum(item.get("peso", 0) for item in self.dados)

        self.card_clientes.set_value(str(total_clientes))
        self.card_notas.set_value(str(total_notas))
        self.card_frete.set_value(formatar_moeda(total_frete))
        self.card_peso.set_value(
            f"{total_peso:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    # ------------------------------------------------------------------
    # Atualização da tabela
    # ------------------------------------------------------------------

    def _atualizar_tabela(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        # Atualiza título da tabela de acordo com o período
        if self.tipo_periodo == "Mês":
            self.lbl_titulo_tabela.setText(f"Ranking de Clientes — {self.mes}/{self.ano}")
        elif self.tipo_periodo == "Ano":
            self.lbl_titulo_tabela.setText(f"Ranking de Clientes — Ano {self.ano}")
        else:
            self.lbl_titulo_tabela.setText("Ranking Geral de Clientes")

        # Remove qualquer span anterior
        self.tabela.clearSpans()
        self.tabela.setRowCount(0)

        if not self.dados:
            self.tabela.setRowCount(1)
            item = QTableWidgetItem("Nenhum cliente encontrado para este período.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QBrush(QColor(colors["text_tertiary"])))
            self.tabela.setItem(0, 0, item)
            self.tabela.setSpan(0, 0, 1, self.tabela.columnCount())
            return

        fonte_normal = cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD)
        fonte_bold = cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD, bold=True)
        cor_frete = QColor(colors["success"])
        cor_padrao = QColor(colors["text_primary"])
        maior_frete = max((float(item.get("frete", 0) or 0) for item in self.dados), default=0) or 1

        self.tabela.setRowCount(len(self.dados))

        for row, item in enumerate(self.dados):
            posicao = f"{row + 1}º"
            cliente = item.get("cliente", "")
            total_notas = str(item.get("total_notas", 0))
            frete = formatar_moeda(item.get("frete", 0))
            peso = (
                f"{item.get('peso', 0):,.2f} kg"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            percentual = f"{item.get('percentual_medio', 0):.2f}%".replace(".", ",")

            valores = [posicao, cliente, total_notas, frete, peso, percentual]

            for col, texto in enumerate(valores):
                celula = QTableWidgetItem(texto)
                celula.setFont(fonte_bold if col in (0, 2, 3) else fonte_normal)

                # Coluna "Frete Gerado" (índice 3) ganha destaque em verde
                celula.setForeground(QBrush(cor_frete if col == 3 else cor_padrao))

                # Alinhamento: # e colunas numéricas centralizado; cliente à esquerda
                if col in (0, 2, 3, 4, 5):
                    celula.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                else:
                    celula.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                self.tabela.setItem(row, col, celula)

            impacto = int((float(item.get("frete", 0) or 0) / maior_frete) * 100)
            impacto_widget = QWidget()
            impacto_layout = QVBoxLayout(impacto_widget)
            impacto_layout.setContentsMargins(8, 8, 8, 8)
            impacto_layout.setSpacing(6)

            destaque = QLabel(f"{impacto}% do líder")
            destaque.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
            destaque.setStyleSheet(f"color: {colors['brand']}; background: transparent;")
            impacto_layout.addWidget(destaque)

            # Simple progress bar using QFrame
            from PySide6.QtWidgets import QProgressBar
            barra = QProgressBar()
            barra.setRange(0, 100)
            barra.setValue(impacto)
            barra.setTextVisible(False)
            barra.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {colors['bg_tertiary']};
                    border: none;
                    border-radius: 4px;
                    height: 8px;
                }}
                QProgressBar::chunk {{
                    background-color: {colors['brand']};
                    border-radius: 4px;
                }}
            """)
            impacto_layout.addWidget(barra)

            self.tabela.setCellWidget(row, 6, impacto_widget)
            self.tabela.setRowHeight(row, 58)

    # ------------------------------------------------------------------
    # Exportação CSV
    # ------------------------------------------------------------------

    def exportar_csv(self):
        if not self.dados:
            QMessageBox.warning(self, "Atenção", "Nenhum dado para exportar.\nCarregue o ranking primeiro.")
            return

        periodo = {"Mês": f"{self.mes}_{self.ano}", "Ano": self.ano}.get(self.tipo_periodo, "geral")
        nome_sugerido = f"ranking_clientes_{periodo}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv"

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar ranking como CSV",
            nome_sugerido,
            "Arquivo CSV (*.csv);;Todos os arquivos (*.*)",
        )

        if not caminho:
            return

        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Posição",
                    "Cliente",
                    "Total Notas",
                    "Valor Mercadoria (R$)",
                    "Frete Gerado (R$)",
                    "Peso (kg)",
                    "% Frete Médio",
                ])
                for i, item in enumerate(self.dados, start=1):
                    writer.writerow([
                        i,
                        item.get("cliente", ""),
                        item.get("total_notas", 0),
                        f"{item.get('valor_notas', 0):.2f}".replace(".", ","),
                        f"{item.get('frete', 0):.2f}".replace(".", ","),
                        f"{item.get('peso', 0):.2f}".replace(".", ","),
                        f"{item.get('percentual_medio', 0):.2f}".replace(".", ","),
                    ])

            QMessageBox.information(
                self,
                "Exportação concluída",
                f"Ranking exportado com sucesso!\n\n{caminho}",
            )

            try:
                import os
                os.startfile(caminho)
            except Exception:
                pass

        except Exception as erro:
            QMessageBox.critical(self, "Erro ao exportar", str(erro))
