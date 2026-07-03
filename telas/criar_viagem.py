"""
Tela para criação de viagens com pesquisa por cliente e seleção múltipla de notas.
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from tkinter import END, ttk, messagebox

import customtkinter as ctk

from services.viagem_service import viagem_service
from utils.loading_overlay import show_loading


def atualizar_marcacao_nota(notas_selecionadas, nota_id, selecionada):
    """Atualiza o conjunto de notas selecionadas de forma simples e previsível."""
    if selecionada:
        notas_selecionadas.add(nota_id)
    else:
        notas_selecionadas.discard(nota_id)
    return notas_selecionadas


def _caminho_json(nome_arquivo, caminho=None):
    """Retorna o caminho para um arquivo JSON de persistência."""
    if caminho is not None:
        return Path(caminho)

    base_dir = Path(__file__).resolve().parent.parent / "backup_dados"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / nome_arquivo


def salvar_rascunho_viagem(dados, caminho=None):
    """Salva o estado atual da viagem em um arquivo JSON."""
    caminho = _caminho_json("rascunho_viagem.json", caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    return caminho


def carregar_rascunho_viagem(caminho=None):
    """Carrega o rascunho salvo, se existir."""
    caminho = _caminho_json("rascunho_viagem.json", caminho)
    if not caminho.exists():
        return None

    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def limpar_rascunho_viagem(caminho=None):
    """Remove o arquivo de rascunho, se existir."""
    caminho = _caminho_json("rascunho_viagem.json", caminho)
    if caminho.exists():
        caminho.unlink()
    return caminho


def adicionar_historico_viagem(dados, caminho=None, limite=8):
    """Adiciona uma viagem ao histórico rápido em formato JSON."""
    caminho = _caminho_json("historico_viagens.json", caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    historico = []
    if caminho.exists():
        with caminho.open("r", encoding="utf-8") as arquivo:
            try:
                historico = json.load(arquivo)
            except json.JSONDecodeError:
                historico = []

    historico.insert(0, dados)
    historico = historico[:limite]

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=2)

    return historico


def listar_historico_viagem(caminho=None):
    """Lista as viagens recentes do histórico."""
    caminho = _caminho_json("historico_viagens.json", caminho)
    if not caminho.exists():
        return []

    with caminho.open("r", encoding="utf-8") as arquivo:
        try:
            return json.load(arquivo)
        except json.JSONDecodeError:
            return []


class TelaCriarViagem(ctk.CTkFrame):
    """Tela melhorada para criação de viagens."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.cliente_selecionado = None
        self.cliente_selecionado_id = None
        self.notas_disponiveis = []
        self.notas_selecionadas = set()
        self.caminhoes_map = {}
        self.caminhoes_catalogo = []
        self.notas_ids = {}
        self.notas_catalogo = {}
        self.notas_selecionadas_tree_ids = {}
        self.caminho_rascunho = _caminho_json("rascunho_viagem.json")
        self.caminho_historico = _caminho_json("historico_viagens.json")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header moderno
        header_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        ctk.CTkLabel(
            header_frame,
            text="🔹 OPERAÇÕES",
            font=("Arial", 11, "bold"),
            text_color="#93C5FD"
        ).pack(anchor="w", padx=28, pady=(14, 2))

        self.titulo = ctk.CTkLabel(
            header_frame,
            text="Criar Nova Viagem",
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF"
        )
        self.titulo.pack(anchor="w", padx=28, pady=(0, 6))

        ctk.CTkLabel(
            header_frame,
            text="Selecione um cliente e as notas para criar uma nova viagem",
            font=("Arial", 13),
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=28, pady=(0, 18))

        self.criar_area_principal()

    def criar_area_principal(self):
        """Cria a área principal com busca e seleção de notas."""
        
        frame_principal = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        frame_principal.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_rowconfigure(1, weight=1)

        # Área de busca de cliente
        self.criar_area_busca_cliente(frame_principal)

        # Área de seleção de notas
        self.criar_area_selecao_notas(frame_principal)

        # Área de resumo e criação
        self.criar_area_resumo(frame_principal)

        # Carregar caminhões e dados salvos
        self.carregar_caminhoes()
        self.after(200, self.carregar_rascunho)

    def criar_area_busca_cliente(self, parent):
        """Cria área de busca por cliente."""
        
        frame_busca = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=14, border_width=1, border_color="#E2E8F0")
        frame_busca.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        frame_busca.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_busca,
            text="👤 Selecione o Cliente",
            font=("Arial", 14, "bold"),
            text_color="#0F172A"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(14, 8))

        linha_busca = ctk.CTkFrame(frame_busca, fg_color="transparent")
        linha_busca.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))
        linha_busca.grid_columnconfigure(0, weight=1)

        self.entrada_busca_cliente = ctk.CTkEntry(
            linha_busca,
            placeholder_text="Digite o nome ou CNPJ do cliente...",
            height=44,
            border_width=2,
            border_color="#E2E8F0",
            fg_color="#FFFFFF",
            text_color="#0F172A",
            font=("Arial", 12)
        )
        self.entrada_busca_cliente.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.entrada_busca_cliente.bind("<Return>", lambda _: self.buscar_cliente())

        ctk.CTkButton(
            linha_busca,
            text="🔍 Buscar",
            width=140,
            height=44,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            font=("Arial", 12, "bold"),
            corner_radius=10,
            command=self.buscar_cliente
        ).grid(row=0, column=1)

        # Label do cliente selecionado
        self.label_cliente_selecionado = ctk.CTkLabel(
            frame_busca,
            text="Nenhum cliente selecionado",
            font=("Arial", 12),
            text_color="#64748B"
        )
        self.label_cliente_selecionado.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 14))

    def criar_area_selecao_notas(self, parent):
        """Cria área de seleção de notas com lista lateral de selecionadas."""
        
        frame_notas = ctk.CTkFrame(parent, fg_color="transparent")
        frame_notas.grid(row=1, column=0, sticky="nsew", padx=18, pady=12)
        frame_notas.grid_columnconfigure(0, weight=2)
        frame_notas.grid_columnconfigure(1, weight=1)
        frame_notas.grid_rowconfigure(1, weight=1)

        linha_titulo = ctk.CTkFrame(frame_notas, fg_color="transparent")
        linha_titulo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        linha_titulo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            linha_titulo,
            text="📦 Selecione as Notas",
            font=("Arial", 14, "bold"),
            text_color="#0F172A"
        ).grid(row=0, column=0, sticky="w")

        linha_botoes = ctk.CTkFrame(linha_titulo, fg_color="transparent")
        linha_botoes.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            linha_botoes,
            text="✅ Todas",
            width=110,
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            font=("Arial", 11, "bold"),
            command=self.selecionar_todas
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            linha_botoes,
            text="⏹ Limpar",
            width=110,
            height=36,
            fg_color="#94A3B8",
            hover_color="#64748B",
            font=("Arial", 11, "bold"),
            command=self.limpar_selecao
        ).pack(side="left", padx=6)

        frame_conteudo = ctk.CTkFrame(frame_notas, fg_color="transparent")
        frame_conteudo.grid(row=1, column=0, columnspan=2, sticky="nsew")
        frame_conteudo.grid_columnconfigure(0, weight=2)
        frame_conteudo.grid_columnconfigure(1, weight=1)
        frame_conteudo.grid_rowconfigure(0, weight=1)

        tabela_frame = ctk.CTkFrame(frame_conteudo, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        tabela_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tabela_frame.grid_columnconfigure(0, weight=1)
        tabela_frame.grid_rowconfigure(0, weight=1)

        colunas = (
            "selecionar", "numero", "cidade", "peso", "data", "status"
        )

        self.tree_notas = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            height=12,
            selectmode="browse"
        )

        titulos = {
            "selecionar": "Sel.",
            "numero": "Nota/CT-e",
            "cidade": "Cidade",
            "peso": "Peso",
            "data": "Data",
            "status": "Status"
        }

        larguras = {
            "selecionar": 55,
            "numero": 180,
            "cidade": 200,
            "peso": 120,
            "data": 150,
            "status": 120
        }

        for col in colunas:
            self.tree_notas.heading(col, text=titulos[col])
            self.tree_notas.column(col, width=larguras[col], anchor="w")

        self.tree_notas.column("selecionar", anchor="center")
        self.tree_notas.column("peso", anchor="e")
        self.tree_notas.column("status", anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree_notas.yview)
        scroll_x = ttk.Scrollbar(tabela_frame, orient="horizontal", command=self.tree_notas.xview)

        self.tree_notas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_notas.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree_notas.bind("<ButtonRelease-1>", self.clicar_na_nota)

        self.frame_selecionadas = ctk.CTkFrame(frame_conteudo, fg_color="#F0F9FF", corner_radius=12, border_width=1, border_color="#BFDBFE")
        self.frame_selecionadas.grid(row=0, column=1, sticky="nsew")
        self.frame_selecionadas.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.frame_selecionadas,
            text="✓ Selecionadas",
            font=("Arial", 13, "bold"),
            text_color="#0F172A"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self.label_nota_selecionada = ctk.CTkLabel(
            self.frame_selecionadas,
            text="0 notas marcadas",
            font=("Arial", 11),
            text_color="#0EA5E9"
        )
        self.label_nota_selecionada.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 8))

        self.tree_selecionadas = ttk.Treeview(
            self.frame_selecionadas,
            columns=("numero", "peso"),
            show="headings",
            height=10,
            selectmode="browse"
        )
        self.tree_selecionadas.heading("numero", text="Nota")
        self.tree_selecionadas.heading("peso", text="Peso")
        self.tree_selecionadas.column("numero", width=140, anchor="w")
        self.tree_selecionadas.column("peso", width=90, anchor="e")
        self.tree_selecionadas.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 8))

        self.frame_selecionadas.grid_rowconfigure(2, weight=1)
        self.frame_selecionadas.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            self.frame_selecionadas,
            text="🗑 Remover",
            height=36,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=("Arial", 11, "bold"),
            command=self.remover_nota_selecionada
        ).grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))


    def criar_area_resumo(self, parent):
        """Cria área de resumo e criação da viagem."""
        
        self.frame_resumo = ctk.CTkFrame(parent, fg_color="#F0F9FF", corner_radius=14, border_width=1, border_color="#BFDBFE")
        self.frame_resumo.grid(row=2, column=0, sticky="ew", padx=18, pady=(12, 18))
        self.frame_resumo.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Cards de resumo
        self.card_qtd = self.criar_card_resumo("QUANTIDADE", "0", 0, "#111827")
        self.card_peso = self.criar_card_resumo("PESO TOTAL", "0 kg", 1, "#b91c1c")
        self.card_frete = self.criar_card_resumo("FRETE TOTAL", "R$ 0,00", 2, "#15803d")
        self.card_volumes = self.criar_card_resumo("VOLUMES", "0", 3, "#2563EB")

        # Linha de criação da viagem
        linha_criacao = ctk.CTkFrame(parent, fg_color="transparent")
        linha_criacao.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))

        ctk.CTkLabel(
            linha_criacao,
            text="CAMINHÃO:",
            font=("Arial", 12, "bold"),
            text_color="#374151"
        ).pack(side="left", padx=(0, 8))

        self.combo_caminhoes = ctk.CTkComboBox(
            linha_criacao,
            width=280,
            values=["Nenhum caminhão cadastrado"]
        )
        self.combo_caminhoes.pack(side="left", padx=(0, 15))
        self.combo_caminhoes.bind("<KeyRelease>", lambda *_: self.atualizar_validacao())

        ctk.CTkLabel(
            linha_criacao,
            text="MOTORISTA:",
            font=("Arial", 12, "bold"),
            text_color="#374151"
        ).pack(side="left", padx=(0, 8))

        self.entrada_motorista = ctk.CTkEntry(
            linha_criacao,
            width=200,
            placeholder_text="Nome do motorista"
        )
        self.entrada_motorista.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            linha_criacao,
            text="� Rascunho",
            width=120,
            height=42,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            command=self.salvar_rascunho_atual
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            linha_criacao,
            text="📂 Carregar",
            width=120,
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.carregar_rascunho
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            linha_criacao,
            text="🧹 Limpar",
            width=110,
            height=42,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.limpar_rascunho
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            linha_criacao,
            text="🚚 CRIAR VIAGEM",
            width=180,
            height=46,
            fg_color="#16A34A",
            hover_color="#15803D",
            font=("Arial", 14, "bold"),
            command=self.criar_viagem
        ).pack(side="right")

        self.label_validacao = ctk.CTkLabel(
            parent,
            text="Selecione notas e um caminhão para validar a viagem.",
            font=("Arial", 12),
            text_color="#6B7280",
            anchor="w"
        )
        self.label_validacao.grid(row=4, column=0, sticky="ew", padx=18, pady=(8, 8))

        self.label_historico = ctk.CTkLabel(
            parent,
            text="Histórico rápido: ainda sem viagens criadas.",
            font=("Arial", 12),
            text_color="#4B5563",
            anchor="w",
            justify="left"
        )
        self.label_historico.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 16))

    def criar_card_resumo(self, titulo, valor, col, cor):
        """Cria um card de resumo."""
        
        card = ctk.CTkFrame(
            self.frame_resumo,
            fg_color="#ffffff",
            corner_radius=10,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.grid(row=0, column=col, padx=8, pady=12, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 11, "bold"),
            text_color="#6B7280"
        ).pack(anchor="w", padx=12, pady=(10, 4))

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 18, "bold"),
            text_color=cor
        )
        label_valor.pack(anchor="w", padx=12, pady=(0, 10))

        return label_valor

    def carregar_caminhoes(self):
        """Carrega a lista de caminhões disponíveis."""
        
        self.caminhoes_map = {}
        self.caminhoes_catalogo = []
        caminhoes = viagem_service.listar_caminhoes_disponiveis()
        valores = []

        for caminhao in caminhoes:
            caminhao_id, placa, modelo, motorista, capacidade = caminhao
            texto = f"{modelo} | {placa} | {capacidade:,.0f} kg"
            self.caminhoes_map[texto] = caminhao_id
            self.caminhoes_catalogo.append({
                "id": caminhao_id,
                "texto": texto,
                "capacidade": capacidade or 0,
            })
            valores.append(texto)

        if not valores:
            valores = ["Nenhum caminhão cadastrado"]

        self.combo_caminhoes.configure(values=valores)
        if valores:
            self.combo_caminhoes.set(valores[0])

        self.atualizar_validacao()

    def buscar_cliente(self):
        """Busca clientes pelo nome digitado."""
        
        termo = self.entrada_busca_cliente.get().strip()
        
        if not termo or len(termo) < 2:
            messagebox.showwarning("Atenção", "Digite pelo menos 2 caracteres para buscar.")
            return

        # Mostrar loading
        overlay = show_loading(self, "Buscando clientes...")

        def tarefa_busca():
            clientes = viagem_service.buscar_clientes(termo)
            
            self.after(0, lambda: overlay.destroy())
            
            if not clientes:
                self.after(0, lambda: messagebox.showinfo("Resultado", "Nenhum cliente encontrado."))
                return

            # Mostrar diálogo para selecionar cliente
            self.after(0, lambda: self.mostrar_dialogo_selecao_cliente(clientes))

        threading.Thread(target=tarefa_busca, daemon=True).start()

    def mostrar_dialogo_selecao_cliente(self, clientes):
        """Mostra diálogo para seleção do cliente."""
        
        janela = ctk.CTkToplevel(self)
        janela.title("Selecionar Cliente")
        janela.geometry("500x400")
        janela.resizable(False, False)
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="Selecione o Cliente",
            font=("Arial", 18, "bold")
        ).pack(pady=(20, 10))

        frame_lista = ctk.CTkFrame(janela)
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

        colunas = ("nome", "cidade", "uf")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=12)

        tree.heading("nome", text="Nome")
        tree.heading("cidade", text="Cidade")
        tree.heading("uf", text="UF")

        tree.column("nome", width=250)
        tree.column("cidade", width=120)
        tree.column("uf", width=50)

        tree.pack(fill="both", expand=True)

        tree.bind("<Double-1>", lambda _: on_selecionar())

        clientes_map = {}
        for cliente in clientes:
            cliente_id, nome, cnpj, cidade, uf = cliente
            item = tree.insert("", "end", values=(nome, cidade or "-", uf or "-"))
            clientes_map[item] = (cliente_id, nome)

        def on_selecionar():
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Atenção", "Selecione um cliente.")
                return

            cliente_id, nome = clientes_map[selecionado]
            self.selecionar_cliente(cliente_id, nome)
            janela.destroy()

        ctk.CTkButton(
            janela,
            text="Selecionar",
            width=150,
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=on_selecionar
        ).pack(pady=10)

    def selecionar_cliente(self, cliente_id, nome):
        """Seleciona um cliente e carrega suas notas."""
        
        self.cliente_selecionado_id = cliente_id
        self.cliente_selecionado = nome
        
        self.label_cliente_selecionado.configure(
            text=f"Cliente selecionado: {nome} • {len(self.notas_selecionadas)} nota(s) preservadas",
            text_color="#16A34A"
        )

        self.notas_ids = {}

        # Carregar notas do cliente sem perder a seleção anterior
        self.carregar_notas_cliente()

    def carregar_notas_cliente(self):
        """Carrega notas disponíveis do cliente selecionado."""
        
        if not self.cliente_selecionado_id:
            return

        # Limpar tabela
        for item in self.tree_notas.get_children():
            self.tree_notas.delete(item)

        # Mostrar loading
        overlay = show_loading(self, "Carregando notas...")

        def tarefa_carregar():
            notas = viagem_service.listar_notas_cliente(
                self.cliente_selecionado_id,
                apenas_disponiveis=True,
                excluir_vinculadas=True
            )

            linhas = []
            for nota in notas:
                (
                    nota_id,
                    numero_cte,
                    chave_nfe,
                    _cliente_nome,
                    cidade,
                    peso,
                    _frete,
                    data,
                    status
                ) = nota

                numero = numero_cte if numero_cte else chave_nfe[:20] if chave_nfe else "-"
                peso = peso or 0
                data_formatada = data[:10] if data else "-"
                marcador = "☐" if nota_id not in self.notas_selecionadas else "☑"
                self.notas_catalogo[nota_id] = {
                    "numero": numero,
                    "cidade": cidade or "-",
                    "peso": peso,
                    "data": data_formatada,
                    "status": status,
                }

                linhas.append((
                    nota_id,
                    (
                        marcador,
                        numero,
                        cidade or "-",
                        f"{peso:,.2f} kg",
                        data_formatada,
                        status,
                    ),
                ))

            def preencher_tabela():
                overlay.destroy()
                self.notas_disponiveis = notas
                self.notas_ids = {}

                for item in self.tree_notas.get_children():
                    self.tree_notas.delete(item)

                for nota_id, valores in linhas:
                    item_id = self.tree_notas.insert("", "end", values=valores)
                    self.notas_ids[item_id] = nota_id

                self.atualizar_resumo()
                self.atualizar_lista_selecionadas()
                self.atualizar_validacao()

            self.after(0, preencher_tabela)

        threading.Thread(target=tarefa_carregar, daemon=True).start()

    def clicar_na_nota(self, event=None):
        """Evento ao clicar em uma nota."""
        
        item = self.tree_notas.identify_row(event.y)
        
        if not item:
            return

        valores = list(self.tree_notas.item(item, "values"))
        
        if not valores:
            return

        nota_id = self.notas_ids.get(item)
        
        if not nota_id:
            return

        selecionada = nota_id not in self.notas_selecionadas
        atualizar_marcacao_nota(self.notas_selecionadas, nota_id, selecionada)
        valores[0] = "☑" if selecionada else "☐"

        self.tree_notas.item(item, values=valores)
        self.atualizar_resumo()
        self.atualizar_lista_selecionadas()
        self.atualizar_validacao()
        self.salvar_rascunho_atual()

    def selecionar_todas(self):
        """Seleciona todas as notas visíveis."""
        
        for item in self.tree_notas.get_children():
            nota_id = self.notas_ids.get(item)
            if nota_id and nota_id not in self.notas_selecionadas:
                atualizar_marcacao_nota(self.notas_selecionadas, nota_id, True)
                valores = list(self.tree_notas.item(item, "values"))
                valores[0] = "☑"
                self.tree_notas.item(item, values=valores)

        self.atualizar_resumo()
        self.atualizar_lista_selecionadas()

    def limpar_selecao(self):
        """Limpa todas as seleções."""
        
        self.notas_selecionadas.clear()
        
        for item in self.tree_notas.get_children():
            valores = list(self.tree_notas.item(item, "values"))
            valores[0] = "☐"
            self.tree_notas.item(item, values=valores)

        self.atualizar_resumo()
        self.atualizar_lista_selecionadas()

    def atualizar_lista_selecionadas(self):
        """Atualiza a lista lateral de notas selecionadas."""
        for item in self.tree_selecionadas.get_children():
            self.tree_selecionadas.delete(item)

        self.notas_selecionadas_tree_ids = {}

        notas_ordenadas = sorted(self.notas_selecionadas)
        for nota_id in notas_ordenadas:
            dados = self.notas_catalogo.get(nota_id, {})
            numero = dados.get("numero", "-")
            peso = dados.get("peso", 0) or 0
            item_id = self.tree_selecionadas.insert(
                "",
                "end",
                values=(numero, f"{peso:,.2f} kg")
            )
            self.notas_selecionadas_tree_ids[item_id] = nota_id

        self.label_nota_selecionada.configure(
            text=f"{len(self.notas_selecionadas)} nota(s) marcada(s)"
        )

    def remover_nota_selecionada(self):
        """Remove a nota selecionada da lista lateral."""
        selecionado = self.tree_selecionadas.focus()
        if not selecionado:
            return

        nota_id = self.notas_selecionadas_tree_ids.get(selecionado)
        if not nota_id:
            return

        self.notas_selecionadas.discard(nota_id)
        self.tree_selecionadas.delete(selecionado)

        for item in self.tree_notas.get_children():
            if self.notas_ids.get(item) == nota_id:
                valores = list(self.tree_notas.item(item, "values"))
                valores[0] = "☐"
                self.tree_notas.item(item, values=valores)
                break

        self.atualizar_resumo()
        self.atualizar_lista_selecionadas()

    def atualizar_resumo(self):
        """Atualiza os cards de resumo."""
        
        notas_ids = list(self.notas_selecionadas)
        resumo = viagem_service.calcular_resumo_selecao(notas_ids)

        self.card_qtd.configure(text=str(resumo["quantidade"]))
        self.card_peso.configure(text=f"{resumo['peso_total']:,.2f} kg")
        self.card_frete.configure(text=f"R$ {resumo['frete_total']:,.2f}")
        self.card_volumes.configure(text=str(resumo["volumes"]))

    def atualizar_validacao(self):
        """Atualiza o status visual com validação de capacidade e sugestão de caminhão."""
        if not self.notas_selecionadas:
            self.label_validacao.configure(
                text="Selecione notas para validar a viagem.",
                text_color="#6B7280"
            )
            return

        caminhao_texto = self.combo_caminhoes.get()
        if not caminhao_texto or "Nenhum caminhão" in caminhao_texto:
            self.label_validacao.configure(
                text="Selecione um caminhão para validar a capacidade.",
                text_color="#F59E0B"
            )
            return

        caminhao_id = self.caminhoes_map.get(caminhao_texto)
        if not caminhao_id:
            self.label_validacao.configure(
                text="Caminhão não encontrado na lista atual.",
                text_color="#DC2626"
            )
            return

        valido, mensagem, _ = viagem_service.validar_capacidade(
            caminhao_id,
            list(self.notas_selecionadas)
        )

        if valido:
            self.label_validacao.configure(
                text=f"Capacidade OK para {caminhao_texto}.",
                text_color="#15803D"
            )
        else:
            sugestao = self.sugerir_caminhao_ideal()
            detalhe = mensagem if mensagem else "Capacidade excedida."
            texto = f"{detalhe}"
            if sugestao:
                texto += f" Sugestão: {sugestao}."
            self.label_validacao.configure(text=texto, text_color="#DC2626")

    def sugerir_caminhao_ideal(self):
        """Sugere um caminhão com capacidade suficiente para as notas selecionadas."""
        if not self.notas_selecionadas:
            return ""

        resumo = viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas))
        peso_total = resumo.get("peso_total", 0) or 0

        for item in self.caminhoes_catalogo:
            if item.get("capacidade", 0) >= peso_total:
                return item.get("texto", "")

        return ""

    def salvar_rascunho_atual(self):
        """Salva o estado atual da tela como rascunho."""
        dados = {
            "cliente_id": self.cliente_selecionado_id,
            "cliente_nome": self.cliente_selecionado,
            "notas": sorted(self.notas_selecionadas),
            "motorista": self.entrada_motorista.get().strip(),
            "caminhao": self.combo_caminhoes.get(),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "quantidade": len(self.notas_selecionadas),
        }
        salvar_rascunho_viagem(dados, self.caminho_rascunho)
        messagebox.showinfo("Rascunho salvo", "O estado atual foi salvo com sucesso.")

    def carregar_rascunho(self):
        """Carrega um rascunho salvo, se existir."""
        dados = carregar_rascunho_viagem(self.caminho_rascunho)
        if not dados:
            messagebox.showinfo("Rascunho", "Nenhum rascunho encontrado.")
            return

        if dados.get("cliente_id") and dados.get("cliente_nome"):
            self.selecionar_cliente(dados["cliente_id"], dados["cliente_nome"])

        self.notas_selecionadas = set(dados.get("notas", []))
        self.entrada_motorista.delete(0, END)
        self.entrada_motorista.insert(0, dados.get("motorista", ""))

        caminhao = dados.get("caminhao")
        if caminhao and caminhao in self.caminhoes_map:
            self.combo_caminhoes.set(caminhao)

        self.atualizar_resumo()
        self.atualizar_lista_selecionadas()
        self.atualizar_validacao()
        self.atualizar_historico()
        messagebox.showinfo("Rascunho carregado", "As informações salvas foram restauradas.")

    def limpar_rascunho(self):
        """Limpa o rascunho salvo."""
        limpar_rascunho_viagem(self.caminho_rascunho)
        messagebox.showinfo("Rascunho", "O rascunho foi removido.")

    def atualizar_historico(self):
        """Atualiza a mensagem de histórico rápido com as últimas viagens."""
        historico = listar_historico_viagem(self.caminho_historico)
        if not historico:
            self.label_historico.configure(text="Histórico rápido: ainda sem viagens criadas.")
            return

        linhas = []
        for item in historico[:3]:
            linhas.append(
                f"• Viagem #{item.get('viagem_id')} | {item.get('motorista', '-')} | {item.get('caminhao', '-')} | {item.get('quantidade', 0)} notas"
            )

        self.label_historico.configure(text="Histórico rápido:\n" + "\n".join(linhas), text_color="#111827")

    def criar_viagem(self):
        """Cria a viagem com as notas selecionadas."""
        
        if not self.cliente_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione um cliente primeiro.")
            return

        if not self.notas_selecionadas:
            messagebox.showwarning("Atenção", "Selecione pelo menos uma nota.")
            return

        caminhao_texto = self.combo_caminhoes.get()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)

        if not caminhao_id or "Nenhum" in caminhao_texto:
            messagebox.showwarning("Atenção", "Selecione um caminhão válido.")
            return

        motorista = self.entrada_motorista.get().strip()

        if not motorista:
            messagebox.showwarning("Atenção", "Informe o motorista da viagem.")
            return

        # Validar capacidade
        valido, mensagem, _ = viagem_service.validar_capacidade(
            caminhao_id,
            list(self.notas_selecionadas)
        )

        if not valido:
            if not messagebox.askyesno(
                "Aviso de Capacidade",
                f"{mensagem}\n\nDeseja continuar mesmo assim?"
            ):
                return

        # Mostrar loading
        overlay = show_loading(self, "Criando viagem...")

        def tarefa_criar():
            # Criar viagem
            try:
                viagem_id = viagem_service.criar_viagem_com_notas(
                    caminhao_id,
                    list(self.notas_selecionadas),
                    motorista
                )

                self.after(0, lambda: overlay.destroy())

                self.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Viagem #{viagem_id} criada com sucesso!\n"
                    f"{len(self.notas_selecionadas)} nota(s) adicionada(s)."
                ))

                self.after(0, lambda: adicionar_historico_viagem({
                    "viagem_id": viagem_id,
                    "motorista": motorista,
                    "caminhao": caminhao_texto,
                    "quantidade": len(self.notas_selecionadas),
                    "peso_total": round(viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas)).get("peso_total", 0), 2),
                    "frete_total": round(viagem_service.calcular_resumo_selecao(list(self.notas_selecionadas)).get("frete_total", 0), 2),
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                }, self.caminho_historico))

                # Limpar seleção
                self.after(0, self.limpar_selecao)
                self.after(0, lambda: self.entrada_motorista.delete(0, "end"))
                self.after(0, lambda: limpar_rascunho_viagem(self.caminho_rascunho))
                self.after(0, self.atualizar_historico)
                
                # Recarregar notas
                self.after(0, self.carregar_notas_cliente)

            except Exception as e:
                self.after(0, lambda: overlay.destroy())
                self.after(0, lambda: messagebox.showerror("Erro", f"Erro ao criar viagem:\n{e}"))

        threading.Thread(target=tarefa_criar, daemon=True).start()
