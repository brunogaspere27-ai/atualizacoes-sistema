import os
import sys
import shutil
import threading
import customtkinter as ctk
from utils.preparar_distribuicao import preparar_base_para_distribuicao
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image

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

from telas.login import TelaLogin
from telas.alterar_senha import ModalAlterarSenha
from telas.gerenciar_usuarios import TelaGerenciarUsuarios
from telas.auditoria import TelaAuditoria
from telas.dashboard import Dashboard
from telas.operacoes import TelaOperacoes
from telas.contas import TelaContas
from telas.historico import TelaHistorico
from telas.ranking_clientes import TelaRankingClientes
from telas.funcionarios import TelaFuncionarios
from telas.combustivel import TelaCombustivel
from telas.manutencao import TelaManutencao
from telas.relatorios import TelaRelatorios
from telas.configuracoes import TelaConfiguracoes
from telas.atualizacao import TelaAtualizacao
from telas.historico_versoes import TelaHistoricoVersoes
from telas.notas import TelaNotas
from telas.criar_viagem import TelaCriarViagem
from telas.publicar_versao import abrir_publicar_versao
from telas.admin_atualizacoes import abrir_admin_atualizacoes

logger = get_logger(__name__)


from telas.theme import setup_theme
from utils.splash_screen import SplashScreen
from utils.env_check import verificar_configuracao_env


