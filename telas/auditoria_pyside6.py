"""
Tela Auditoria do Sistema - CW Transportadora - PySide6
Registro completo de todas as ações realizadas no sistema.
"""

from __future__ import annotations

import csv
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QScrollArea,
    QFileDialog,
)
from PySide6.QtCore import Qt, QTimer

from services.auditoria_service import auditoria_service
from telas.theme_pyside6 import theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ModernCard
from utils.logger import get_logger

logger = get_logger(__name__)

_POR_PAGINA = 100


class TelaAuditoria(QWidget):
    """Tela de auditoria do sistema em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pagina_atual = 0
        self._total_registros = 0
        self._dados: list = []
        self._setup_ui()
        self._carregar_dados()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {colors['bg_primary']}; border: none; }}")
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {colors['bg_primary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        cl.setSpacing(tokens.SPACING_XL)
        content.setLayout(cl)
        scroll.setWidget(content)

        # Cards resumo
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; border: 1px solid {colors['border_subtle']}; }}")
        rl = QHBoxLayout()
        rl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_MD, tokens.SPACING_XL, tokens.SPACING_MD)
        rl.setSpacing(tokens.SPACING_LG)
        resumo_frame.setLayout(rl)

        self._cards = {}
        for titulo, chave in [("Logins hoje", "logins"), ("Tentativas falhas", "falhas"), ("Alterações hoje", "alteracoes")]:
            card = QFrame()
            card.setStyleSheet(f"QFrame {{ background-color: {colors['bg_primary']}; border-radius: {tokens.RADIUS_MD}px; border: 1px solid {colors['border_subtle']}; }}")
            cardl = QVBoxLayout()
            cardl.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
            card.setLayout(cardl)
            t = QLabel(titulo)
            t.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            t.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            cardl.addWidget(t)
            v = QLabel("0")
            v.setFont(theme_manager.get_font(tokens.FONT_SIZE_XL, bold=True))
            v.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
            cardl.addWidget(v)
            self._cards[chave] = v
            rl.addWidget(card)
        cl.addWidget(resumo_frame)

        # Filtros
        filtros = ModernCard(padding=tokens.SPACING_LG)
        fr = QHBoxLayout()
        fr.setSpacing(tokens.SPACING_MD)

        fr.addWidget(self._lbl_filtro("Ação:"))
        self.combo_acao = QComboBox()
        self.combo_acao.addItems(["Todas"])
        self.combo_acao.setMinimumHeight(38)
        self.combo_acao.setMinimumWidth(160)
        fr.addWidget(self.combo_acao)

        fr.addWidget(self._lbl_filtro("Módulo:"))
        self.combo_modulo = QComboBox()
        self.combo_modulo.addItems(["Todos", "auth", "usuarios", "viagens", "financeiro", "sistema"])
        self.combo_modulo.setMinimumHeight(38)
        self.combo_modulo.setMinimumWidth(120)
        fr.addWidget(self.combo_modulo)

        fr.addWidget(self._lbl_filtro("De:"))
        self.entry_data_inicio = QLineEdit()
        self.entry_data_inicio.setPlaceholderText("YYYY-MM-DD")
        self.entry_data_inicio.setFixedWidth(110)
        self.entry_data_inicio.setMinimumHeight(38)
        self._aplicar_estilo_entry(self.entry_data_inicio)
        fr.addWidget(self.entry_data_inicio)

        fr.addWidget(self._lbl_filtro("Até:"))
        self.entry_data_fim = QLineEdit()
        self.entry_data_fim.setPlaceholderText("YYYY-MM-DD")
        self.entry_data_fim.setFixedWidth(110)
        self.entry_data_fim.setMinimumHeight(38)
        self._aplicar_estilo_entry(self.entry_data_fim)
        fr.addWidget(self.entry_data_fim)

        fr.addStretch()

        btn_exportar = ModernButton("Exportar CSV", ButtonStyle.SUCCESS)
        btn_exportar.clicked.connect(self._exportar_csv)
        fr.addWidget(btn_exportar)

        btn_buscar = ModernButton("Buscar", ButtonStyle.PRIMARY)
        btn_buscar.clicked.connect(self._buscar)
        fr.addWidget(btn_buscar)

        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Tabela
        card = ModernCard(padding=tokens.SPACING_XL)
        colunas = [
            ("ID", 50), ("Data/Hora", 150), ("Usuário", 140), ("Ação", 150),
            ("Módulo", 100), ("Registro Afetado", 140), ("Detalhes", 250),
        ]
        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setMinimumHeight(350)

        h = self.tabela.horizontalHeader()
        for i, (_, w) in enumerate(colunas):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.setStyleSheet(f"""
            QTableWidget {{ background-color: {colors['bg_secondary']}; alternate-background-color: {colors['table_row_odd']};
                gridline-color: {colors['border_subtle']}; border: 1px solid {colors['border_subtle']};
                border-radius: {tokens.RADIUS_MD}px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QTableWidget::item {{ padding: 6px 10px; border: none; color: {colors['text_primary']}; }}
            QTableWidget::item:selected {{ background-color: {colors['violet_soft']}; }}
            QHeaderView::section {{ background-color: {colors['table_header_bg']}; color: {colors['table_header_text']};
                padding: 8px; border: none; border-bottom: 2px solid {colors['border_default']};
                font-weight: 700; font-size: {tokens.FONT_SIZE_SM}px; }}
        """)

        card.add_widget(self.tabela)

        # Paginação
        pag = QHBoxLayout()
        pag.setSpacing(tokens.SPACING_MD)

        self.btn_anterior = ModernButton("< Anterior", ButtonStyle.SECONDARY)
        self.btn_anterior.clicked.connect(self._pagina_anterior)
        pag.addWidget(self.btn_anterior)

        self.label_pagina = QLabel("Página 1 de 1")
        self.label_pagina.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD, bold=True))
        self.label_pagina.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        pag.addWidget(self.label_pagina)

        self.btn_proximo = ModernButton("Próximo >", ButtonStyle.SECONDARY)
        self.btn_proximo.clicked.connect(self._pagina_proxima)
        pag.addWidget(self.btn_proximo)

        pag.addStretch()

        self.label_total = QLabel("0 registros")
        self.label_total.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        self.label_total.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        pag.addWidget(self.label_total)

        card.add_layout(pag)
        cl.addWidget(card)

    def _lbl_filtro(self, texto) -> QLabel:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        lbl = QLabel(texto)
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        return lbl

    def _aplicar_estilo_entry(self, entry: QLineEdit):
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        entry.setStyleSheet(f"""
            QLineEdit {{ background-color: {colors['bg_tertiary']}; color: {colors['text_primary']};
                border: 1.5px solid {colors['border_subtle']}; border-radius: {tokens.RADIUS_MD}px;
                padding: 6px 10px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {colors['violet']}; }}
        """)

    def _get_filtros(self) -> dict:
        acao = self.combo_acao.currentText()
        modulo = self.combo_modulo.currentText()
        data_inicio = self.entry_data_inicio.text().strip()
        data_fim = self.entry_data_fim.text().strip()

        return {
            "acao": acao if acao != "Todas" else None,
            "modulo": modulo if modulo != "Todos" else None,
            "data_inicio": data_inicio or None,
            "data_fim": data_fim or None,
        }

    def _buscar(self):
        self._pagina_atual = 0
        self._carregar_dados()

    def _carregar_dados(self):
        filtros = self._get_filtros()
        offset = self._pagina_atual * _POR_PAGINA

        def tarefa():
            try:
                dados = auditoria_service.listar(
                    acao=filtros["acao"],
                    modulo=filtros["modulo"],
                    data_inicio=filtros["data_inicio"],
                    data_fim=filtros["data_fim"],
                    limite=_POR_PAGINA,
                    offset=offset,
                )
                total = auditoria_service.contar_total(
                    acao=filtros["acao"],
                    modulo=filtros["modulo"],
                    data_inicio=filtros["data_inicio"],
                    data_fim=filtros["data_fim"],
                )
                stats = auditoria_service.estatisticas_hoje()
                QTimer.singleShot(0, lambda: self._aplicar_dados(dados, total, stats))
            except Exception as e:
                logger.error(f"Erro ao carregar auditoria: {e}")
                QTimer.singleShot(0, lambda: self._aplicar_dados([], 0, {}))

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_dados(self, dados, total, stats):
        self._dados = dados
        self._total_registros = total

        # Tabela
        self.tabela.setRowCount(0)
        for row_data in dados:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                row_data["id"],
                row_data["criado_em"],
                row_data["usuario_nome"],
                row_data["acao"],
                row_data["modulo"],
                row_data["registro_afetado"],
                row_data["detalhes"],
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

        # Paginação
        total_paginas = max(1, (self._total_registros + _POR_PAGINA - 1) // _POR_PAGINA)
        self.label_pagina.setText(f"Página {self._pagina_atual + 1} de {total_paginas}")
        self.label_total.setText(f"{self._total_registros} registros")

        self.btn_anterior.setEnabled(self._pagina_atual > 0)
        self.btn_proximo.setEnabled(
            (self._pagina_atual + 1) * _POR_PAGINA < self._total_registros
        )

        # Cards
        self._cards["logins"].setText(str(stats.get("logins", 0)))
        self._cards["falhas"].setText(str(stats.get("tentativas_falhas", 0)))
        self._cards["alteracoes"].setText(str(stats.get("alteracoes", 0)))

    def _pagina_anterior(self):
        if self._pagina_atual > 0:
            self._pagina_atual -= 1
            self._carregar_dados()

    def _pagina_proxima(self):
        self._pagina_atual += 1
        self._carregar_dados()

    def _exportar_csv(self):
        if not self._dados:
            QMessageBox.warning(self, "Atenção", "Nenhum dado para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Auditoria",
            f"auditoria_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv",
            "CSV (*.csv)",
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Data/Hora", "Usuário", "Ação",
                    "Módulo", "Registro", "Detalhes",
                ])
                for row in self._dados:
                    writer.writerow([
                        row["id"], row["criado_em"], row["usuario_nome"],
                        row["acao"], row["modulo"], row["registro_afetado"],
                        row["detalhes"],
                    ])
            QMessageBox.information(self, "Sucesso", f"Auditoria exportada:\n{caminho}")
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))
