"""
Tela de Notas - PySide6 com visual CTk (fundo escuro, cards brancos)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame, QFileDialog,
    QMessageBox, QDialog, QInputDialog
)
from PySide6.QtCore import Qt
from datetime import datetime

from services.notas_service import notas_service
from services.viagem_service import viagem_service
from utils.logger import get_logger

logger = get_logger(__name__)

FONT_FAMILY = "Segoe UI"


def style_botao_verde(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #15803d;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover { background-color: #166534; }
        QPushButton:pressed { background-color: #14532d; }
    """)


def style_botao_vermelho(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #b91c1c;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover { background-color: #7f1d1d; }
        QPushButton:pressed { background-color: #991b1b; }
    """)


def style_botao_cinza(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #374151;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover { background-color: #111827; }
        QPushButton:pressed { background-color: #1f2937; }
    """)


def style_card(widget: QFrame):
    widget.setStyleSheet("""
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
        }
        QLabel {
            background: transparent;
            color: #111827;
        }
    """)


def style_entry(entry: QLineEdit):
    entry.setStyleSheet("""
        QLineEdit {
            background-color: #f9fafb;
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 13px;
        }
        QLineEdit:focus { border-color: #15803d; }
    """)


def style_combo(combo: QComboBox):
    combo.setStyleSheet("""
        QComboBox {
            background-color: #f9fafb;
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
        }
        QComboBox:focus { border-color: #15803d; }
        QComboBox::drop-down { border: none; width: 30px; }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #111827;
            border: 1px solid #d1d5db;
            selection-background-color: #15803d;
            selection-color: #ffffff;
        }
    """)


def style_tabela(table: QTableWidget):
    table.setStyleSheet("""
        QTableWidget {
            background-color: #ffffff;
            color: #111827;
            border: none;
            gridline-color: #e5e7eb;
            font-size: 13px;
        }
        QHeaderView::section {
            background-color: #f9fafb;
            color: #374151;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #e5e7eb;
            font-weight: 600;
            font-size: 12px;
        }
        QTableWidget::item {
            padding: 8px 10px;
            border-bottom: 1px solid #f3f4f6;
        }
        QTableWidget::item:selected {
            background-color: rgba(21, 128, 61, 0.1);
            color: #111827;
        }
    """)


class TelaNotas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notas_ids = {}
        self.caminhoes_map = {}
        self.notas_marcadas = set()
        self._setup_ui()
        self.carregar_caminhoes()
        self.carregar_manifestos()

    def _setup_ui(self):
        self.setStyleSheet("background-color: #0B1120;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 16px;
            }
            QLabel { background: transparent; color: #ffffff; }
        """)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(22, 16, 22, 16)
        hl.setSpacing(4)

        lbl_tag = QLabel("NOTAS FISCAIS")
        lbl_tag.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")
        hl.addWidget(lbl_tag)

        lbl_titulo = QLabel("Notas Importadas")
        lbl_titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
        hl.addWidget(lbl_titulo)

        lbl_sub = QLabel("Gerenciamento de manifestos, notas fiscais e criação de viagens.")
        lbl_sub.setStyleSheet("font-size: 12px; color: #9ca3af;")
        hl.addWidget(lbl_sub)
        layout.addWidget(header)

        # Resumo
        self.resumo = QLabel("Selecione um manifesto para visualizar as notas.")
        self.resumo.setStyleSheet("font-size: 14px; font-weight: bold; color: #e5e7eb; padding: 4px 8px;")
        layout.addWidget(self.resumo)

        # Card Manifestos
        self._criar_card_manifestos(layout)
        # Barra Viagem
        self._criar_barra_viagem(layout)
        # Card Notas
        self._criar_card_notas(layout)

        layout.addStretch()

    def _criar_card_manifestos(self, layout):
        card = QFrame()
        style_card(card)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(12)

        lbl = QLabel("📁 MANIFESTOS / ARQUIVOS TXT")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #111827;")
        cl.addWidget(lbl)

        # Botões
        btn_row = QHBoxLayout()
        btn_importar = QPushButton("Importar Manifesto TXT")
        style_botao_verde(btn_importar)
        btn_importar.setFixedHeight(38)
        btn_importar.clicked.connect(self.importar_manifesto)
        btn_row.addWidget(btn_importar)

        btn_apagar = QPushButton("Apagar")
        style_botao_vermelho(btn_apagar)
        btn_apagar.setFixedHeight(38)
        btn_apagar.clicked.connect(self.apagar_manifesto_selecionado)
        btn_row.addWidget(btn_apagar)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        # Filtros
        filtros = QHBoxLayout()
        self.combo_periodo_manifestos = QComboBox()
        self.combo_periodo_manifestos.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo_manifestos.currentTextChanged.connect(self.atualizar_filtro_manifestos)
        style_combo(self.combo_periodo_manifestos)
        self.combo_periodo_manifestos.setFixedWidth(130)
        filtros.addWidget(self.combo_periodo_manifestos)

        self.combo_mes_manifestos = QComboBox()
        self.combo_mes_manifestos.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes_manifestos.setCurrentText(datetime.now().strftime("%m"))
        self.combo_mes_manifestos.currentTextChanged.connect(self.atualizar_filtro_manifestos)
        style_combo(self.combo_mes_manifestos)
        self.combo_mes_manifestos.setFixedWidth(90)
        filtros.addWidget(self.combo_mes_manifestos)

        ano_atual = datetime.now().year
        self.combo_ano_manifestos = QComboBox()
        self.combo_ano_manifestos.addItems([str(a) for a in range(ano_atual - 5, ano_atual + 2)])
        self.combo_ano_manifestos.setCurrentText(str(ano_atual))
        self.combo_ano_manifestos.currentTextChanged.connect(self.atualizar_filtro_manifestos)
        style_combo(self.combo_ano_manifestos)
        self.combo_ano_manifestos.setFixedWidth(100)
        filtros.addWidget(self.combo_ano_manifestos)
        filtros.addStretch()
        cl.addLayout(filtros)

        # Tabela
        self.tabela_manifestos = QTableWidget()
        self.tabela_manifestos.setColumnCount(7)
        self.tabela_manifestos.setHorizontalHeaderLabels([
            "ID", "Arquivo TXT", "Importado em", "Valor Notas", "Notas", "Frete Total", "Peso Total"
        ])
        self.tabela_manifestos.horizontalHeader().setStretchLastSection(True)
        self.tabela_manifestos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabela_manifestos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_manifestos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela_manifestos.setAlternatingRowColors(False)
        self.tabela_manifestos.verticalHeader().setVisible(False)
        self.tabela_manifestos.setColumnWidth(0, 50)
        self.tabela_manifestos.setColumnWidth(1, 330)
        self.tabela_manifestos.setColumnWidth(2, 160)
        self.tabela_manifestos.setColumnWidth(3, 150)
        self.tabela_manifestos.setColumnWidth(4, 80)
        self.tabela_manifestos.setColumnWidth(5, 140)
        self.tabela_manifestos.setColumnWidth(6, 140)
        style_tabela(self.tabela_manifestos)
        self.tabela_manifestos.itemSelectionChanged.connect(self.selecionar_manifesto)
        cl.addWidget(self.tabela_manifestos)

        layout.addWidget(card)

    def _criar_barra_viagem(self, layout):
        card = QFrame()
        style_card(card)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(12)

        lbl = QLabel("🚚 CRIAR VIAGEM COM NOTAS SELECIONADAS")
        lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        cl.addWidget(lbl)

        linha = QHBoxLayout()

        self.combo_caminhoes = QComboBox()
        self.combo_caminhoes.addItem("Nenhum caminhão cadastrado")
        style_combo(self.combo_caminhoes)
        self.combo_caminhoes.setFixedWidth(330)
        linha.addWidget(self.combo_caminhoes)

        self.entrada_motorista_viagem = QLineEdit()
        self.entrada_motorista_viagem.setPlaceholderText("Motorista da viagem")
        style_entry(self.entrada_motorista_viagem)
        self.entrada_motorista_viagem.setFixedWidth(210)
        linha.addWidget(self.entrada_motorista_viagem)

        btn_novo = QPushButton("+ Novo Veículo")
        style_botao_cinza(btn_novo)
        btn_novo.setFixedHeight(38)
        btn_novo.setFixedWidth(140)
        btn_novo.clicked.connect(self.abrir_novo_veiculo)
        linha.addWidget(btn_novo)

        btn_criar = QPushButton("✅ Criar Viagem")
        style_botao_verde(btn_criar)
        btn_criar.setFixedHeight(38)
        btn_criar.setFixedWidth(150)
        btn_criar.clicked.connect(self.criar_viagem_selecionadas)
        linha.addWidget(btn_criar)

        btn_apagar_v = QPushButton("🗑 Apagar Viagem")
        style_botao_vermelho(btn_apagar_v)
        btn_apagar_v.setFixedHeight(38)
        btn_apagar_v.setFixedWidth(150)
        btn_apagar_v.clicked.connect(self.apagar_viagem_selecionada)
        linha.addWidget(btn_apagar_v)

        self.label_selecao = QLabel("Notas selecionadas: 0")
        self.label_selecao.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        linha.addWidget(self.label_selecao)
        linha.addStretch()

        cl.addLayout(linha)
        layout.addWidget(card)

    def _criar_card_notas(self, layout):
        card = QFrame()
        style_card(card)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(12)

        lbl = QLabel("📄 NOTAS DO MANIFESTO SELECIONADO")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #111827;")
        cl.addWidget(lbl)

        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(9)
        self.tabela_notas.setHorizontalHeaderLabels([
            "Sel.", "CT-e / Chave", "Remetente", "Cliente / Destinatário",
            "Origem", "Destino", "Frete", "Peso", "Status"
        ])
        self.tabela_notas.horizontalHeader().setStretchLastSection(True)
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_notas.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela_notas.setAlternatingRowColors(False)
        self.tabela_notas.verticalHeader().setVisible(False)
        self.tabela_notas.setColumnWidth(0, 55)
        self.tabela_notas.setColumnWidth(1, 180)
        self.tabela_notas.setColumnWidth(2, 280)
        self.tabela_notas.setColumnWidth(3, 300)
        self.tabela_notas.setColumnWidth(4, 160)
        self.tabela_notas.setColumnWidth(5, 180)
        self.tabela_notas.setColumnWidth(6, 130)
        self.tabela_notas.setColumnWidth(7, 120)
        self.tabela_notas.setColumnWidth(8, 120)
        style_tabela(self.tabela_notas)
        self.tabela_notas.cellClicked.connect(self.clicar_na_nota)
        cl.addWidget(self.tabela_notas)

        layout.addWidget(card, 1)

    def importar_manifesto(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Manifesto TXT", "",
            "Arquivos TXT (*.txt);;Todos os arquivos (*.*)"
        )
        if not caminho:
            return
        try:
            resultado = notas_service.importar_manifesto(caminho)
            QMessageBox.information(
                self, "Importação concluída",
                f"Arquivo: {resultado['arquivo']}\n\n"
                f"Notas encontradas: {resultado['encontradas']}\n"
                f"Notas salvas: {resultado['salvas']}\n"
                f"Notas duplicadas: {resultado['duplicadas']}"
            )
            self.carregar_manifestos()
        except Exception as erro:
            QMessageBox.critical(self, "Erro ao importar manifesto", str(erro))

    def apagar_manifesto_selecionado(self):
        selecionado = self.tabela_manifestos.selectedItems()
        if not selecionado:
            QMessageBox.warning(self, "Atenção", "Selecione um manifesto para apagar.")
            return

        row = selecionado[0].row()
        manifesto_id = self.tabela_manifestos.item(row, 0).text()
        nome_arquivo = self.tabela_manifestos.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Apagar manifesto",
            f"Deseja apagar este manifesto?\n\n{nome_arquivo}\n\n"
            "Todas as notas desse manifesto também serão apagadas."
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            ids_manifesto = {nota[0] for nota in notas_service.listar_notas_por_manifesto(manifesto_id)}
            notas_service.apagar_manifesto(manifesto_id)

            self.tabela_notas.setRowCount(0)
            self.resumo.setText("Selecione um manifesto para visualizar as notas.")
            self.notas_ids = {}
            self.notas_marcadas -= ids_manifesto
            self.atualizar_selecao()
            self.carregar_manifestos()
        except Exception as erro:
            QMessageBox.critical(self, "Erro ao apagar manifesto", str(erro))

    def carregar_caminhoes(self):
        self.caminhoes_map = {}
        caminhoes = viagem_service.listar_caminhoes_disponiveis()
        valores = []
        for caminhao in caminhoes:
            caminhao_id, placa, modelo, motorista, capacidade = caminhao
            texto = f"{modelo} | {placa} | {capacidade:,.0f} kg"
            self.caminhoes_map[texto] = caminhao_id
            valores.append(texto)

        self.combo_caminhoes.clear()
        if valores:
            self.combo_caminhoes.addItems(valores)
            self.combo_caminhoes.setCurrentText(valores[0])
        else:
            self.combo_caminhoes.addItem("Nenhum caminhão cadastrado")

    def obter_filtro_manifestos(self):
        tipo_periodo = self.combo_periodo_manifestos.currentText()
        mes = self.combo_mes_manifestos.currentText()
        ano = self.combo_ano_manifestos.currentText()
        if tipo_periodo == "Geral":
            return "Geral", None, None
        if tipo_periodo == "Mês":
            return "Mês", mes, ano
        if tipo_periodo == "Ano":
            return "Ano", None, ano
        return "Geral", None, None

    def atualizar_filtro_manifestos(self):
        try:
            self.carregar_manifestos()
        except Exception as erro:
            logger.error(f"Erro ao atualizar filtro de manifestos: {erro}")

    def carregar_manifestos(self):
        self.tabela_manifestos.setRowCount(0)
        tipo_periodo, mes, ano = self.obter_filtro_manifestos()
        manifestos = notas_service.listar_manifestos(tipo_periodo, mes, ano)

        for manifesto in manifestos:
            manifesto_id, nome_arquivo, data_importacao, total_notas, valor_notas, frete_total, peso_total = manifesto
            row = self.tabela_manifestos.rowCount()
            self.tabela_manifestos.insertRow(row)
            self.tabela_manifestos.setItem(row, 0, QTableWidgetItem(str(manifesto_id)))
            self.tabela_manifestos.setItem(row, 1, QTableWidgetItem(f"📁 {nome_arquivo}"))
            self.tabela_manifestos.setItem(row, 2, QTableWidgetItem(str(data_importacao)))
            self.tabela_manifestos.setItem(row, 3, QTableWidgetItem(f"R$ {valor_notas:,.2f}"))
            self.tabela_manifestos.setItem(row, 4, QTableWidgetItem(str(total_notas)))
            self.tabela_manifestos.setItem(row, 5, QTableWidgetItem(f"R$ {frete_total:,.2f}"))
            self.tabela_manifestos.setItem(row, 6, QTableWidgetItem(f"{peso_total:,.2f} kg"))

            for col in range(7):
                item = self.tabela_manifestos.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col in (3, 5, 6):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if col == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if manifestos:
            self.tabela_manifestos.selectRow(0)
            self.selecionar_manifesto()
        else:
            self.tabela_notas.setRowCount(0)
            self.resumo.setText("Nenhum manifesto encontrado para o período selecionado.")
            self.notas_ids = {}
            self.atualizar_selecao()

    def selecionar_manifesto(self):
        selecionado = self.tabela_manifestos.selectedItems()
        if not selecionado:
            return
        row = selecionado[0].row()
        manifesto_id = self.tabela_manifestos.item(row, 0).text()
        nome_arquivo = self.tabela_manifestos.item(row, 1).text()
        self.carregar_notas_manifesto(manifesto_id, nome_arquivo)

    def carregar_notas_manifesto(self, manifesto_id, nome_arquivo):
        self.tabela_notas.setRowCount(0)
        self.notas_ids = {}

        dados = notas_service.listar_notas_por_manifesto(manifesto_id)
        total_frete = 0
        total_valor_notas = 0
        total_peso = 0

        for linha in dados:
            id_nota, chave_nfe, numero_cte, remetente, destinatario, origem, destino, valor_mercadoria, frete, peso, status = linha
            frete = frete or 0
            valor_mercadoria = valor_mercadoria or 0
            total_valor_notas += valor_mercadoria
            peso = peso or 0
            total_frete += frete
            total_peso += peso
            cte = numero_cte if numero_cte else chave_nfe

            if status != "Disponível":
                marcador = "—"
            elif id_nota in self.notas_marcadas:
                marcador = "☑"
            else:
                marcador = "☐"

            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            self.tabela_notas.setItem(row, 0, QTableWidgetItem(marcador))
            self.tabela_notas.setItem(row, 1, QTableWidgetItem(str(cte or "-")))
            self.tabela_notas.setItem(row, 2, QTableWidgetItem(str(remetente or "-")))
            self.tabela_notas.setItem(row, 3, QTableWidgetItem(str(destinatario or "-")))
            self.tabela_notas.setItem(row, 4, QTableWidgetItem(str(origem or "-")))
            self.tabela_notas.setItem(row, 5, QTableWidgetItem(str(destino or "-")))
            self.tabela_notas.setItem(row, 6, QTableWidgetItem(f"R$ {frete:,.2f}"))
            self.tabela_notas.setItem(row, 7, QTableWidgetItem(f"{peso:,.2f} kg"))
            self.tabela_notas.setItem(row, 8, QTableWidgetItem(str(status or "-")))

            for col in range(9):
                item = self.tabela_notas.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col in (6, 7):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if col in (0, 8):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.notas_ids[row] = id_nota

        self.resumo.setText(
            f"{nome_arquivo}   |   Notas: {len(dados)}   |   Valor Notas: R$ {total_valor_notas:,.2f}   |   "
            f"Frete Total: R$ {total_frete:,.2f}   |   Peso Total: {total_peso:,.2f} kg"
        )
        self.atualizar_selecao()

    def clicar_na_nota(self, row, column):
        if row < 0 or row >= self.tabela_notas.rowCount():
            return

        valores = []
        for c in range(self.tabela_notas.columnCount()):
            item = self.tabela_notas.item(row, c)
            valores.append(item.text() if item else "")

        status = valores[8]
        id_nota = self.notas_ids.get(row)

        if not id_nota:
            return

        if status != "Disponível":
            QMessageBox.warning(
                self, "Atenção",
                f"Essa nota não está disponível (status: {status}).\n"
                "Notas em viagem ou entregues não podem ser selecionadas."
            )
            return

        if id_nota in self.notas_marcadas:
            self.notas_marcadas.remove(id_nota)
            valores[0] = "☐"
        else:
            self.notas_marcadas.add(id_nota)
            valores[0] = "☑"

        for c, v in enumerate(valores):
            self.tabela_notas.item(row, c).setText(v)

        self.atualizar_selecao()

    def atualizar_selecao(self):
        self.label_selecao.setText(f"Notas selecionadas: {len(self.notas_marcadas)}")

    def criar_viagem_selecionadas(self):
        if not self.notas_marcadas:
            QMessageBox.warning(self, "Atenção", "Selecione pelo menos uma nota.")
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)

        if not caminhao_id or "Nenhum" in caminhao_texto:
            QMessageBox.warning(self, "Atenção", "Selecione um caminhão válido.")
            return

        motorista = self.entrada_motorista_viagem.text().strip()
        if not motorista:
            QMessageBox.warning(self, "Atenção", "Informe o motorista da viagem.")
            return

        notas_ids = list(self.notas_marcadas)
        valido, mensagem, _ = viagem_service.validar_capacidade(caminhao_id, notas_ids)
        if not valido:
            reply = QMessageBox.question(
                self, "Aviso de Capacidade",
                f"{mensagem}\n\nDeseja continuar mesmo assim?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            viagem_id = viagem_service.criar_viagem_com_notas(caminhao_id, notas_ids, motorista)
        except Exception as erro:
            QMessageBox.critical(self, "Erro ao criar viagem", str(erro))
            self.selecionar_manifesto()
            return

        QMessageBox.information(
            self, "Viagem criada",
            f"Viagem #{viagem_id} criada com sucesso!\n{len(notas_ids)} nota(s) adicionada(s)."
        )

        self.entrada_motorista_viagem.clear()
        self.notas_marcadas.clear()
        self.selecionar_manifesto()

    def apagar_viagem_selecionada(self):
        viagem_id, ok = QInputDialog.getInt(
            self, "Apagar Viagem",
            "Informe o número da viagem que deseja apagar:", min=1
        )
        if not ok or not viagem_id:
            return

        reply = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Deseja apagar a viagem #{viagem_id}?\n\n"
            "As notas dessa viagem voltarão a ficar disponíveis para serem adicionadas em outra viagem."
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            total_notas = notas_service.apagar_viagem(viagem_id)
            QMessageBox.information(
                self, "Viagem apagada",
                f"Viagem #{viagem_id} apagada com sucesso!\n{total_notas} nota(s) liberada(s)."
            )
            self.selecionar_manifesto()
        except Exception as erro:
            QMessageBox.critical(self, "Erro ao apagar viagem", str(erro))

    def abrir_novo_veiculo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cadastrar Novo Veículo")
        dialog.setMinimumSize(420, 420)
        dialog.setStyleSheet("background-color: #0B1120;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        lbl = QLabel("🚚 Novo Veículo")
        lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        layout.addWidget(lbl)

        entrada_placa = QLineEdit()
        entrada_placa.setPlaceholderText("Placa ou nome")
        style_entry(entrada_placa)
        layout.addWidget(entrada_placa)

        entrada_modelo = QLineEdit()
        entrada_modelo.setPlaceholderText("Modelo")
        style_entry(entrada_modelo)
        layout.addWidget(entrada_modelo)

        entrada_motorista = QLineEdit()
        entrada_motorista.setPlaceholderText("Motorista padrão")
        style_entry(entrada_motorista)
        layout.addWidget(entrada_motorista)

        entrada_capacidade = QLineEdit()
        entrada_capacidade.setPlaceholderText("Capacidade em kg")
        style_entry(entrada_capacidade)
        layout.addWidget(entrada_capacidade)

        entrada_media = QLineEdit()
        entrada_media.setPlaceholderText("Média km/L")
        style_entry(entrada_media)
        layout.addWidget(entrada_media)

        def salvar():
            try:
                placa = entrada_placa.text().strip()
                modelo = entrada_modelo.text().strip()
                motorista = entrada_motorista.text().strip()
                capacidade = float(entrada_capacidade.text().replace(",", "."))
                media = float(entrada_media.text().replace(",", "."))

                if not placa or not modelo:
                    QMessageBox.warning(dialog, "Atenção", "Informe placa/nome e modelo.")
                    return

                notas_service.cadastrar_caminhao(placa, modelo, motorista, capacidade, media)
                QMessageBox.information(dialog, "Sucesso", "Veículo cadastrado com sucesso!")
                dialog.accept()
                self.carregar_caminhoes()
            except Exception as erro:
                logger.error(f"Erro ao cadastrar veículo: {erro}")
                QMessageBox.critical(dialog, "Erro", "Verifique os dados informados.")

        btn = QPushButton("Salvar Veículo")
        style_botao_verde(btn)
        btn.setFixedHeight(42)
        btn.clicked.connect(salvar)
        layout.addWidget(btn)

        dialog.exec()
