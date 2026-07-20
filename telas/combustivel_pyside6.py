"""
Tela Combustível - CW Transportadora - PySide6
Controle de abastecimentos, consumo e média km/L.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer

from services.frota_service import frota_service
from telas.theme_pyside6 import theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ModernCard
from utils.helpers import formatar_moeda, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaCombustivel(QWidget):
    """Tela de controle de combustível em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._geracao = 0
        self._setup_ui()
        self._carregar_abastecimentos()

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

        # Filtros
        filtros = ModernCard(padding=tokens.SPACING_LG)
        fr = QHBoxLayout()
        fr.setSpacing(tokens.SPACING_MD)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setMinimumHeight(40)
        self.combo_periodo.setMinimumWidth(110)
        self.combo_periodo.currentTextChanged.connect(lambda: self._carregar_abastecimentos())
        fr.addWidget(self.combo_periodo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.setMinimumHeight(40)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_abastecimentos())
        fr.addWidget(self.combo_mes)

        self.entry_ano = QLineEdit(datetime.now().strftime("%Y"))
        self.entry_ano.setFixedWidth(80)
        self.entry_ano.setMinimumHeight(40)
        self.entry_ano.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_ano)

        self.entry_busca = QLineEdit()
        self.entry_busca.setPlaceholderText("Buscar veículo, motorista ou posto...")
        self.entry_busca.setMinimumHeight(40)
        self.entry_busca.setMinimumWidth(220)
        self.entry_busca.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_busca)

        fr.addStretch()

        btn_novo = ModernButton("+ Novo Abastecimento", ButtonStyle.PRIMARY)
        btn_novo.clicked.connect(self._abrir_modal)
        fr.addWidget(btn_novo)

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
        for titulo, chave in [("Abastecimentos", "qtd"), ("Litros", "litros"), ("Gasto total", "gasto"), ("Média geral", "media")]:
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
            ("ID", 45), ("Data", 100), ("Veículo", 160), ("Motorista", 140),
            ("KM", 90), ("Litros", 80), ("R$/Litro", 90), ("Total", 100),
            ("Média", 90), ("Custo/KM", 90), ("Posto", 130), ("Status", 90),
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
            QTableWidget::item:selected {{ background-color: {colors['emerald_soft']}; }}
            QHeaderView::section {{ background-color: {colors['table_header_bg']}; color: {colors['table_header_text']};
                padding: 8px; border: none; border-bottom: 2px solid {colors['border_default']};
                font-weight: 700; font-size: {tokens.FONT_SIZE_SM}px; }}
        """)

        self.tabela.cellDoubleClicked.connect(self._editar_abastecimento)
        card.add_widget(self.tabela)

        # Botões
        br = QHBoxLayout()
        br.addStretch()
        btn_excluir = ModernButton("Excluir", ButtonStyle.DANGER)
        btn_excluir.clicked.connect(self._excluir)
        br.addWidget(btn_excluir)
        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_abastecimentos)
        br.addWidget(btn_atualizar)
        card.add_layout(br)

        cl.addWidget(card)

    def _debounce_carregar(self):
        if hasattr(self, '_debounce_timer') and self._debounce_timer:
            self._debounce_timer.stop()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._carregar_abastecimentos)
        self._debounce_timer.start(300)

    def _carregar_abastecimentos(self):
        self._geracao += 1
        geracao = self._geracao
        tipo = self.combo_periodo.currentText()
        mes = self.combo_mes.currentText()
        ano = self.entry_ano.text().strip()
        busca = self.entry_busca.text().strip()

        def tarefa():
            try:
                dados = frota_service.listar_abastecimentos(tipo, mes, ano, busca)
                QTimer.singleShot(0, lambda: self._aplicar_dados(dados, geracao))
            except Exception as e:
                logger.error(f"Erro ao carregar: {e}")
                QTimer.singleShot(0, lambda: self._aplicar_dados([], geracao))

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_dados(self, dados, geracao):
        if geracao != self._geracao:
            return
        self.tabela.setRowCount(0)
        total_litros = total_gasto = 0
        medias = []

        for linha in dados:
            total_litros += float(linha[5] or 0)
            total_gasto += float(linha[7] or 0)
            if float(linha[8] or 0) > 0:
                medias.append(float(linha[8] or 0))

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            status = self._status_media(linha[8])
            valores = [
                linha[0], linha[1], linha[2] or "", linha[3] or "",
                self._fmt_num(linha[4]), f"{self._fmt_num(linha[5])} L",
                formatar_moeda(linha[6]), formatar_moeda(linha[7]),
                f"{self._fmt_num(linha[8])} km/L" if linha[8] else "-",
                formatar_moeda(linha[9]), linha[10] or "", status,
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

        media_geral = sum(medias) / len(medias) if medias else 0
        self._resumo["qtd"].setText(str(len(dados)))
        self._resumo["litros"].setText(f"{self._fmt_num(total_litros)} L")
        self._resumo["gasto"].setText(formatar_moeda(total_gasto))
        self._resumo["media"].setText(f"{self._fmt_num(media_geral)} km/L")

    def _abrir_modal(self, dados=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Abastecimento")
        dlg.resize(520, 600)
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        layout = QVBoxLayout()
        dlg.setLayout(layout)

        titulo = QLabel("Cadastro de Abastecimento")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_XL, bold=True))
        layout.addWidget(titulo)

        card = ModernCard(padding=tokens.SPACING_XL)
        veiculos = frota_service.listar_veiculos_disponiveis("abastecimentos")

        def campo(label_texto):
            lbl = QLabel(label_texto)
            lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
            card.add_widget(lbl)
            entry = QLineEdit()
            entry.setMinimumHeight(40)
            card.add_widget(entry)
            return entry

        data_entry = campo("Data")
        data_entry.setText(datetime.now().strftime("%d/%m/%Y"))

        lbl = QLabel("Veículo")
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        card.add_widget(lbl)
        combo_veiculo = QComboBox()
        combo_veiculo.addItems(veiculos if veiculos else ["Nenhum veículo"])
        combo_veiculo.setMinimumHeight(40)
        card.add_widget(combo_veiculo)

        motorista_entry = campo("Motorista")
        km_entry = campo("KM atual")
        litros_entry = campo("Litros")
        valor_litro_entry = campo("Valor por litro")
        posto_entry = campo("Posto")
        obs_entry = campo("Observação")

        if dados:
            data_entry.setText(dados[1] or "")
            idx = combo_veiculo.findText(dados[2] or "")
            if idx >= 0:
                combo_veiculo.setCurrentIndex(idx)
            motorista_entry.setText(dados[3] or "")
            km_entry.setText(str(dados[4] or "").replace(".", ","))
            litros_entry.setText(str(dados[5] or "").replace(".", ","))
            valor_litro_entry.setText(str(dados[6] or "").replace(".", ","))
            posto_entry.setText(dados[10] or "")
            obs_entry.setText(dados[11] or "")

        def salvar():
            if not data_entry.text().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe a data.")
                return
            if not combo_veiculo.currentText().strip():
                QMessageBox.warning(dlg, "Atenção", "Informe o veículo.")
                return
            km = parse_numero(km_entry.text())
            lts = parse_numero(litros_entry.text())
            vl = parse_numero(valor_litro_entry.text())
            if km <= 0 or lts <= 0 or vl <= 0:
                QMessageBox.warning(dlg, "Atenção", "Informe KM, litros e valor por litro.")
                return
            total = lts * vl
            media, custo_km = frota_service.calcular_media_e_custo(
                combo_veiculo.currentText(), km, lts, total, dados[0] if dados else None
            )
            valores = (
                data_entry.text().strip(), combo_veiculo.currentText().strip(),
                motorista_entry.text().strip(), km, lts, vl, total, media, custo_km,
                posto_entry.text().strip(), obs_entry.text().strip(),
            )
            frota_service.salvar_abastecimento(dados[0] if dados else None, valores)
            dlg.accept()
            self._carregar_abastecimentos()
            QMessageBox.information(dlg, "Sucesso", "Abastecimento salvo com sucesso!")

        btn = ModernButton("Salvar Abastecimento", ButtonStyle.SUCCESS)
        btn.clicked.connect(salvar)
        card.add_widget(btn)
        layout.addWidget(card)
        dlg.exec()

    def _editar_abastecimento(self, row, col):
        item = self.tabela.item(row, 0)
        if not item:
            return
        abastecimento_id = item.text()
        dados = frota_service.obter_abastecimento(abastecimento_id)
        if dados:
            self._abrir_modal(dados)

    def _excluir(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um abastecimento.")
            return
        abastecimento_id = self.tabela.item(row, 0).text()
        resp = QMessageBox.question(self, "Confirmar", "Deseja excluir este abastecimento?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        frota_service.excluir_abastecimento(abastecimento_id)
        self._carregar_abastecimentos()

    @staticmethod
    def _status_media(media) -> str:
        media = float(media or 0)
        if media <= 0:
            return "1º registro"
        if media < 5:
            return "⚠ Baixa"
        if media > 14:
            return "⚠ Conferir"
        return "✅ OK"

    @staticmethod
    def _fmt_num(valor) -> str:
        v = float(valor or 0)
        return str(int(v)) if v == int(v) else f"{v:.2f}".replace(".", ",")
