"""
Tela Funcionários - CW Transportadora - PySide6
Cadastro, folha de pagamento e controle de horas extras.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea, QFormLayout, QStackedWidget,
)
from PySide6.QtCore import Qt, QTimer

from services.funcionarios_service import funcionarios_service
from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ModernCard
from utils.helpers import formatar_moeda, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaFuncionarios(QWidget):
    """Tela de funcionários em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {colors['bg_primary']};")
        root.addWidget(self.stack)

        # Página 0: Funcionários
        self.stack.addWidget(self._build_pagina_funcionarios())
        # Página 1: Folha do Mês
        self.stack.addWidget(self._build_pagina_folha())

        self.stack.setCurrentIndex(0)

    def _build_pagina_funcionarios(self) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        w = QWidget()
        cl = QVBoxLayout()
        cl.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        cl.setSpacing(tokens.SPACING_XL)
        w.setLayout(cl)

        # Botões
        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_folha = ModernButton("Ver Folha do Mês", ButtonStyle.SUCCESS)
        btn_folha.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        botoes.addWidget(btn_folha)
        btn_novo = ModernButton("+ Criar Funcionário", ButtonStyle.PRIMARY)
        btn_novo.clicked.connect(lambda: self._abrir_modal_funcionario())
        botoes.addWidget(btn_novo)
        cl.addLayout(botoes)

        # Busca
        filtros = ModernCard(padding=tokens.SPACING_LG)
        fr = QHBoxLayout()
        self.entry_busca = QLineEdit()
        self.entry_busca.setPlaceholderText("Buscar funcionário...")
        self.entry_busca.setMinimumHeight(40)
        self.entry_busca.setMinimumWidth(300)
        self.entry_busca.textChanged.connect(lambda: self._carregar_funcionarios())
        fr.addWidget(self.entry_busca)
        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_funcionarios)
        fr.addWidget(btn_atualizar)
        fr.addStretch()
        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Tabela
        card = ModernCard(padding=tokens.SPACING_XL)
        colunas = [
            ("ID", 50), ("Funcionário", 230), ("Cargo", 160), ("Telefone", 130),
            ("Admissão", 110), ("Salário", 120), ("Vale Refeição", 120), ("Status", 90),
        ]
        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setMinimumHeight(350)

        h = self.tabela.horizontalHeader()
        for i, (_, w_val) in enumerate(colunas):
            h.resizeSection(i, w_val)
        h.setStretchLastSection(True)

        self.tabela.setStyleSheet(self._tabela_style())
        self.tabela.cellDoubleClicked.connect(lambda: self._editar_selecionado())
        card.add_widget(self.tabela)

        br = QHBoxLayout()
        br.addStretch()
        btn_editar = ModernButton("Editar Cadastro", ButtonStyle.PRIMARY)
        btn_editar.clicked.connect(self._editar_selecionado)
        br.addWidget(btn_editar)
        btn_excluir = ModernButton("Excluir", ButtonStyle.DANGER)
        btn_excluir.clicked.connect(self._excluir_funcionario)
        br.addWidget(btn_excluir)
        card.add_layout(br)
        cl.addWidget(card)

        self._carregar_funcionarios()
        return w

    def _build_pagina_folha(self) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        w = QWidget()
        cl = QVBoxLayout()
        cl.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        cl.setSpacing(tokens.SPACING_XL)
        w.setLayout(cl)

        # Topo com voltar
        topo = QHBoxLayout()
        btn_voltar = ModernButton("← Voltar", ButtonStyle.SECONDARY)
        btn_voltar.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        topo.addWidget(btn_voltar)
        titulo = QLabel("Folha do Mês")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        topo.addWidget(titulo)
        topo.addStretch()
        cl.addLayout(topo)

        # Filtros
        filtros = ModernCard(padding=tokens.SPACING_LG)
        fr = QHBoxLayout()
        fr.setSpacing(tokens.SPACING_MD)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.setMinimumHeight(40)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_folha_mes())
        fr.addWidget(self.combo_mes)

        self.entry_ano = QLineEdit(datetime.now().strftime("%Y"))
        self.entry_ano.setFixedWidth(80)
        self.entry_ano.setMinimumHeight(40)
        self.entry_ano.textChanged.connect(lambda: self._carregar_folha_mes())
        fr.addWidget(self.entry_ano)

        self.entry_busca_folha = QLineEdit()
        self.entry_busca_folha.setPlaceholderText("Buscar na folha...")
        self.entry_busca_folha.setMinimumHeight(40)
        self.entry_busca_folha.setMinimumWidth(220)
        self.entry_busca_folha.textChanged.connect(lambda: self._carregar_folha_mes())
        fr.addWidget(self.entry_busca_folha)

        btn_gerar = ModernButton("Gerar / Atualizar Folha", ButtonStyle.SUCCESS)
        btn_gerar.clicked.connect(self._gerar_folha_todos)
        fr.addWidget(btn_gerar)

        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_folha_mes)
        fr.addWidget(btn_atualizar)

        fr.addStretch()
        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Resumo
        resumo_frame = QFrame()
        resumo_frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; border: 1px solid {colors['border_subtle']}; }}")
        rl = QHBoxLayout()
        rl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_MD, tokens.SPACING_XL, tokens.SPACING_MD)
        rl.setSpacing(tokens.SPACING_LG)
        resumo_frame.setLayout(rl)

        self._resumo = {}
        for titulo, chave in [("Funcionários", "func"), ("Horas extras", "horas"), ("Total hora extra", "valor_hora"), ("Total folha", "total")]:
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
            self._resumo[chave] = v
            rl.addWidget(card)
        cl.addWidget(resumo_frame)

        # Tabela
        card = ModernCard(padding=tokens.SPACING_XL)
        colunas = [
            ("ID", 50), ("Funcionário", 210), ("Cargo", 150), ("Salário", 110),
            ("Vale", 100), ("Horas", 80), ("Valor Hora", 100), ("Total H.Extra", 120),
            ("Outros", 100), ("Total", 120), ("Status", 80),
        ]
        self.tabela_folha = QTableWidget(0, len(colunas))
        self.tabela_folha.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela_folha.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_folha.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_folha.setAlternatingRowColors(True)
        self.tabela_folha.verticalHeader().setVisible(False)
        self.tabela_folha.setMinimumHeight(350)

        h = self.tabela_folha.horizontalHeader()
        for i, (_, w_val) in enumerate(colunas):
            h.resizeSection(i, w_val)
        h.setStretchLastSection(True)

        self.tabela_folha.setStyleSheet(self._tabela_style())
        self.tabela_folha.cellDoubleClicked.connect(lambda: self._abrir_modal_hora_extra())
        card.add_widget(self.tabela_folha)

        br = QHBoxLayout()
        br.addStretch()
        btn_hora = ModernButton("Lançar Hora Extra", ButtonStyle.PRIMARY)
        btn_hora.clicked.connect(self._abrir_modal_hora_extra)
        br.addWidget(btn_hora)
        btn_remover = ModernButton("Remover da Folha", ButtonStyle.DANGER)
        btn_remover.clicked.connect(self._remover_da_folha)
        br.addWidget(btn_remover)
        card.add_layout(br)
        cl.addWidget(card)

        self._carregar_folha_mes()
        return w

    def _tabela_style(self) -> str:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        return f"""
            QTableWidget {{ background-color: {colors['bg_secondary']}; alternate-background-color: {colors['table_row_odd']};
                gridline-color: {colors['border_subtle']}; border: 1px solid {colors['border_subtle']};
                border-radius: {tokens.RADIUS_MD}px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QTableWidget::item {{ padding: 6px 10px; border: none; color: {colors['text_primary']}; }}
            QTableWidget::item:selected {{ background-color: {colors['sky_soft']}; }}
            QHeaderView::section {{ background-color: {colors['table_header_bg']}; color: {colors['table_header_text']};
                padding: 8px; border: none; border-bottom: 2px solid {colors['border_default']};
                font-weight: 700; font-size: {tokens.FONT_SIZE_SM}px; }}
        """

    def _carregar_funcionarios(self):
        self.tabela.setRowCount(0)
        busca = self.entry_busca.text().strip()

        def tarefa():
            try:
                dados = funcionarios_service.listar_funcionarios(busca)
                QTimer.singleShot(0, lambda: self._aplicar_funcionarios(dados))
            except Exception as e:
                logger.error(f"Erro: {e}")

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_funcionarios(self, dados):
        self.tabela.setRowCount(0)
        for linha in dados:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                linha[0], linha[1], linha[2] or "", linha[3] or "",
                linha[4] or "", formatar_moeda(linha[5]),
                formatar_moeda(linha[6]), linha[7] or "Ativo",
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

    def _carregar_folha_mes(self):
        self.tabela_folha.setRowCount(0)
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()
        busca = self.entry_busca_folha.text().strip()
        if not ano:
            return

        def tarefa():
            try:
                dados = funcionarios_service.listar_folha_mes(mes, ano, busca)
                QTimer.singleShot(0, lambda: self._aplicar_folha(dados))
            except Exception as e:
                logger.error(f"Erro: {e}")

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_folha(self, dados):
        self.tabela_folha.setRowCount(0)
        total_horas = 0
        total_hora_extra = 0
        total_folha = 0

        for linha in dados:
            total_horas += float(linha[5] or 0)
            total_hora_extra += float(linha[7] or 0)
            total_folha += float(linha[9] or 0)

            row = self.tabela_folha.rowCount()
            self.tabela_folha.insertRow(row)
            v = float(linha[5] or 0)
            qtd_horas = str(int(v)) if v == int(v) else f"{v:.2f}"
            valores = [
                linha[0], linha[1], linha[2] or "",
                formatar_moeda(linha[3]), formatar_moeda(linha[4]),
                qtd_horas, formatar_moeda(linha[6]),
                formatar_moeda(linha[7]), formatar_moeda(linha[8]),
                formatar_moeda(linha[9]), linha[10] or "Ativo",
            ]
            for col, texto in enumerate(valores):
                self.tabela_folha.setItem(row, col, QTableWidgetItem(str(texto)))

        self._resumo["func"].setText(str(len(dados)))
        self._resumo["horas"].setText(f"{total_horas:.0f}")
        self._resumo["valor_hora"].setText(formatar_moeda(total_hora_extra))
        self._resumo["total"].setText(formatar_moeda(total_folha))

    def _get_funcionario_selecionado(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um funcionário.")
            return None
        item = self.tabela.item(row, 0)
        return int(item.text()) if item else None

    def _editar_selecionado(self):
        fid = self._get_funcionario_selecionado()
        if not fid:
            return
        funcionario = funcionarios_service.obter_funcionario(fid)
        if funcionario:
            self._abrir_modal_funcionario(funcionario)

    def _excluir_funcionario(self):
        fid = self._get_funcionario_selecionado()
        if not fid:
            return
        row = self.tabela.currentRow()
        nome = self.tabela.item(row, 1).text() if self.tabela.item(row, 1) else ""
        resp = QMessageBox.question(self, "Confirmar", f"Deseja excluir {nome}?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        funcionarios_service.excluir_funcionario(fid)
        self._carregar_funcionarios()

    def _abrir_modal_funcionario(self, funcionario=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Funcionário")
        dlg.resize(520, 480)

        colors = theme_manager.colors
        tokens = theme_manager.tokens

        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        layout.setSpacing(tokens.SPACING_MD)
        dlg.setLayout(layout)

        titulo = QLabel("Cadastro de Funcionário")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']};")
        layout.addWidget(titulo)

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; }}")
        fl = QFormLayout()
        fl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        fl.setSpacing(tokens.SPACING_SM)
        frame.setLayout(fl)

        input_style = self._input_style("sky")

        entry_nome = QLineEdit()
        entry_nome.setPlaceholderText("Nome do funcionário")
        entry_nome.setStyleSheet(input_style)
        fl.addRow(self._lbl("Nome"), entry_nome)

        entry_cargo = QLineEdit()
        entry_cargo.setPlaceholderText("Cargo")
        entry_cargo.setStyleSheet(input_style)
        fl.addRow(self._lbl("Cargo"), entry_cargo)

        entry_tel = QLineEdit()
        entry_tel.setPlaceholderText("Telefone")
        entry_tel.setStyleSheet(input_style)
        fl.addRow(self._lbl("Telefone"), entry_tel)

        entry_adm = QLineEdit()
        entry_adm.setPlaceholderText("Data admissão")
        entry_adm.setStyleSheet(input_style)
        fl.addRow(self._lbl("Admissão"), entry_adm)

        entry_sal = QLineEdit()
        entry_sal.setPlaceholderText("Salário")
        entry_sal.setStyleSheet(input_style)
        fl.addRow(self._lbl("Salário"), entry_sal)

        entry_vale = QLineEdit()
        entry_vale.setPlaceholderText("Vale refeição")
        entry_vale.setStyleSheet(input_style)
        fl.addRow(self._lbl("Vale Refeição"), entry_vale)

        combo_status = QComboBox()
        combo_status.addItems(["Ativo", "Inativo"])
        combo_status.setMinimumHeight(40)
        combo_status.setStyleSheet(input_style.replace("QLineEdit", "QComboBox"))
        fl.addRow(self._lbl("Status"), combo_status)

        funcionario_id = None
        if funcionario:
            funcionario_id = funcionario[0]
            entry_nome.setText(funcionario[1] or "")
            entry_cargo.setText(funcionario[2] or "")
            entry_tel.setText(funcionario[3] or "")
            entry_adm.setText(funcionario[4] or "")
            entry_sal.setText(str(funcionario[5] or "").replace(".", ","))
            entry_vale.setText(str(funcionario[6] or "").replace(".", ","))
            combo_status.setCurrentText(funcionario[7] or "Ativo")

        layout.addWidget(frame)

        def salvar():
            if not entry_nome.text().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe o nome do funcionário.")
                return
            dados = (
                entry_nome.text().strip(),
                entry_cargo.text().strip(),
                entry_tel.text().strip(),
                entry_adm.text().strip(),
                parse_numero(entry_sal.text()),
                parse_numero(entry_vale.text()),
                combo_status.currentText(),
            )
            funcionarios_service.salvar_funcionario(funcionario_id, dados)
            dlg.accept()
            self._carregar_funcionarios()
            QMessageBox.information(dlg, "Sucesso", "Funcionário salvo com sucesso!")

        btn_salvar = ModernButton("Salvar", ButtonStyle.PRIMARY)
        btn_salvar.clicked.connect(salvar)
        layout.addWidget(btn_salvar)

        dlg.exec()

    def _abrir_modal_hora_extra(self):
        row = self.tabela_folha.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um funcionário da folha.")
            return

        item_id = self.tabela_folha.item(row, 0)
        item_nome = self.tabela_folha.item(row, 1)
        if not item_id or not item_nome:
            return

        funcionario_id = int(item_id.text())
        nome = item_nome.text()
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()

        folha = funcionarios_service.obter_folha_funcionario(funcionario_id, mes, ano)
        if not folha:
            QMessageBox.warning(self, "Atenção", "Esse funcionário ainda não está na folha. Clique em Gerar/Atualizar Folha do Mês.")
            return

        salario = folha[1] or 0
        vale = folha[2] or 0
        qtd_atual = folha[3] or ""
        valor_hora_atual = folha[4] or ""
        outros_atual = folha[6] or ""

        dlg = QDialog(self)
        dlg.setWindowTitle("Hora Extra")
        dlg.resize(480, 500)

        colors = theme_manager.colors
        tokens = theme_manager.tokens

        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        layout.setSpacing(tokens.SPACING_MD)
        dlg.setLayout(layout)

        titulo = QLabel(f"Folha de {nome}")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']};")
        layout.addWidget(titulo)

        ref = QLabel(f"Referência: {mes}/{ano}")
        ref.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD))
        ref.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        layout.addWidget(ref)

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; }}")
        fl = QFormLayout()
        fl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        fl.setSpacing(tokens.SPACING_SM)
        frame.setLayout(fl)

        input_style = self._input_style("sky")

        entry_qtd = QLineEdit()
        entry_qtd.setPlaceholderText("Ex: 10")
        entry_qtd.setStyleSheet(input_style)
        if qtd_atual not in ("", None, 0):
            entry_qtd.setText(str(qtd_atual).replace(".", ","))
        fl.addRow(self._lbl("Qtd. horas extras"), entry_qtd)

        entry_valor_hora = QLineEdit()
        entry_valor_hora.setPlaceholderText("Ex: 25,00")
        entry_valor_hora.setStyleSheet(input_style)
        if valor_hora_atual not in ("", None, 0):
            entry_valor_hora.setText(str(valor_hora_atual).replace(".", ","))
        fl.addRow(self._lbl("Valor por hora"), entry_valor_hora)

        entry_outros = QLineEdit()
        entry_outros.setPlaceholderText("Ex: 100,00 ou -50,00")
        entry_outros.setStyleSheet(input_style)
        if outros_atual not in ("", None, 0):
            entry_outros.setText(str(outros_atual).replace(".", ","))
        fl.addRow(self._lbl("Outros adicionais"), entry_outros)

        label_total = QLabel("")
        label_total.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG, bold=True))
        label_total.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        fl.addRow(label_total)

        def atualizar_total():
            qtd = parse_numero(entry_qtd.text())
            valor_hora = parse_numero(entry_valor_hora.text())
            outros = parse_numero(entry_outros.text())
            total_he = qtd * valor_hora
            total = float(salario or 0) + float(vale or 0) + total_he + outros
            label_total.setText(f"Hora extra: {formatar_moeda(total_he)}\nTotal da folha: {formatar_moeda(total)}")

        entry_qtd.textChanged.connect(atualizar_total)
        entry_valor_hora.textChanged.connect(atualizar_total)
        entry_outros.textChanged.connect(atualizar_total)
        atualizar_total()

        layout.addWidget(frame)

        def salvar():
            qtd = parse_numero(entry_qtd.text())
            valor_hora = parse_numero(entry_valor_hora.text())
            outros = parse_numero(entry_outros.text())
            funcionarios_service.salvar_hora_extra(funcionario_id, mes, ano, qtd, valor_hora, outros)
            dlg.accept()
            self._carregar_folha_mes()
            QMessageBox.information(dlg, "Sucesso", "Lançamento salvo na folha!")

        btn_salvar = ModernButton("Salvar na Folha", ButtonStyle.SUCCESS)
        btn_salvar.clicked.connect(salvar)
        layout.addWidget(btn_salvar)

        dlg.exec()

    def _gerar_folha_todos(self):
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()
        if not ano:
            QMessageBox.warning(self, "Atenção", "Informe o ano.")
            return

        resp = QMessageBox.question(self, "Gerar folha", f"Deseja gerar/atualizar a folha de todos os funcionários ativos para {mes}/{ano}?")
        if resp != QMessageBox.StandardButton.Yes:
            return

        funcionarios = funcionarios_service.listar_funcionarios_ativos()
        if not funcionarios:
            QMessageBox.warning(self, "Atenção", "Nenhum funcionário ativo encontrado.")
            return

        total = funcionarios_service.gerar_folha_todos(mes, ano)
        self._carregar_folha_mes()
        QMessageBox.information(self, "Sucesso", f"Folha de {total} funcionários gerada para {mes}/{ano}.")

    def _remover_da_folha(self):
        row = self.tabela_folha.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um funcionário da folha.")
            return

        item_id = self.tabela_folha.item(row, 0)
        item_nome = self.tabela_folha.item(row, 1)
        if not item_id or not item_nome:
            return

        funcionario_id = int(item_id.text())
        nome = item_nome.text()
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()

        resp = QMessageBox.question(self, "Remover da folha", f"Deseja remover {nome} da folha {mes}/{ano}?")
        if resp != QMessageBox.StandardButton.Yes:
            return

        funcionarios_service.remover_da_folha(funcionario_id, mes, ano)
        self._carregar_folha_mes()

    def _input_style(self, accent: str) -> str:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        accent_color = colors.get(accent, colors["sky"])
        return f"""
            QLineEdit {{ background-color: {colors['bg_primary']}; color: {colors['text_primary']};
                border: 1.5px solid {colors['border_subtle']}; border-radius: {tokens.RADIUS_MD}px;
                padding: 8px 12px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {accent_color}; }}
        """

    def _lbl(self, texto) -> QLabel:
        colors = theme_manager.colors
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: 600; background: transparent;")
        return lbl
