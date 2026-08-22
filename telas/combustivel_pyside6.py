"""
Tela Combustível - CW Transportadora - PySide6 Premium Dark Red
Controle de abastecimentos, consumo e média km/L.
Design System CW - Premium Dark Industrial
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea, QGridLayout,
)
from PySide6.QtCore import Qt, QTimer

from services.frota_service import frota_service
from ui.theme.cw_theme import cw_theme
from ui.components import KPICard, CWCard, CWButton, ButtonVariant, ButtonSize, CWTable
from utils.helpers import formatar_moeda, formatar_peso, parse_numero
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
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {c['bg_primary']}; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
            QScrollBar::handle:vertical {{ background: {c['border_subtle']}; border-radius: 4px; min-height: 40px; }}
            QScrollBar::handle:vertical:hover {{ background: {c['border_default']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0px; }}
        """)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(t._2XL, t._2XL, t._2XL, t._2XL)
        cl.setSpacing(t.XL)
        content.setLayout(cl)
        scroll.setWidget(content)

        # Filtros card
        filtros = CWCard("Filtros", padding=t.LG)
        fr = QHBoxLayout()
        fr.setSpacing(t.MD)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setMinimumHeight(40)
        self.combo_periodo.setMinimumWidth(110)
        self.combo_periodo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: {t.SM}px {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QComboBox:hover {{ border-color: {c['border_strong']}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {c['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                selection-background-color: {c['primary_soft']};
                selection-color: {c['primary']};
            }}
        """)
        self.combo_periodo.currentTextChanged.connect(lambda: self._carregar_abastecimentos())
        fr.addWidget(self.combo_periodo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.setMinimumHeight(40)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.setStyleSheet(self.combo_periodo.styleSheet())
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_abastecimentos())
        fr.addWidget(self.combo_mes)

        self.entry_ano = QLineEdit(datetime.now().strftime("%Y"))
        self.entry_ano.setPlaceholderText("Ano")
        self.entry_ano.setMinimumWidth(80)
        self.entry_ano.setMinimumHeight(40)
        self.entry_ano.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{ border: 1px solid {c['border_focus']}; }}
        """)
        self.entry_ano.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_ano)

        self.entry_busca = QLineEdit()
        self.entry_busca.setPlaceholderText("Buscar veículo, motorista ou posto...")
        self.entry_busca.setMinimumWidth(220)
        self.entry_busca.setMinimumHeight(40)
        self.entry_busca.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{ border: 1px solid {c['border_focus']}; }}
        """)
        self.entry_busca.textChanged.connect(lambda: self._debounce_carregar())
        fr.addWidget(self.entry_busca)

        fr.addStretch()

        btn_novo = CWButton("+ Novo Abastecimento", ButtonVariant.PRIMARY, ButtonSize.MD)
        btn_novo.clicked.connect(self._abrir_modal)
        fr.addWidget(btn_novo)

        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Resumo cards - KPI style
        resumo_layout = QHBoxLayout()
        resumo_layout.setSpacing(t.LG)

        self._resumo = {}
        kpi_configs = [
            ("Abastecimentos", "qtd"),
            ("Litros", "litros"),
            ("Gasto total", "gasto"),
            ("Média geral", "media")
        ]

        for titulo, chave in kpi_configs:
            kpi_card = QFrame()
            kpi_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['bg_elevated']};
                    border: 1px solid {c['border_subtle']};
                    border-radius: {r.LG}px;
                }}
            """)
            kpi_layout = QVBoxLayout()
            kpi_layout.setContentsMargins(t.LG, t.MD, t.LG, t.MD)
            kpi_layout.setSpacing(t.XS)
            kpi_card.setLayout(kpi_layout)

            t_label = QLabel(titulo)
            t_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            t_label.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            kpi_layout.addWidget(t_label)

            v_label = QLabel("0")
            v_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
            v_label.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            kpi_layout.addWidget(v_label)

            self._resumo[chave] = v_label
            resumo_layout.addWidget(kpi_card)

        cl.addLayout(resumo_layout)

        # Tabela card
        tabela_card = CWCard("Histórico de Abastecimentos", padding=t.XL)
        colunas = [
            "ID", "Data", "Veículo", "Motorista",
            "KM", "Litros", "R$/Litro", "Total",
            "Posto", "Status"
        ]
        self.tabela = CWTable(colunas)
        self.tabela.setMinimumHeight(350)

        # Configurar larguras das colunas
        h = self.tabela.horizontalHeader()
        widths = [45, 100, 160, 140, 90, 80, 90, 100, 140, 90]
        for i, w in enumerate(widths):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.cellDoubleClicked.connect(self._editar_abastecimento)
        tabela_card.add_widget(self.tabela)

        # Botões
        br = QHBoxLayout()
        br.addStretch()
        btn_excluir = CWButton("Excluir", ButtonVariant.DANGER, ButtonSize.MD)
        btn_excluir.clicked.connect(self._excluir)
        br.addWidget(btn_excluir)
        btn_atualizar = CWButton("Atualizar", ButtonVariant.SECONDARY, ButtonSize.MD)
        btn_atualizar.clicked.connect(self._carregar_abastecimentos)
        br.addWidget(btn_atualizar)
        tabela_card.add_layout(br)

        cl.addWidget(tabela_card)

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
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius
        
        dlg.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg_primary']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(t._2XL, t._2XL, t._2XL, t._2XL)
        layout.setSpacing(t.XL)
        dlg.setLayout(layout)

        titulo = QLabel("Cadastro de Abastecimento")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        titulo.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        layout.addWidget(titulo)

        card = CWCard(padding=t.XL)
        veiculos = frota_service.listar_veiculos_disponiveis("abastecimentos")

        def campo(label_texto):
            lbl = QLabel(label_texto)
            lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
            lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            card.add_widget(lbl)
            entry = QLineEdit()
            entry.setMinimumHeight(40)
            entry.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {c['bg_primary']};
                    border: 1px solid {c['border_default']};
                    border-radius: {r.MD}px;
                    padding: 0 {t.MD}px;
                    font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                    color: {c['text_primary']};
                }}
                QLineEdit:focus {{ border: 1px solid {c['border_focus']}; }}
            """)
            card.add_widget(entry)
            return entry

        data_entry = campo("Data")
        data_entry.setText(datetime.now().strftime("%d/%m/%Y"))

        lbl = QLabel("Veículo")
        lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        card.add_widget(lbl)
        combo_veiculo = QComboBox()
        combo_veiculo.addItems(veiculos if veiculos else ["Nenhum veículo"])
        combo_veiculo.setMinimumHeight(40)
        combo_veiculo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: {t.SM}px {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QComboBox:hover {{ border-color: {c['border_strong']}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {c['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                selection-background-color: {c['primary_soft']};
                selection-color: {c['primary']};
            }}
        """)
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

        btn = CWButton("Salvar Abastecimento", ButtonVariant.SUCCESS, ButtonSize.MD)
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
