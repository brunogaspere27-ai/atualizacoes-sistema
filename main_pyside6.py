"""
CW Transportadora - Sistema de Gestão Logística
Versão PySide6 (Qt6) - Interface Moderna 2026

Ponto de entrada da aplicação com arquitetura preservada.
Migração de CustomTkinter para PySide6 mantendo 100% da funcionalidade.
"""

import os
import sys
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMessageBox, QInputDialog, QSplashScreen, QLabel,
    QLineEdit
)

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QIcon, QFont

try:
    from PIL import Image  # opcional (usado por PyInstaller/legacy)
except ImportError:  # pragma: no cover - PIL não é obrigatório na versão PySide6
    Image = None

from config.settings import settings
from services.sync_service import sync_service
from services.update_service import update_service
from services.github_update_service import github_update_service
from services.financeiro_service import financeiro_service
from services.auth_service import auth_service
from services.auditoria_service import auditoria_service, ACAO_LOGOUT
from utils.database import criar_banco, criar_caminhoes_padrao
from utils.sync import contar_pendencias_sync
from utils.logger import get_logger
from utils.preparar_distribuicao import preparar_base_para_distribuicao
from utils.env_check import verificar_configuracao_env

from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.icons import get_icon, get_pixmap
from utils.components_aurora import AuroraSidebar, AuroraTopBar, AuroraButton, ButtonStyle, SeparatorLine

# Importar telas Aurora
from telas.login_aurora import LoginAurora
from telas.dashboard_aurora import DashboardAurora
from telas.operacoes_pyside6 import TelaOperacoes
from telas.notas_pyside6 import TelaNotas
from telas.ranking_pyside6 import TelaRankingClientes
from telas.historico_versoes_pyside6 import TelaHistoricoVersoes

logger = get_logger(__name__)


# ------------------------------------------------------------------ Instrumentação
import time as _time
_START_TIME = _time.time()


def _log_step(msg: str) -> None:
    """Log com timestamp desde o boot, tanto no stdout quanto no logger.

    Usado para diagnóstico de startup lento. Se algo travar, o último `_log_step`
    impresso mostra onde.
    """
    elapsed = _time.time() - _START_TIME
    line = f"[STARTUP +{elapsed:6.2f}s] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    try:
        logger.info(line)
    except Exception:
        pass


