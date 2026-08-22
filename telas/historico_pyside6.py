"""
Tela Histórico de Viagens - PySide6 com visual CTk (fundo escuro, cards brancos)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QDialog, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import datetime

from services.historico_service import historico_service

FONT_FAMILY = "Segoe UI"


def style_card(widget: QFrame, bg="#ffffff"):
    widget.setStyleSheet(f"""
        QFrame {{
            background-color: {bg};
            border: 1px solid #e5e7eb;
            border-radius: 16px;
        }}
        QLabel {{
            background: transparent;
            color: #111827;
        }}
    """)


def style_card_resumo(widget: QFrame):
    widget.setStyleSheet("""
        QFrame {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
        }
        QLabel {
            background: transparent;
        }
    """)


def style_botao_atualizar(btn: QPushButton):
    btn.setStyleSheet("""
        QPushButton {
            background-color: #111827;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover { background-color: #374151; }
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


class DialogoNotasViagem(QDialog):
    def __init__(self, viagem_id, parent=None):
        super().__init__(parent)
        self.viagem_id = viagem_id
        self.setWindowTitle(f"Notas da Viagem #{viagem_id}")
        self.setMinimumSize(1150, 720)
        self.setStyleSheet("background-color: #0B1120;")
        self._setup_ui()
        self._carregar_notas()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        lbl = QLabel(f"📦 DETALHES DA VIAGEM #{self.viagem_id}")
        lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #EF4444;")
        layout.addWidget(lbl)

        detalhes = historico_service.buscar_detalhes_viagem(self.viagem_id)
        if detalhes:
            id_viagem, data_saida, data_retorno, motorista, status_viagem, peso_total_banco, frete_total_banco, modelo, placa, capacidade = detalhes
            capacidade = capacidade or 0
            peso_total_banco = peso_total_banco or 0
            uso = (peso_total_banco / capacidade * 100) if capacidade > 0 else 0

            info = QFrame()
            style_card(info)
            il = QHBoxLayout(info)
            il.setContentsMargins(12, 12, 12, 12)
            il.setSpacing(8)

            def card_info(titulo, valor, cor="#111827"):
                c = QFrame()
                style_card_resumo(c)
                cl = QVBoxLayout(c)
                cl.setContentsMargins(12, 10, 12, 10)
                tl = QLabel(titulo)
                tl.setStyleSheet("font-size: 10px; font-weight: bold; color: #6b7280;")
                cl.addWidget(tl)
                vl = QLabel(valor)
                vl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {cor};")
                cl.addWidget(vl)
                return c

            il.addWidget(card_info("CAMINHÃO", f"{modelo or '-'} | {placa or '-'}"), 1)
            il.addWidget(card_info("MOTORISTA", motorista or "-"), 1)
            il.addWidget(card_info("SAÍDA", data_saida or "-"), 1)
            il.addWidget(card_info("RETORNO", data_retorno or "-"), 1)
            cor_status = "#15803d" if status_viagem == "Finalizada" else "#b91c1c"
            il.addWidget(card_info("STATUS", status_viagem or "-", cor_status), 1)
            il.addWidget(card_info("CAPACIDADE", f"{uso:.1f}% usada"), 1)
            layout.addWidget(info)

        frame = QFrame()
        style_card(frame)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 16, 16, 16)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "CT-e", "Remetente", "Cliente", "Origem", "Destino", "Frete", "Peso", "Status"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setColumnWidth(0, 180)
        self.tabela.setColumnWidth(1, 250)
        self.tabela.setColumnWidth(2, 250)
        self.tabela.setColumnWidth(3, 130)
        self.tabela.setColumnWidth(4, 140)
        self.tabela.setColumnWidth(5, 110)
        self.tabela.setColumnWidth(6, 110)
        self.tabela.setColumnWidth(7, 120)
        style_tabela(self.tabela)
        fl.addWidget(self.tabela)
        layout.addWidget(frame, 1)

        # Resumo
        resumo = QFrame()
        style_card(resumo)
        rl = QHBoxLayout(resumo)
        rl.setContentsMargins(16, 12, 16, 12)

        self.lbl_notas_resumo = QLabel("Notas: 0")
        self.lbl_notas_resumo.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        rl.addWidget(self.lbl_notas_resumo)

        self.lbl_peso_resumo = QLabel("Peso Total: 0 kg")
        self.lbl_peso_resumo.setStyleSheet("font-size: 15px; font-weight: bold; color: #b91c1c;")
        rl.addWidget(self.lbl_peso_resumo)

        self.lbl_frete_resumo = QLabel("Frete Total: R$ 0,00")
        self.lbl_frete_resumo.setStyleSheet("font-size: 15px; font-weight: bold; color: #15803d;")
        rl.addWidget(self.lbl_frete_resumo)
        rl.addStretch()
        layout.addWidget(resumo)

    def _carregar_notas(self):
        self.tabela.setRowCount(0)
        notas = historico_service.listar_notas_da_viagem(self.viagem_id)

        total_frete = 0
        total_peso = 0

        for nota in notas:
            id_nota, numero_cte, remetente, destinatario, origem, destino, valor_frete, peso, status = nota
            valor_frete = valor_frete or 0
            peso = peso or 0
            total_frete += valor_frete
            total_peso += peso

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(numero_cte or "-")))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(remetente or "-")))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(destinatario or "-")))
            self.tabela.setItem(row, 3, QTableWidgetItem(str(origem or "-")))
            self.tabela.setItem(row, 4, QTableWidgetItem(str(destino or "-")))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {valor_frete:,.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{peso:,.2f} kg"))
            self.tabela.setItem(row, 7, QTableWidgetItem(str(status or "-")))

            for col in range(8):
                item = self.tabela.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col in (5, 6):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.lbl_notas_resumo.setText(f"Notas: {len(notas)}")
        self.lbl_peso_resumo.setText(f"Peso Total: {total_peso:,.2f} kg")
        self.lbl_frete_resumo.setText(f"Frete Total: R$ {total_frete:,.2f}")


class TelaHistorico(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.viagens_ids = {}
        self._setup_ui()
        self.carregar_viagens()

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

        lbl_tag = QLabel("HISTÓRICO DE VIAGENS")
        lbl_tag.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")
        hl.addWidget(lbl_tag)

        lbl_titulo = QLabel("Viagens")
        lbl_titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
        hl.addWidget(lbl_titulo)

        lbl_sub = QLabel("Acompanhamento de viagens, notas, fretes e peso transportado.")
        lbl_sub.setStyleSheet("font-size: 12px; color: #9ca3af;")
        hl.addWidget(lbl_sub)
        layout.addWidget(header)

        # Resumo
        self.frame_resumo = QFrame()
        style_card(self.frame_resumo)
        rl = QHBoxLayout(self.frame_resumo)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.setSpacing(12)

        self.card_total = self._criar_card_resumo("VIAGENS", "0", 0, "#111827", rl)
        self.card_notas = self._criar_card_resumo("NOTAS", "0", 1, "#111827", rl)
        self.card_frete = self._criar_card_resumo("FRETE TOTAL", "R$ 0,00", 2, "#15803d", rl)
        self.card_peso = self._criar_card_resumo("PESO TOTAL", "0 kg", 3, "#b91c1c", rl)
        layout.addWidget(self.frame_resumo)

        # Tabela
        frame = QFrame()
        style_card(frame)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 16, 16, 16)
        fl.setSpacing(12)

        topo = QHBoxLayout()
        lbl_lista = QLabel("Lista de Viagens Criadas")
        lbl_lista.setStyleSheet("font-size: 17px; font-weight: bold; color: #111827;")
        topo.addWidget(lbl_lista)
        topo.addStretch()

        btn_atualizar = QPushButton("🔄 Atualizar")
        style_botao_atualizar(btn_atualizar)
        btn_atualizar.setFixedHeight(38)
        btn_atualizar.clicked.connect(self.carregar_viagens)
        topo.addWidget(btn_atualizar)
        fl.addLayout(topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(11)
        self.tabela.setHorizontalHeaderLabels([
            "Viagem", "Data Saída", "Caminhão", "Placa/Nome", "Motorista",
            "Status", "Notas", "Peso", "Frete", "Ver", "Finalizar"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setColumnWidth(0, 80)
        self.tabela.setColumnWidth(1, 150)
        self.tabela.setColumnWidth(2, 220)
        self.tabela.setColumnWidth(3, 140)
        self.tabela.setColumnWidth(4, 180)
        self.tabela.setColumnWidth(5, 120)
        self.tabela.setColumnWidth(6, 80)
        self.tabela.setColumnWidth(7, 130)
        self.tabela.setColumnWidth(8, 140)
        self.tabela.setColumnWidth(9, 110)
        self.tabela.setColumnWidth(10, 110)
        style_tabela(self.tabela)
        self.tabela.cellDoubleClicked.connect(self.clique_acao_viagem)
        fl.addWidget(self.tabela)

        layout.addWidget(frame, 1)
        layout.addStretch()

    def _criar_card_resumo(self, titulo, valor, col, cor, parent_layout):
        card = QFrame()
        style_card_resumo(card)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)

        tl = QLabel(titulo)
        tl.setStyleSheet("font-size: 10px; font-weight: bold; color: #6b7280;")
        cl.addWidget(tl)

        vl = QLabel(valor)
        vl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {cor};")
        cl.addWidget(vl)

        parent_layout.addWidget(card, 1)
        return vl

    def carregar_viagens(self):
        self.tabela.setRowCount(0)
        self.viagens_ids = {}

        viagens = historico_service.listar_viagens()

        total_viagens = len(viagens)
        total_notas = 0
        total_frete = 0
        total_peso = 0

        for viagem in viagens:
            viagem_id, data_saida, modelo, placa, motorista, status, peso_total, frete_total, qtd_notas = viagem
            peso_total = peso_total or 0
            frete_total = frete_total or 0
            qtd_notas = qtd_notas or 0

            total_notas += qtd_notas
            total_frete += frete_total
            total_peso += peso_total

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(f"#{viagem_id}"))
            self.tabela.setItem(row, 1, QTableWidgetItem(str(data_saida or "-")))
            self.tabela.setItem(row, 2, QTableWidgetItem(modelo or "-"))
            self.tabela.setItem(row, 3, QTableWidgetItem(placa or "-"))
            self.tabela.setItem(row, 4, QTableWidgetItem(motorista or "-"))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(status or "-")))
            self.tabela.setItem(row, 6, QTableWidgetItem(str(qtd_notas)))
            self.tabela.setItem(row, 7, QTableWidgetItem(f"{peso_total:,.2f} kg"))
            self.tabela.setItem(row, 8, QTableWidgetItem(f"R$ {frete_total:,.2f}"))
            self.tabela.setItem(row, 9, QTableWidgetItem("👁 Ver Notas"))
            finalizar_texto = "✅ Finalizar" if status != "Finalizada" else "Finalizada"
            self.tabela.setItem(row, 10, QTableWidgetItem(finalizar_texto))

            for col in range(11):
                item = self.tabela.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col in (0, 5, 6, 9, 10):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col in (7, 8):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.viagens_ids[row] = viagem_id

        self.card_total.setText(str(total_viagens))
        self.card_notas.setText(str(total_notas))
        self.card_frete.setText(f"R$ {total_frete:,.2f}")
        self.card_peso.setText(f"{total_peso:,.2f} kg")

    def clique_acao_viagem(self, row, column):
        if row < 0 or row >= self.tabela.rowCount():
            return

        viagem_id = self.viagens_ids.get(row)
        if not viagem_id:
            return

        valores = []
        for c in range(self.tabela.columnCount()):
            item = self.tabela.item(row, c)
            valores.append(item.text() if item else "")

        status = valores[5]

        if column == 9:  # Ver Notas
            self.abrir_notas_viagem(viagem_id)
            return

        if column == 10:  # Finalizar
            if status == "Finalizada":
                QMessageBox.information(self, "Viagem finalizada", "Essa viagem já está finalizada.")
                return

            reply = QMessageBox.question(self, "Finalizar viagem", f"Deseja finalizar a viagem #{viagem_id}?")
            if reply != QMessageBox.StandardButton.Yes:
                return

            data_retorno = datetime.now().strftime("%d/%m/%Y %H:%M")
            historico_service.finalizar_viagem(viagem_id, data_retorno)
            QMessageBox.information(self, "Sucesso", f"Viagem #{viagem_id} finalizada com sucesso!")
            self.carregar_viagens()

    def abrir_notas_viagem(self, viagem_id):
        dialogo = DialogoNotasViagem(viagem_id, self)
        dialogo.exec()
