"""
Tela Manutenção da Frota - CW Transportadora - PySide6
Controle de revisões, oficinas, custos e próximos vencimentos por KM.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea, QFormLayout, QPlainTextEdit,
)
from PySide6.QtCore import Qt, QTimer

from services.frota_service import frota_service
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWInput, CWTable
from utils.components import ModernCard, ModernInput, ModernButton, ButtonStyle, ModernTable
from utils.helpers import formatar_moeda, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaManutencao(QWidget):
    """Tela de manutenção da frota em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._geracao = 0
        self._setup_ui()
        self._carregar_manutencoes()

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
        self.combo_periodo.setMinimumHeight(40)
        self.combo_periodo.setMinimumWidth(110)
        self.combo_periodo.currentTextChanged.connect(lambda: self._carregar_manutencoes())
        fr.addWidget(self.combo_periodo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.setMinimumHeight(cw_theme.spacing.SPACING_XL * 2 + cw_theme.spacing.SPACING_SM)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_manutencoes())
        fr.addWidget(self.combo_mes)

        self.entry_ano = ModernInput(datetime.now().strftime("%Y"))
        self.entry_ano.setMinimumWidth(80)
        self.entry_ano.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_ano)

        self.entry_busca = ModernInput("Buscar veículo, oficina ou tipo...")
        self.entry_busca.setMinimumWidth(220)
        self.entry_busca.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_busca)

        fr.addStretch()

        btn_novo = ModernButton("Nova Manutenção", ButtonStyle.PRIMARY, icon_name="plus")
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
        for titulo, chave in [("Manutenções", "qtd"), ("Gasto total", "gasto"), ("Pendentes", "pendentes"), ("Pagas", "pagas")]:
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
            v.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
            cardl.addWidget(v)
            self._resumo[chave] = v
            rl.addWidget(card)
        cl.addWidget(resumo_frame)

        # Tabela
        card = ModernCard(padding=cw_theme.spacing.SPACING_XL)
        colunas = [
            ("ID", 45), ("Data", 100), ("Veículo", 170), ("KM", 90),
            ("Tipo", 110), ("Oficina", 150), ("Valor", 110),
        ]
        self.tabela = ModernTable()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setMinimumHeight(350)

        h = self.tabela.horizontalHeader()
        for i, (_, w) in enumerate(colunas):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.cellDoubleClicked.connect(self._editar_manutencao)
        card.add_widget(self.tabela)

        # Botões
        br = QHBoxLayout()
        br.addStretch()
        btn_excluir = ModernButton("Excluir", ButtonStyle.DANGER)
        btn_excluir.clicked.connect(self._excluir)
        br.addWidget(btn_excluir)
        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_manutencoes)
        br.addWidget(btn_atualizar)
        card.add_layout(br)

        cl.addWidget(card)

    def _debounce_carregar(self):
        if hasattr(self, '_debounce_timer') and self._debounce_timer:
            self._debounce_timer.stop()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._carregar_manutencoes)
        self._debounce_timer.start(300)

    def _carregar_manutencoes(self):
        self._geracao += 1
        geracao = self._geracao
        tipo = self.combo_periodo.currentText()
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()
        busca = self.entry_busca.text().strip()

        def tarefa():
            try:
                dados = frota_service.listar_manutencoes(tipo, mes, ano, busca)
                QTimer.singleShot(0, lambda: self._aplicar_dados(dados, geracao))
            except Exception as e:
                logger.error(f"Erro ao carregar: {e}")
                QTimer.singleShot(0, lambda: self._aplicar_dados([], geracao))

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_dados(self, dados, geracao):
        if geracao != self._geracao:
            return
        self.tabela.setRowCount(0)
        total_gasto = 0
        pendentes = 0
        pagas = 0

        for linha in dados:
            valor = float(linha[7] or 0)
            status = linha[9] or "Pendente"
            total_gasto += valor
            if status == "Pago":
                pagas += 1
            elif status == "Pendente":
                pendentes += 1

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                linha[0], linha[1], linha[2] or "",
                self._fmt_num(linha[3]), linha[4] or "",
                linha[6] or "", formatar_moeda(linha[7]),
                self._fmt_num(linha[8]), status, linha[5] or "",
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

        self._resumo["qtd"].setText(str(len(dados)))
        self._resumo["gasto"].setText(formatar_moeda(total_gasto))
        self._resumo["pendentes"].setText(str(pendentes))
        self._resumo["pagas"].setText(str(pagas))

    def _fmt_num(self, valor) -> str:
        v = float(valor or 0)
        return str(int(v)) if v == int(v) else f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _abrir_modal(self, dados=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Manutenção")
        dlg.resize(580, 700)

        colors = cw_theme.colors
        tokens = cw_theme.spacing

        layout = QVBoxLayout()
        layout.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL)
        layout.setSpacing(cw_theme.spacing.SPACING_MD)
        dlg.setLayout(layout)

        titulo = QLabel("Cadastro de Manutenção")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {cw_theme.colors['text_primary']};")
        layout.addWidget(titulo)

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {cw_theme.colors['bg_secondary']}; border-radius: {cw_theme.radius.XL}px; }}")
        fl = QFormLayout()
        fl.setContentsMargins(cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_XL)
        fl.setSpacing(cw_theme.spacing.SPACING_SM)
        frame.setLayout(fl)

        lbl_style = f"color: {cw_theme.colors['text_secondary']}; font-weight: 600;"
        input_style = f"""
            QLineEdit {{ background-color: {cw_theme.colors['bg_primary']}; color: {cw_theme.colors['text_primary']};
                border: 1.5px solid {cw_theme.colors['border_subtle']}; border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px; font-size: {cw_theme.typography.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {cw_theme.colors['warning']}; }}
        """

        # Data
        entry_data = QLineEdit()
        entry_data.setText(datetime.now().strftime("%d/%m/%Y"))
        entry_data.setStyleSheet(input_style)
        fl.addRow(self._lbl("Data"), entry_data)

        # Veículo
        veiculos = frota_service.listar_veiculos_disponiveis("manutencoes")
        combo_veiculo = QComboBox()
        combo_veiculo.addItems(veiculos if veiculos else [])
        combo_veiculo.setMinimumHeight(40)
        combo_veiculo.setEditable(True)
        combo_veiculo.setStyleSheet(input_style.replace("QLineEdit", "QComboBox"))
        fl.addRow(self._lbl("Veículo"), combo_veiculo)

        # KM atual
        entry_km = QLineEdit()
        entry_km.setStyleSheet(input_style)
        fl.addRow(self._lbl("KM atual"), entry_km)

        # Tipo
        combo_tipo = QComboBox()
        combo_tipo.addItems([
            "Preventiva", "Corretiva", "Troca de óleo", "Pneus", "Freios",
            "Suspensão", "Elétrica", "Motor", "Revisão geral", "Outro",
        ])
        combo_tipo.setMinimumHeight(40)
        combo_tipo.setStyleSheet(input_style.replace("QLineEdit", "QComboBox"))
        fl.addRow(self._lbl("Tipo"), combo_tipo)

        # Descrição
        entry_desc = QLineEdit()
        entry_desc.setStyleSheet(input_style)
        fl.addRow(self._lbl("Descrição"), entry_desc)

        # Oficina
        entry_oficina = QLineEdit()
        entry_oficina.setStyleSheet(input_style)
        fl.addRow(self._lbl("Oficina / Fornecedor"), entry_oficina)

        # Valor
        entry_valor = QLineEdit()
        entry_valor.setStyleSheet(input_style)
        fl.addRow(self._lbl("Valor"), entry_valor)

        # Próxima revisão
        entry_prox = QLineEdit()
        entry_prox.setStyleSheet(input_style)
        fl.addRow(self._lbl("Próxima revisão (KM)"), entry_prox)

        # Status
        combo_status = QComboBox()
        combo_status.addItems(["Pendente", "Pago", "Agendado", "Cancelado"])
        combo_status.setMinimumHeight(40)
        combo_status.setStyleSheet(input_style.replace("QLineEdit", "QComboBox"))
        fl.addRow(self._lbl("Status"), combo_status)

        # Observação
        entry_obs = QLineEdit()
        entry_obs.setStyleSheet(input_style)
        fl.addRow(self._lbl("Observação"), entry_obs)

        # Preencher se edição
        manutencao_id = None
        if dados:
            manutencao_id = dados[0]
            entry_data.setText(dados[1] or "")
            combo_veiculo.setCurrentText(dados[2] or "")
            entry_km.setText(str(dados[3] or "").replace(".", ","))
            combo_tipo.setCurrentText(dados[4] or "Preventiva")
            entry_desc.setText(dados[5] or "")
            entry_oficina.setText(dados[6] or "")
            entry_valor.setText(str(dados[7] or "").replace(".", ","))
            entry_prox.setText(str(dados[8] or "").replace(".", ","))
            combo_status.setCurrentText(dados[9] or "Pendente")
            entry_obs.setText(dados[10] or "")

        layout.addWidget(frame)

        def salvar():
            if not entry_data.text().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe a data.")
                return
            if not combo_veiculo.currentText().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe o veículo.")
                return

            valores = (
                entry_data.text().strip(),
                combo_veiculo.currentText().strip(),
                parse_numero(entry_km.text()),
                combo_tipo.currentText(),
                entry_desc.text().strip(),
                entry_oficina.text().strip(),
                parse_numero(entry_valor.text()),
                parse_numero(entry_prox.text()),
                combo_status.currentText(),
                entry_obs.text().strip(),
            )
            frota_service.salvar_manutencao(manutencao_id, valores)
            dlg.accept()
            self._carregar_manutencoes()
            QMessageBox.information(dlg, "Sucesso", "Manutenção salva com sucesso!")

        btn_salvar = ModernButton("Salvar Manutenção", ButtonStyle.SUCCESS, icon_name="save")
        btn_salvar.clicked.connect(salvar)
        layout.addWidget(btn_salvar)

        dlg.exec()

    def _editar_manutencao(self, row, col):
        item = self.tabela.item(row, 0)
        if not item:
            return
        manutencao_id = item.text()
        dados = frota_service.obter_manutencao(manutencao_id)
        if dados:
            self._abrir_modal(dados)

    def _excluir(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma manutenção.")
            return

        item = self.tabela.item(row, 0)
        if not item:
            return
        manutencao_id = item.text()

        resp = QMessageBox.question(self, "Confirmar", "Deseja excluir esta manutenção?")
        if resp != QMessageBox.StandardButton.Yes:
            return

        frota_service.excluir_manutencao(manutencao_id)
        self._carregar_manutencoes()

    def _lbl(self, texto) -> QLabel:
        colors = cw_theme.colors
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"color: {cw_theme.colors['text_secondary']}; font-weight: 600; background: transparent;")
        return lbl
