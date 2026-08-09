"""
Tela Gerenciar Usuários - CW Transportadora - PySide6
Administração de usuários: criar, editar, excluir, ativar/desativar, permissões.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QDialog,
    QScrollArea, QFormLayout, QCheckBox, QGridLayout,
)
from PySide6.QtCore import Qt

from config.settings import settings
from services.auth_service import MODULOS_PERMISSOES, auth_service, SenhaFracaError
from services.usuario_service import usuario_service
from services.auditoria_service import (
    auditoria_service,
    ACAO_USUARIO_CRIADO, ACAO_USUARIO_EXCLUIDO,
    ACAO_USUARIO_ATIVADO, ACAO_USUARIO_DESATIVADO,
    ACAO_PERMISSAO_ALTERADA, ACAO_SENHA_REDEFINIDA,
    ACAO_NIVEL_ALTERADO,
)
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWInput, CWTable
from utils.logger import get_logger

logger = get_logger(__name__)

_NIVEIS = ["comum", "operacional", "mestre"]
_ACOES_PERMISSAO = ["visualizar", "criar", "editar", "excluir", "exportar", "sincronizar"]


class TelaGerenciarUsuarios(QWidget):
    """Tela de administração de usuários em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._carregar_usuarios()

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

        # Barra de botões
        barra = ModernCard(padding=tokens.SPACING_LG)
        br = QHBoxLayout()
        btn_novo = ModernButton("+ Novo Usuário", ButtonStyle.PRIMARY)
        btn_novo.clicked.connect(lambda: self._abrir_modal_criar())
        br.addWidget(btn_novo)
        br.addStretch()
        btn_atualizar = ModernButton("Atualizar", ButtonStyle.SECONDARY)
        btn_atualizar.clicked.connect(self._carregar_usuarios)
        br.addWidget(btn_atualizar)
        barra.add_layout(br)
        cl.addWidget(barra)

        # Tabela
        card = ModernCard(padding=tokens.SPACING_XL)
        colunas = [
            ("ID", 50), ("Nome Completo", 220), ("Usuário", 130), ("Nível", 110),
            ("Status", 90), ("Último Login", 150), ("Criado em", 150),
        ]
        self.tabela = ModernTable()
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setMinimumHeight(350)

        h = self.tabela.horizontalHeader()
        for i, (_, w) in enumerate(colunas):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)

        self.tabela.cellDoubleClicked.connect(self._editar_selecionado)
        card.add_widget(self.tabela)

        # Ações
        acoes = QHBoxLayout()
        btn_editar = ModernButton("Editar", ButtonStyle.PRIMARY)
        btn_editar.clicked.connect(self._editar_selecionado)
        acoes.addWidget(btn_editar)

        btn_toggle = ModernButton("Ativar/Desativar", ButtonStyle.WARNING)
        btn_toggle.clicked.connect(self._toggle_ativo)
        acoes.addWidget(btn_toggle)

        btn_senha = ModernButton("Redefinir Senha", ButtonStyle.SECONDARY)
        btn_senha.clicked.connect(self._redefinir_senha)
        acoes.addWidget(btn_senha)

        btn_permissoes = ModernButton("Permissões", ButtonStyle.SUCCESS)
        btn_permissoes.clicked.connect(self._abrir_permissoes)
        acoes.addWidget(btn_permissoes)

        acoes.addStretch()

        btn_excluir = ModernButton("Excluir", ButtonStyle.DANGER)
        btn_excluir.clicked.connect(self._excluir_selecionado)
        acoes.addWidget(btn_excluir)
        card.add_layout(acoes)

        cl.addWidget(card)

    def _carregar_usuarios(self):
        self.tabela.setRowCount(0)
        for u in usuario_service.listar_usuarios():
            status = "Ativo" if u["ativo"] else "Inativo"
            if u["bloqueado_ate"]:
                status = "Bloqueado"
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            valores = [
                u["id"], u["nome_completo"], u["usuario"],
                u["nivel_acesso"].capitalize(), status,
                u["ultimo_login"] or "Nunca", u["criado_em"] or "",
            ]
            for col, texto in enumerate(valores):
                self.tabela.setItem(row, col, QTableWidgetItem(str(texto)))

    def _get_usuario_selecionado(self) -> int | None:
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um usuário na tabela.")
            return None
        item = self.tabela.item(row, 0)
        return int(item.text()) if item else None

    def _abrir_modal_criar(self, usuario_id: int | None = None):
        dados = usuario_service.obter_usuario(usuario_id) if usuario_id else None
        dlg = _ModalCriarEditarUsuario(self, dados=dados, on_salvo=self._carregar_usuarios)
        dlg.exec()

    def _editar_selecionado(self):
        uid = self._get_usuario_selecionado()
        if uid:
            self._abrir_modal_criar(uid)

    def _toggle_ativo(self):
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return

        if dados["ativo"]:
            resp = QMessageBox.question(self, "Desativar Usuário", f"Deseja desativar o usuário '{dados['usuario']}'?")
            if resp != QMessageBox.StandardButton.Yes:
                return
            usuario_service.desativar_usuario(uid)
            auditoria_service.registrar(ACAO_USUARIO_DESATIVADO, "usuarios", dados["usuario"])
        else:
            usuario_service.ativar_usuario(uid)
            auditoria_service.registrar(ACAO_USUARIO_ATIVADO, "usuarios", dados["usuario"])
        self._carregar_usuarios()

    def _redefinir_senha(self):
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        resp = QMessageBox.question(self, "Redefinir Senha", "Isso vai gerar uma nova senha temporária.\nO usuário será obrigado a alterá-la no próximo login.\n\nContinuar?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            senha_temp = usuario_service.redefinir_senha(uid)
            auditoria_service.registrar(ACAO_SENHA_REDEFINIDA, "usuarios", str(uid))
            QMessageBox.information(self, "Senha Redefinida", f"Nova senha temporária:\n\n{senha_temp}\n\nInforme ao usuário com segurança.")
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _excluir_selecionado(self):
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return
        resp = QMessageBox.question(self, "Excluir Usuário", f"ATENÇÃO!\n\nDeseja excluir permanentemente o usuário '{dados['usuario']}'?\nEsta ação não pode ser desfeita.")
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            usuario_service.excluir_usuario(uid)
            auditoria_service.registrar(ACAO_USUARIO_EXCLUIDO, "usuarios", dados["usuario"])
            self._carregar_usuarios()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _abrir_permissoes(self):
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return
        if dados["nivel_acesso"] == "mestre":
            QMessageBox.information(self, "Administrador Mestre", "O mestre tem acesso total. Permissões não são configuráveis.")
            return
        if dados["nivel_acesso"] == "operacional":
            QMessageBox.information(self, "Administrador Operacional", "Operacionais têm acesso completo (exceto administração de usuários).\nPermissões individuais não são aplicáveis.")
            return
        dlg = _ModalPermissoes(self, uid, dados["nome_completo"], on_salvo=self._carregar_usuarios)
        dlg.exec()


class _ModalCriarEditarUsuario(QDialog):
    def __init__(self, parent, dados=None, on_salvo=None):
        super().__init__(parent)
        self._dados = dados
        self._editando = dados is not None
        self._on_salvo = on_salvo
        self.setWindowTitle("Editar Usuário" if self._editando else "Novo Usuário")
        self.resize(460, 480)
        self._setup_ui()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        layout.setSpacing(tokens.SPACING_MD)
        self.setLayout(layout)

        titulo = QLabel("Editar Usuário" if self._editando else "Criar Novo Usuário")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']};")
        layout.addWidget(titulo)

        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; }}")
        fl = QFormLayout()
        fl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        fl.setSpacing(tokens.SPACING_SM)
        frame.setLayout(fl)

        input_style = f"""
            QLineEdit {{ background-color: {colors['bg_primary']}; color: {colors['text_primary']};
                border: 1.5px solid {colors['border_subtle']}; border-radius: {tokens.RADIUS_MD}px;
                padding: 8px 12px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {colors['violet']}; }}
        """

        self.entry_nome = QLineEdit()
        self.entry_nome.setStyleSheet(input_style)
        if self._dados:
            self.entry_nome.setText(self._dados.get("nome_completo", ""))
        fl.addRow(self._lbl("Nome completo"), self.entry_nome)

        self.entry_usuario = QLineEdit()
        self.entry_usuario.setStyleSheet(input_style)
        if self._dados:
            self.entry_usuario.setText(self._dados.get("usuario", ""))
        fl.addRow(self._lbl("Usuário (login)"), self.entry_usuario)

        self.entry_senha = None
        if not self._editando:
            self.entry_senha = QLineEdit()
            self.entry_senha.setStyleSheet(input_style)
            fl.addRow(self._lbl("Senha inicial"), self.entry_senha)

        self.combo_nivel = QComboBox()
        self.combo_nivel.addItems(_NIVEIS)
        self.combo_nivel.setMinimumHeight(40)
        self.combo_nivel.setStyleSheet(input_style.replace("QLineEdit", "QComboBox"))
        if self._dados:
            self.combo_nivel.setCurrentText(self._dados.get("nivel_acesso", "comum"))
        fl.addRow(self._lbl("Nível de acesso"), self.combo_nivel)

        self.label_erro = QLabel("")
        self.label_erro.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        self.label_erro.setStyleSheet(f"color: {colors['rose']}; background: transparent;")
        self.label_erro.setWordWrap(True)
        fl.addRow(self.label_erro)

        layout.addWidget(frame)

        texto_btn = "ATUALIZAR" if self._editando else "SALVAR"
        btn_salvar = ModernButton(texto_btn, ButtonStyle.PRIMARY)
        btn_salvar.setMinimumHeight(44)
        btn_salvar.clicked.connect(self._salvar)
        layout.addWidget(btn_salvar)

    def _salvar(self):
        nome = self.entry_nome.text().strip()
        usuario = self.entry_usuario.text().strip()
        nivel = self.combo_nivel.currentText()

        if not nome:
            self.label_erro.setText("Informe o nome completo.")
            return
        if not usuario:
            self.label_erro.setText("Informe o nome de usuário.")
            return

        try:
            if self._editando:
                if nivel != self._dados.get("nivel_acesso"):
                    usuario_service.alterar_nivel_acesso(self._dados["id"], nivel)
                    auditoria_service.registrar(
                        ACAO_NIVEL_ALTERADO, "usuarios", usuario,
                        detalhes=f"Nível alterado para '{nivel}'",
                    )
            else:
                senha = self.entry_senha.text() if self.entry_senha else ""
                if not senha:
                    self.label_erro.setText("Informe a senha inicial.")
                    return
                usuario_service.criar_usuario(
                    nome, usuario, senha, nivel,
                    auth_service.usuario_atual["id"],
                )
                auditoria_service.registrar(
                    ACAO_USUARIO_CRIADO, "usuarios", usuario,
                    detalhes=f"Nível: {nivel}",
                )

            if self._on_salvo:
                self._on_salvo()
            self.accept()

        except (ValueError, SenhaFracaError) as erro:
            self.label_erro.setText(str(erro))
        except Exception as erro:
            logger.error(f"Erro ao salvar usuário: {erro}")
            self.label_erro.setText("Erro inesperado.")

    def _lbl(self, texto) -> QLabel:
        colors = theme_manager.colors
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: 600; background: transparent;")
        return lbl