class App(QMainWindow):
    """Aplicação principal CW Transportadora em PySide6."""

    # Sinal usado para propagar resultados do bootstrap de volta à UI thread.
    # QTimer.singleShot() NÃO é thread-safe quando chamado de threads não-Qt;
    # emitir um Signal é a forma correta de cruzar a barreira de thread em Qt.
    _bootstrap_concluido = Signal(object)  # payload: senha_mestre ou None
    _bootstrap_erro = Signal(str)

    def __init__(self):
        super().__init__()
        _log_step("App.__init__: início")

        # Conectar sinais do bootstrap antes de disparar a thread
        self._bootstrap_concluido.connect(self._on_bootstrap_concluido)
        self._bootstrap_erro.connect(self._on_bootstrap_erro)

        # Carregar configurações
        settings.reload()
        self.config = settings.configuracoes
        _log_step("App.__init__: settings.reload() ok")

        # Configurar tema Aurora
        self.cores = aurora_theme_manager.colors
        aurora_theme_manager.apply_to_app(QApplication.instance())
        _log_step("App.__init__: tema Aurora aplicado")

        # Estado da aplicação
        self.ultima_sync_texto = "Ainda não sincronizado"
        self.tela_atual = "dashboard"
        self.splash = None  # deprecated - mantido só pra compat

        # Configurar janela principal
        self._setup_window()
        _log_step("App.__init__: _setup_window ok")

        # Inicializar componentes
        self._init_components()
        _log_step("App.__init__: _init_components ok")

        # Mostrar login IMEDIATAMENTE (sem splash, sem espera)
        self._show_login()
        _log_step("App.__init__: _show_login ok (login criado)")

        # Preparar ambiente em THREAD REAL (banco, bcrypt, cloud check).
        # Aguardamos 50ms para garantir que o primeiro paint do login foi feito.
        QTimer.singleShot(50, self._start_background_bootstrap)
        _log_step("App.__init__: bootstrap agendado. __init__ concluído.")

    def _start_background_bootstrap(self):
        """Dispara o bootstrap em thread separada."""
        _log_step("bootstrap: disparando thread")
        threading.Thread(
            target=self._background_bootstrap,
            daemon=True,
            name="cw-bootstrap",
        ).start()

    def _background_bootstrap(self):
        """Roda inicialização pesada em thread separada (banco, cloud, etc).

        IMPORTANTE: nunca chamar QTimer.singleShot() daqui — não é thread-safe.
        Usamos Signal para despachar de volta para a UI thread.
        """
        try:
            _log_step("bootstrap[thread]: iniciando _prepare_environment")
            senha_mestre = self._prepare_environment()
            _log_step("bootstrap[thread]: _prepare_environment concluído")
            # Emitir sinal — Qt enfileira a chamada na UI thread automaticamente
            self._bootstrap_concluido.emit(senha_mestre)
        except Exception as erro:
            logger.error(f"Falha no bootstrap: {erro}", exc_info=True)
            self._bootstrap_erro.emit(str(erro))

    def _on_bootstrap_concluido(self, senha_mestre: object):
        """Chamado na UI thread quando o bootstrap termina com sucesso."""
        # Configurar atalhos agora que estamos na UI thread
        self._setup_shortcuts()
        if senha_mestre:
            self._show_master_password_dialog(senha_mestre)
        cloud_msg = getattr(self, "_cloud_warning_msg", None)
        if cloud_msg:
            QTimer.singleShot(900, lambda: self._show_cloud_warning(cloud_msg))
        self._check_saved_session()

    def _on_bootstrap_erro(self, mensagem: str):
        """Chamado na UI thread quando o bootstrap falha."""
        logger.error(f"Bootstrap falhou: {mensagem}")
        # Mesmo em caso de erro no bootstrap, o login ainda funciona normalmente
        self._check_saved_session()
    
    def _setup_window(self):
        """Configura a janela principal."""
        self.setWindowTitle("CW TRANSPORTADORA V8 — Sistema de Gestão Logística")
        self.setMinimumSize(1200, 720)
        self.resize(1550, 900)
        
        # Aplicar stylesheet do tema Aurora
        self.setStyleSheet(aurora_theme_manager.get_stylesheet())
        
        # Ícone da aplicação
        logo_path = str(settings.resource_path("assets/logo_cw.jpg"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # Fundo da área de conteúdo
        colors = aurora_theme_manager.colors
        self.setStyleSheet(self.styleSheet() + f"""
        QMainWindow {{
            background-color: {colors['bg_primary']};
        }}
        """)
    
    def _init_components(self):
        """Inicializa os componentes da UI."""
        # Container principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal (sidebar + right panel)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_layout)

        # Sidebar (será criada após login)
        self.sidebar = None

        # Right panel: topbar + content
        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightPanel")
        colors = aurora_theme_manager.colors
        self.right_panel.setStyleSheet(f"""
        QWidget#rightPanel {{
            background-color: {colors['bg_primary']};
        }}
        """)
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.right_panel.setLayout(self.right_layout)

        # TopBar (será criada após login)
        self.topbar = None

        # Área de conteúdo
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet(f"""
        QWidget#contentArea {{
            background-color: {colors['bg_primary']};
        }}
        """)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_area.setLayout(self.content_layout)

        # Stacked widget para telas
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        # Adicionar right panel ao layout principal
        self.main_layout.addWidget(self.right_panel, 1)

        # Tela de login (inicialmente)
        self.login_widget = None

        # Referências para telas
        self.telas = {}

        # Botões opcionais
        self.btn_sync = None

        # Títulos das telas (icônes usados em placeholders)
        self.titulos_telas = {
            "dashboard": ("PAINEL PRINCIPAL", "Controle operacional, financeiro e logístico da frota", "dashboard"),
            "operacoes": ("NOVA OPERAÇÃO", "Registro de transferências SP → Cascavel", "operations"),
            "notas": ("NOTAS IMPORTADAS", "Importação de manifestos TXT e gestão de notas", "notes"),
            "criar_viagem": ("CRIAR VIAGEM", "Montagem de viagens por cliente e seleção de notas", "truck"),
            "historico": ("VIAGENS", "Histórico, acompanhamento e finalização de viagens", "trips"),
            "ranking_clientes": ("RANKING DE CLIENTES", "Desempenho e volume por cliente", "ranking"),
            "combustivel": ("COMBUSTÍVEL", "Abastecimentos, consumo e média km/L", "fuel"),
            "contas": ("CONTAS", "Contas a pagar, a receber e fluxo financeiro", "accounts"),
            "relatorios": ("RELATÓRIOS", "Relatórios gerenciais e exportação em PDF", "reports"),
            "manutencao": ("MANUTENÇÃO", "Registro e controle de manutenção da frota", "maintenance"),
            "funcionarios": ("FUNCIONÁRIOS", "Cadastro de equipe e folha de pagamento", "employees"),
            "configuracoes": ("CONFIGURAÇÕES", "Empresa, backup, tema e preferências do sistema", "settings"),
            "historico_versoes": ("HISTÓRICO DE VERSÕES", "Informações de atualizações e releases do sistema", "history"),
            "minha_conta": ("MINHA CONTA", "Preferências e alteração de senha", "user"),
            "usuarios": ("GERENCIAR USUÁRIOS", "Administração de usuários e permissões", "admin"),
            "auditoria": ("AUDITORIA", "Registro de ações do sistema", "audit"),
            "publicar_versao": ("PUBLICAR VERSÃO", "Distribuir nova versão para todos os computadores", "upload"),
            "admin_atualizacoes": ("ADMIN. DE ATUALIZAÇÕES", "Gerencie publicações e visualize histórico de versões", "sync"),
        }
    
    def _create_splash(self):
        """Deprecated: não usamos mais splash - o login é mostrado direto."""
        self.splash = None
    
    def _prepare_environment(self) -> Optional[str]:
        """Prepara o ambiente do sistema (banco, cloud, backup).

        Retorna a senha gerada do primeiro mestre (ou None se já existia),
        para que o chamador possa exibir o diálogo na UI thread.

        IMPORTANTE: este método roda em thread de background.
        NÃO chamar QTimer.singleShot() aqui — use Signals para comunicar
        resultados de volta à UI thread.
        """
        # Criar banco de dados
        _log_step("prepare_env: criando banco...")
        criar_banco()
        _log_step("prepare_env: banco pronto")

        _log_step("prepare_env: caminhões padrão...")
        criar_caminhoes_padrao()
        _log_step("prepare_env: caminhões ok")

        # Garantir usuário mestre (PBKDF2 pode levar ~250ms — ok aqui em background)
        _log_step("prepare_env: garantindo usuário mestre...")
        senha_inicial_mestre = auth_service.garantir_usuario_mestre()
        _log_step("prepare_env: usuário mestre ok")

        # Verificar configuração de nuvem
        _log_step("prepare_env: verificando .env cloud...")
        _cloud_ok, _cloud_msg = verificar_configuracao_env()
        _log_step(f"prepare_env: cloud check -> ok={_cloud_ok}")
        if not _cloud_ok:
            # Armazena para exibir na UI thread via _on_bootstrap_concluido
            self._cloud_warning_msg = _cloud_msg
        else:
            self._cloud_warning_msg = None

        # Backup automático em sub-thread (não bloqueia o bootstrap)
        threading.Thread(target=self.backup_automatico, daemon=True).start()

        _log_step("prepare_env: concluído")
        return senha_inicial_mestre
    
    def _check_saved_session(self):
        """Verifica se há sessão salva - se houver, faz login automático."""
        usuario_salvo = auth_service.verificar_sessao_salva()

        if usuario_salvo:
            # Auto-login: transita direto pra interface principal
            QTimer.singleShot(300, self._init_main_interface)
    
    def _show_master_password_dialog(self, senha: str):
        """Mostra diálogo com senha do usuário mestre."""
        QMessageBox.information(
            self,
            "Usuário mestre criado",
            f"Um usuário mestre foi criado para o primeiro acesso:\n\n"
            f"  Usuário: bruno\n"
            f"  Senha temporária: {senha}\n\n"
            f"Essa senha também foi salva em "
            f"'{auth_service.arquivo_primeiro_acesso}'.\n"
            f"Você precisará trocá-la no primeiro login."
        )
    
    def _show_cloud_warning(self, mensagem: str):
        """Mostra aviso sobre sincronização desativada."""
        QMessageBox.warning(
            self,
            "⚠️ Sincronização Desativada",
            mensagem
        )
    
    def _show_login(self):
        """Mostra a tela de login imediatamente."""
        # Remover content area e topbar do right panel
        if self.content_area.parent() is self.right_panel:
            self.right_layout.removeWidget(self.content_area)
            self.content_area.setParent(None)
        if self.topbar and self.topbar.parent() is self.right_panel:
            self.right_layout.removeWidget(self.topbar)
            self.topbar.setParent(None)

        # Se já existe login, não duplicar
        if self.login_widget is not None:
            return

        self.login_widget = LoginAurora()
        self.login_widget.login_sucesso.connect(self._on_login_success)

        self.main_layout.addWidget(self.login_widget)

        # Fechar splash se ainda estiver visível (compat)
        self._close_splash()

    def _close_splash(self):
        """Fecha o splash com segurança (idempotente)."""
        splash = getattr(self, "splash", None)
        if splash is None:
            return
        try:
            if splash.isVisible():
                splash.close()
        except RuntimeError:
            # splash já destruído
            pass

    def _splash_message(self, texto: str):
        """Atualiza a mensagem do splash se ele ainda existir."""
        splash = getattr(self, "splash", None)
        if splash is None:
            return
        try:
            if splash.isVisible():
                splash.showMessage(
                    texto,
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                    Qt.GlobalColor.white,
                )
        except RuntimeError:
            pass
    
    def _on_login_success(self, usuario_dados: Dict[str, Any]):
        """Callback quando login é bem-sucedido."""
        # Remover tela de login
        if self.login_widget:
            self.main_layout.removeWidget(self.login_widget)
            self.login_widget.deleteLater()
            self.login_widget = None
        
        # Verificar se precisa alterar senha
        if usuario_dados.get("deve_alterar_senha"):
            # TODO: Implementar modal de alteração de senha
            pass
        
        # Iniciar interface principal
        self._init_main_interface()
    
    def _init_main_interface(self):
        """Inicializa a interface principal após login."""
        QApplication.processEvents()

        # Criar sidebar + topbar
        self._create_sidebar()

        # Adicionar content area ao right panel (após topbar)
        self.right_layout.addWidget(self.content_area, 1)
        self.content_area.show()

        # Carregar dashboard
        QTimer.singleShot(0, self._load_dashboard)

        # Atualizar status de sync
        self.atualizar_ultima_sync(sync_service.ultimo_resultado)

        # Iniciar sincronização em background
        QTimer.singleShot(500, lambda: self.sincronizar_nuvem(mostrar_mensagem=False, reparar_fila=True))
        self.iniciar_sync_automatico()

        # Verificar atualizações em background
        QTimer.singleShot(1500, self.verificar_atualizacao_inicio)
    
    def _create_sidebar(self):
        """Cria a sidebar de navegação e TopBar Aurora."""
        # --- TopBar Aurora ---
        self.topbar = AuroraTopBar()
        usuario = auth_service.usuario_atual or {}
        usuario_id = usuario.get("id")
        nome_usuario = usuario.get("nome_completo", "Usuário")
        avatar_letter = nome_usuario[0] if nome_usuario else "U"
        self.topbar.set_user_info(nome_usuario, avatar_letter, usuario_id=usuario_id)
        self.topbar.profile_requested.connect(lambda: self._on_navigation("minha_conta"))
        self.topbar.settings_requested.connect(lambda: self._on_navigation("configuracoes"))
        self.topbar.password_requested.connect(lambda: self._on_navigation("minha_conta"))
        self.topbar.logout_requested.connect(self.fazer_logout)
        self.right_layout.addWidget(self.topbar)

        # --- Sidebar Aurora ---
        self.sidebar = AuroraSidebar()
        self.sidebar.navigation_requested.connect(self._on_navigation)

        # User card
        nivel = usuario.get("nivel", "operador")
        nivel_label = "Mestre" if nivel == "mestre" else "Operador"
        self.sidebar.add_user_card(nome_usuario, nivel_label, avatar_letter, usuario_id=usuario_id)

        # Menu items
        self.sidebar.add_section("Principal")
        self.sidebar.add_menu_item("dashboard", "Dashboard", "home", AccentColor.AURORA)

        self.sidebar.add_section("Operacional")
        self.sidebar.add_menu_item("operacoes", "Nova Operação", "operations", AccentColor.AURORA)
        self.sidebar.add_menu_item("notas", "Notas", "notes", AccentColor.AURORA)
        self.sidebar.add_menu_item("criar_viagem", "Criar Viagem", "truck", AccentColor.OCEAN)
        self.sidebar.add_menu_item("historico", "Viagens", "trips", AccentColor.OCEAN)
        self.sidebar.add_menu_item("ranking_clientes", "Ranking", "ranking", AccentColor.EMBER)

        self.sidebar.add_section("Frota")
        self.sidebar.add_menu_item("combustivel", "Combustível", "fuel", AccentColor.FOREST)
        self.sidebar.add_menu_item("manutencao", "Manutenção", "maintenance", AccentColor.EMBER)

        self.sidebar.add_section("Financeiro")
        self.sidebar.add_menu_item("contas", "Contas", "accounts", AccentColor.CRIMSON)
        self.sidebar.add_menu_item("relatorios", "Relatórios", "reports", AccentColor.COSMOS)

        self.sidebar.add_section("RH")
        self.sidebar.add_menu_item("funcionarios", "Funcionários", "employees", AccentColor.OCEAN)

        self.sidebar.add_section("Sistema")
        self.sidebar.add_menu_item("configuracoes", "Configurações", "settings", AccentColor.AURORA)

        if auth_service.eh_mestre:
            self.sidebar.add_section("Administração")
            self.sidebar.add_menu_item("usuarios", "Usuários", "admin", AccentColor.AURORA)
            self.sidebar.add_menu_item("auditoria", "Auditoria", "audit", AccentColor.EMBER)
            self.sidebar.add_menu_item("historico_versoes", "Versões", "history", AccentColor.COSMOS)

        # Bottom: sync + logout
        separator = SeparatorLine("horizontal")
        self.sidebar.add_bottom_widget(separator)

        self.btn_sync = AuroraButton("Sincronizar", ButtonStyle.OCEAN, "sync", parent=self.sidebar)
        self.btn_sync.clicked.connect(lambda: self.sincronizar_nuvem(mostrar_mensagem=True))
        self.sidebar.add_bottom_widget(self.btn_sync)

        btn_logout = AuroraButton("Sair", ButtonStyle.GHOST, "logout", parent=self.sidebar)
        btn_logout.clicked.connect(self.fazer_logout)
        self.sidebar.add_bottom_widget(btn_logout)

        # Insert sidebar at the beginning of main_layout
        self.main_layout.insertWidget(0, self.sidebar)
        self.sidebar.set_active_item("dashboard")
        self._update_breadcrumb("dashboard")
    
    def _create_header(self):
        """Deprecated: cada tela agora possui seu próprio cabeçalho."""
        return None

    def _on_navigation(self, tela: str):
        """Manipula navegação entre telas."""
        self.sidebar.set_active_item(tela)
        self._load_tela(tela)
        self._update_breadcrumb(tela)

    def _update_breadcrumb(self, tela: str):
        """Atualiza o breadcrumb da TopBar."""
        if not self.topbar:
            return
        section_map = {
            "dashboard": ("Principal", "Dashboard"),
            "operacoes": ("Operacional", "Nova Operação"),
            "notas": ("Operacional", "Notas"),
            "criar_viagem": ("Operacional", "Criar Viagem"),
            "historico": ("Operacional", "Viagens"),
            "ranking_clientes": ("Operacional", "Ranking"),
            "combustivel": ("Frota", "Combustível"),
            "manutencao": ("Frota", "Manutenção"),
            "contas": ("Financeiro", "Contas"),
            "relatorios": ("Financeiro", "Relatórios"),
            "funcionarios": ("RH", "Funcionários"),
            "configuracoes": ("Sistema", "Configurações"),
            "minha_conta": ("Sistema", "Meu Perfil"),
            "usuarios": ("Administração", "Usuários"),
            "auditoria": ("Administração", "Auditoria"),
            "historico_versoes": ("Administração", "Versões"),
        }
        section, page = section_map.get(tela, ("", tela.replace("_", " ").title()))
        self.topbar.set_breadcrumb(section, page)

    def _load_tela(self, tela: str):
        """Carrega uma tela específica (com placeholder polido para telas não migradas)."""
        self.tela_atual = tela

        # Despachar para o método específico de cada tela
        loaders = {
            "dashboard": self._load_dashboard,
            "operacoes": self._load_operacoes,
            "notas": self._load_notas,
            "ranking_clientes": self._load_ranking_clientes,
            "historico_versoes": self._load_historico_versoes,
            "criar_viagem": self._load_criar_viagem,
            "historico": self._load_historico,
            "combustivel": self._load_combustivel,
            "manutencao": self._load_manutencao,
            "contas": self._load_contas,
            "relatorios": self._load_relatorios,
            "funcionarios": self._load_funcionarios,
            "configuracoes": self._load_configuracoes,
            "usuarios": self._load_usuarios,
            "auditoria": self._load_auditoria,
            "minha_conta": self._load_perfil,
        }

        loader = loaders.get(tela)
        if loader:
            loader()
            return

        # Fallback: placeholder para telas ainda não migradas
        if tela not in self.telas:
            from utils.components_aurora import PlaceholderScreen
            titulo, subtitulo, icone = self.titulos_telas.get(
                tela, (tela.upper(), "Tela em desenvolvimento", "settings")
            )
            accent_por_tela = {
                "minha_conta": AccentColor.AURORA,
                "publicar_versao": AccentColor.FOREST,
                "admin_atualizacoes": AccentColor.AURORA,
            }.get(tela, AccentColor.AURORA)

            placeholder = PlaceholderScreen(
                title=titulo,
                subtitle=subtitulo,
                icon_name=icone,
                accent=accent_por_tela,
            )
            self.telas[tela] = placeholder
            self.stacked_widget.addWidget(placeholder)

        self.stacked_widget.setCurrentWidget(self.telas[tela])
    
    def _load_dashboard(self):
        """Carrega o dashboard Aurora."""
        if "dashboard" not in self.telas:
            try:
                self.telas["dashboard"] = DashboardAurora()
            except Exception as erro:
                logger.error(f"Falha ao carregar dashboard Aurora: {erro}")
                from utils.components_aurora import PlaceholderScreen
                self.telas["dashboard"] = PlaceholderScreen(
                    title="PAINEL PRINCIPAL",
                    subtitle=f"N\u00e3o foi poss\u00edvel carregar o dashboard.\n{erro}",
                    icon_name="warning",
                    accent=AccentColor.CRIMSON,
                )
            self.stacked_widget.addWidget(self.telas["dashboard"])

        self.stacked_widget.setCurrentWidget(self.telas["dashboard"])
        self.tela_atual = "dashboard"

    def _carregar_tela_generica(self, chave: str, classe):
        """Carrega uma tela PySide6 de forma genérica com tratamento de erro."""
        if chave not in self.telas:
            try:
                self.telas[chave] = classe()
            except Exception as erro:
                logger.error(f"Falha ao carregar tela '{chave}': {erro}")
                from utils.components_aurora import PlaceholderScreen
                titulo, subtitulo, icone = self.titulos_telas.get(
                    chave, (chave.upper(), "Erro ao carregar", "warning")
                )
                self.telas[chave] = PlaceholderScreen(
                    title=titulo,
                    subtitle=f"Não foi possível carregar esta tela.\n{erro}",
                    icon_name="warning",
                    accent=AccentColor.CRIMSON,
                )
            self.stacked_widget.addWidget(self.telas[chave])
        self.stacked_widget.setCurrentWidget(self.telas[chave])
        self.tela_atual = chave

    def _load_operacoes(self):
        self._carregar_tela_generica("operacoes", TelaOperacoes)

    def _load_notas(self):
        self._carregar_tela_generica("notas", TelaNotas)

    def _load_ranking_clientes(self):
        self._carregar_tela_generica("ranking_clientes", TelaRankingClientes)

    def _load_historico_versoes(self):
        self._carregar_tela_generica("historico_versoes", TelaHistoricoVersoes)

    def _load_criar_viagem(self):
        from telas.criar_viagem_pyside6 import TelaCriarViagem
        self._carregar_tela_generica("criar_viagem", TelaCriarViagem)

    def _load_historico(self):
        from telas.historico_pyside6 import TelaHistorico
        self._carregar_tela_generica("historico", TelaHistorico)

    def _load_combustivel(self):
        from telas.combustivel_pyside6 import TelaCombustivel
        self._carregar_tela_generica("combustivel", TelaCombustivel)

    def _load_manutencao(self):
        from telas.manutencao_pyside6 import TelaManutencao
        self._carregar_tela_generica("manutencao", TelaManutencao)

    def _load_contas(self):
        from telas.contas_pyside6 import TelaContas
        self._carregar_tela_generica("contas", TelaContas)

    def _load_relatorios(self):
        from telas.relatorios_pyside6 import TelaRelatorios
        self._carregar_tela_generica("relatorios", TelaRelatorios)

    def _load_funcionarios(self):
        from telas.funcionarios_pyside6 import TelaFuncionarios
        self._carregar_tela_generica("funcionarios", TelaFuncionarios)

    def _load_configuracoes(self):
        from telas.configuracoes_pyside6 import TelaConfiguracoes
        self._carregar_tela_generica("configuracoes", TelaConfiguracoes)

    def _load_usuarios(self):
        from telas.gerenciar_usuarios_pyside6 import TelaGerenciarUsuarios
        self._carregar_tela_generica("usuarios", TelaGerenciarUsuarios)

    def _load_perfil(self):
        from telas.perfil_pyside6 import TelaPerfil
        self._carregar_tela_generica("minha_conta", TelaPerfil)

    def _load_auditoria(self):
        from telas.auditoria_pyside6 import TelaAuditoria
        self._carregar_tela_generica("auditoria", TelaAuditoria)

    def fazer_logout(self):
        """Faz logout do usuário."""
        usuario = auth_service.usuario_atual
        if usuario:
            auditoria_service.registrar(
                ACAO_LOGOUT, "auth", usuario["usuario"],
                usuario_id=usuario["id"],
                usuario_nome=usuario["nome_completo"],
            )
        auth_service.logout()

        # Limpar UI principal
        if self.sidebar:
            self.main_layout.removeWidget(self.sidebar)
            self.sidebar.deleteLater()
            self.sidebar = None

        if self.topbar:
            self.right_layout.removeWidget(self.topbar)
            self.topbar.deleteLater()
            self.topbar = None

        # Remover área de conteúdo e limpar telas cacheadas
        if self.content_area.parent() is self.right_panel:
            self.right_layout.removeWidget(self.content_area)
            self.content_area.setParent(None)

        for nome, widget in list(self.telas.items()):
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        self.telas.clear()

        self.btn_sync = None

        # Mostrar login novamente
        self._show_login()
    
    def backup_automatico(self):
        """Executa backup automático do banco de dados."""
        try:
            pasta_backup = settings.backup_auto_dir
            origem_db = settings.db_path
            
            if not origem_db.exists():
                return
            
            if not pasta_backup.exists():
                pasta_backup.mkdir(parents=True, exist_ok=True)
            
            nome_backup = f"backup_auto_{datetime.now().strftime('%d%m%Y_%H%M%S')}.db"
            destino_db = pasta_backup / nome_backup
            
            shutil.copy2(origem_db, destino_db)
            
            # Manter apenas os últimos 20 backups
            backups = sorted(
                pasta_backup.glob("*.db"),
                key=lambda item: item.stat().st_mtime,
                reverse=True
            )
            
            for backup_antigo in backups[20:]:
                backup_antigo.unlink(missing_ok=True)
        
        except Exception as erro:
            logger.error(f"Erro no backup automático: {erro}")
    
    def preparar_distribuicao(self):
        """Prepara a base para distribuição."""
        if sync_service.sincronizando:
            QMessageBox.warning(
                self,
                "Sincronização em andamento",
                "Aguarde a sincronização terminar antes de preparar a distribuição."
            )
            return
        
        confirmar, ok = QInputDialog.getText(
            self,
            "Preparar Distribuição",
            "ATENÇÃO!\n\n"
            "Isso vai apagar TODOS os dados locais e da nuvem.\n\n"
            "Digite ZERAR para confirmar:",
            QLineEdit.EchoMode.Normal,
            "",
        )
        
        if not ok or confirmar != "ZERAR":
            return
        
        criar_backup = QMessageBox.question(
            self,
            "Backup",
            "Deseja criar um backup antes de limpar?\n\n"
            "Sim = cria backup\n"
            "Não = limpa sem backup",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if criar_backup == QMessageBox.StandardButton.Cancel:
            return
        
        try:
            backup = preparar_base_para_distribuicao(
                criar_backup=(criar_backup == QMessageBox.StandardButton.Yes)
            )
            
            if backup:
                mensagem = f"Base zerada com sucesso!\n\nBackup criado em:\n{backup}"
            else:
                mensagem = "Base zerada com sucesso!\n\nNenhum backup foi criado."
            
            QMessageBox.information(self, "Preparação concluída", mensagem)
        
        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao preparar distribuição",
                f"Não foi possível concluir a preparação da distribuição.\n\nDetalhes: {str(erro)}"
            )
    
    def sincronizar_nuvem(self, mostrar_mensagem=False, reparar_fila=True):
        """Sincroniza dados com a nuvem."""
        if sync_service.sincronizando:
            return
        
        inicio = datetime.now()
        
        if self.btn_sync:
            self.btn_sync.setText("☁️ Sincronizando...")
            self.btn_sync.setEnabled(False)
        
        def tarefa():
            try:
                resultado = sync_service.executar(reparar_fila=reparar_fila)
                
                cor = resultado.get("status")
                if resultado.get("offline"):
                    cor = "offline"
                elif resultado.get("status") == "partial":
                    cor = "partial"
                elif resultado.get("status") == "error":
                    cor = "error"
                
                duracao = (datetime.now() - inicio).total_seconds()
                
                # Atualizar UI na thread principal
                QTimer.singleShot(0, lambda: self._atualizar_status_sync(resultado, cor, duracao))
                
                if mostrar_mensagem:
                    QTimer.singleShot(0, lambda: QMessageBox.information(
                        self,
                        "Sincronização",
                        resultado.get("mensagem", "Sincronização concluída!")
                    ))
            
            except Exception as erro:
                QTimer.singleShot(0, lambda: self._mostrar_erro_sync(erro, mostrar_mensagem))
            
            finally:
                QTimer.singleShot(0, self._reset_sync_button)
        
        threading.Thread(target=tarefa, daemon=True).start()
    
    def _atualizar_status_sync(self, resultado, cor, duracao):
        """Atualiza o status de sincronização na UI."""
        self.atualizar_ultima_sync(resultado)
        
        if self.btn_sync:
            texto = "☁️ Sincronizar Nuvem" if settings.supabase_enabled else "☁️ Modo Local"
            self.btn_sync.setText(texto)
    
    def _mostrar_erro_sync(self, erro, mostrar_mensagem):
        """Mostra erro de sincronização."""
        if self.btn_sync:
            self.btn_sync.setText("☁️ Sincronizar Nuvem")
        
        if mostrar_mensagem:
            QMessageBox.critical(
                self,
                "Erro ao sincronizar",
                f"A sincronização não pôde ser concluída.\n\nDetalhes: {str(erro)}"
            )
    
    def _reset_sync_button(self):
        """Reseta o botão de sincronização."""
        if self.btn_sync:
            texto = "☁️ Sincronizar Nuvem" if settings.supabase_enabled else "☁️ Modo Local"
            self.btn_sync.setText(texto)
            self.btn_sync.setEnabled(True)
    
    def atualizar_ultima_sync(self, resultado=None):
        """Atualiza informações da última sincronização."""
        resultado = resultado or {}
        pendencias = resultado.get("pendencias", contar_pendencias_sync())
        ultima_sync = resultado.get("ultima_sync")
        offline = resultado.get("offline", False)
        
        if offline:
            self.ultima_sync_texto = "⚪ Modo local"
        else:
            agora_txt = ultima_sync or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.ultima_sync_texto = f"🟢 Online - Última sync: {agora_txt}"
        
        # TODO: Atualizar label na sidebar quando implementado
    
    def iniciar_sync_automatico(self):
        """Inicia sincronização automática em intervalos regulares."""
        intervalo = settings.intervalo_sync_ms
        QTimer.singleShot(intervalo, self.executar_sync_automatico)
    
    def executar_sync_automatico(self):
        """Executa sincronização automática."""
        if not sync_service.sincronizando:
            self.sincronizar_nuvem(mostrar_mensagem=False, reparar_fila=False)
        
        intervalo = settings.intervalo_sync_ms
        QTimer.singleShot(intervalo, self.executar_sync_automatico)
    
    def verificar_atualizacao_inicio(self):
        """Verifica atualizações em background ao iniciar."""
        def tarefa():
            try:
                if settings.github_use_cdn and settings.github_repo_owner and settings.github_repo_name:
                    resultado = github_update_service.check_for_updates()
                else:
                    resultado = update_service.check_for_updates()
                
                if resultado.get("has_update") and resultado.get("download_url"):
                    QTimer.singleShot(0, lambda: self._mostrar_dialogo_atualizacao(resultado))
            except Exception as e:
                logger.error(f"Erro ao verificar atualização ao iniciar: {e}")
        
        threading.Thread(target=tarefa, daemon=True).start()
    
    def _mostrar_dialogo_atualizacao(self, resultado):
        """Mostra diálogo de atualização disponível."""
        # TODO: Implementar tela de atualização PySide6
        QMessageBox.information(
            self,
            "Atualização Disponível",
            f"Nova versão disponível: {resultado.get('version', 'N/A')}\n\n"
            f"Detalhes: {resultado.get('mensagem', 'Consulte o histórico de versões.')}"
        )
    
    def _setup_shortcuts(self):
        """Configura atalhos de teclado."""
        # TODO: Implementar atalhos com QShortcut
        pass
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela."""
        # Backup automático ao fechar
        self.backup_automatico()
        
        # Confirmar fechamento
        reply = QMessageBox.question(
            self,
            "Fechar Sistema",
            "Deseja realmente fechar o CW Transportadora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Função principal para iniciar a aplicação."""
    _log_step("main(): início")

    # Habilitar high-DPI se disponível
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    # Criar aplicação Qt
    _log_step("main(): criando QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("CW Transportadora")
    app.setOrganizationName("CW Transportadora")
    _log_step("main(): QApplication pronto")

    # Fonte padrão consistente (Segoe UI no Windows, fallback automático)
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # Ícone global
    logo_path = str(settings.resource_path("assets/logo_cw.jpg"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    # Criar e mostrar janela principal
    _log_step("main(): instanciando App()...")
    window = App()
    _log_step("main(): App() pronto")

    # Log da tela primária para diagnóstico
    try:
        screen = app.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            _log_step(
                f"main(): tela primária = {geo.width()}x{geo.height()} "
                f"@ ({geo.x()},{geo.y()}) DPR={screen.devicePixelRatio()}"
            )
    except Exception as exc:
        _log_step(f"main(): falha ao consultar tela: {exc}")

    # Estratégia bulletproof: abrir maximizada + garantir foco.
    # showMaximized() ocupa a tela inteira — impossível não ver.
    _log_step("main(): chamando showMaximized()")

    # Forçar StaysOnTop temporário (removido depois de 3s) para
    # vencer a política de foco do Windows 11/25H2 quando lançado via py.exe
    window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    window.showMaximized()
    window.raise_()
    window.activateWindow()

    def _remover_stays_on_top():
        try:
            window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            window.show()  # re-mostra pra aplicar a mudança de flag
            _log_step("main(): WindowStaysOnTopHint removido")
        except Exception as exc:
            _log_step(f"main(): falha ao remover stays-on-top: {exc}")

    QTimer.singleShot(3000, _remover_stays_on_top)

    # Log da geometria efetiva após show
    try:
        g = window.geometry()
        _log_step(
            f"main(): geometria efetiva = {g.width()}x{g.height()} @ ({g.x()},{g.y()}) "
            f"visible={window.isVisible()} minimized={window.isMinimized()} "
            f"maximized={window.isMaximized()}"
        )
    except Exception:
        pass

    _log_step("main(): entrando em app.exec()")

    # Executar loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
