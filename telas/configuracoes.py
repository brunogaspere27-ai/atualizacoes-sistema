import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from config.settings import settings
from services.config_service import config_service
from services.viagem_service import viagem_service


class TelaConfiguracoes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F8")

        self.base_dir = str(settings.project_dir)
        self.config_path = str(settings.config_path)
        self.db_path = str(settings.db_path)

        self.campos = {}
        self.dados = config_service.carregar_configuracoes()

        self.criar_layout()

    def configuracao_padrao(self):
        return {
            "empresa": "CW TRANSPORTADORA",
            "cnpj": "",
            "telefone": "",
            "email": "",
            "cidade": "Cascavel",
            "uf": "PR",
            "pasta_relatorios": "relatorios_gerados",
            "meta_lucro": "10000",
            "imposto_percentual": "3",
            "alerta_revisao": "8000",
            "revisao_obrigatoria": "10000",
            "tema": "Vermelho CW",
            "cor_tema": "Vermelho"
        }

    def criar_layout(self):
        topo = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=24)
        topo.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            topo,
            text="CONFIGURAÇÕES DO SISTEMA",
            font=("Arial", 13, "bold"),
            text_color="#93c5fd"
        ).pack(anchor="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Central de Configurações",
            font=("Arial", 34, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=24)

        ctk.CTkLabel(
            topo,
            text="Dados da empresa, backup, banco de dados e preferências do sistema.",
            font=("Arial", 14),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=24, pady=(0, 18))

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=25, pady=5)
        self.container.grid_columnconfigure((0, 1), weight=1)

        self.criar_card_empresa()
        self.criar_card_sistema()
        self.criar_card_backup()
        self.criar_card_banco()
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
            font=("Arial", 14, "bold"),
            command=self.salvar
        ).pack(side="left")

        ctk.CTkButton(
            botoes,
            text="Restaurar Padrão",
            height=46,
            width=190,
            fg_color="#111827",
            hover_color="#374151",
            font=("Arial", 14, "bold"),
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
            font=("Arial", 20, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=22, pady=(20, 3))

        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=("Arial", 12),
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
            font=("Arial", 12, "bold"),
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
            font=("Arial", 12, "bold"),
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
            font=("Arial", 11),
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
                font=("Arial", 12, "bold"),
                text_color="#64748b"
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                linha,
                text=valor,
                font=("Arial", 12, "bold"),
                text_color="#111827"
            ).pack(side="right", padx=12, pady=10)

        self.botao(card, "Atualizar Informações", "#2563EB", "#1D4ED8", self.recarregar_tela)

    def criar_card_limpeza(self):
        """Card para limpeza de dados do sistema."""
        card = self.criar_card(
            "🗑️ Limpeza de Dados",
            "Remova dados salvos para recadastramento. Use com cuidado!",
            2,
            0
        )

        ctk.CTkLabel(
            card,
            text="Caminhões cadastrados",
            font=("Arial", 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=22, pady=(8, 4))

        ctk.CTkLabel(
            card,
            text="Remove todos os veículos para permitir novo cadastramento.",
            font=("Arial", 11),
            text_color="#64748b"
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self.botao(card, "🗑️ Apagar Todos os Caminhões", "#DC2626", "#B91C1C", self.apagar_caminhoes)

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

    def criar_entry(self, master, chave, label):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(fill="x", padx=22, pady=6)

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 12, "bold"),
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
            font=("Arial", 13, "bold"),
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
