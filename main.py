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
from utils.database import criar_banco, criar_caminhoes_padrao
from utils.sync import contar_pendencias_sync
from utils.logger import get_logger

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
from telas.notas import TelaNotas
from telas.criar_viagem import TelaCriarViagem

logger = get_logger(__name__)


from telas.theme import setup_theme
from utils.splash_screen import SplashScreen


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

        self.splash.update_status("Carregando interface...")
        self.backup_automatico()
        self.protocol("WM_DELETE_WINDOW", self.fechar_sistema)

        self.botoes_menu = []
        self.tela_atual = "dashboard"
        self.mapa_botoes = {}
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
        }

        self.splash.update_status("Montando interface...")
        self.criar_sidebar()
        self.criar_area_principal()
        self.mostrar_dashboard()
        self.atualizar_ultima_sync(sync_service.ultimo_resultado)

        self.splash.update_status("Sincronizando dados...")
        self.sincronizar_nuvem(mostrar_mensagem=False)
        self.iniciar_sync_automatico()

        # Verificar atualizações ao iniciar (em background)
        self.verificar_atualizacao_inicio()

        # Configurar atalhos de teclado
        self.configurar_atalhos()
        
        self.splash.update_status("Pronto!")
        self.after(500, self.splash.close)

    def backup_automatico(self):
        try:
            pasta_backup = settings.backup_auto_dir
            origem_db = settings.db_path

            if not origem_db.exists():
                return

            nome_backup = f"backup_auto_{datetime.now().strftime('%d%m%Y_%H%M%S')}.db"
            destino_db = pasta_backup / nome_backup

            shutil.copy2(origem_db, destino_db)

            if not pasta_backup.exists():
                pasta_backup.mkdir(parents=True, exist_ok=True)

            backups = [
                pasta_backup / arquivo
                for arquivo in pasta_backup.iterdir()
                if arquivo.name.endswith(".db")
            ]

            backups.sort(
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
                font=("Arial", 48, "bold"),
                text_color="#DC2626"
            ).pack(pady=(0, 5))

        ctk.CTkLabel(
            logo_frame,
            text="CW TRANSPORTADORA",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(0, 10))

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

        self.botao_sync = ctk.CTkButton(
            self.sidebar,
            text="☁️  Sincronizar Nuvem",
            height=46,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=("Arial", 14, "bold"),
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
            font=("Arial", 13, "bold"),
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
            font=("Arial", 12, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.label_sync_status = ctk.CTkLabel(
            self.card_sync,
            text="🟡 Verificando",
            font=("Arial", 12, "bold"),
            text_color="#FACC15"
        )
        self.label_sync_status.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_ultima = ctk.CTkLabel(
            self.card_sync,
            text="🕒 Última sync: ainda não sincronizado",
            font=("Arial", 10),
            text_color="#CBD5E1",
            wraplength=230,
            justify="left"
        )
        self.label_status_ultima.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_pendencias = ctk.CTkLabel(
            self.card_sync,
            text="📦 Pendências: 0",
            font=("Arial", 10, "bold"),
            text_color="#CBD5E1"
        )
        self.label_status_pendencias.pack(anchor="w", padx=14, pady=(2, 2))

        self.label_status_resumo = ctk.CTkLabel(
            self.card_sync,
            text=f"🔄 Automático: a cada {settings.intervalo_sync_segundos}s",
            font=("Arial", 10),
            text_color="#94A3B8",
            wraplength=230,
            justify="left"
        )
        self.label_status_resumo.pack(anchor="w", padx=14, pady=(2, 12))


        footer = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.cores["sidebar_card"],
            corner_radius=10
        )
        footer.pack(fill="x", padx=15, pady=(10, 12), side="bottom")

        ctk.CTkLabel(
            footer,
            text="⏱ Atualizado em",
            font=("Arial", 11),
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            footer,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        self.label_ultima_sync = ctk.CTkLabel(
            footer,
            text=self.ultima_sync_texto,
            font=("Arial", 11),
            text_color="#CBD5E1",
            wraplength=230,
            justify="left"
        )
        self.label_ultima_sync.pack(anchor="w", padx=15, pady=(0, 12))

        ctk.CTkButton(
            self.sidebar,
            text="↪  Sair",
            height=46,
            fg_color=self.cores["sidebar_card"],
            hover_color=self.cores["hover"],
            text_color="white",
            corner_radius=10,
            anchor="w",
            font=("Arial", 14, "bold"),
            command=self.fechar_sistema
        ).pack(fill="x", padx=15, pady=(0, 18), side="bottom")

    def atualizar_status_sync(self, status, cor="#CBD5E1"):
        try:
            self.label_sync_status.configure(text=status, text_color=cor)
        except Exception:
            pass

        try:
            pendencias = contar_pendencias_sync()
            self.label_status_pendencias.configure(
                text=f"📦 Pendências: {pendencias}"
            )
        except Exception:
            pass

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
            self.label_ultima_sync.configure(text=self.ultima_sync_texto)
        except Exception:
            pass

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

    def sincronizar_nuvem(self, mostrar_mensagem=False):
        if sync_service.sincronizando:
            self.atualizar_status_sync("🟡 Sincronização em andamento...", "#FACC15")
            return

        inicio = datetime.now()
        self.atualizar_status_sync("🟡 Sincronizando...", "#FACC15")
        try:
            self.label_status_resumo.configure(text="🔄 Enviando e baixando alterações...")
        except Exception:
            pass
        self.botao_sync.configure(text="☁️  Sincronizando...")

        def tarefa():
            try:
                resultado = sync_service.executar()

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
            self.sincronizar_nuvem(mostrar_mensagem=False)

        self.after(settings.intervalo_sync_ms, self.executar_sync_automatico)

    def verificar_atualizacao_inicio(self):
        """Verifica atualizações em background ao iniciar o aplicativo."""
        def tarefa():
            try:
                resultado = update_service.check_for_updates()
                
                if resultado.get("has_update") and resultado.get("download_url"):
                    self.after(0, lambda: self.mostrar_dialogo_atualizacao(resultado))
            except Exception as e:
                logger.error(f"Erro ao verificar atualização ao iniciar: {e}")
        
        # Executar após 3 segundos para não atrasar a inicialização
        threading.Thread(target=tarefa, daemon=True).start()

    def mostrar_dialogo_atualizacao(self, resultado):
        """Mostra diálogo informando sobre nova atualização disponível."""
        from tkinter import simpledialog
        
        mensagem = (
            f"Nova versão disponível: {resultado['latest_version']}\n"
            f"Versão atual: {resultado['current_version']}\n\n"
            f"Deseja baixar e instalar a atualização agora?"
        )
        
        if messagebox.askyesno(
            "Atualização Disponível",
            mensagem
        ):
            self.baixar_e_instalar_atualizacao(resultado)

    def baixar_e_instalar_atualizacao(self, resultado):
        """Baixa e instala a atualização com barra de progresso."""
        download_url = resultado.get("download_url")
        
        if not download_url:
            messagebox.showerror(
                "Erro",
                "URL de download não disponível."
            )
            return
        
        # Criar janela de progresso
        progresso_janela = ctk.CTkToplevel(self)
        progresso_janela.title("Baixando Atualização")
        progresso_janela.geometry("400x150")
        progresso_janela.resizable(False, False)
        progresso_janela.grab_set()
        
        ctk.CTkLabel(
            progresso_janela,
            text="Baixando atualização...",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(progresso_janela, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        label_status = ctk.CTkLabel(
            progresso_janela,
            text="Iniciando...",
            font=("Arial", 11)
        )
        label_status.pack(pady=5)
        
        def progresso_callback(downloaded, total):
            if total > 0:
                porcentagem = (downloaded / total) * 100
                self.after(0, lambda: progress_bar.set(porcentagem / 100))
                self.after(0, lambda: label_status.configure(
                    text=f"{downloaded / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB"
                ))
        
        def tarefa_download():
            success, result = update_service.download_update(
                download_url,
                progresso_callback
            )
            
            self.after(0, lambda: progresso_janela.destroy())
            
            if success:
                # Perguntar se deseja instalar
                if messagebox.askyesno(
                    "Download Concluído",
                    "A atualização foi baixada. Deseja instalar agora?\n\n"
                    "O aplicativo será fechado durante a instalação."
                ):
                    success_install, msg = update_service.install_update(result)
                    
                    if success_install:
                        messagebox.showinfo("Instalação", msg)
                        self.fechar_sistema()
                    else:
                        messagebox.showerror("Erro", msg)
            else:
                mostrar_erro_profissional(
                    self,
                    "Erro na atualização",
                    "Não foi possível concluir o download da atualização.",
                    result,
                )
        
        threading.Thread(target=tarefa_download, daemon=True).start()

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
            font=("Arial", 12, "bold"),
            text_color=self.cores["texto_suave"]
        ).place(relx=0.97, y=30, anchor="e")

        self.label_header_titulo = ctk.CTkLabel(
            self.header,
            text="PAINEL PRINCIPAL",
            font=("Arial", 25, "bold"),
            text_color=self.cores["texto"]
        )
        self.label_header_titulo.place(x=30, y=16)

        self.label_header_subtitulo = ctk.CTkLabel(
            self.header,
            text="Controle operacional, financeiro e logístico da frota",
            font=("Arial", 12),
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
            self.sidebar,
            text=texto,
            height=48,
            fg_color="transparent",
            hover_color=self.cores["hover"],
            text_color="white",
            corner_radius=12,
            anchor="w",
            font=("Arial", 13, "bold"),
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
        except Exception:
            pass

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

    def mostrar_dashboard(self):
        self.limpar_tela()
        self.atualizar_header("dashboard")
        self.ativar_primeiro_botao()
        self.dashboard = Dashboard(self.container)
        self.dashboard.pack(fill="both", expand=True)

    def mostrar_notas(self):
        self.limpar_tela()
        self.atualizar_header("notas")
        self.tela_notas = TelaNotas(self.container)
        self.tela_notas.pack(fill="both", expand=True)

    def mostrar_criar_viagem(self):
        self.limpar_tela()
        self.atualizar_header("criar_viagem")
        self.tela_criar_viagem = TelaCriarViagem(self.container)
        self.tela_criar_viagem.pack(fill="both", expand=True)

    def mostrar_operacoes(self):
        self.limpar_tela()
        self.atualizar_header("operacoes")
        self.tela_operacoes = TelaOperacoes(self.container)
        self.tela_operacoes.pack(fill="both", expand=True)

    def mostrar_historico(self):
        self.limpar_tela()
        self.atualizar_header("historico")
        self.tela_historico = TelaHistorico(self.container)
        self.tela_historico.pack(fill="both", expand=True)

    def mostrar_ranking_clientes(self):
        self.limpar_tela()
        self.atualizar_header("ranking_clientes")
        self.tela_ranking_clientes = TelaRankingClientes(self.container)
        self.tela_ranking_clientes.pack(fill="both", expand=True)

    def mostrar_combustivel(self):
        self.limpar_tela()
        self.atualizar_header("combustivel")
        self.tela_combustivel = TelaCombustivel(self.container)
        self.tela_combustivel.pack(fill="both", expand=True)

    def mostrar_contas(self):
        self.limpar_tela()
        self.atualizar_header("contas")
        self.tela_contas = TelaContas(self.container)
        self.tela_contas.pack(fill="both", expand=True)

    def mostrar_manutencao(self):
        self.limpar_tela()
        self.atualizar_header("manutencao")
        self.tela_manutencao = TelaManutencao(self.container)
        self.tela_manutencao.pack(fill="both", expand=True)

    def mostrar_relatorios(self):
        self.limpar_tela()
        self.atualizar_header("relatorios")
        self.tela_relatorios = TelaRelatorios(self.container)
        self.tela_relatorios.pack(fill="both", expand=True)


    def fechar_sistema(self):
        try:
            self.backup_automatico()
        except Exception as erro:
            logger.error(f"Erro ao fechar sistema: {erro}")

        self.destroy()

    def mostrar_funcionarios(self):
        self.limpar_tela()
        self.atualizar_header("funcionarios")
        self.tela_funcionarios = TelaFuncionarios(self.container)
        self.tela_funcionarios.pack(fill="both", expand=True)

    def mostrar_configuracoes(self):
        self.limpar_tela()
        self.atualizar_header("configuracoes")
        self.tela_configuracoes = TelaConfiguracoes(self.container)
        self.tela_configuracoes.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
