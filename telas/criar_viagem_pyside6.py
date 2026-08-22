"""
Tela Criar Viagem - PySide6 com visual CTk (fundo escuro #0B1120, cards brancos)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QAbstractItemView, QFrame, QLineEdit, QMessageBox, QDialog,
    QInputDialog
)
from PySide6.QtCore import Qt

from services.viagem_service import viagem_service


def _style_botao_verde(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #15803d; color: #FFFFFF; border: none;
            border-radius: 8px; padding: 10px 24px;
            font-weight: 600; font-size: 13px;
        }
        QPushButton:hover { background-color: #166534; }
        QPushButton:pressed { background-color: #14532d; }
    """)

def _style_botao_cinza(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #374151; color: #FFFFFF; border: none;
            border-radius: 8px; padding: 10px 24px;
            font-weight: 600; font-size: 13px;
        }
        QPushButton:hover { background-color: #111827; }
    """)

def _style_botao_azul(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #2563EB; color: #FFFFFF; border: none;
            border-radius: 8px; padding: 10px 24px;
            font-weight: 600; font-size: 13px;
        }
        QPushButton:hover { background-color: #1D4ED8; }
    """)

def _style_card(frame: QFrame):
    frame.setStyleSheet("""
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
        }
        QLabel { background: transparent; color: #111827; }
    """)

def _style_entry(entry: QLineEdit):
    entry.setStyleSheet("""
        QLineEdit {
            background-color: #f9fafb; color: #111827;
            border: 1px solid #d1d5db; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
        }
        QLineEdit:focus { border-color: #15803d; }
    """)

def _style_combo(combo: QComboBox):
    combo.setStyleSheet("""
        QComboBox {
            background-color: #f9fafb; color: #111827;
            border: 1px solid #d1d5db; border-radius: 8px;
            padding: 8px 14px; font-size: 13px;
        }
        QComboBox:focus { border-color: #15803d; }
        QComboBox::drop-down { border: none; width: 30px; }
        QComboBox QAbstractItemView {
            background-color: #ffffff; color: #111827;
            border: 1px solid #d1d5db;
            selection-background-color: #15803d;
            selection-color: #ffffff;
        }
    """)

def _style_tabela(table: QTableWidget):
    table.setStyleSheet("""
        QTableWidget {
            background-color: #ffffff; color: #111827;
            border: none; gridline-color: #e5e7eb; font-size: 13px;
        }
        QHeaderView::section {
            background-color: #f9fafb; color: #374151;
            padding: 10px; border: none;
            border-bottom: 2px solid #e5e7eb;
            font-weight: 600; font-size: 12px;
        }
        QTableWidget::item {
            padding: 8px 10px; border-bottom: 1px solid #f3f4f6;
        }
        QTableWidget::item:selected {
            background-color: rgba(21, 128, 61, 0.1); color: #111827;
        }
    """)


