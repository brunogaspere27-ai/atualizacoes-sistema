"""
Tela Contas a Pagar e Receber - CW Transportadora - PySide6
Controle de vencimentos, pagamentos, recebimentos e fluxo financeiro.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea, QFormLayout,
)
from PySide6.QtCore import Qt, QTimer

from services.financeiro_service import financeiro_service
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWInput, CWTable
from utils.components import ModernCard, ModernInput, ModernButton, ButtonStyle, ModernTable
from utils.helpers import formatar_moeda, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaContas(QWidget):
    """Tela de contas a pagar e receber em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._geracao = 0
        self._setup_ui()
        self._carregar_contas()

    def _setup_ui(self):
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

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

        # Filtros
        filtros = ModernCard(padding=cw_theme.spacing.SPACING_LG)
        fr = QHBoxLayout()
        fr.setSpacing(cw_theme.spacing.SPACING_MD)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setMinimumHeight(cw_theme.spacing.SPACING_XL * 2 + cw_theme.spacing.SPACING_SM)
        self.combo_periodo.setMinimumWidth(110)
        self.combo_periodo.currentTextChanged.connect(lambda: self._carregar_contas())
        fr.addWidget(self.combo_periodo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.setMinimumHeight(cw_theme.spacing.SPACING_XL * 2 + cw_theme.spacing.SPACING_SM)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_contas())
        fr.addWidget(self.combo_mes)

        self.entry_ano = ModernInput(datetime.now().strftime("%Y"))
        self.entry_ano.setMinimumWidth(80)
        self.entry_ano.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_ano)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Pagar", "Receber"])
        self.combo_tipo.setMinimumHeight(cw_theme.spacing.SPACING_XL * 2 + cw_theme.spacing.SPACING_SM)
        self.combo_tipo.setMinimumWidth(110)
        self.combo_tipo.currentTextChanged.connect(lambda: self._carregar_contas())
        fr.addWidget(self.combo_tipo)

        self.entry_busca = ModernInput("Buscar descrição, pessoa ou categoria...")
        self.entry_busca.setMinimumWidth(220)
        self.entry_busca.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_busca)

        fr.addStretch()

        btn_novo = ModernButton("+ Nova Conta", ButtonStyle.PRIMARY)
        btn_novo.clicked.connect(self._abrir_modal)
        fr.addWidget(btn_novo)

        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Resumo
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_secondary']}; border-radius: {cw_theme.radius.XL}px; border: none; }}")
        rl = QHBoxLayout()
        rl.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_MD, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_MD)
        rl.setSpacing(cw_theme.spacing.SPACING_LG)
        resumo_frame.setLayout(rl)

        self._resumo = {}
        for titulo, chave, cor in [
            ("A receber", "receber", cw_theme.colors["success"]),
            ("A pagar", "pagar", cw_theme.colors["rose"]),
            ("Pago/Recebido", "pago", cw_theme.colors["sky"]),
            ("Saldo previsto", "saldo", cw_theme.colors["text_primary"]),
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
            v = QLabel("R$ 0,00")
            v.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
            v.setStyleSheet(f"color: {cor}; background: transparent;")
            cardl.addWidget(v)
            self._resumo[chave] = v
            rl.addWidget(card)
        cl.addWidget(resumo_frame)

        # Tabela
        card = ModernCard(padding=cw_theme.spacing.SPACING_XL)
        colunas = [
            ("ID", 45), ("Tipo", 70), ("Descrição", 220), ("Cliente/Forn.", 190),
            ("Categoria", 110), ("Valor", 110), ("Vencimento", 110),
        ]
        self.tabela = ModernTable()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setMinimumHeight(350)

        h = self.tabela.horizontalHeader()
        for i, (_, w) in enumerate(colunas):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.cellDoubleClicked.connect(self._editar_conta)
        card.add_widget(self.tabela)

        # Botões
        br = QHBoxLayout()
        br.addStretch()
        btn_pago = ModernButton("Marcar Pago/Recebido", ButtonStyle.SUCCESS)
        btn_pago.clicked.connect(self._marcar_pago)
        br.addWidget(btn_pago)
        btn_excluir = ModernButton("Excluir", ButtonStyle.DANGER)
        btn_excluir.clicked.connect(self._excluir)
        br.addWidget(btn_excluir)
        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_contas)
        br.addWidget(btn_atualizar)
        card.add_layout(br)

        cl.addWidget(card)

    def _debounce_carregar(self):
        if hasattr(self, '_debounce_timer') and self._debounce_timer:
            self._debounce_timer.stop()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._carregar_contas)
        self._debounce_timer.start(300)

    def _carregar_contas(self):
        self._geracao += 1
        geracao = self._geracao
        tipo_periodo = self.combo_periodo.currentText()
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()
        filtro_tipo = self.combo_tipo.currentText()
        busca = self.entry_busca.text().strip()

        def tarefa():
            try:
                dados = financeiro_service.listar_contas(tipo_periodo, mes, ano, filtro_tipo, busca)
                QTimer.singleShot(0, lambda: self._aplicar_dados(dados, geracao))
            except Exception as e:
                logger.error(f"Erro ao carregar: {e}")
                QTimer.singleShot(0, lambda: self._aplicar_dados([], geracao))

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_dados(self, dados, geracao):
        if geracao != self._geracao:
            return
        self.tabela.setRowCount(0)
        total_receber = 0
        total_pagar = 0
        total_pago = 0

        hoje = datetime.now().date()

        for linha in dados:
            conta_id, tipo, descricao, pessoa, categoria, valor, vencimento, pagamento, status, observacao = linha
            valor = float(valor or 0)
            status_tela = status or "Pendente"

            if status_tela == "Pendente":
                venc_data = self._converter_data(vencimento)
                if venc_data and venc_data < hoje:
                    status_tela = "Atrasado"

            if tipo == "Receber" and status_tela not in ["Recebido", "Cancelado"]:
                total_receber += valor
            if tipo == "Pagar" and status_tela not in ["Pago", "Cancelado"]:
                total_pagar += valor
            if status_tela in ["Pago", "Recebido"]:
                total_pago += valor

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                conta_id, tipo, descricao or "", pessoa or "",
                categoria or "", formatar_moeda(valor),
                vencimento or "", pagamento or "", status_tela, observacao or "",
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

        saldo = total_receber - total_pagar
        self._resumo["receber"].setText(formatar_moeda(total_receber))
        self._resumo["pagar"].setText(formatar_moeda(total_pagar))
        self._resumo["pago"].setText(formatar_moeda(total_pago))
        self._resumo["saldo"].setText(formatar_moeda(saldo))

    def _converter_data(self, texto):
        try:
            return datetime.strptime(str(texto), "%d/%m/%Y").date()
        except Exception:
            return None

    def _abrir_modal(self, dados=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Conta")
        dlg.resize(560, 680)

        colors = cw_theme.colors
        tokens = cw_theme.spacing

        layout = QVBoxLayout()
        layout.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL)
        layout.setSpacing(cw_theme.spacing.SPACING_MD)
        dlg.setLayout(layout)

        titulo = QLabel("Cadastro de Conta")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {cw_theme.colors['text_primary']};")
        layout.addWidget(titulo)

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_secondary']}; border-radius: {cw_theme.radius.XL}px; }}")
        fl = QFormLayout()
        fl.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL)
        fl.setSpacing(cw_theme.spacing.SPACING_SM)
        frame.setLayout(fl)

        input_style = f"""
            QLineEdit {{ background-color: {cw_theme.colors['bg_primary']}; color: {cw_theme.colors['text_primary']};
                border: 1.5px solid {cw_theme.colors['border_subtle']}; border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px; font-size: {cw_theme.typography.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {cw_theme.colors['info']}; }}
        """
        combo_style = input_style.replace("QLineEdit", "QComboBox")

        # Tipo
        combo_tipo = QComboBox()
        combo_tipo.addItems(["Pagar", "Receber"])
        combo_tipo.setMinimumHeight(40)
        combo_tipo.setStyleSheet(combo_style)
        fl.addRow(self._lbl("Tipo"), combo_tipo)

        # Descrição
        entry_desc = QLineEdit()
        entry_desc.setStyleSheet(input_style)
        fl.addRow(self._lbl("Descrição"), entry_desc)

        # Pessoa
        entry_pessoa = QLineEdit()
        entry_pessoa.setStyleSheet(input_style)
        fl.addRow(self._lbl("Cliente / Fornecedor"), entry_pessoa)

        # Categoria
        combo_cat = QComboBox()
        combo_cat.addItems([
            "Frete", "Combustível", "Manutenção", "Folha", "Fornecedor",
            "Imposto", "Aluguel", "Pedágio", "Cliente", "Outro",
        ])
        combo_cat.setMinimumHeight(40)
        combo_cat.setStyleSheet(combo_style)
        fl.addRow(self._lbl("Categoria"), combo_cat)

        # Valor
        entry_valor = QLineEdit()
        entry_valor.setStyleSheet(input_style)
        fl.addRow(self._lbl("Valor"), entry_valor)

        # Vencimento
        entry_venc = QLineEdit()
        entry_venc.setText(datetime.now().strftime("%d/%m/%Y"))
        entry_venc.setStyleSheet(input_style)
        fl.addRow(self._lbl("Vencimento"), entry_venc)

        # Pagamento
        entry_pag = QLineEdit()
        entry_pag.setStyleSheet(input_style)
        fl.addRow(self._lbl("Data pagamento/recebimento"), entry_pag)

        # Status
        combo_status = QComboBox()
        combo_status.addItems(["Pendente", "Pago", "Recebido", "Atrasado", "Cancelado"])
        combo_status.setMinimumHeight(40)
        combo_status.setStyleSheet(combo_style)
        fl.addRow(self._lbl("Status"), combo_status)

        # Observação
        entry_obs = QLineEdit()
        entry_obs.setStyleSheet(input_style)
        fl.addRow(self._lbl("Observação"), entry_obs)

        # Preencher se edição
        conta_id = None
        if dados:
            conta_id = dados[0]
            combo_tipo.setCurrentText(dados[1] or "Pagar")
            entry_desc.setText(dados[2] or "")
            entry_pessoa.setText(dados[3] or "")
            combo_cat.setCurrentText(dados[4] or "Outro")
            entry_valor.setText(str(dados[5] or "").replace(".", ","))
            entry_venc.setText(dados[6] or "")
            entry_pag.setText(dados[7] or "")
            combo_status.setCurrentText(dados[8] or "Pendente")
            entry_obs.setText(dados[9] or "")

        layout.addWidget(frame)

        def salvar():
            if not entry_desc.text().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe a descrição.")
                return
            if parse_numero(entry_valor.text()) <= 0:
                QMessageBox.warning(dlg, "Atenção", "Informe o valor.")
                return

            valores = (
                combo_tipo.currentText(),
                entry_desc.text().strip(),
                entry_pessoa.text().strip(),
                combo_cat.currentText(),
                parse_numero(entry_valor.text()),
                entry_venc.text().strip(),
                entry_pag.text().strip(),
                combo_status.currentText(),
                entry_obs.text().strip(),
            )
            financeiro_service.salvar_conta(conta_id, valores)
            dlg.accept()
            self._carregar_contas()
            QMessageBox.information(dlg, "Sucesso", "Conta salva com sucesso!")

        btn_salvar = ModernButton("Salvar Conta", ButtonStyle.SUCCESS)
        btn_salvar.clicked.connect(salvar)
        layout.addWidget(btn_salvar)

        dlg.exec()

    def _editar_conta(self, row, col):
        item = self.tabela.item(row, 0)
        if not item:
            return
        conta_id = item.text()
        dados = financeiro_service.obter_conta(conta_id)
        if dados:
            self._abrir_modal(dados)

    def _marcar_pago(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma conta.")
            return

        item_id = self.tabela.item(row, 0)
        item_tipo = self.tabela.item(row, 1)
        if not item_id or not item_tipo:
            return

        conta_id = item_id.text()
        tipo = item_tipo.text()
        novo_status = "Recebido" if tipo == "Receber" else "Pago"
        data_pagamento = datetime.now().strftime("%d/%m/%Y")

        financeiro_service.marcar_pago(conta_id, tipo, data_pagamento)
        self._carregar_contas()

    def _excluir(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma conta.")
            return

        item = self.tabela.item(row, 0)
        if not item:
            return
        conta_id = item.text()

        resp = QMessageBox.question(self, "Confirmar", "Deseja excluir esta conta?")
        if resp != QMessageBox.StandardButton.Yes:
            return

        financeiro_service.excluir_conta(conta_id)
        self._carregar_contas()

    def _lbl(self, texto) -> QLabel:
        colors = cw_theme.colors
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"color: {cw_theme.colors['text_secondary']}; font-weight: 600; background: transparent;")
        return lbl
