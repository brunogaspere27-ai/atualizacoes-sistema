"""
Tela Histórico de Viagens - CW Transportadora - PySide6
Acompanhamento, finalização e visualização de viagens.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QAbstractItemView, QSizePolicy,
    QDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from services.historico_service import historico_service
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWInput, CWTable
from utils.components import ModernCard, ModernButton, ButtonStyle, ModernTable
from utils.helpers import formatar_moeda


class TelaHistorico(QWidget):
    """Tela de histórico de viagens em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viagens_ids: dict = {}
        self._setup_ui()
        self._carregar_viagens()

    def _setup_ui(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {cw_theme.colors['bg_primary']}; border: none; }}")
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {cw_theme.colors['bg_primary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_2XL)
        cl.setSpacing(cw_theme.spacing.SPACING_XL)
        content.setLayout(cl)
        scroll.setWidget(content)

        # Cards de resumo
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_secondary']}; border-radius: {cw_theme.radius.XL}px; border: none; }}")
        rl = QHBoxLayout()
        rl.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_MD)
        rl.setSpacing(cw_theme.spacing.SPACING_LG)
        resumo_frame.setLayout(rl)

        self._resumo = {}
        for titulo, chave, cor in [
            ("VIAGENS", "total", cw_theme.colors["text_primary"]),
            ("NOTAS", "notas", cw_theme.colors["text_primary"]),
            ("FRETE TOTAL", "frete", cw_theme.colors["success"]),
            ("PESO TOTAL", "peso", cw_theme.colors["rose"]),
        ]:
            card = QFrame()
            card.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_primary']}; border-radius: {cw_theme.radius.MD}px; border: none; }}")
            cardl = QVBoxLayout()
            cardl.setContentsMargins(cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_SM, cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_SM)
            card.setLayout(cardl)
            t = QLabel(titulo)
            t.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
            t.setStyleSheet(f"color: {cw_theme.colors['text_tertiary']}; background: transparent;")
            cardl.addWidget(t)
            v = QLabel("0")
            v.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
            v.setStyleSheet(f"color: {cor}; background: transparent;")
            cardl.addWidget(v)
            self._resumo[chave] = v
            rl.addWidget(card)
        cl.addWidget(resumo_frame)

        # Tabela
        card = ModernCard(padding=cw_theme.spacing.SPACING_XL)

        row = QHBoxLayout()
        titulo_tbl = QLabel("Lista de Viagens Criadas")
        titulo_tbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        titulo_tbl.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
        row.addWidget(titulo_tbl)
        row.addStretch()
        btn_atualizar = ModernButton("🔄 Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_viagens)
        row.addWidget(btn_atualizar)
        card.add_layout(row)

        colunas = [
            ("Viagem", 70), ("Data Saída", 130), ("Caminhão", 200),
            ("Placa", 120), ("Motorista", 160), ("Status", 110),
            ("Notas", 70), ("Peso", 120), ("Frete", 120),
        ]
        self.tabela = ModernTable()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setMinimumHeight(400)

        h = self.tabela.horizontalHeader()
        for i, (_, w) in enumerate(colunas):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.cellDoubleClicked.connect(self._clique_acao_viagem)
        card.add_widget(self.tabela)

        # Botões de ação
        acao_row = QHBoxLayout()
        acao_row.addStretch()
        btn_notas = ModernButton("Ver Notas", ButtonStyle.PRIMARY, icon_name="eye")
        btn_notas.clicked.connect(self._abrir_notas_viagem)
        acao_row.addWidget(btn_notas)
        btn_finalizar = ModernButton("Finalizar", ButtonStyle.SUCCESS, icon_name="check_circle")
        btn_finalizar.clicked.connect(self._finalizar_viagem)
        acao_row.addWidget(btn_finalizar)
        card.add_layout(acao_row)

        cl.addWidget(card)

    def _carregar_viagens(self):
        self.tabela.setRowCount(0)
        self.viagens_ids = {}

        viagens = historico_service.listar_viagens()
        total_notas = total_frete = total_peso = 0

        for viagem in viagens:
            vid, data_saida, modelo, placa, motorista, status, peso_total, frete_total, qtd_notas = viagem
            peso_total = peso_total or 0
            frete_total = frete_total or 0
            qtd_notas = qtd_notas or 0
            total_notas += qtd_notas
            total_frete += frete_total
            total_peso += peso_total

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                f"#{vid}", data_saida, modelo or "-", placa or "-",
                motorista or "-", status or "-", str(qtd_notas),
                f"{peso_total:,.2f} kg", f"R$ {frete_total:,.2f}",
            ]
            for col, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
                self.tabela.setItem(row, col, item)
            self.viagens_ids[row] = vid

        self._resumo["total"].setText(str(len(viagens)))
        self._resumo["notas"].setText(str(total_notas))
        self._resumo["frete"].setText(f"R$ {total_frete:,.2f}")
        self._resumo["peso"].setText(f"{total_peso:,.2f} kg")

    def _get_viagem_selecionada(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma viagem na tabela.")
            return None
        return self.viagens_ids.get(row)

    def _clique_acao_viagem(self, row, col):
        vid = self.viagens_ids.get(row)
        if not vid:
            return
        # Duplo clique na coluna Status - finalizar
        if col == 5:
            self._finalizar_viagem()

    def _finalizar_viagem(self):
        vid = self._get_viagem_selecionada()
        if not vid:
            return

        row = self.tabela.currentRow()
        status = self.tabela.item(row, 5).text() if self.tabela.item(row, 5) else ""
        if status == "Finalizada":
            QMessageBox.information(self, "Viagem finalizada", "Essa viagem já está finalizada.")
            return

        resp = QMessageBox.question(self, "Finalizar viagem", f"Deseja finalizar a viagem #{vid}?")
        if resp != QMessageBox.StandardButton.Yes:
            return

        data_retorno = datetime.now().strftime("%d/%m/%Y %H:%M")
        historico_service.finalizar_viagem(vid, data_retorno)
        QMessageBox.information(self, "Sucesso", f"Viagem #{vid} finalizada com sucesso!")
        self._carregar_viagens()

    def _abrir_notas_viagem(self):
        vid = self._get_viagem_selecionada()
        if not vid:
            return

        notas = historico_service.listar_notas_da_viagem(vid)
        detalhes = historico_service.buscar_detalhes_viagem(vid)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Notas da Viagem #{vid}")
        dlg.resize(1000, 600)
        layout = QVBoxLayout()
        dlg.setLayout(layout)

        colors = cw_theme.colors
        tokens = cw_theme.spacing

        titulo = QLabel(f"DETALHES DA VIAGEM #{vid}")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {cw_theme.colors['primary']}; background: transparent;")
        layout.addWidget(titulo)

        if detalhes:
            id_v, data_saida, data_retorno, motorista, status_v, peso_tb, frete_tb, modelo, placa, capacidade = detalhes
            capacidade = capacidade or 0
            peso_tb = peso_tb or 0
            uso = (peso_tb / capacidade * 100) if capacidade > 0 else 0

            info_frame = QFrame()
            info_frame.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_secondary']}; border-radius: {cw_theme.radius.XL}px; }}")
            il = QHBoxLayout()
            il.setContentsMargins(cw_theme.spacing.SPACING_LG, cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_LG, cw_theme.spacing.SPACING_MD)
            info_frame.setLayout(il)

            for t, v in [
                ("CAMINHÃO", f"{modelo or '-'} | {placa or '-'}"),
                ("MOTORISTA", motorista or "-"),
                ("SAÍDA", data_saida or "-"),
                ("RETORNO", data_retorno or "-"),
                ("STATUS", status_v or "-"),
                ("CAPACIDADE", f"{uso:.1f}% usada"),
            ]:
                f = QFrame()
                f.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_primary']}; border-radius: {cw_theme.radius.MD}px; }}")
                fl = QVBoxLayout()
                fl.setContentsMargins(cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_SM, cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_SM)
                f.setLayout(fl)
                tl = QLabel(t)
                tl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS, bold=True))
                tl.setStyleSheet(f"color: {cw_theme.colors['text_tertiary']}; background: transparent;")
                fl.addWidget(tl)
                vl = QLabel(v)
                vl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
                vl.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
                fl.addWidget(vl)
                il.addWidget(f)

            layout.addWidget(info_frame)

        # Tabela de notas
        colunas = ["CT-e", "Remetente", "Cliente", "Origem", "Destino", "Frete", "Peso", "Status"]
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setAlternatingRowColors(False)
        tabela.verticalHeader().setVisible(False)

        total_frete = total_peso = 0
        for nota in notas:
            id_n, numero_cte, remetente, destinatario, origem, destino, valor_frete, peso, status = nota
            valor_frete = valor_frete or 0
            peso = peso or 0
            total_frete += valor_frete
            total_peso += peso
            row = tabela.rowCount()
            tabela.insertRow(row)
            valores = [numero_cte, remetente, destinatario, origem, destino,
                       f"R$ {valor_frete:,.2f}", f"{peso:,.2f} kg", status]
            for col, texto in enumerate(valores):
                tabela.setItem(row, col, QTableWidgetItem(texto))

        tabela.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(tabela)

        # Resumo
        resumo_lbl = QLabel(f"Notas: {len(notas)}  |  Peso: {total_peso:,.2f} kg  |  Frete: R$ {total_frete:,.2f}")
        resumo_lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD, bold=True))
        resumo_lbl.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: {cw_theme.colors['bg_secondary']}; padding: 12px; border-radius: {cw_theme.radius.MD}px;")
        layout.addWidget(resumo_lbl)

        dlg.exec()