class TelaCriarViagem(QWidget):
    def __init__(self, cliente_pre_selecionado=None, parent=None):
        super().__init__(parent)
        self.cliente_pre_selecionado = cliente_pre_selecionado
        self.cliente_selecionado_id = None
        self.notas_disponiveis = []
        self.notas_selecionadas = set()
        self.caminhoes_map = {}
        self.notas_ids = {}

        self.setStyleSheet("background-color: #0B1120;")
        self._setup_ui()
        self._carregar_caminhoes()

        if cliente_pre_selecionado:
            self._selecionar_cliente(*cliente_pre_selecionado)

    def _setup_ui(self):
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

        lbl_tag = QLabel("OPERACIONAL")
        lbl_tag.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")
        hl.addWidget(lbl_tag)

        lbl_titulo = QLabel("Criar Nova Viagem")
        lbl_titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
        hl.addWidget(lbl_titulo)

        lbl_sub = QLabel("Selecione um cliente e as notas para criar uma nova viagem")
        lbl_sub.setStyleSheet("font-size: 12px; color: #9ca3af;")
        hl.addWidget(lbl_sub)
        layout.addWidget(header)

        # Card Busca Cliente
        card_cliente = QFrame()
        _style_card(card_cliente)
        cl = QVBoxLayout(card_cliente)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(12)

        lbl_busca = QLabel("👤 Selecione o Cliente")
        lbl_busca.setStyleSheet("font-size: 14px; font-weight: bold; color: #111827;")
        cl.addWidget(lbl_busca)

        linha_busca = QHBoxLayout()
        self.entrada_busca_cliente = QLineEdit()
        self.entrada_busca_cliente.setPlaceholderText("Digite o nome ou CNPJ do cliente...")
        _style_entry(self.entrada_busca_cliente)
        linha_busca.addWidget(self.entrada_busca_cliente)

        btn_buscar = QPushButton("🔍 Buscar")
        _style_botao_azul(btn_buscar)
        btn_buscar.setFixedHeight(44)
        btn_buscar.clicked.connect(self._buscar_cliente)
        linha_busca.addWidget(btn_buscar)
        cl.addLayout(linha_busca)

        self.lbl_cliente_selecionado = QLabel("Nenhum cliente selecionado")
        self.lbl_cliente_selecionado.setStyleSheet("font-size: 12px; color: #64748B;")
        cl.addWidget(self.lbl_cliente_selecionado)
        layout.addWidget(card_cliente)

        # Card Notas
        card_notas = QFrame()
        _style_card(card_notas)
        cn = QVBoxLayout(card_notas)
        cn.setContentsMargins(16, 16, 16, 16)
        cn.setSpacing(12)

        topo_notas = QHBoxLayout()
        lbl_notas = QLabel("📦 Selecione as Notas")
        lbl_notas.setStyleSheet("font-size: 14px; font-weight: bold; color: #111827;")
        topo_notas.addWidget(lbl_notas)
        topo_notas.addStretch()

        btn_todas = QPushButton("✅ Todas")
        _style_botao_verde(btn_todas)
        btn_todas.setFixedHeight(36)
        btn_todas.clicked.connect(self._selecionar_todas)
        topo_notas.addWidget(btn_todas)

        btn_limpar = QPushButton("⏹ Limpar")
        _style_botao_cinza(btn_limpar)
        btn_limpar.setFixedHeight(36)
        btn_limpar.clicked.connect(self._limpar_selecao)
        topo_notas.addWidget(btn_limpar)
        cn.addLayout(topo_notas)

        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(6)
        self.tabela_notas.setHorizontalHeaderLabels([
            "Sel.", "Nota/CT-e", "Cidade", "Peso", "Data", "Status"
        ])
        self.tabela_notas.horizontalHeader().setStretchLastSection(True)
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_notas.verticalHeader().setVisible(False)
        self.tabela_notas.setColumnWidth(0, 55)
        self.tabela_notas.setColumnWidth(1, 180)
        self.tabela_notas.setColumnWidth(2, 200)
        self.tabela_notas.setColumnWidth(3, 120)
        self.tabela_notas.setColumnWidth(4, 150)
        self.tabela_notas.setColumnWidth(5, 120)
        _style_tabela(self.tabela_notas)
        self.tabela_notas.cellClicked.connect(self._clicar_nota)
        cn.addWidget(self.tabela_notas)
        layout.addWidget(card_notas, 1)

        # Card Resumo
        self.card_resumo = QFrame()
        _style_card(self.card_resumo)
        cr = QHBoxLayout(self.card_resumo)
        cr.setContentsMargins(16, 14, 16, 14)
        cr.setSpacing(12)

        self.card_qtd = self._criar_card_resumo("QUANTIDADE", "0", "#111827", cr)
        self.card_peso = self._criar_card_resumo("PESO TOTAL", "0 kg", "#b91c1c", cr)
        self.card_frete = self._criar_card_resumo("FRETE TOTAL", "R$ 0,00", "#15803d", cr)
        self.card_volumes = self._criar_card_resumo("VOLUMES", "0", "#2563EB", cr)
        layout.addWidget(self.card_resumo)

        # Linha Criação
        linha_criacao = QHBoxLayout()

        lbl_cam = QLabel("CAMINHÃO:")
        lbl_cam.setStyleSheet("font-size: 12px; font-weight: bold; color: #374151;")
        linha_criacao.addWidget(lbl_cam)

        self.combo_caminhoes = QComboBox()
        self.combo_caminhoes.addItem("Nenhum caminhão cadastrado")
        _style_combo(self.combo_caminhoes)
        self.combo_caminhoes.setFixedWidth(280)
        linha_criacao.addWidget(self.combo_caminhoes)

        lbl_mot = QLabel("MOTORISTA:")
        lbl_mot.setStyleSheet("font-size: 12px; font-weight: bold; color: #374151;")
        linha_criacao.addWidget(lbl_mot)

        self.entrada_motorista = QLineEdit()
        self.entrada_motorista.setPlaceholderText("Nome do motorista")
        _style_entry(self.entrada_motorista)
        self.entrada_motorista.setFixedWidth(200)
        linha_criacao.addWidget(self.entrada_motorista)

        linha_criacao.addStretch()

        btn_criar = QPushButton("🚚 CRIAR VIAGEM")
        _style_botao_verde(btn_criar)
        btn_criar.setFixedHeight(46)
        btn_criar.setFixedWidth(180)
        btn_criar.clicked.connect(self._criar_viagem)
        linha_criacao.addWidget(btn_criar)
        layout.addLayout(linha_criacao)

        # Label validação
        self.lbl_validacao = QLabel("Selecione notas e um caminhão para validar a viagem.")
        self.lbl_validacao.setStyleSheet("font-size: 12px; color: #6B7280;")
        layout.addWidget(self.lbl_validacao)

        layout.addStretch()

    def _criar_card_resumo(self, titulo, valor, cor, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QLabel { background: transparent; }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)

        tl = QLabel(titulo)
        tl.setStyleSheet("font-size: 11px; font-weight: bold; color: #6B7280;")
        cl.addWidget(tl)

        vl = QLabel(valor)
        vl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {cor};")
        cl.addWidget(vl)

        parent_layout.addWidget(card, 1)
        return vl

    def _carregar_caminhoes(self):
        self.caminhoes_map = {}
        self.combo_caminhoes.clear()
        caminhoes = viagem_service.listar_caminhoes_disponiveis()
        valores = []

        for caminhao in caminhoes:
            caminhao_id, placa, modelo, motorista, capacidade = caminhao
            texto = f"{modelo} | {placa} | {capacidade:,.0f} kg"
            self.caminhoes_map[texto] = caminhao_id
            valores.append(texto)

        if valores:
            self.combo_caminhoes.addItems(valores)
            self.combo_caminhoes.setCurrentText(valores[0])
        else:
            self.combo_caminhoes.addItem("Nenhum caminhão cadastrado")

    def _buscar_cliente(self):
        termo = self.entrada_busca_cliente.text().strip()
        if not termo or len(termo) < 2:
            QMessageBox.warning(self, "Atenção", "Digite pelo menos 2 caracteres para buscar.")
            return

        clientes = viagem_service.buscar_clientes(termo)
        if not clientes:
            QMessageBox.information(self, "Resultado", "Nenhum cliente encontrado.")
            return

        self._mostrar_dialogo_clientes(clientes)

    def _mostrar_dialogo_clientes(self, clientes):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Cliente")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet("background-color: #0B1120;")
        dl = QVBoxLayout(dialog)
        dl.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("Selecione o Cliente")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        dl.addWidget(lbl)

        tabela = QTableWidget()
        tabela.setColumnCount(3)
        tabela.setHorizontalHeaderLabels(["Nome", "Cidade", "UF"])
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.verticalHeader().setVisible(False)
        tabela.setColumnWidth(0, 250)
        tabela.setColumnWidth(1, 120)
        tabela.setColumnWidth(2, 50)
        _style_tabela(tabela)
        dl.addWidget(tabela)

        for cliente in clientes:
            cliente_id, nome, cnpj, cidade, uf = cliente
            row = tabela.rowCount()
            tabela.insertRow(row)
            tabela.setItem(row, 0, QTableWidgetItem(nome))
            tabela.setItem(row, 1, QTableWidgetItem(cidade or "-"))
            tabela.setItem(row, 2, QTableWidgetItem(uf or "-"))
            for c in range(3):
                item = tabela.item(row, c)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        def on_selecionar():
            selecionado = tabela.selectedItems()
            if not selecionado:
                QMessageBox.warning(dialog, "Atenção", "Selecione um cliente.")
                return
            row = selecionado[0].row()
            cliente_id = clientes[row][0]
            nome = clientes[row][1]
            self._selecionar_cliente(cliente_id, nome)
            dialog.accept()

        btn = QPushButton("Selecionar")
        _style_botao_verde(btn)
        btn.setFixedHeight(40)
        btn.clicked.connect(on_selecionar)
        dl.addWidget(btn)

        dialog.exec()

    def _selecionar_cliente(self, cliente_id, nome):
        self.cliente_selecionado_id = cliente_id
        self.lbl_cliente_selecionado.setText(
            f"Cliente selecionado: {nome}  •  {len(self.notas_selecionadas)} nota(s) preservadas"
        )
        self.lbl_cliente_selecionado.setStyleSheet("font-size: 12px; color: #16A34A;")
        self._carregar_notas_cliente()

    def _carregar_notas_cliente(self):
        if not self.cliente_selecionado_id:
            return

        self.tabela_notas.setRowCount(0)
        self.notas_ids = {}
        self.notas_disponiveis = []

        notas = viagem_service.listar_notas_cliente(
            self.cliente_selecionado_id,
            apenas_disponiveis=True,
            excluir_vinculadas=True
        )

        for nota in notas:
            # nota: (id, numero_cte, chave_nfe, cliente_nome, cidade, peso, frete, data, status)
            nota_id = nota[0]
            numero = nota[1] or nota[2] or "-"
            cidade = nota[4] or "-"
            peso = nota[5] or 0
            data = nota[7][:10] if nota[7] else "-"
            status = nota[8] or "Disponível"

            marcador = "☑" if nota_id in self.notas_selecionadas else "☐"

            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            self.tabela_notas.setItem(row, 0, QTableWidgetItem(marcador))
            self.tabela_notas.setItem(row, 1, QTableWidgetItem(str(numero)))
            self.tabela_notas.setItem(row, 2, QTableWidgetItem(str(cidade)))
            self.tabela_notas.setItem(row, 3, QTableWidgetItem(f"{peso:,.2f} kg"))
            self.tabela_notas.setItem(row, 4, QTableWidgetItem(str(data)))
            self.tabela_notas.setItem(row, 5, QTableWidgetItem(str(status)))

            for c in range(6):
                item = self.tabela_notas.item(row, c)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if c in (3,):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.notas_ids[row] = nota_id
            self.notas_disponiveis.append(nota_id)

        self._atualizar_resumo()
        self._atualizar_validacao()

    def _clicar_nota(self, row, column):
        if row < 0 or row >= self.tabela_notas.rowCount():
            return

        nota_id = self.notas_ids.get(row)
        if not nota_id:
            return

        item = self.tabela_notas.item(row, 0)
        if not item:
            return

        if item.text() == "☐":
            item.setText("☑")
            self.notas_selecionadas.add(nota_id)
        elif item.text() == "☑":
            item.setText("☐")
            self.notas_selecionadas.discard(nota_id)

        self._atualizar_resumo()
        self._atualizar_validacao()

    def _selecionar_todas(self):
        for row in range(self.tabela_notas.rowCount()):
            nota_id = self.notas_ids.get(row)
            if nota_id:
                self.tabela_notas.item(row, 0).setText("☑")
                self.notas_selecionadas.add(nota_id)
        self._atualizar_resumo()
        self._atualizar_validacao()

    def _limpar_selecao(self):
        self.notas_selecionadas.clear()
        for row in range(self.tabela_notas.rowCount()):
            self.tabela_notas.item(row, 0).setText("☐")
        self._atualizar_resumo()
        self._atualizar_validacao()

    def _atualizar_resumo(self):
        notas_ids = list(self.notas_selecionadas)
        resumo = viagem_service.calcular_resumo_selecao(notas_ids)

        self.card_qtd.setText(str(resumo.get("quantidade", 0)))
        self.card_peso.setText(f"{resumo.get('peso_total', 0):,.2f} kg")
        self.card_frete.setText(f"R$ {resumo.get('frete_total', 0):,.2f}")
        self.card_volumes.setText(str(resumo.get("volumes", 0)))

    def _atualizar_validacao(self):
        if not self.notas_selecionadas:
            self.lbl_validacao.setText("Selecione notas para validar a viagem.")
            self.lbl_validacao.setStyleSheet("font-size: 12px; color: #6B7280;")
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        if not caminhao_texto or "Nenhum" in caminhao_texto:
            self.lbl_validacao.setText("Selecione um caminhão para validar a capacidade.")
            self.lbl_validacao.setStyleSheet("font-size: 12px; color: #F59E0B;")
            return

        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        if not caminhao_id:
            self.lbl_validacao.setText("Caminhão não encontrado na lista atual.")
            self.lbl_validacao.setStyleSheet("font-size: 12px; color: #DC2626;")
            return

        valido, mensagem, _ = viagem_service.validar_capacidade(
            caminhao_id,
            list(self.notas_selecionadas)
        )

        if valido:
            self.lbl_validacao.setText(f"Capacidade OK para {caminhao_texto}.")
            self.lbl_validacao.setStyleSheet("font-size: 12px; color: #15803D;")
        else:
            self.lbl_validacao.setText(mensagem)
            self.lbl_validacao.setStyleSheet("font-size: 12px; color: #DC2626;")

    def _criar_viagem(self):
        if not self.cliente_selecionado_id:
            QMessageBox.warning(self, "Atenção", "Selecione um cliente primeiro.")
            return

        if not self.notas_selecionadas:
            QMessageBox.warning(self, "Atenção", "Selecione pelo menos uma nota.")
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)

        if not caminhao_id or "Nenhum" in caminhao_texto:
            QMessageBox.warning(self, "Atenção", "Selecione um caminhão válido.")
            return

        motorista = self.entrada_motorista.text().strip()
        if not motorista:
            QMessageBox.warning(self, "Atenção", "Informe o motorista da viagem.")
            return

        valido, mensagem, _ = viagem_service.validar_capacidade(
            caminhao_id,
            list(self.notas_selecionadas)
        )

        if not valido:
            reply = QMessageBox.question(
                self, "Aviso de Capacidade",
                f"{mensagem}\n\nDeseja continuar mesmo assim?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            viagem_id = viagem_service.criar_viagem_com_notas(
                caminhao_id,
                list(self.notas_selecionadas),
                motorista
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro ao criar viagem", str(e))
            return

        QMessageBox.information(
            self, "Sucesso",
            f"Viagem #{viagem_id} criada com sucesso!\n"
            f"{len(self.notas_selecionadas)} nota(s) adicionada(s)."
        )

        self.entrada_motorista.clear()
        self.notas_selecionadas.clear()
        self.tabela_notas.setRowCount(0)
        self._atualizar_resumo()
        self._atualizar_validacao()
