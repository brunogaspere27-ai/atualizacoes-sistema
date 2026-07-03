import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from services.historico_service import historico_service


class TelaHistorico(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.viagens_ids = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self,
            text="🚚 VIAGENS",
            font=("Arial", 28, "bold"),
            text_color="#b91c1c"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 18))

        self.criar_resumo()
        self.criar_tabela()
        self.carregar_viagens()

    def criar_resumo(self):

        self.frame_resumo = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        self.frame_resumo.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        self.frame_resumo.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_total = self.criar_card_resumo("VIAGENS", "0", 0, "#111827")
        self.card_notas = self.criar_card_resumo("NOTAS", "0", 1, "#111827")
        self.card_frete = self.criar_card_resumo("FRETE TOTAL", "R$ 0,00", 2, "#15803d")
        self.card_peso = self.criar_card_resumo("PESO TOTAL", "0 kg", 3, "#b91c1c")

    def criar_card_resumo(self, titulo, valor, col, cor):

        card = ctk.CTkFrame(
            self.frame_resumo,
            fg_color="#f9fafb",
            corner_radius=14,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.grid(row=0, column=col, padx=8, pady=14, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 10, "bold"),
            text_color="#6b7280"
        ).pack(anchor="w", padx=12, pady=(12, 4))

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 17, "bold"),
            text_color=cor
        )
        label_valor.pack(anchor="w", padx=12, pady=(0, 12))

        return label_valor

    def criar_tabela(self):

        frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(frame, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        ctk.CTkLabel(
            topo,
            text="Lista de Viagens Criadas",
            font=("Arial", 17, "bold"),
            text_color="#111827"
        ).pack(side="left")

        ctk.CTkButton(
            topo,
            text="🔄 Atualizar",
            width=120,
            fg_color="#111827",
            hover_color="#374151",
            command=self.carregar_viagens
        ).pack(side="right")

        tabela_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        tabela_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        tabela_frame.grid_columnconfigure(0, weight=1)
        tabela_frame.grid_rowconfigure(0, weight=1)

        colunas = (
            "id", "data", "caminhao", "placa", "motorista",
            "status", "notas", "peso", "frete", "ver", "finalizar"
        )

        self.tree = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            height=22
        )

        titulos = {
            "id": "Viagem",
            "data": "Data Saída",
            "caminhao": "Caminhão",
            "placa": "Placa/Nome",
            "motorista": "Motorista",
            "status": "Status",
            "notas": "Notas",
            "peso": "Peso",
            "frete": "Frete",
            "ver": "Ver",
            "finalizar": "Finalizar"
        }

        larguras = {
            "id": 80,
            "data": 150,
            "caminhao": 220,
            "placa": 140,
            "motorista": 180,
            "status": 120,
            "notas": 80,
            "peso": 130,
            "frete": 140,
            "ver": 110,
            "finalizar": 110
        }

        for col in colunas:
            self.tree.heading(col, text=titulos[col])
            self.tree.column(col, width=larguras[col], anchor="w")

        self.tree.column("id", anchor="center")
        self.tree.column("status", anchor="center")
        self.tree.column("notas", anchor="center")
        self.tree.column("peso", anchor="e")
        self.tree.column("frete", anchor="e")
        self.tree.column("ver", anchor="center")
        self.tree.column("finalizar", anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tabela_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", self.clique_acao_viagem)

    def carregar_viagens(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.viagens_ids = {}

        viagens = historico_service.listar_viagens()

        total_viagens = len(viagens)
        total_notas = 0
        total_frete = 0
        total_peso = 0

        for viagem in viagens:
            (
                viagem_id,
                data_saida,
                modelo,
                placa,
                motorista,
                status,
                peso_total,
                frete_total,
                qtd_notas
            ) = viagem

            peso_total = peso_total or 0
            frete_total = frete_total or 0
            qtd_notas = qtd_notas or 0

            total_notas += qtd_notas
            total_frete += frete_total
            total_peso += peso_total

            item_id = self.tree.insert("", "end", values=(
                f"#{viagem_id}",
                data_saida,
                modelo or "-",
                placa or "-",
                motorista or "-",
                status or "-",
                qtd_notas,
                f"{peso_total:,.2f} kg",
                f"R$ {frete_total:,.2f}",
                "👁 Ver Notas",
                "✅ Finalizar" if status != "Finalizada" else "Finalizada"
            ))

            self.viagens_ids[item_id] = viagem_id

        self.card_total.configure(text=str(total_viagens))
        self.card_notas.configure(text=str(total_notas))
        self.card_frete.configure(text=f"R$ {total_frete:,.2f}")
        self.card_peso.configure(text=f"{total_peso:,.2f} kg")

    def clique_acao_viagem(self, event=None):

        item = self.tree.focus()

        if not item:
            return

        coluna = self.tree.identify_column(event.x)
        valores = self.tree.item(item, "values")

        if not valores:
            return

        viagem_id = self.viagens_ids.get(item)
        status = valores[5]

        if coluna == "#10":
            self.abrir_notas_viagem()
            return

        if coluna == "#11":

            if status == "Finalizada":
                messagebox.showinfo(
                    "Viagem finalizada",
                    "Essa viagem já está finalizada."
                )
                return

            confirmar = messagebox.askyesno(
                "Finalizar viagem",
                f"Deseja finalizar a viagem #{viagem_id}?"
            )

            if not confirmar:
                return

            data_retorno = datetime.now().strftime("%d/%m/%Y %H:%M")

            historico_service.finalizar_viagem(viagem_id, data_retorno)

            messagebox.showinfo(
                "Sucesso",
                f"Viagem #{viagem_id} finalizada com sucesso!"
            )

            self.carregar_viagens()

    def abrir_notas_viagem(self, event=None):

        item = self.tree.focus()

        if not item:
            return

        viagem_id = self.viagens_ids.get(item)

        if not viagem_id:
            return

        notas = historico_service.listar_notas_da_viagem(viagem_id)
        detalhes = historico_service.buscar_detalhes_viagem(viagem_id)

        janela = ctk.CTkToplevel(self)
        janela.title(f"Notas da Viagem #{viagem_id}")
        janela.geometry("1150x720")
        janela.configure(fg_color="#f3f4f6")
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text=f"📦 DETALHES DA VIAGEM #{viagem_id}",
            font=("Arial", 24, "bold"),
            text_color="#b91c1c"
        ).pack(anchor="w", padx=20, pady=(20, 10))

        if detalhes:
            (
                id_viagem,
                data_saida,
                data_retorno,
                motorista,
                status_viagem,
                peso_total_banco,
                frete_total_banco,
                modelo,
                placa,
                capacidade
            ) = detalhes

            capacidade = capacidade or 0
            peso_total_banco = peso_total_banco or 0

            uso_capacidade = 0

            if capacidade > 0:
                uso_capacidade = (peso_total_banco / capacidade) * 100

            info = ctk.CTkFrame(janela, fg_color="#ffffff", corner_radius=16)
            info.pack(fill="x", padx=20, pady=(0, 10))

            def card_info(titulo, valor, cor="#111827"):
                card = ctk.CTkFrame(
                    info,
                    fg_color="#f9fafb",
                    corner_radius=12,
                    border_width=1,
                    border_color="#e5e7eb"
                )
                card.pack(side="left", expand=True, fill="x", padx=8, pady=12)

                ctk.CTkLabel(
                    card,
                    text=titulo,
                    font=("Arial", 10, "bold"),
                    text_color="#6b7280"
                ).pack(anchor="w", padx=12, pady=(10, 2))

                ctk.CTkLabel(
                    card,
                    text=valor,
                    font=("Arial", 14, "bold"),
                    text_color=cor
                ).pack(anchor="w", padx=12, pady=(0, 10))

            card_info("CAMINHÃO", f"{modelo or '-'} | {placa or '-'}")
            card_info("MOTORISTA", motorista or "-")
            card_info("SAÍDA", data_saida or "-")
            card_info("RETORNO", data_retorno or "-")
            card_info(
                "STATUS",
                status_viagem or "-",
                "#15803d" if status_viagem == "Finalizada" else "#b91c1c"
            )
            card_info("CAPACIDADE", f"{uso_capacidade:.1f}% usada")

        frame = ctk.CTkFrame(janela, fg_color="#ffffff", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        colunas = (
            "cte", "remetente", "cliente", "origem",
            "destino", "frete", "peso", "status"
        )

        tree = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=20
        )

        titulos = {
            "cte": "CT-e",
            "remetente": "Remetente",
            "cliente": "Cliente",
            "origem": "Origem",
            "destino": "Destino",
            "frete": "Frete",
            "peso": "Peso",
            "status": "Status"
        }

        larguras = {
            "cte": 180,
            "remetente": 250,
            "cliente": 250,
            "origem": 130,
            "destino": 140,
            "frete": 110,
            "peso": 110,
            "status": 120
        }

        for col in colunas:
            tree.heading(col, text=titulos[col])
            tree.column(col, width=larguras[col], anchor="w")

        tree.column("frete", anchor="e")
        tree.column("peso", anchor="e")
        tree.column("status", anchor="center")

        tree.pack(fill="both", expand=True, padx=12, pady=12)

        total_frete = 0
        total_peso = 0

        for nota in notas:
            (
                id_nota,
                numero_cte,
                remetente,
                destinatario,
                origem,
                destino,
                valor_frete,
                peso,
                status
            ) = nota

            valor_frete = valor_frete or 0
            peso = peso or 0

            total_frete += valor_frete
            total_peso += peso

            tree.insert("", "end", values=(
                numero_cte,
                remetente,
                destinatario,
                origem,
                destino,
                f"R$ {valor_frete:,.2f}",
                f"{peso:,.2f} kg",
                status
            ))

        resumo = ctk.CTkFrame(janela, fg_color="#ffffff", corner_radius=16)
        resumo.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            resumo,
            text=f"Notas: {len(notas)}",
            font=("Arial", 15, "bold"),
            text_color="#111827"
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            resumo,
            text=f"Peso Total: {total_peso:,.2f} kg",
            font=("Arial", 15, "bold"),
            text_color="#b91c1c"
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            resumo,
            text=f"Frete Total: R$ {total_frete:,.2f}",
            font=("Arial", 15, "bold"),
            text_color="#15803d"
        ).pack(side="right", padx=20, pady=15)

    
