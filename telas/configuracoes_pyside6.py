"""
Tela Configurações - CW Transportadora - PySide6
Dados da empresa, backup, banco de dados e preferências do sistema.
"""

from __future__ import annotations

import os
import sys
import threading

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QFrame, QMessageBox, QScrollArea, QGridLayout,
    QCheckBox,
)
from PySide6.QtCore import Qt

from config.settings import settings
from services.config_service import config_service
from services.viagem_service import viagem_service
from services.update_service import update_service, CANAL_ESTAVEL, CANAL_BETA, CANAL_DEV
from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ModernCard
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaConfiguracoes(QWidget):
    """Tela de configurações em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.campos: dict = {}
        self.dados = config_service.carregar_configuracoes()
        self._setup_ui()

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

        # Grid 2 colunas
        grid = QGridLayout()
        grid.setSpacing(tokens.SPACING_LG)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        row = 0
        # Card Empresa
        card_empresa = self._criar_card("🏢 Dados da Empresa", "Essas informações aparecem em relatórios, PDFs e identificação do sistema.")
        self._criar_entry(card_empresa, "empresa", "Nome da empresa")
        self._criar_entry(card_empresa, "cnpj", "CNPJ")
        self._criar_entry(card_empresa, "telefone", "Telefone")
        self._criar_entry(card_empresa, "email", "E-mail")
        self._criar_entry(card_empresa, "cidade", "Cidade")
        self._criar_entry(card_empresa, "uf", "UF")
        grid.addWidget(card_empresa, 0, 0)

        # Card Sistema
        card_sistema = self._criar_card("⚙️ Preferências do Sistema", "Configure metas, pasta dos relatórios e aparência do sistema.")
        self._criar_entry(card_sistema, "meta_lucro", "Meta mensal de lucro")
        self._criar_entry(card_sistema, "imposto_percentual", "Imposto padrão (%)")
        self._criar_entry(card_sistema, "pasta_relatorios", "Pasta dos relatórios")
        self._criar_entry(card_sistema, "alerta_revisao", "Alerta de revisão com KM")
        self._criar_entry(card_sistema, "revisao_obrigatoria", "Revisão obrigatória com KM")

        colors = theme_manager.colors
        tokens = theme_manager.tokens

        lbl_tema = QLabel("Tema visual")
        lbl_tema.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: 600; background: transparent;")
        card_sistema.layout().addWidget(lbl_tema)
        combo_tema = QComboBox()
        combo_tema.addItems(["Vermelho CW", "Claro", "Premium Escuro"])
        combo_tema.setMinimumHeight(40)
        combo_tema.setCurrentText(self.dados.get("tema", "Vermelho CW"))
        combo_tema.setStyleSheet(self._combo_style())
        card_sistema.layout().addWidget(combo_tema)
        self.campos["tema"] = combo_tema

        lbl_cor = QLabel("Cor principal")
        lbl_cor.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: 600; background: transparent;")
        card_sistema.layout().addWidget(lbl_cor)
        combo_cor = QComboBox()
        combo_cor.addItems(["Vermelho", "Azul", "Verde", "Roxo", "Preto"])
        combo_cor.setMinimumHeight(40)
        combo_cor.setCurrentText(self.dados.get("cor_tema", "Vermelho"))
        combo_cor.setStyleSheet(self._combo_style())
        card_sistema.layout().addWidget(combo_cor)
        self.campos["cor_tema"] = combo_cor
        grid.addWidget(card_sistema, 0, 1)

        # Card Backup
        card_backup = self._criar_card("🗂 Backup e Arquivos", "Faça backup do banco, configurações e relatórios gerados.")
        btn_sistema = ModernButton("Abrir Pasta do Sistema", ButtonStyle.SECONDARY)
        btn_sistema.clicked.connect(self._abrir_pasta_sistema)
        card_backup.layout().addWidget(btn_sistema)
        btn_rel = ModernButton("Abrir Pasta dos Relatórios", ButtonStyle.PRIMARY)
        btn_rel.clicked.connect(self._abrir_pasta_relatorios)
        card_backup.layout().addWidget(btn_rel)
        btn_backup = ModernButton("Fazer Backup Completo", ButtonStyle.SUCCESS)
        btn_backup.clicked.connect(self._fazer_backup)
        card_backup.layout().addWidget(btn_backup)
        grid.addWidget(card_backup, 1, 0)

        # Card Banco
        card_banco = self._criar_card("🧠 Banco de Dados", "Informações técnicas do banco usado pelo sistema.")
        info = config_service.info_banco()
        for titulo_item, valor_item in [
            ("Arquivo do banco", "cw_transportadora.db"),
            ("Tamanho", info["tamanho"]),
            ("Tabelas", str(info["tabelas"])),
            ("Registros principais", str(info["registros"])),
            ("Último backup", info["ultimo_backup"]),
        ]:
            row_frame = QFrame()
            row_frame.setStyleSheet(f"QFrame {{ background-color: {colors['bg_tertiary']}; border-radius: {tokens.RADIUS_MD}px; }}")
            rl = QHBoxLayout()
            rl.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
            row_frame.setLayout(rl)
            lbl_t = QLabel(titulo_item)
            lbl_t.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            lbl_t.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            rl.addWidget(lbl_t)
            rl.addStretch()
            lbl_v = QLabel(valor_item)
            lbl_v.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            lbl_v.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
            rl.addWidget(lbl_v)
            card_banco.layout().addWidget(row_frame)

        btn_info = ModernButton("Atualizar Informações", ButtonStyle.PRIMARY)
        btn_info.clicked.connect(self._recarregar_tela)
        card_banco.layout().addWidget(btn_info)
        grid.addWidget(card_banco, 1, 1)

        # Card Atualizações
        card_atualizacoes = self._criar_card("🔄 Atualizações", "Configure canal, verificação automática e verifique novas versões.")
        info_versao = update_service.obter_versao_instalada()
        versao = info_versao.get("versao", "0.0.0")

        lbl_versao = QLabel(f"Versão instalada: {versao}")
        lbl_versao.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD, bold=True))
        lbl_versao.setStyleSheet(f"color: {colors['emerald']}; background: transparent;")
        card_atualizacoes.layout().addWidget(lbl_versao)

        self.check_auto = QCheckBox("Verificar atualizações automaticamente")
        self.check_auto.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent; font-weight: 600;")
        if settings.enable_auto_update:
            self.check_auto.setChecked(True)
        card_atualizacoes.layout().addWidget(self.check_auto)

        lbl_canal = QLabel("Canal de atualização")
        lbl_canal.setStyleSheet(f"color: {colors['text_secondary']}; font-weight: 600; background: transparent;")
        card_atualizacoes.layout().addWidget(lbl_canal)
        self.combo_canal = QComboBox()
        self.combo_canal.addItems(["Estável", "Beta", "Desenvolvimento"])
        self.combo_canal.setMinimumHeight(40)
        canal_map = {CANAL_ESTAVEL: "Estável", CANAL_BETA: "Beta", CANAL_DEV: "Desenvolvimento"}
        self.combo_canal.setCurrentText(canal_map.get(update_service.channel, "Estável"))
        self.combo_canal.setStyleSheet(self._combo_style())
        card_atualizacoes.layout().addWidget(self.combo_canal)

        self.btn_verificar = ModernButton("Verificar Agora", ButtonStyle.PRIMARY)
        self.btn_verificar.clicked.connect(self._verificar_atualizacao)
        card_atualizacoes.layout().addWidget(self.btn_verificar)

        self.label_resultado = QLabel("")
        self.label_resultado.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        self.label_resultado.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        card_atualizacoes.layout().addWidget(self.label_resultado)

        grid.addWidget(card_atualizacoes, 2, 1)

        # Card Limpeza
        card_limpeza = self._criar_card("🗑️ Limpeza de Dados", "Remova dados salvos para recadastramento. Use com cuidado!")
        lbl_limpeza = QLabel("Caminhões cadastrados - Remove todos os veículos para permitir novo cadastramento.")
        lbl_limpeza.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl_limpeza.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        lbl_limpeza.setWordWrap(True)
        card_limpeza.layout().addWidget(lbl_limpeza)
        btn_apagar = ModernButton("🗑️ Apagar Todos os Caminhões", ButtonStyle.DANGER)
        btn_apagar.clicked.connect(self._apagar_caminhoes)
        card_limpeza.layout().addWidget(btn_apagar)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet(f"QFrame {{ background-color: {colors['border_subtle']}; max-height: 2px; }}")
        card_limpeza.layout().addWidget(separador)

        # Reset completo (mestre)
        lbl_reset = QLabel("🔐 Reset Completo (Mestre)")
        lbl_reset.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_reset.setStyleSheet(f"color: {colors['rose']}; background: transparent;")
        card_limpeza.layout().addWidget(lbl_reset)

        lbl_reset_desc = QLabel("Apaga TODOS os dados (manifestos, notas, contas, etc.) EXCETO usuários.\nApenas para usuário mestre.")
        lbl_reset_desc.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl_reset_desc.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        lbl_reset_desc.setWordWrap(True)
        card_limpeza.layout().addWidget(lbl_reset_desc)

        btn_reset = ModernButton("⚠️ Apagar Todos os Dados (Exceto Usuários)", ButtonStyle.DANGER)
        btn_reset.clicked.connect(self._apagar_todos_dados_exceto_usuarios)
        card_limpeza.layout().addWidget(btn_reset)

        grid.addWidget(card_limpeza, 2, 0)

        cl.addLayout(grid)

        # Botões finais
        botoes = QHBoxLayout()
        btn_salvar = ModernButton("Salvar Configurações", ButtonStyle.SUCCESS)
        btn_salvar.setMinimumHeight(46)
        btn_salvar.setMinimumWidth(230)
        btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(btn_salvar)

        btn_restaurar = ModernButton("Restaurar Padrão", ButtonStyle.SECONDARY)
        btn_restaurar.setMinimumHeight(46)
        btn_restaurar.setMinimumWidth(190)
        btn_restaurar.clicked.connect(self._restaurar_padrao)
        botoes.addWidget(btn_restaurar)

        botoes.addStretch()
        cl.addLayout(botoes)

    def _criar_card(self, titulo: str, subtitulo: str) -> QFrame:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: {colors['bg_secondary']}; border-radius: {tokens.RADIUS_XL}px; border: 1px solid {colors['border_subtle']}; }}")
        cl = QVBoxLayout()
        cl.setContentsMargins(tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL, tokens.SPACING_XL)
        cl.setSpacing(tokens.SPACING_SM)
        card.setLayout(cl)

        lbl_t = QLabel(titulo)
        lbl_t.setFont(theme_manager.get_font(tokens.FONT_SIZE_XL, bold=True))
        lbl_t.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        cl.addWidget(lbl_t)

        lbl_s = QLabel(subtitulo)
        lbl_s.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl_s.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        lbl_s.setWordWrap(True)
        cl.addWidget(lbl_s)

        return card

    def _criar_entry(self, parent: QFrame, chave: str, label: str):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        lbl = QLabel(label)
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        parent.layout().addWidget(lbl)

        entry = QLineEdit()
        entry.setText(str(self.dados.get(chave, "")))
        entry.setMinimumHeight(40)
        entry.setStyleSheet(self._input_style())
        parent.layout().addWidget(entry)
        self.campos[chave] = entry

    def _input_style(self) -> str:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        return f"""
            QLineEdit {{ background-color: {colors['bg_primary']}; color: {colors['text_primary']};
                border: 1.5px solid {colors['border_subtle']}; border-radius: {tokens.RADIUS_MD}px;
                padding: 8px 12px; font-size: {tokens.FONT_SIZE_MD}px; }}
            QLineEdit:focus {{ border: 1.5px solid {colors['amber']}; }}
        """

    def _combo_style(self) -> str:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        return f"""
            QComboBox {{ background-color: {colors['bg_primary']}; color: {colors['text_primary']};
                border: 1.5px solid {colors['border_subtle']}; border-radius: {tokens.RADIUS_MD}px;
                padding: 8px 12px; font-size: {tokens.FONT_SIZE_MD}px; }}
        """

    def _salvar(self):
        try:
            dados = {}
            for chave, campo in self.campos.items():
                if isinstance(campo, QLineEdit):
                    dados[chave] = campo.text().strip()
                elif isinstance(campo, QComboBox):
                    dados[chave] = campo.currentText().strip()

            config_service.salvar_configuracoes(dados)

            resp = QMessageBox.question(self, "Configurações salvas", "Configurações salvas com sucesso!\n\nDeseja reiniciar o sistema agora para aplicar o tema?")
            if resp == QMessageBox.StandardButton.Yes:
                python = sys.executable
                os.execl(python, python, *sys.argv)
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _restaurar_padrao(self):
        resp = QMessageBox.question(self, "Restaurar padrão", "Deseja restaurar todas as configurações padrão?")
        if resp != QMessageBox.StandardButton.Yes:
            return
        self.dados = config_service.restaurar_padrao()
        for chave, campo in self.campos.items():
            if isinstance(campo, QLineEdit):
                campo.setText(str(self.dados.get(chave, "")))
            elif isinstance(campo, QComboBox):
                campo.setCurrentText(str(self.dados.get(chave, "")))
        self._salvar()

    def _abrir_pasta_sistema(self):
        try:
            os.startfile(config_service.abrir_pasta_sistema())
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _abrir_pasta_relatorios(self):
        try:
            pasta = config_service.abrir_pasta_relatorios(
                self.campos["pasta_relatorios"].text().strip() or "relatorios_gerados"
            )
            os.startfile(pasta)
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _fazer_backup(self):
        try:
            pasta = config_service.fazer_backup(
                self.campos["pasta_relatorios"].text().strip() or "relatorios_gerados"
            )
            QMessageBox.information(self, "Backup concluído", f"Backup realizado com sucesso!\n\nPasta:\n{pasta}")
            os.startfile(pasta)
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _verificar_atualizacao(self):
        self.btn_verificar.setEnabled(False)
        self.btn_verificar.setText("Verificando...")
        self.label_resultado.setText("Buscando novas versões...")
        self.label_resultado.setStyleSheet(f"color: {theme_manager.colors['amber']}; background: transparent;")

        canal_nome = self.combo_canal.currentText()
        canal_map_rev = {"Estável": CANAL_ESTAVEL, "Beta": CANAL_BETA, "Desenvolvimento": CANAL_DEV}
        canal = canal_map_rev.get(canal_nome, CANAL_ESTAVEL)

        def tarefa():
            try:
                resultado = update_service.check_for_updates(channel=canal)
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._resultado_verificacao(resultado))
            except Exception as e:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._resultado_verificacao({"error": str(e)}))

        threading.Thread(target=tarefa, daemon=True).start()

    def _resultado_verificacao(self, resultado):
        colors = theme_manager.colors
        self.btn_verificar.setEnabled(True)
        self.btn_verificar.setText("Verificar Agora")

        if resultado.get("error"):
            self.label_resultado.setText(f"Erro: {resultado['error']}")
            self.label_resultado.setStyleSheet(f"color: {colors['rose']}; background: transparent;")
            return

        if resultado.get("has_update"):
            self.label_resultado.setText(f"Nova versão: {resultado['latest_version']}!")
            self.label_resultado.setStyleSheet(f"color: {colors['emerald']}; background: transparent;")
        else:
            self.label_resultado.setText("Sistema está atualizado!")
            self.label_resultado.setStyleSheet(f"color: {colors['emerald']}; background: transparent;")

    def _apagar_caminhoes(self):
        resp = QMessageBox.question(self, "Apagar Caminhões", "Tem certeza que deseja apagar TODOS os caminhões cadastrados?\n\nEsta ação não pode ser desfeita.")
        if resp != QMessageBox.StandardButton.Yes:
            return
        resp2 = QMessageBox.question(self, "Confirmação Final", "ÚLTIMA CONFIRMAÇÃO: Apagar TODOS os caminhões?")
        if resp2 != QMessageBox.StandardButton.Yes:
            return
        try:
            sucesso = viagem_service.apagar_caminhoes()
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Todos os caminhões foram apagados com sucesso!")
                self._recarregar_tela()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível apagar os caminhões.")
        except Exception as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao apagar caminhões:\n{erro}")

    def _apagar_todos_dados_exceto_usuarios(self):
        """Apaga todos os dados do sistema EXCETO usuários (apenas mestre)."""
        from services.auth_service import auth_service

        # Verificar se é usuário mestre
        if not auth_service.eh_mestre:
            QMessageBox.critical(self, "Acesso Negado", "Esta função está disponível apenas para o usuário mestre do sistema.")
            return

        resp = QMessageBox.question(
            self,
            "⚠️ RESET COMPLETO DO SISTEMA",
            "Tem certeza que deseja apagar TODOS os dados do sistema?\n\n"
            "Isso irá apagar:\n"
            "• Todos os manifestos baixados\n"
            "• Todas as notas fiscais\n"
            "• Todos os clientes cadastrados\n"
            "• Todos os caminhões\n"
            "• Todas as viagens\n"
            "• Todas as contas a pagar/receber\n"
            "• Todos os abastecimentos\n"
            "• Todas as manutenções\n"
            "• Todos os funcionários\n\n"
            "O que será MANTIDO:\n"
            "• Todos os usuários do sistema\n"
            "• Permissões dos usuários\n"
            "• Histórico de auditoria\n\n"
            "Esta ação NÃO PODE ser desfeita!"
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        resp2 = QMessageBox.question(
            self,
            "🔐 CONFIRMAÇÃO FINAL",
            "ÚLTIMA CONFIRMAÇÃO: Você realmente deseja apagar TODOS os dados?\n\n"
            "Clique SIM apenas se tiver certeza absoluta.\n\n"
            "Esta ação apagará permanentemente todos os dados operacionais do sistema."
        )
        if resp2 != QMessageBox.StandardButton.Yes:
            return

        try:
            sucesso = viagem_service.apagar_todos_dados_exceto_usuarios()
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Todos os dados foram apagados com sucesso!\n\nOs usuários foram mantidos.\nVocê pode começar a recadastrar os dados agora.")
                self._recarregar_tela()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível apagar os dados. Verifique o banco de dados.")
        except Exception as erro:
            QMessageBox.critical(self, "Erro", f"Erro ao apagar dados:\n{erro}")

    def _recarregar_tela(self):
        self.campos = {}
        self.dados = config_service.carregar_configuracoes()
        # Limpar e recriar UI
        for child in self.findChildren(QWidget):
            if child is not self:
                child.setParent(None)
                child.deleteLater()
        self._setup_ui()