def mostrar_erro_profissional(master, titulo: str, mensagem: str, detalhe: str | None = None):
    """Exibe um erro com mensagem amigável e detalhe opcional."""
    if detalhe:
        mensagem = f"{mensagem}\n\nDetalhes: {detalhe}"
    messagebox.showerror(titulo, mensagem)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        settings.reload()
        self.config = settings.configuracoes
        # configure global theme and obtain colors
        self.cores = setup_theme(settings)

        self.ultima_sync_texto = "Ainda não sincronizado"

        self.title("CW TRANSPORTADORA V6 - Sistema de Gestão Logística")
        self.geometry("1550x900")
        self.minsize(1300, 780)
        self.configure(fg_color=self.cores["fundo"])

        self.base_dir = str(settings.project_dir)
        self.logo_path = str(settings.resource_path("assets/logo_cw.jpg"))

        # Criar splash screen
        self.splash = SplashScreen(self, self.logo_path)
        self.update_idletasks()

        self.splash.update_status("Preparando ambiente...")
        criar_banco()
        criar_caminhoes_padrao()

        # Garantir usuario mestre existe (gera senha aleatoria no primeiro boot)
        senha_inicial_mestre = auth_service.garantir_usuario_mestre()
        if senha_inicial_mestre:
            self.after(500, lambda s=senha_inicial_mestre: messagebox.showinfo(
                "Usuário mestre criado",
                "Um usuário mestre foi criado para o primeiro acesso:\n\n"
                "  Usuário: bruno\n"
                f"  Senha temporária: {s}\n\n"
                "Essa senha também foi salva em "
                f"'{auth_service.arquivo_primeiro_acesso}'.\n"
                "Você precisará trocá-la no primeiro login."
            ))

        # Verificar configuração de nuvem e avisar usuário se necessário
        _cloud_ok, _cloud_msg = verificar_configuracao_env()
        if not _cloud_ok:
            self.after(900, lambda m=_cloud_msg: messagebox.showwarning(
                "⚠️ Sincronização Desativada", m
            ))

        self.splash.update_status("Carregando interface...")
        self.backup_automatico()
        self.protocol("WM_DELETE_WINDOW", self.fechar_sistema)

        self.botoes_menu = []
        self.tela_atual = "dashboard"
        self.mapa_botoes = {}
        self.sidebar = None
        self.area_direita = None
        self.container = None
        self.header = None
        self._login_view = None

        self.titulos_telas = {
            "dashboard": ("PAINEL PRINCIPAL", "Controle operacional, financeiro e logístico da frota"),
            "operacoes": ("NOVA OPERAÇÃO", "Registro de transferências SP → Cascavel"),
            "notas": ("NOTAS IMPORTADAS", "Importação de manifestos TXT e gestão de notas"),
            "criar_viagem": ("CRIAR VIAGEM", "Montagem de viagens por cliente e seleção de notas"),
            "historico": ("VIAGENS", "Histórico, acompanhamento e finalização de viagens"),
            "ranking_clientes": ("RANKING DE CLIENTES", "Desempenho e volume por cliente"),
            "combustivel": ("COMBUSTÍVEL", "Abastecimentos, consumo e média km/L"),
            "contas": ("CONTAS", "Contas a pagar, a receber e fluxo financeiro"),
            "relatorios": ("RELATÓRIOS", "Relatórios gerenciais e exportação em PDF"),
            "manutencao": ("MANUTENÇÃO", "Registro e controle de manutenção da frota"),
            "funcionarios": ("FUNCIONÁRIOS", "Cadastro de equipe e folha de pagamento"),
            "configuracoes": ("CONFIGURAÇÕES", "Empresa, backup, tema e preferências do sistema"),
            "historico_versoes": ("HISTORICO DE VERSOES", "Informacoes de atualizacoes e releases do sistema"),
            "usuarios": ("GERENCIAR USUÁRIOS", "Administração de usuários e permissões"),
            "auditoria": ("AUDITORIA", "Registro de ações do sistema"),
            "publicar_versao": ("PUBLICAR VERSÃO", "Distribuir nova versão para todos os computadores"),
            "admin_atualizacoes": ("ADMINISTRAÇÃO DE ATUALIZAÇÕES", "Gerencie publicações e visualize histórico de versões"),
        }

        # Verificar sessao salva (Lembrar de mim)
        usuario_salvo = auth_service.verificar_sessao_salva()

        if usuario_salvo:
            self.splash.update_status(f"Bem-vindo, {usuario_salvo['nome_completo']}!")
            self._iniciar_app_principal()
        else:
            self._mostrar_tela_login()

    def _mostrar_tela_login(self):
        """Exibe a tela de login no container principal."""
        # Limpar qualquer view existente
        for child in self.winfo_children():
            if child not in (getattr(self, 'splash', None),):
                try:
                    child.destroy()
                except Exception:
                    pass

        self._login_view = TelaLogin(self, on_login_sucesso=self._on_login_sucesso)
        self._login_view.pack(fill="both", expand=True)

        # Fechar splash se ainda estiver aberto
        try:
            if hasattr(self, 'splash') and self.splash:
                self.after(300, self.splash.close)
        except Exception:
            pass

    def _on_login_sucesso(self, usuario_dados):
        """Chamado quando o login é bem-sucedido."""
        # Destruir tela de login
        if self._login_view:
            self._login_view.destruir_binds()
            self._login_view.destroy()
            self._login_view = None

        # Verificar se precisa alterar senha (primeiro login)
        if usuario_dados.get("deve_alterar_senha"):
            ModalAlterarSenha(
                self,
                obrigatorio=True,
                on_sucesso=lambda: self._iniciar_app_principal(),
            )
        else:
            self._iniciar_app_principal()

    def _iniciar_app_principal(self):
        """Constroi a interface principal apos autenticacao."""
        self.splash.update_status("Montando interface...")
        self.botoes_menu = []
        self.mapa_botoes = {}
        self.criar_sidebar()
        self.criar_area_principal()
        self.mostrar_dashboard()
        self.atualizar_ultima_sync(sync_service.ultimo_resultado)

        self.splash.update_status("Sincronizando dados...")
        self.sincronizar_nuvem(mostrar_mensagem=False, reparar_fila=True)
        self.iniciar_sync_automatico()

        self.verificar_atualizacao_inicio()
        self.configurar_atalhos()

        self.splash.update_status("Pronto!")
        self.after(500, self.splash.close)

    def fazer_logout(self):
        """Faz logout: limpa sessao e volta para tela de login."""
        usuario = auth_service.usuario_atual
        if usuario:
            auditoria_service.registrar(
                ACAO_LOGOUT, "auth", usuario["usuario"],
                usuario_id=usuario["id"],
                usuario_nome=usuario["nome_completo"],
            )
        auth_service.logout()

        # Destruir UI principal
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None
        if self.area_direita:
            self.area_direita.destroy()
            self.area_direita = None

        self._mostrar_tela_login()

    def mostrar_alterar_senha(self):
        """Abre modal para alterar a propria senha."""
        ModalAlterarSenha(self, obrigatorio=False)

    def mostrar_usuarios(self):
        """Tela de gerenciamento de usuarios (apenas mestre)."""
        if not auth_service.tem_permissao("usuarios", "visualizar"):
            messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar este modulo.")
            return
        self.limpar_tela()
        self.atualizar_header("usuarios")
        self.tela_usuarios = TelaGerenciarUsuarios(self.container)
        self.tela_usuarios.pack(fill="both", expand=True)

    def mostrar_auditoria(self):
        """Tela de auditoria (apenas mestre)."""
        if not auth_service.tem_permissao("auditoria", "visualizar"):
            messagebox.showwarning("Acesso Negado", "Voce nao tem permissao para acessar este modulo.")
            return
        self.limpar_tela()
        self.atualizar_header("auditoria")
        self.tela_auditoria = TelaAuditoria(self.container)
        self.tela_auditoria.pack(fill="both", expand=True)


    def backup_automatico(self):
        try:
            pasta_backup = settings.backup_auto_dir
            origem_db = settings.db_path

            if not origem_db.exists():
                return

            # Garante que a pasta existe antes de tentar copiar
            if not pasta_backup.exists():
                pasta_backup.mkdir(parents=True, exist_ok=True)

            nome_backup = f"backup_auto_{datetime.now().strftime('%d%m%Y_%H%M%S')}.db"
            destino_db = pasta_backup / nome_backup

            shutil.copy2(origem_db, destino_db)

            backups = sorted(
                pasta_backup.glob("*.db"),
                key=lambda item: item.stat().st_mtime,
                reverse=True
            )

            for backup_antigo in backups[20:]:
                backup_antigo.unlink(missing_ok=True)

        except Exception as erro:
            logger.error(f"Erro no backup automático: {erro}")

    def criar_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=275,
            fg_color=self.cores["sidebar"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo (fixo no topo)
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.cores["sidebar"],
            corner_radius=0
        )
        logo_frame.pack(fill="x", pady=(25, 15))

        if os.path.exists(self.logo_path):
            with Image.open(self.logo_path) as logo_image:
                imagem = ctk.CTkImage(
                    light_image=logo_image.copy(),
                    dark_image=logo_image.copy(),
                    size=(185, 115)
                )
            ctk.CTkLabel(logo_frame, image=imagem, text="").pack(pady=(0, 5))
        else:
            ctk.CTkLabel(
                logo_frame,
                text="CW",
                font=(self.cores["font_family"], 48, "bold"),
                text_color="#DC2626"
            ).pack(pady=(0, 5))

        ctk.CTkLabel(
            logo_frame,
            text="CW TRANSPORTADORA",
            font=(self.cores["font_family"], 14, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(0, 10))

        # Area scrollavel para botoes de menu
        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color=self.cores["sidebar"],
            scrollbar_button_color=self.cores.get("sidebar_card", "#1F2937"),
            scrollbar_button_hover_color=self.cores.get("hover", "#374151"),
        )
        self.sidebar_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self.criar_botao_menu("🏠  Página Inicial", self.mostrar_dashboard, "dashboard")
        self.criar_botao_menu("🧾  Nova Operação", self.mostrar_operacoes, "operacoes")
        self.criar_botao_menu("📋  Notas Importadas", self.mostrar_notas, "notas")
        self.criar_botao_menu("🚚  Criar Viagem", self.mostrar_criar_viagem, "criar_viagem")
        self.criar_botao_menu("📊  Viagens", self.mostrar_historico, "historico")
        self.criar_botao_menu("🏆  Ranking Clientes", self.mostrar_ranking_clientes, "ranking_clientes")
        self.criar_botao_menu("⛽  Combustível", self.mostrar_combustivel, "combustivel")
        self.criar_botao_menu("💳  Contas", self.mostrar_contas, "contas")
        self.criar_botao_menu("📊  Relatórios", self.mostrar_relatorios, "relatorios")
        self.criar_botao_menu("🔧  Manutenção", self.mostrar_manutencao, "manutencao")
        self.criar_botao_menu("👥  Funcionários", self.mostrar_funcionarios, "funcionarios")
        self.criar_botao_menu("⚙️  Configurações", self.mostrar_configuracoes, "configuracoes")

        # Botoes administrativos (visiveis apenas para mestre)
        if auth_service.eh_mestre:
            ctk.CTkFrame(self.sidebar_scroll, fg_color="#1E293B", height=1).pack(fill="x", padx=20, pady=(8, 4))
            self.criar_botao_menu("👑  Usuários", self.mostrar_usuarios, "usuarios")
            self.criar_botao_menu("📋  Auditoria", self.mostrar_auditoria, "auditoria")
            self.criar_botao_menu("🔄  Historico Versoes", self.mostrar_historico_versoes, "historico_versoes")
            ctk.CTkFrame(self.sidebar_scroll, fg_color="#1E293B", height=1).pack(fill="x", padx=20, pady=(8, 4))
            self.criar_botao_menu("📤  Publicar Versão", self.mostrar_publicar_versao, "publicar_versao")
            self.criar_botao_menu("⚙️  Admin Atualizações", self.mostrar_admin_atualizacoes, "admin_atualizacoes")

        # Minha Conta (visivel para todos)
        self.criar_botao_menu("🔑  Minha Conta", self.mostrar_alterar_senha, "minha_conta")

        # Agenda atualização do badge de contas vencidas 2s após a janela aparecer
        self.after(2000, self._atualizar_badge_contas)

        self.botao_sync = ctk.CTkButton(
            self.sidebar,
            text="☁️  Sincronizar Nuvem",
            height=46,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=(self.cores["font_family"], 14, "bold"),
            command=lambda: self.sincronizar_nuvem(mostrar_mensagem=True)
        )
        self.botao_sync.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkButton(
            self.sidebar,
            text="🧹  Zerar / Preparar Distribuição",
            height=42,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=(self.cores["font_family"], 13, "bold"),
            command=self.preparar_distribuicao
        ).pack(fill="x", padx=15, pady=(6, 8))

        self.card_sync = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.cores["sidebar_card"],
            corner_radius=12
        )
        self.card_sync.pack(fill="x", padx=15, pady=(8, 10))

        ctk.CTkLabel(
            self.card_sync,
            text="☁️ STATUS DA NUVEM",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.label_sync_status = ctk.CTkLabel(
            self.card_sync,
            text="🟡 Verificando",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#FACC15"
        )
        self.label_sync_status.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_ultima = ctk.CTkLabel(
            self.card_sync,
            text="🕒 Última sync: ainda não sincronizado",
            font=(self.cores["font_family"], 10),
            text_color="#CBD5E1",
            wraplength=230,
            justify="left"
        )
        self.label_status_ultima.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_pendencias = ctk.CTkLabel(
            self.card_sync,
            text="📦 Pendências: 0",
            font=(self.cores["font_family"], 10, "bold"),
            text_color="#CBD5E1"
        )
        self.label_status_pendencias.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_resumo = ctk.CTkLabel(
            self.card_sync,
            text=f"🔄 Automático: a cada {settings.intervalo_sync_segundos}s",
            font=(self.cores["font_family"], 10),
            text_color="#94A3B8",
            wraplength=230,
            justify="left"
        )
        self.label_status_resumo.pack(anchor="w", padx=14, pady=(2, 12))

        ctk.CTkButton(
            self.sidebar,
            text="↩  Sair da Conta",
            height=42,
            fg_color="#374151",
            hover_color="#1F2937",
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=(self.cores["font_family"], 13, "bold"),
            command=self.fazer_logout
        ).pack(fill="x", padx=15, pady=(0, 4), side="bottom")
        
        ctk.CTkButton(
            self.sidebar,
            text="✕  Fechar Sistema",
            height=42,
            fg_color=self.cores["sidebar_card"],
            hover_color=self.cores["hover"],
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=(self.cores["font_family"], 13, "bold"),
            command=self.fechar_sistema
        ).pack(fill="x", padx=15, pady=(0, 14), side="bottom")

    def atualizar_status_sync(self, status, cor="#CBD5E1"):
        try:
            self.label_sync_status.configure(text=status, text_color=cor)
        except Exception as erro:
            logger.debug(f"Label sync não disponível: {erro}")

        try:
            pendencias = contar_pendencias_sync()
            self.label_status_pendencias.configure(
                text=f"📦 Pendências: {pendencias}"
            )
        except Exception as erro:
            logger.debug(f"Label pendências não disponível: {erro}")

    def atualizar_ultima_sync(self, resultado=None):
        resultado = resultado or {}
        pendencias = resultado.get("pendencias", contar_pendencias_sync())
        ultima_sync = resultado.get("ultima_sync")
        offline = resultado.get("offline", False)
        mensagem = resultado.get("mensagem", "")

        if offline:
            status_texto = "⚪ Modo local"
            ultima_texto = "🕒 Última sync: nuvem desabilitada"
            resumo = mensagem or "☁️ Nuvem não configurada"
        else:
            agora_txt = ultima_sync or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            status_texto = "🟢 Online"
            ultima_texto = f"🕒 Última sync: {agora_txt}"
            resumo = "✅ Tudo enviado" if pendencias == 0 else "🔄 Aguardando próximo envio"

        self.ultima_sync_texto = (
            f"{status_texto}\n"
            f"{ultima_texto}\n"
            f"📦 Pendências: {pendencias}"
        )

        try:
            self.label_status_ultima.configure(text=ultima_texto)
            self.label_status_pendencias.configure(text=f"📦 Pendências: {pendencias}")
            self.label_status_resumo.configure(text=resumo)
        except Exception as erro:
            logger.debug(f"Labels de sync não disponíveis: {erro}")

    def preparar_distribuicao(self):
        if sync_service.sincronizando:
            messagebox.showwarning(
                "Sincronização em andamento",
                "Aguarde a sincronização terminar antes de preparar a distribuição."
            )
            return

        confirmar = simpledialog.askstring(
            "Preparar Distribuição",
            "ATENÇÃO!\n\n"
            "Isso vai apagar TODOS os dados locais e da nuvem.\n\n"
            "Digite ZERAR para confirmar:"
        )

        if confirmar != "ZERAR":
            return

        criar_backup = messagebox.askyesnocancel(
            "Backup",
            "Deseja criar um backup antes de limpar?\n\n"
            "Sim = cria backup\n"
            "Não = limpa sem backup\n"
            "Cancelar = cancela tudo"
        )

        if criar_backup is None:
            return

        try:
            self.atualizar_status_sync("🧹 Preparando distribuição...", "#FACC15")

            backup = preparar_base_para_distribuicao(criar_backup=criar_backup)

            self.atualizar_status_sync("🟢 Base zerada", "#22C55E")

            if backup:
                mensagem = f"Base zerada com sucesso!\n\nBackup criado em:\n{backup}"
            else:
                mensagem = "Base zerada com sucesso!\n\nNenhum backup foi criado."

            messagebox.showinfo(
                "Preparação concluída",
                mensagem
            )

        except Exception as erro:
            self.atualizar_status_sync("🔴 Erro ao preparar", "#EF4444")

            mostrar_erro_profissional(
                self,
                "Erro ao preparar distribuição",
                "Não foi possível concluir a preparação da distribuição.",
                str(erro),
            )

    def sincronizar_nuvem(self, mostrar_mensagem=False, reparar_fila=True):
        if sync_service.sincronizando:
            self.atualizar_status_sync("🟡 Sincronização em andamento...", "#FACC15")
            return

        inicio = datetime.now()
        self.atualizar_status_sync("🟡 Sincronizando...", "#FACC15")
        try:
            self.label_status_resumo.configure(text="🔄 Enviando e baixando alterações...")
        except Exception as erro:
            logger.debug(f"Label resumo não disponível: {erro}")
        self.botao_sync.configure(text="☁️  Sincronizando...")

        def tarefa():
            try:
                resultado = sync_service.executar(reparar_fila=reparar_fila)

                cor = "#22C55E"
                status = "🟢 Nuvem sincronizada"

                if resultado.get("offline"):
                    cor = "#94A3B8"
                    status = "⚪ Modo local"
                elif resultado.get("status") == "partial":
                    cor = "#FACC15"
                    status = "🟡 Sync parcial"
                elif resultado.get("status") == "error":
                    cor = "#EF4444"
                    status = "🔴 Erro na nuvem"

                self.after(
                    0,
                    lambda: self.atualizar_status_sync(
                        status,
                        cor
                    )
                )

                duracao = (datetime.now() - inicio).total_seconds()

                self.after(0, lambda r=resultado: self.atualizar_ultima_sync(r))
                self.after(
                    0,
                    lambda d=duracao, r=resultado: self.label_status_resumo.configure(
                        text=f"{r.get('mensagem', 'Concluído')} em {d:.1f}s"
                    )
                )

                if mostrar_mensagem:
                    self.after(
                        0,
                        lambda r=resultado: messagebox.showinfo(
                            "Sincronização",
                            r.get("mensagem", "Sincronização concluída!")
                        )
                    )

            except Exception as erro:
                self.after(
                    0,
                    lambda: self.atualizar_status_sync(
                        "🔴 Erro na nuvem",
                        "#EF4444"
                    )
                )

                if mostrar_mensagem:
                    self.after(
                        0,
                        lambda e=erro: mostrar_erro_profissional(
                            self,
                            "Erro ao sincronizar",
                            "A sincronização não pôde ser concluída.",
                            str(e),
                        )
                    )

            finally:
                self.after(
                    0,
                    lambda: self.botao_sync.configure(
                        text="☁️  Sincronizar Nuvem" if settings.supabase_enabled else "☁️  Modo Local"
                    )
                )

        threading.Thread(target=tarefa, daemon=True).start()

    def iniciar_sync_automatico(self):
        self.after(settings.intervalo_sync_ms, self.executar_sync_automatico)


    def executar_sync_automatico(self):
        if not sync_service.sincronizando:
            self.sincronizar_nuvem(mostrar_mensagem=False, reparar_fila=False)

        self.after(settings.intervalo_sync_ms, self.executar_sync_automatico)

    def verificar_atualizacao_inicio(self):
        """Verifica atualizações em background ao iniciar o aplicativo."""
        def tarefa():
            try:
                # Usar GitHub se configurado, caso contrário usa update_service original
                if settings.github_use_cdn and settings.github_repo_owner and settings.github_repo_name:
                    resultado = github_update_service.check_for_updates()
                else:
                    resultado = update_service.check_for_updates()
                
                if resultado.get("has_update") and resultado.get("download_url"):
                    self.after(0, lambda: self.mostrar_dialogo_atualizacao(resultado))
            except Exception as e:
                logger.error(f"Erro ao verificar atualização ao iniciar: {e}")
        
        # Executar após 3 segundos para não atrasar a inicialização
        threading.Thread(target=tarefa, daemon=True).start()

    def mostrar_dialogo_atualizacao(self, resultado):
        """Abre o dialog profissional de atualizacao."""
        TelaAtualizacao(self, resultado)

    def configurar_atalhos(self):
        """Configura atalhos de teclado globais."""
        self.bind("<Control-d>", lambda e: self.navegar_para("dashboard"))
        self.bind("<Control-o>", lambda e: self.navegar_para("operacoes"))
        self.bind("<Control-n>", lambda e: self.navegar_para("notas"))
        self.bind("<Control-v>", lambda e: self.navegar_para("criar_viagem"))
        self.bind("<Control-h>", lambda e: self.navegar_para("historico"))
        self.bind("<Control-r>", lambda e: self.navegar_para("relatorios"))
        self.bind("<Control-s>", lambda e: self.sincronizar_nuvem(mostrar_mensagem=True))
        self.bind("<Control-q>", lambda e: self.fechar_sistema())
        self.bind("<F5>", lambda e: self.sincronizar_nuvem(mostrar_mensagem=True))
        self.bind("<Escape>", lambda e: self.navegar_para("dashboard"))

    def criar_area_principal(self):
        self.area_direita = ctk.CTkFrame(self, fg_color=self.cores["fundo"])
        self.area_direita.pack(side="right", fill="both", expand=True)

        self.header = ctk.CTkFrame(
            self.area_direita,
            height=82,
            fg_color=self.cores["header"],
            corner_radius=0
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        ctk.CTkLabel(
            self.header,
            text=f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=(self.cores["font_family"], 12, "bold"),
            text_color=self.cores["texto_suave"]
        ).place(relx=0.97, y=30, anchor="e")

        self.label_header_titulo = ctk.CTkLabel(
            self.header,
            text="PAINEL PRINCIPAL",
            font=(self.cores["font_family"], 25, "bold"),
            text_color=self.cores["texto"]
        )
        self.label_header_titulo.place(x=30, y=16)

        self.label_header_subtitulo = ctk.CTkLabel(
            self.header,
            text="Controle operacional, financeiro e logístico da frota",
            font=(self.cores["font_family"], 12),
            text_color=self.cores["texto_suave"]
        )
        self.label_header_subtitulo.place(x=32, y=50)

        self.container = ctk.CTkFrame(
            self.area_direita,
            fg_color=self.cores["fundo"]
        )
        self.container.pack(fill="both", expand=True, padx=22, pady=18)

    def criar_botao_menu(self, texto, comando, chave_tela):
        botao = ctk.CTkButton(
            self.sidebar_scroll,
            text=texto,
            height=48,
            fg_color="transparent",
            hover_color=self.cores["hover"],
            text_color="white",
            corner_radius=12,
            anchor="w",
            font=(self.cores["font_family"], 13, "bold"),
        )

        botao.configure(command=lambda b=botao, c=comando: self.executar_menu(b, c))
        botao.pack(fill="x", padx=12, pady=6)
        self.botoes_menu.append(botao)
        self.mapa_botoes[chave_tela] = botao

    def navegar_para(self, chave_tela):
        botao = self.mapa_botoes.get(chave_tela)
        comando = getattr(self, f"mostrar_{chave_tela}", None)
        if botao and comando:
            self.executar_menu(botao, comando)

    def atualizar_header(self, chave_tela):
        titulo, subtitulo = self.titulos_telas.get(
            chave_tela,
            ("CW TRANSPORTADORA", "Sistema de gestão logística"),
        )
        self.tela_atual = chave_tela
        try:
            self.label_header_titulo.configure(text=titulo)
            self.label_header_subtitulo.configure(text=subtitulo)
        except Exception as erro:
            logger.debug(f"Label header não disponível: {erro}")

    def executar_menu(self, botao, comando):
        for b in self.botoes_menu:
            b.configure(fg_color="transparent")

        botao.configure(fg_color=self.cores["principal"])
        comando()

    def ativar_primeiro_botao(self):
        if self.botoes_menu:
            self.botoes_menu[0].configure(fg_color=self.cores["principal"])

    def limpar_tela(self):
        for child in self.container.winfo_children():
            child.destroy()

    def _verificar_permissao(self, modulo: str) -> bool:
        """Verifica permissao e mostra aviso se negado. Retorna True se OK."""
        if not auth_service.tem_permissao(modulo, "visualizar"):
            messagebox.showwarning(
                "Acesso Negado",
                "Voce nao tem permissao para acessar este modulo.",
            )
            return False
        return True

    def mostrar_dashboard(self):
        if not self._verificar_permissao("dashboard"):
            return
        self.limpar_tela()
        self.atualizar_header("dashboard")
        self.ativar_primeiro_botao()
        self.dashboard = Dashboard(self.container)
        self.dashboard.pack(fill="both", expand=True)

    def mostrar_notas(self):
        if not self._verificar_permissao("notas"):
            return
        self.limpar_tela()
        self.atualizar_header("notas")
        self.tela_notas = TelaNotas(self.container)
        self.tela_notas.pack(fill="both", expand=True)

    def mostrar_criar_viagem(self):
        if not self._verificar_permissao("criar_viagem"):
            return
        self.limpar_tela()
        self.atualizar_header("criar_viagem")
        self.tela_criar_viagem = TelaCriarViagem(self.container)
        self.tela_criar_viagem.pack(fill="both", expand=True)

    def mostrar_operacoes(self):
        if not self._verificar_permissao("operacoes"):
            return
        self.limpar_tela()
        self.atualizar_header("operacoes")
        self.tela_operacoes = TelaOperacoes(self.container)
        self.tela_operacoes.pack(fill="both", expand=True)

    def mostrar_historico(self):
        if not self._verificar_permissao("historico"):
            return
        self.limpar_tela()
        self.atualizar_header("historico")
        self.tela_historico = TelaHistorico(self.container)
        self.tela_historico.pack(fill="both", expand=True)

    def mostrar_ranking_clientes(self):
        if not self._verificar_permissao("ranking_clientes"):
            return
        self.limpar_tela()
        self.atualizar_header("ranking_clientes")
        self.tela_ranking_clientes = TelaRankingClientes(self.container)
        self.tela_ranking_clientes.pack(fill="both", expand=True)

    def mostrar_combustivel(self):
        if not self._verificar_permissao("combustivel"):
            return
        self.limpar_tela()
        self.atualizar_header("combustivel")
        self.tela_combustivel = TelaCombustivel(self.container)
        self.tela_combustivel.pack(fill="both", expand=True)

    def mostrar_contas(self):
        if not self._verificar_permissao("contas"):
            return
        self.limpar_tela()
        self.atualizar_header("contas")
        self.tela_contas = TelaContas(self.container)
        self.tela_contas.pack(fill="both", expand=True)
        # Quando o usuário abre Contas, atualiza o badge após sair
        self.after(500, self._atualizar_badge_contas)

    def mostrar_manutencao(self):
        if not self._verificar_permissao("manutencao"):
            return
        self.limpar_tela()
        self.atualizar_header("manutencao")
        self.tela_manutencao = TelaManutencao(self.container)
        self.tela_manutencao.pack(fill="both", expand=True)

    def mostrar_relatorios(self):
        if not self._verificar_permissao("relatorios"):
            return
        self.limpar_tela()
        self.atualizar_header("relatorios")
        self.tela_relatorios = TelaRelatorios(self.container)
        self.tela_relatorios.pack(fill="both", expand=True)


    def fechar_sistema(self):
        def _finalizar():
            try:
                if settings.supabase_enabled and not sync_service.sincronizando:
                    sync_service.executar(reparar_fila=True)
            except Exception as erro:
                logger.error(f"Erro ao sincronizar ao fechar: {erro}")

            try:
                self.backup_automatico()
            except Exception as erro:
                logger.error(f"Erro ao criar backup no fechamento: {erro}")

            self.after(0, self.destroy)

        # Executa em thread para não travar a UI, com timeout de 10s
        t = threading.Thread(target=_finalizar, daemon=True)
        t.start()
        # Se a thread não terminar em 10s, força o fechamento
        self.after(10000, self.destroy)

    def mostrar_funcionarios(self):
        if not self._verificar_permissao("funcionarios"):
            return
        self.limpar_tela()
        self.atualizar_header("funcionarios")
        self.tela_funcionarios = TelaFuncionarios(self.container)
        self.tela_funcionarios.pack(fill="both", expand=True)

    def mostrar_configuracoes(self):
        if not self._verificar_permissao("configuracoes"):
            return
        self.limpar_tela()
        self.atualizar_header("configuracoes")
        self.tela_configuracoes = TelaConfiguracoes(self.container)
        self.tela_configuracoes.pack(fill="both", expand=True)

    def mostrar_historico_versoes(self):
        """Tela de historico de versoes (acessivel via configuracoes ou sidebar)."""
        self.limpar_tela()
        self.atualizar_header("historico_versoes")
        self.tela_hist_versoes = TelaHistoricoVersoes(self.container)
        self.tela_hist_versoes.pack(fill="both", expand=True)

    def mostrar_publicar_versao(self):
        """Abre o dialogo para publicar nova versao (apenas mestre)."""
        abrir_publicar_versao(self, on_concluida=self._on_publicacao_concluida)

    def _on_publicacao_concluida(self):
        """Callback quando a publicacao e concluida."""
        # Atualizar a tela de historico de versoes se estiver visivel
        if self.tela_atual == "historico_versoes":
            self.mostrar_historico_versoes()

    def mostrar_admin_atualizacoes(self):
        """Tela de administracao de atualizacoes (apenas mestre)."""
        self.limpar_tela()
        self.atualizar_header("admin_atualizacoes")
        abrir_admin_atualizacoes(self.container, self.mostrar_dashboard)

    # ------------------------------------------------------------------
    # Badge de contas vencidas no menu lateral
    # ------------------------------------------------------------------

    def _atualizar_badge_contas(self) -> None:
        """
        Consulta contas vencidas em background e atualiza o texto
        do botão 'Contas' no sidebar com um badge visual.
        Reagenda a si mesmo a cada 5 minutos para manter o dado fresco.
        """
        def _consultar():
            try:
                vencidas = financeiro_service.contar_contas_vencidas()
            except Exception as erro:
                logger.warning(f"Erro ao consultar contas vencidas: {erro}")
                vencidas = 0
            self.after(0, lambda: self._aplicar_badge_contas(vencidas))

        threading.Thread(target=_consultar, daemon=True).start()
        # Reagenda para daqui a 5 minutos
        self.after(300_000, self._atualizar_badge_contas)

    def _aplicar_badge_contas(self, vencidas: int) -> None:
        """Aplica o badge vermelho no botão Contas ou remove se não houver."""
        botao = self.mapa_botoes.get("contas")
        if not botao:
            return
        try:
            if vencidas > 0:
                botao.configure(text=f"💳  Contas  🔴 {vencidas}")
            else:
                botao.configure(text="💳  Contas")
        except Exception as erro:
            logger.debug(f"Widget de contas não disponível: {erro}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
