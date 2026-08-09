"""
Tela Criar Viagem - CW Transportadora - PySide6
Montagem de viagens por cliente e seleção de notas.
Migração completa da tela CustomTkinter para PySide6.
"""

from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSizePolicy, QAbstractItemView,
    QComboBox, QDialog,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor

from services.viagem_service import viagem_service
from services.rascunho_viagem_service import (
    atualizar_marcacao_nota,
    salvar_rascunho_viagem,
    carregar_rascunho_viagem,
    limpar_rascunho_viagem,
    adicionar_historico_viagem,
    listar_historico_viagem,
)
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWTable, CWBadge, BadgeVariant
from utils.helpers import formatar_moeda, formatar_peso, parse_numero
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaCriarViagem(QWidget):
    """Tela de criação de viagens com seleção de cliente e notas (PySide6)."""
    
    # Sinais para comunicação thread-safe
    _notas_carregadas = Signal(list)

    def __init__(self, parent=None, cliente_pre_selecionado: tuple = None):
        super().__init__(parent)

        self.cliente_selecionado = None
        self.cliente_selecionado_id = None
        self.notas_selecionadas: set = set()
        self.caminhoes_map: dict = {}
        self.caminhoes_catalogo: list = []
        self.notas_ids: dict = {}
        self.notas_catalogo: dict = {}
        self.notas_selecionadas_tree_ids: dict = {}

        self._resumo_labels: dict[str, QLabel] = {}
        self._cliente_pre_selecionado = cliente_pre_selecionado  # (id, nome) tuple
        
        # Conectar sinal para thread-safe comunicação
        self._notas_carregadas.connect(self._preencher_tabela_notas)

        self._setup_ui()
        self._carregar_caminhoes()
        
        # Se houver cliente pré-selecionado, carrega automaticamente
        if self._cliente_pre_selecionado:
            QTimer.singleShot(100, self._selecionar_cliente_com_delay)
        else:
            QTimer.singleShot(200, self._carregar_rascunho)

    # ------------------------------------------------------------------ UI
    def _setup_ui(self):
        c = cw_theme.colors
        t = cw_theme.spacing

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {c['bg_primary']}; border: none; }}")
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(t._2XL, t._2XL, t._2XL, t._2XL)
        cl.setSpacing(t.XL)
        content.setLayout(cl)
        scroll.setWidget(content)

        # Busca cliente
        cl.addWidget(self._build_busca_cliente())

        # Notas: tabela + selecionadas
        row = QHBoxLayout()
        row.setSpacing(t.LG)
        row.addWidget(self._build_tabela_notas(), stretch=2)
        row.addWidget(self._build_resumo(), stretch=1)
        cl.addLayout(row)

        # Botões de ação
        cl.addWidget(self._build_acoes())

        cl.addStretch()

        # Criação da viagem
        cl.addWidget(self._build_criacao_viagem())

        # Validação
        self.label_validacao = QLabel("Selecione notas e um caminhão para validar a viagem.")
        self.label_validacao.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self.label_validacao.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        self.label_validacao.setWordWrap(True)
        cl.addWidget(self.label_validacao)

        # Histórico rápido
        self.label_historico = QLabel("Histórico rápido: ainda sem viagens criadas.")
        self.label_historico.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self.label_historico.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        self.label_historico.setWordWrap(True)
        cl.addWidget(self.label_historico)

    def _build_busca_cliente(self) -> CWCard:
        c = cw_theme.colors
        t = cw_theme.spacing
        card = CWCard(padding=t.XL)

        lbl = QLabel("Selecione o Cliente")
        lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        card.add_widget(lbl)

        row = QHBoxLayout()
        row.setSpacing(t.MD)

        self.entrada_busca = QLineEdit()
        self.entrada_busca.setPlaceholderText("Digite o nome ou CNPJ do cliente...")
        self.entrada_busca.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border_default']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{
                border: 1px solid {c['border_focus']};
            }}
        """)
        self.entrada_busca.returnPressed.connect(self._buscar_cliente)
        row.addWidget(self.entrada_busca, stretch=1)

        btn_buscar = CWButton("Buscar", ButtonVariant.PRIMARY, ButtonSize.MD)
        btn_buscar.clicked.connect(self._buscar_cliente)
        row.addWidget(btn_buscar)

        card.add_layout(row)

        self.label_cliente = QLabel("Nenhum cliente selecionado")
        self.label_cliente.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self.label_cliente.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        card.add_widget(self.label_cliente)

        return card

    def _build_tabela_notas(self) -> CWCard:
        c = cw_theme.colors
        t = cw_theme.spacing
        card = CWCard(padding=t.XL)

        # Título + botões
        row = QHBoxLayout()
        titulo = QLabel("Selecione as Notas")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        titulo.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        row.addWidget(titulo)
        row.addStretch()

        btn_todas = CWButton("Todas", ButtonVariant.SUCCESS, ButtonSize.SM)
        btn_todas.clicked.connect(self._selecionar_todas)
        row.addWidget(btn_todas)

        btn_limpar = CWButton("Limpar", ButtonVariant.SECONDARY, ButtonSize.SM)
        btn_limpar.clicked.connect(self._limpar_selecao)
        row.addWidget(btn_limpar)

        card.add_layout(row)

        # Tabela - usando CWTable
        colunas = ["Sel.", "Nota/CT-c", "Cidade", "Peso", "Data", "Status"]
        self.tabela_notas = CWTable(colunas)
        self.tabela_notas.setMinimumHeight(300)

        header = self.tabela_notas.horizontalHeader()
        col_widths = [55, 180, 200, 120, 150, 120]
        for i, w in enumerate(col_widths):
            header.resizeSection(i, w)
        header.setStretchLastSection(True)

        self.tabela_notas.cellClicked.connect(self._clicar_na_nota)
        card.add_widget(self.tabela_notas)
        return card

    def _build_selecionadas(self) -> CWCard:
        c = cw_theme.colors
        t = cw_theme.spacing
        card = CWCard(padding=t.XL)

        lbl = QLabel("Selecionadas")
        lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD, bold=True))
        lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        card.add_widget(lbl)

        self.label_qtd_selecionadas = QLabel("0 notas marcadas")
        self.label_qtd_selecionadas.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self.label_qtd_selecionadas.setStyleSheet(f"color: {c['primary']}; background: transparent;")
        card.add_widget(self.label_qtd_selecionadas)

        colunas = ["Nota", "Peso"]
        self.tabela_selecionadas = CWTable(colunas)
        self.tabela_selecionadas.setMinimumHeight(250)

        h = self.tabela_selecionadas.horizontalHeader()
        col_widths = [140, 90]
        for i, w in enumerate(col_widths):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)
        card.add_widget(self.tabela_selecionadas)

        btn_remover = CWButton("Remover", ButtonVariant.DANGER, ButtonSize.SM)
        btn_remover.clicked.connect(self._remover_nota_selecionada)
        card.add_widget(btn_remover)

        return card

    def _build_resumo(self) -> QFrame:
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {c['bg_secondary']}; border-radius: {r.LG}px; border: 1px solid {c['border_subtle']}; }}")
        layout = QHBoxLayout()
        layout.setContentsMargins(t.XL, t.MD, t.XL, t.MD)
        layout.setSpacing(t.LG)
        frame.setLayout(layout)

        for titulo, chave, cor in [
            ("QUANTIDADE", "qtd", c["text_primary"]),
            ("PESO TOTAL", "peso", c["primary"]),
            ("FRETE TOTAL", "frete", c["success"]),
            ("VOLUMES", "volumes", c["info"]),
        ]:
            card_frame = QFrame()
            card_frame.setStyleSheet(f"QFrame {{ background-color: {c['bg_primary']}; border-radius: {r.MD}px; border: none; }}")
            cl = QVBoxLayout()
            cl.setContentsMargins(t.MD, t.SM, t.MD, t.SM)
            card_frame.setLayout(cl)

            t_lbl = QLabel(titulo)
            t_lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
            t_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
            cl.addWidget(t_lbl)

            v = QLabel("0")
            v.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
            v.setStyleSheet(f"color: {cor}; background: transparent;")
            cl.addWidget(v)

            self._resumo_labels[chave] = v
            layout.addWidget(card_frame)

        return frame

    def _build_criacao_viagem(self) -> QFrame:
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {c['bg_secondary']}; border-radius: {r.LG}px; border: 1px solid {c['border_subtle']}; }}")
        layout = QHBoxLayout()
        layout.setContentsMargins(t.XL, t.MD, t.XL, t.MD)
        layout.setSpacing(t.MD)
        frame.setLayout(layout)

        lbl_caminhao = QLabel("CAMINHÃO:")
        lbl_caminhao.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl_caminhao.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_caminhao)

        self.combo_caminhoes = QComboBox()
        self.combo_caminhoes.setMinimumHeight(42)
        self.combo_caminhoes.setMinimumWidth(250)
        self.combo_caminhoes.setStyleSheet(f"""
            QComboBox {{ background-color: {c['bg_tertiary']}; color: {c['text_primary']};
                border: 1.5px solid {c['border_subtle']}; border-radius: {r.MD}px;
                padding: {t.SM}px {t.MD}px; font-size: {cw_theme.typography.FONT_SIZE_MD}px; }}
            QComboBox:focus {{ border-color: {c['border_focus']}; }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self.combo_caminhoes.currentTextChanged.connect(lambda: self._atualizar_validacao())
        layout.addWidget(self.combo_caminhoes)

        lbl_motorista = QLabel("MOTORISTA:")
        lbl_motorista.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl_motorista.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_motorista)

        self.entrada_motorista = QLineEdit()
        self.entrada_motorista.setPlaceholderText("Nome do motorista...")
        self.entrada_motorista.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{
                border: 1px solid {c['border_focus']};
            }}
        """)
        layout.addWidget(self.entrada_motorista)

        layout.addStretch()

        btn_salvar_rasc = CWButton("Rascunho", ButtonVariant.SECONDARY, ButtonSize.MD)
        btn_salvar_rasc.clicked.connect(self._salvar_rascunho_atual)
        layout.addWidget(btn_salvar_rasc)

        btn_carregar = CWButton("Carregar", ButtonVariant.SECONDARY, ButtonSize.MD)
        btn_carregar.clicked.connect(self._carregar_rascunho)
        layout.addWidget(btn_carregar)

        btn_limpar = CWButton("Limpar", ButtonVariant.GHOST, ButtonSize.MD)
        btn_limpar.clicked.connect(self._limpar_rascunho)
        layout.addWidget(btn_limpar)

        btn_criar = CWButton("CRIAR VIAGEM", ButtonVariant.SUCCESS, ButtonSize.MD)
        btn_criar.clicked.connect(self._criar_viagem)
        layout.addWidget(btn_criar)

        return frame

    # ------------------------------------------------------------------ Lógica
    def _selecionar_cliente_com_delay(self):
        """Seleciona cliente pré-selecionado da busca global."""
        if self._cliente_pre_selecionado:
            cliente_id, cliente_nome = self._cliente_pre_selecionado
            self._selecionar_cliente(cliente_id, cliente_nome)
    
    def _carregar_caminhoes(self):
        self.caminhoes_map = {}
        self.caminhoes_catalogo = []
        self.combo_caminhoes.clear()
        caminhoes = viagem_service.listar_caminhoes_disponiveis()
        for caminhao in caminhoes:
            cid, placa, modelo, motorista, capacidade = caminhao
            texto = f"{modelo} | {placa} | {capacidade:,.0f} kg"
            self.caminhoes_map[texto] = cid
            self.caminhoes_catalogo.append({"id": cid, "texto": texto, "capacidade": capacidade or 0})
            self.combo_caminhoes.addItem(texto)
        if not caminhoes:
            self.combo_caminhoes.addItem("Nenhum caminhão cadastrado")
        self._atualizar_validacao()

    def _buscar_cliente(self):
        termo = self.entrada_busca.text().strip()
        if not termo or len(termo) < 2:
            QMessageBox.warning(self, "Atenção", "Digite pelo menos 2 caracteres para buscar.")
            return

        def tarefa():
            clientes = viagem_service.buscar_clientes(termo)
            if not clientes:
                QTimer.singleShot(0, lambda: QMessageBox.information(self, "Resultado", "Nenhum cliente encontrado."))
                return
            QTimer.singleShot(0, lambda: self._mostrar_dialogo_clientes(clientes))

        threading.Thread(target=tarefa, daemon=True).start()

    def _mostrar_dialogo_clientes(self, clientes):
        dlg = QDialog(self)
        dlg.setWindowTitle("Selecionar Cliente")
        dlg.resize(500, 400)
        layout = QVBoxLayout()
        dlg.setLayout(layout)

        lbl = QLabel("Selecione o Cliente")
        lbl.setFont(theme_manager.get_font(theme_manager.tokens.FONT_SIZE_XL, bold=True))
        layout.addWidget(lbl)

        tabela = QTableWidget(len(clientes), 3)
        tabela.setHorizontalHeaderLabels(["Nome", "Cidade", "UF"])
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.verticalHeader().setVisible(False)
        tabela.setAlternatingRowColors(False)

        for i, c in enumerate(clientes):
            cid, nome, cnpj, cidade, uf = c
            tabela.setItem(i, 0, QTableWidgetItem(nome))
            tabela.setItem(i, 1, QTableWidgetItem(cidade or "-"))
            tabela.setItem(i, 2, QTableWidgetItem(uf or "-"))

        tabela.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(tabela)

        def on_selecionar():
            row = tabela.currentRow()
            if row < 0:
                return
            cid, nome = clientes[row][0], clientes[row][1]
            self._selecionar_cliente(cid, nome)
            dlg.accept()

        btn = ModernButton("Selecionar", ButtonStyle.PRIMARY)
        btn.clicked.connect(on_selecionar)
        layout.addWidget(btn)

        tabela.cellDoubleClicked.connect(on_selecionar)
        dlg.exec()

    def _selecionar_cliente(self, cliente_id, nome):
        # Limpar estado anterior
        self.cliente_selecionado_id = cliente_id
        self.cliente_selecionado = nome
        self.notas_selecionadas.clear()
        self.notas_ids = {}
        self.notas_catalogo = {}
        
        colors = theme_manager.colors
        self.label_cliente.setText(f"Cliente selecionado: {nome} • {len(self.notas_selecionadas)} nota(s)")
        self.label_cliente.setStyleSheet(f"color: {colors['emerald']}; background: transparent;")
        
        self._carregar_notas_cliente()

    def _carregar_notas_cliente(self):
        if not self.cliente_selecionado_id:
            return

        def tarefa():
            notas = viagem_service.listar_notas_cliente(
                self.cliente_selecionado_id,
                apenas_disponiveis=True,
                excluir_vinculadas=True,
            )
            # Usar Signal em vez de QTimer.singleShot para thread-safety
            self._notas_carregadas.emit(notas)

        threading.Thread(target=tarefa, daemon=True).start()

    def _preencher_tabela_notas(self, notas):
        self.tabela_notas.setRowCount(0)
        self.notas_ids = {}

        for nota in notas:
            nota_id, numero_cte, chave_nfe, _cliente, cidade, peso, _frete, data, status = nota
            numero = numero_cte if numero_cte else (chave_nfe[:20] if chave_nfe else "-")
            peso = peso or 0
            data_fmt = data[:10] if data else "-"
            marcador = "☑" if nota_id in self.notas_selecionadas else "☐"

            self.notas_catalogo[nota_id] = {
                "numero": numero, "cidade": cidade or "-", "peso": peso,
                "data": data_fmt, "status": status,
            }

            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            valores = [marcador, numero, cidade or "-", f"{peso:,.2f} kg", data_fmt, status]
            for col, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
                self.tabela_notas.setItem(row, col, item)
                self.notas_ids[row] = nota_id
        
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _clicar_na_nota(self, row, col):
        nota_id = self.notas_ids.get(row)
        if nota_id is None:
            return
        selecionada = nota_id not in self.notas_selecionadas
        atualizar_marcacao_nota(self.notas_selecionadas, nota_id, selecionada)
        item = self.tabela_notas.item(row, 0)
        if item:
            item.setText("☑" if selecionada else "☐")
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()

    def _selecionar_todas(self):
        for row in range(self.tabela_notas.rowCount()):
            nota_id = self.notas_ids.get(row)
            if nota_id and nota_id not in self.notas_selecionadas:
                atualizar_marcacao_nota(self.notas_selecionadas, nota_id, True)
                item = self.tabela_notas.item(row, 0)
                if item:
                    item.setText("☑")
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()

    def _limpar_selecao(self):
        self.notas_selecionadas.clear()
        for row in range(self.tabela_notas.rowCount()):
            item = self.tabela_notas.item(row, 0)
            if item:
                item.setText("☐")
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()

    def _atualizar_lista_selecionadas(self):
        self.tabela_selecionadas.setRowCount(0)
        self.notas_selecionadas_tree_ids = {}
        for nota_id in sorted(self.notas_selecionadas):
            dados = self.notas_catalogo.get(nota_id, {})
            row = self.tabela_selecionadas.rowCount()
            self.tabela_selecionadas.insertRow(row)
            self.tabela_selecionadas.setItem(row, 0, QTableWidgetItem(dados.get("numero", "-")))
            peso = dados.get("peso", 0) or 0
            self.tabela_selecionadas.setItem(row, 1, QTableWidgetItem(f"{peso:,.2f} kg"))
            self.notas_selecionadas_tree_ids[row] = nota_id
        self.label_qtd_selecionadas.setText(f"{len(self.notas_selecionadas)} nota(s) marcada(s)")

    def _remover_nota_selecionada(self):
        row = self.tabela_selecionadas.currentRow()
        if row < 0:
            return
        nota_id = self.notas_selecionadas_tree_ids.get(row)
        if nota_id is None:
            return
        self.notas_selecionadas.discard(nota_id)
        # Atualizar marcador na tabela principal
        for r in range(self.tabela_notas.rowCount()):
            if self.notas_ids.get(r) == nota_id:
                item = self.tabela_notas.item(r, 0)
                if item:
                    item.setText("☐")
                break
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()

    def _atualizar_resumo(self):
        notas_ids = list(self.notas_selecionadas)
        resumo = viagem_service.calcular_resumo_selecao(notas_ids)
        self._resumo_labels["qtd"].setText(str(resumo["quantidade"]))
        self._resumo_labels["peso"].setText(f"{resumo['peso_total']:,.2f} kg")
        self._resumo_labels["frete"].setText(f"R$ {resumo['frete_total']:,.2f}")
        self._resumo_labels["volumes"].setText(str(resumo["volumes"]))

    def _atualizar_validacao(self):
        colors = theme_manager.colors
        if not self.notas_selecionadas:
            self.label_validacao.setText("Selecione notas para validar a viagem.")
            self.label_validacao.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            return

        caminhao_texto = self.combo_caminhoes.currentText()
        if not caminhao_texto or "Nenhum caminhão" in caminhao_texto:
            self.label_validacao.setText("Selecione um caminhão para validar a capacidade.")
            self.label_validacao.setStyleSheet(f"color: {colors['amber']}; background: transparent;")
            return

        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        if not caminhao_id:
            self.label_validacao.setText("Caminhão não encontrado na lista atual.")
            self.label_validacao.setStyleSheet(f"color: {colors['error']}; background: transparent;")
            return

        valido, mensagem, _ = viagem_service.validar_capacidade(caminhao_id, list(self.notas_selecionadas))
        if valido:
            self.label_validacao.setText(f"Capacidade OK para {caminhao_texto}.")
            self.label_validacao.setStyleSheet(f"color: {colors['emerald']}; background: transparent;")
        else:
            sugestao = self._sugerir_caminhao_ideal()
            texto = mensagem or "Capacidade excedida."
            if sugestao:
                texto += f" Sugestão: {sugestao}."
            self.label_validacao.setText(texto)
            self.label_validacao.setStyleSheet(f"color: {colors['error']}; background: transparent;")

    def _sugerir_caminhao_ideal(self) -> str:
        if not self.notas_selecionadas:
            return ""
        resumo = viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas))
        peso = resumo.get("peso_total", 0) or 0
        for item in self.caminhoes_catalogo:
            if item.get("capacidade", 0) >= peso:
                return item.get("texto", "")
        return ""

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

        valido, mensagem, _ = viagem_service.validar_capacidade(caminhao_id, list(self.notas_selecionadas))
        if not valido:
            resp = QMessageBox.question(self, "Aviso de Capacidade", f"{mensagem}\n\nDeseja continuar mesmo assim?")
            if resp != QMessageBox.StandardButton.Yes:
                return

        def tarefa():
            try:
                viagem_id = viagem_service.criar_viagem_com_notas(
                    caminhao_id, list(self.notas_selecionadas), motorista
                )
                resumo = viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas))
                adicionar_historico_viagem({
                    "viagem_id": viagem_id, "motorista": motorista,
                    "caminhao": caminhao_texto, "quantidade": len(self.notas_selecionadas),
                    "peso_total": round(resumo.get("peso_total", 0), 2),
                    "frete_total": round(resumo.get("frete_total", 0), 2),
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }, None)

                QTimer.singleShot(0, lambda: QMessageBox.information(
                    self, "Sucesso",
                    f"Viagem #{viagem_id} criada com sucesso!\n{len(self.notas_selecionadas)} nota(s)."
                ))
                QTimer.singleShot(0, self._limpar_selecao)
                QTimer.singleShot(0, lambda: self.entrada_motorista.clear())
                QTimer.singleShot(0, self._atualizar_historico)
                QTimer.singleShot(0, self._carregar_notas_cliente)
            except Exception as e:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(e)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _salvar_rascunho_atual(self):
        dados = {
            "cliente_id": self.cliente_selecionado_id,
            "cliente_nome": self.cliente_selecionado,
            "notas": sorted(self.notas_selecionadas),
            "motorista": self.entrada_motorista.text().strip(),
            "caminhao": self.combo_caminhoes.currentText(),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "quantidade": len(self.notas_selecionadas),
        }
        salvar_rascunho_viagem(dados, None)
        QMessageBox.information(self, "Rascunho salvo", "O estado atual foi salvo com sucesso.")

    def _carregar_rascunho(self):
        dados = carregar_rascunho_viagem(None)
        if not dados:
            return
        if dados.get("cliente_id") and dados.get("cliente_nome"):
            self._selecionar_cliente(dados["cliente_id"], dados["cliente_nome"])
        self.notas_selecionadas = set(dados.get("notas", []))
        self.entrada_motorista.setText(dados.get("motorista", ""))
        caminhao = dados.get("caminhao")
        if caminhao:
            idx = self.combo_caminhoes.findText(caminhao)
            if idx >= 0:
                self.combo_caminhoes.setCurrentIndex(idx)
        self._atualizar_resumo()
        self._atualizar_lista_selecionadas()
        self._atualizar_validacao()
        self._atualizar_historico()

    def _limpar_rascunho(self):
        limpar_rascunho_viagem(None)
        QMessageBox.information(self, "Rascunho", "O rascunho foi removido.")

    def _atualizar_historico(self):
        historico = listar_historico_viagem(None)
        if not historico:
            self.label_historico.setText("Histórico rápido: ainda sem viagens criadas.")
            return
        linhas = []
        for item in historico[:3]:
            linhas.append(
                f"• Viagem #{item.get('viagem_id')} | {item.get('motorista', '-')} | "
                f"{item.get('caminhao', '-')} | {item.get('quantidade', 0)} notas"
            )
        self.label_historico.setText("Histórico rápido:\n" + "\n".join(linhas))