class _ModalPermissoes(QDialog):
    def __init__(self, parent, usuario_id: int, nome: str, on_salvo=None):
        super().__init__(parent)
        self._usuario_id = usuario_id
        self._on_salvo = on_salvo
        self._checkboxes: dict[str, dict[str, QCheckBox]] = {}
        self.setWindowTitle(f"Permissões - {nome}")
        self.resize(620, 600)
        self._setup_ui()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        layout.setSpacing(tokens.SPACING_MD)
        self.setLayout(layout)

        titulo = QLabel("Configurar Permissões")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']};")
        layout.addWidget(titulo)

        sub = QLabel("Marque as ações permitidas para cada módulo.")
        sub.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        sub.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        layout.addWidget(sub)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_LG}px; }}")

        content = QWidget()
        content.setStyleSheet(f"background-color: {colors['bg_secondary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_MD, tokens.SPACING_MD, tokens.SPACING_MD)
        cl.setSpacing(tokens.SPACING_SM)
        content.setLayout(cl)
        scroll.setWidget(content)

        permissoes = usuario_service.obter_permissoes(self._usuario_id)

        # Header
        header = QFrame()
        header.setStyleSheet(f"QFrame {{ background-color: {colors['bg_tertiary']}; border-radius: {tokens.RADIUS_MD}px; }}")
        hl = QHBoxLayout()
        hl.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
        header.setLayout(hl)

        lbl_mod = QLabel("Módulo")
        lbl_mod.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_mod.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        lbl_mod.setMinimumWidth(140)
        hl.addWidget(lbl_mod)

        for acao in _ACOES_PERMISSAO:
            lbl = QLabel(acao.capitalize())
            lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setMinimumWidth(75)
            hl.addWidget(lbl)
        cl.addWidget(header)

        # Rows
        for modulo, nome_modulo in MODULOS_PERMISSOES.items():
            if modulo in ("usuarios", "auditoria"):
                continue

            row = QFrame()
            row.setStyleSheet(f"QFrame {{ background-color: {colors['bg_primary']}; border-radius: {tokens.RADIUS_MD}px; }}")
            rl = QHBoxLayout()
            rl.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
            row.setLayout(rl)

            lbl_nome = QLabel(nome_modulo)
            lbl_nome.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD))
            lbl_nome.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
            lbl_nome.setMinimumWidth(140)
            rl.addWidget(lbl_nome)

            self._checkboxes[modulo] = {}
            perm_modulo = permissoes.get(modulo, {})

            for acao in _ACOES_PERMISSAO:
                cb = QCheckBox()
                cb.setChecked(perm_modulo.get(acao, False))
                cb.setStyleSheet(f"""
                    QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 2px solid {colors['border_subtle']}; }}
                    QCheckBox::indicator:checked {{ background-color: {colors['emerald']}; border: 2px solid {colors['emerald']}; }}
                """)
                self._checkboxes[modulo][acao] = cb
                rl.addWidget(cb)
                rl.setAlignment(cb, Qt.AlignmentFlag.AlignCenter)

            cl.addWidget(row)

        layout.addWidget(scroll)

        btn_salvar = ModernButton("SALVAR PERMISSÕES", ButtonStyle.SUCCESS)
        btn_salvar.setMinimumHeight(44)
        btn_salvar.clicked.connect(self._salvar)
        layout.addWidget(btn_salvar)

    def _salvar(self):
        permissoes: dict[str, dict[str, bool]] = {}
        for modulo, acoes_cbs in self._checkboxes.items():
            permissoes[modulo] = {
                acao: cb.isChecked() for acao, cb in acoes_cbs.items()
            }

        try:
            usuario_service.salvar_permissoes(self._usuario_id, permissoes)
            auditoria_service.registrar(
                ACAO_PERMISSAO_ALTERADA, "usuarios", str(self._usuario_id),
                detalhes="Permissões atualizadas",
            )
            QMessageBox.information(self, "Sucesso", "Permissões salvas com sucesso!")
            if self._on_salvo:
                self._on_salvo()
            self.accept()
        except Exception as erro:
            logger.error(f"Erro ao salvar permissões: {erro}")
            QMessageBox.critical(self, "Erro", str(erro))
