import os
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox
from config.settings import settings
from services.config_service import config_service
from services.viagem_service import viagem_service
from services.update_service import update_service, CANAL_ESTAVEL, CANAL_BETA, CANAL_DEV
from telas.theme import setup_theme, criar_header
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaConfiguracoes(ctk.CTkFrame):
    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self.base_dir = str(settings.project_dir)
        self.config_path = str(settings.config_path)
        self.db_path = str(settings.db_path)

        self.campos = {}
        self.dados = config_service.carregar_configuracoes()

        self.criar_layout()

    def configuracao_padrao(self) -> dict:
        """Delega ao settings para evitar duplicação da lista de defaults."""
        return settings._config_padrao()

    def criar_layout(self):
        ff = self.cores["font_family"]
        criar_header(
            self,
            tag="CONFIGURAÇÕES DO SISTEMA",
            titulo="Central de Configurações",
            subtitulo="Dados da empresa, backup, banco de dados e preferências do sistema.",
            cores=self.cores,
        )

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=25, pady=5)
        self.container.grid_columnconfigure((0, 1), weight=1)

        self.criar_card_empresa()
        self.criar_card_sistema()
        self.criar_card_backup()
        self.criar_card_banco()
        self.criar_card_atualizacoes()
        self.criar_card_limpeza()

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(fill="x", padx=25, pady=(5, 18))

        ctk.CTkButton(
            botoes,
            text="Salvar Configurações",
            height=46,
            width=230,
            fg_color="#16A34A",
            hover_color="#15803D",
            font=(self.cores["font_family"], 14, "bold"),
            command=self.salvar
        ).pack(side="left")

        ctk.CTkButton(
            botoes,
            text="Restaurar Padrão",
            height=46,
            width=190,
            fg_color="#111827",
            hover_color="#374151",
            font=(self.cores["font_family"], 14, "bold"),
            command=self.restaurar_padrao
        ).pack(side="left", padx=12)

    def criar_card(self, titulo, subtitulo, row, col):
        card = ctk.CTkFrame(
            self.container,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=titulo,
            font=(self.cores["font_family"], 20, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=22, pady=(20, 3))

        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=(self.cores["font_family"], 12),
            text_color="#64748b",
            wraplength=430,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 14))

        return card

    def criar_card_empresa(self):
        card = self.criar_card(
            "🏢 Dados da Empresa",
            "Essas informações aparecem em relatórios, PDFs e identificação do sistema.",
            0,
            0
        )

        self.criar_entry(card, "empresa", "Nome da empresa")
        self.criar_entry(card, "cnpj", "CNPJ")
        self.criar_entry(card, "telefone", "Telefone")
        self.criar_entry(card, "email", "E-mail")
        self.criar_entry(card, "cidade", "Cidade")
        self.criar_entry(card, "uf", "UF")

    def criar_card_sistema(self):
        card = self.criar_card(
            "⚙️ Preferências do Sistema",
            "Configure metas, pasta dos relatórios e aparência do sistema.",
            0,
            1
        )

        self.criar_entry(card, "meta_lucro", "Meta mensal de lucro")
        self.criar_entry(card, "imposto_percentual", "Imposto padrão (%)")
        self.criar_entry(card, "pasta_relatorios", "Pasta dos relatórios")
        self.criar_entry(card, "alerta_revisao", "Alerta de revisão com KM")
        self.criar_entry(card, "revisao_obrigatoria", "Revisão obrigatória com KM")

        ctk.CTkLabel(
            card,
            text="Tema visual",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=22, pady=(7, 2))

        tema = ctk.CTkComboBox(
            card,
            values=["Vermelho CW", "Claro", "Premium Escuro"],
            height=39
        )
        tema.pack(fill="x", padx=22, pady=(0, 10))
        tema.set(self.dados.get("tema", "Vermelho CW"))
        self.campos["tema"] = tema

        ctk.CTkLabel(
            card,
            text="Cor principal",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=22, pady=(7, 2))

        cor_tema = ctk.CTkComboBox(
            card,
            values=["Vermelho", "Azul", "Verde", "Roxo", "Preto"],
            height=39
        )
        cor_tema.pack(fill="x", padx=22, pady=(0, 10))
        cor_tema.set(self.dados.get("cor_tema", "Vermelho"))
        self.campos["cor_tema"] = cor_tema

    def criar_card_backup(self):
        card = self.criar_card(
            "🗂 Backup e Arquivos",
            "Faça backup do banco, configurações e relatórios gerados.",
            1,
            0
        )

        self.botao(card, "Abrir Pasta do Sistema", "#111827", "#374151", self.abrir_pasta_sistema)
        self.botao(card, "Abrir Pasta dos Relatórios", "#2563EB", "#1D4ED8", self.abrir_pasta_relatorios)
        self.botao(card, "Fazer Backup Completo", "#16A34A", "#15803D", self.fazer_backup)

        ctk.CTkLabel(
            card,
            text="O backup copia o banco SQLite, configurações e pasta de relatórios.",
            font=(self.cores["font_family"], 11),
            text_color="#64748b",
            wraplength=430,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(10, 20))

    def criar_card_banco(self):
        card = self.criar_card(
            "🧠 Banco de Dados",
            "Informações técnicas do banco usado pelo sistema.",
            1,
            1
        )

        info = self.info_banco()

        itens = [
            ("Arquivo do banco", "cw_transportadora.db"),
            ("Tamanho", info["tamanho"]),
            ("Tabelas", str(info["tabelas"])),
            ("Registros principais", str(info["registros"])),
            ("Último backup", info["ultimo_backup"])
        ]

        for titulo, valor in itens:
            linha = ctk.CTkFrame(card, fg_color="#f8fafc", corner_radius=12)
            linha.pack(fill="x", padx=22, pady=5)

            ctk.CTkLabel(
                linha,
                text=titulo,
                font=(self.cores["font_family"], 12, "bold"),
                text_color="#64748b"
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                linha,
                text=valor,
                font=(self.cores["font_family"], 12, "bold"),
                text_color="#111827"
            ).pack(side="right", padx=12, pady=10)

        self.botao(card, "Atualizar Informações", "#2563EB", "#1D4ED8", self.recarregar_tela)

    def criar_card_atualizacoes(self):
        """Card de configuracoes de atualizacao."""
        card = self.criar_card(
            "🔄 Atualizacoes",
            "Configure canal, verificacao automatica e verifique novas versoes.",
            2,
            1
        )

        # Versao atual
        info_versao = update_service.obter_versao_instalada()
        versao = info_versao.get("versao", "0.0.0")

        row_versao = ctk.CTkFrame(card, fg_color="#F0FDF4", corner_radius=12)
        row_versao.pack(fill="x", padx=22, pady=(4, 8))

        ctk.CTkLabel(
            row_versao, text=f"Versao instalada: {versao}",
            font=(self.cores["font_family"], 13, "bold"), text_color="#166534",
        ).pack(side="left", padx=14, pady=10)

        # Checkbox auto-check
        self._check_auto = ctk.CTkCheckBox(
            card, text="Verificar atualizacoes automaticamente",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#374151", fg_color="#16A34A",
            hover_color="#15803D",
        )
        self._check_auto.pack(anchor="w", padx=22, pady=(6, 4))
        if settings.enable_auto_update:
            self._check_auto.select()

        # Canal
        ctk.CTkLabel(
            card, text="Canal de atualizacao",
            font=(self.cores["font_family"], 12, "bold"), text_color="#374151",
        ).pack(anchor="w", padx=22, pady=(8, 2))

        self._combo_canal = ctk.CTkComboBox(
            card,
            values=["Estavel", "Beta", "Desenvolvimento"],
            height=39, font=(self.cores["font_family"], 12),
        )
        self._combo_canal.pack(fill="x", padx=22, pady=(0, 8))

        canal_map = {CANAL_ESTAVEL: "Estavel", CANAL_BETA: "Beta", CANAL_DEV: "Desenvolvimento"}
        self._combo_canal.set(canal_map.get(update_service.channel, "Estavel"))

        # Botao verificar agora
        self._btn_verificar = ctk.CTkButton(
            card, text="Verificar Agora", height=42,
            fg_color="#2563EB", hover_color="#1D4ED8",
            font=(self.cores["font_family"], 13, "bold"),
            command=self._verificar_atualizacao_manual,
        )
        self._btn_verificar.pack(fill="x", padx=22, pady=(4, 8))

        self._label_resultado = ctk.CTkLabel(
            card, text="",
            font=(self.cores["font_family"], 11), text_color="#6B7280",
        )
        self._label_resultado.pack(anchor="w", padx=22, pady=(0, 4))

        # Botao historico
        ctk.CTkButton(
            card, text="Ver Historico de Versoes", height=42,
            fg_color="#111827", hover_color="#374151",
            font=(self.cores["font_family"], 13, "bold"),
            command=self._abrir_historico,
        ).pack(fill="x", padx=22, pady=(4, 16))

    def _verificar_atualizacao_manual(self):
        """Verifica atualizacoes em background."""
        self._btn_verificar.configure(state="disabled", text="Verificando...")
        self._label_resultado.configure(text="Buscando novas versoes...", text_color="#F59E0B")

        canal_nome = self._combo_canal.get()
        canal_map_rev = {"Estavel": CANAL_ESTAVEL, "Beta": CANAL_BETA, "Desenvolvimento": CANAL_DEV}
        canal = canal_map_rev.get(canal_nome, CANAL_ESTAVEL)

        def _tarefa():
            try:
                resultado = update_service.check_for_updates(channel=canal)
                if self.winfo_exists():
                    self.after(0, lambda: self._resultado_verificacao(resultado))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda: self._resultado_verificacao({"error": str(e)}))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _resultado_verificacao(self, resultado):
        if not self.winfo_exists():
            return

        self._btn_verificar.configure(state="normal", text="Verificar Agora")

        if resultado.get("error"):
            self._label_resultado.configure(
                text=f"Erro: {resultado['error']}", text_color="#DC2626"
            )
            return

        if resultado.get("has_update"):
            self._label_resultado.configure(
                text=f"Nova versao: {resultado['latest_version']}!", text_color="#16A34A"
            )
            from telas.atualizacao import TelaAtualizacao
            TelaAtualizacao(self.winfo_toplevel(), resultado)
        else:
            self._label_resultado.configure(
                text="Sistema esta atualizado!", text_color="#16A34A"
            )

    def _abrir_historico(self):
        """Abre tela de historico de versoes."""
        # Navegar via main app
        app = self.winfo_toplevel()
        if hasattr(app, "mostrar_historico_versoes"):
            app.mostrar_historico_versoes()

    def criar_card_limpeza(self):
        """Card para limpeza de dados do sistema."""
        card = self.criar_card(
            "🗑️ Limpeza de Dados",
            "Remova dados salvos para recadastramento. Use com cuidado!",
            3,
            0
        )

        ctk.CTkLabel(
            card,
            text="Caminhões cadastrados",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=22, pady=(8, 4))

        ctk.CTkLabel(
            card,
            text="Remove todos os veículos para permitir novo cadastramento.",
            font=(self.cores["font_family"], 11),
            text_color="#64748b"
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self.botao(card, "🗑️ Apagar Todos os Caminhões", "#DC2626", "#B91C1C", self.apagar_caminhoes)

        # Separador
        ctk.CTkFrame(card, height=2, fg_color="#e5e7eb").pack(fill="x", padx=22, pady=(20, 16))

        ctk.CTkLabel(
            card,
            text="🔐 Reset Completo (Mestre)",
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#DC2626"
        ).pack(anchor="w", padx=22, pady=(8, 4))

        ctk.CTkLabel(
            card,
            text="Apaga TODOS os dados (manifestos, notas, contas, etc.) EXCETO usuários.\nApenas para usuário mestre.",
            font=(self.cores["font_family"], 11),
            text_color="#64748b",
            wraplength=430,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self.botao(card, "⚠️ Apagar Todos os Dados (Exceto Usuários)", "#7C2D12", "#991B1B", self.apagar_todos_dados_exceto_usuarios)

    def apagar_caminhoes(self):
        """Apaga todos os caminhões do sistema."""
        confirmar = messagebox.askyesno(
            "Apagar Caminhões",
            "Tem certeza que deseja apagar TODOS os caminhões cadastrados?\n\n"
            "Esta ação não pode ser desfeita e você precisará recadastrar os veículos."
        )

        if not confirmar:
            return

        confirmar_novamente = messagebox.askyesno(
            "Confirmação Final",
            "ÚLTIMA CONFIRMAÇÃO: Apagar TODOS os caminhões?\n\n"
            "Clique SIM apenas se tem certeza."
        )

        if not confirmar_novamente:
            return

        try:
            sucesso = viagem_service.apagar_caminhoes()

            if sucesso:
                messagebox.showinfo(
                    "Sucesso",
                    "Todos os caminhões foram apagados com sucesso!\n\n"
                    "Você pode recadastrar novos veículos agora."
                )
                self.recarregar_tela()
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível apagar os caminhões. Verifique o banco de dados."
                )

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao apagar caminhões:\n{erro}")

    def apagar_todos_dados_exceto_usuarios(self):
        """Apaga todos os dados do sistema EXCETO usuários (apenas mestre)."""
        from services.auth_service import auth_service
        
        # Verificar se é usuário mestre
        if not auth_service.eh_mestre:
            messagebox.showerror(
                "Acesso Negado",
                "Esta função está disponível apenas para o usuário mestre do sistema."
            )
            return
        
        confirmar = messagebox.askyesno(
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

        if not confirmar:
            return

        confirmar_novamente = messagebox.askyesno(
            "🔐 CONFIRMAÇÃO FINAL",
            "ÚLTIMA CONFIRMAÇÃO: Você realmente deseja apagar TODOS os dados?\n\n"
            "Clique SIM apenas se tiver certeza absoluta.\n\n"
            "Esta ação apagará permanentemente todos os dados operacionais do sistema."
        )

        if not confirmar_novamente:
            return

        try:
            sucesso = viagem_service.apagar_todos_dados_exceto_usuarios()

            if sucesso:
                messagebox.showinfo(
                    "Sucesso",
                    "Todos os dados foram apagados com sucesso!\n\n"
                    "Os usuários foram mantidos.\n"
                    "Você pode começar a recadastrar os dados agora."
                )
                self.recarregar_tela()
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível apagar os dados. Verifique o banco de dados."
                )

        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao apagar dados:\n{erro}")

    def criar_entry(self, master, chave, label):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", padx=22, pady=6)

        ctk.CTkLabel(
            frame,
            text=label,
            font=(self.cores["font_family"], 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w")

        entry = ctk.CTkEntry(frame, height=39)
        entry.pack(fill="x", pady=(4, 0))
        entry.insert(0, str(self.dados.get(chave, "")))

        self.campos[chave] = entry

    def botao(self, master, texto, cor, hover, comando):
        ctk.CTkButton(
            master,
            text=texto,
            height=42,
            fg_color=cor,
            hover_color=hover,
            font=(self.cores["font_family"], 13, "bold"),
            command=comando
        ).pack(fill="x", padx=22, pady=7)

    def salvar(self):
        try:
            dados = {}

            for chave, campo in self.campos.items():
                dados[chave] = campo.get().strip()

            config_service.salvar_configuracoes(dados)

            reiniciar = messagebox.askyesno(
                "Configurações salvas",
                "Configurações salvas com sucesso!\n\nDeseja reiniciar o sistema agora para aplicar o tema?"
            )

            if reiniciar:
                python = sys.executable
                os.execl(python, python, *sys.argv)

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def restaurar_padrao(self):
        confirmar = messagebox.askyesno(
            "Restaurar padrão",
            "Deseja restaurar todas as configurações padrão?"
        )

        if not confirmar:
            return

        self.dados = config_service.restaurar_padrao()

        for chave, campo in self.campos.items():
            campo.delete(0, "end")
            campo.insert(0, self.dados.get(chave, ""))

        self.salvar()

    def abrir_pasta_sistema(self):
        try:
            os.startfile(config_service.abrir_pasta_sistema())
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def abrir_pasta_relatorios(self):
        try:
            pasta = config_service.abrir_pasta_relatorios(
                self.campos["pasta_relatorios"].get().strip() or "relatorios_gerados"
            )
            os.startfile(pasta)

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def fazer_backup(self):
        try:
            pasta_backup = config_service.fazer_backup(
                self.campos["pasta_relatorios"].get().strip() or "relatorios_gerados"
            )

            messagebox.showinfo(
                "Backup concluído",
                f"Backup realizado com sucesso!\n\nPasta:\n{pasta_backup}"
            )

            os.startfile(pasta_backup)

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def info_banco(self):
        return config_service.info_banco()

    def recarregar_tela(self):
        self.campos = {}
        self.dados = config_service.carregar_configuracoes()

        for widget in self.winfo_children():
            widget.destroy()

        self.criar_layout()
