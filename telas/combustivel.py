import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.database import criar_banco
from services.frota_service import frota_service


class TelaCombustivel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F8")

        criar_banco()
        self.criar_layout()
        self.carregar_abastecimentos()

    def criar_layout(self):
        topo = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=24)
        topo.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            topo,
            text="CONTROLE DE COMBUSTÍVEL",
            font=("Arial", 13, "bold"),
            text_color="#93c5fd"
        ).pack(anchor="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Abastecimentos",
            font=("Arial", 34, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=24)

        ctk.CTkLabel(
            topo,
            text="Controle de consumo, média km/L, custo por km e gasto por veículo.",
            font=("Arial", 14),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=24, pady=(0, 18))

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        filtros.pack(fill="x", padx=25, pady=10)

        self.tipo_periodo = ctk.CTkComboBox(
            filtros,
            values=["Geral", "Mês", "Ano"],
            width=120,
            command=lambda e: self.carregar_abastecimentos()
        )
        self.tipo_periodo.set("Geral")
        self.tipo_periodo.pack(side="left", padx=12, pady=12)

        self.mes = ctk.CTkComboBox(
            filtros,
            values=["01", "02", "03", "04", "05", "06",
                    "07", "08", "09", "10", "11", "12"],
            width=90,
            command=lambda e: self.carregar_abastecimentos()
        )
        self.mes.set(datetime.now().strftime("%m"))
        self.mes.pack(side="left", padx=8)

        self.ano = ctk.CTkEntry(filtros, width=90, placeholder_text="Ano")
        self.ano.insert(0, datetime.now().strftime("%Y"))
        self.ano.pack(side="left", padx=8)
        self.ano.bind("<KeyRelease>", lambda e: self.carregar_abastecimentos())

        self.busca = ctk.CTkEntry(
            filtros,
            width=240,
            placeholder_text="Buscar veículo, motorista ou posto..."
        )
        self.busca.pack(side="left", padx=8)
        self.busca.bind("<KeyRelease>", lambda e: self.carregar_abastecimentos())

        ctk.CTkButton(
            filtros,
            text="+ Novo Abastecimento",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.abrir_modal_abastecimento
        ).pack(side="right", padx=12)

        self.frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resumo.pack(fill="x", padx=25, pady=(5, 0))

        self.card_qtd = self.criar_card_resumo("Abastecimentos", "0")
        self.card_litros = self.criar_card_resumo("Litros", "0 L")
        self.card_gasto = self.criar_card_resumo("Gasto total", "R$ 0,00")
        self.card_media = self.criar_card_resumo("Média geral", "0 km/L")

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=25, pady=12)

        colunas = (
            "id", "data", "veiculo", "motorista", "km", "litros",
            "valor_litro", "total", "media", "custo_km", "posto", "status"
        )

        self.tabela = ttk.Treeview(card, columns=colunas, show="headings", height=17)

        titulos = {
            "id": "ID",
            "data": "Data",
            "veiculo": "Veículo",
            "motorista": "Motorista",
            "km": "KM",
            "litros": "Litros",
            "valor_litro": "R$/Litro",
            "total": "Total",
            "media": "Média",
            "custo_km": "Custo/KM",
            "posto": "Posto",
            "status": "Status"
        }

        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, anchor="center", width=105)

        self.tabela.column("id", width=45)
        self.tabela.column("veiculo", width=170)
        self.tabela.column("motorista", width=150)
        self.tabela.column("posto", width=140)

        self.tabela.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela.bind("<Double-1>", self.editar_abastecimento)

        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            rodape,
            text="Excluir",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.excluir_abastecimento
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Atualizar",
            fg_color="#111827",
            hover_color="#374151",
            command=self.carregar_abastecimentos
        ).pack(side="right", padx=5)

    def criar_card_resumo(self, titulo, valor):
        card = ctk.CTkFrame(self.frame_resumo, fg_color="white", corner_radius=16)
        card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 12),
            text_color="#6B7280"
        ).pack(pady=(10, 0))

        label = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 20, "bold"),
            text_color="#111827"
        )
        label.pack(pady=(2, 10))

        return label

    def abrir_modal_abastecimento(self, dados=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Abastecimento")
        janela.geometry("560x700")
        janela.grab_set()

        abastecimento_id = dados[0] if dados else None

        ctk.CTkLabel(
            janela,
            text="Cadastro de Abastecimento",
            font=("Arial", 24, "bold")
        ).pack(pady=(20, 10))

        frame = ctk.CTkFrame(janela, fg_color="white", corner_radius=18)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        veiculos = self.buscar_veiculos()

        data = self.criar_campo(frame, "Data")
        data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ctk.CTkLabel(
            frame,
            text="Veículo",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))

        linha_veiculo = ctk.CTkFrame(frame, fg_color="transparent")
        linha_veiculo.pack(fill="x", padx=20, pady=(0, 8))

        veiculo = ctk.CTkComboBox(
            linha_veiculo,
            values=veiculos,
            height=40
        )
        veiculo.pack(side="left", fill="x", expand=True)

        def adicionar_veiculo():
            novo = ctk.CTkInputDialog(
                text="Digite o nome do novo veículo:",
                title="Novo veículo"
            ).get_input()

            if novo and novo.strip():
                novo = novo.strip()

                if novo not in veiculos:
                    veiculos.append(novo)

                veiculo.configure(values=veiculos)
                veiculo.set(novo)

        ctk.CTkButton(
            linha_veiculo,
            text="+",
            width=42,
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=adicionar_veiculo
        ).pack(side="right", padx=(8, 0))

        if veiculos:
            veiculo.set(veiculos[0])

        motorista = self.criar_campo(frame, "Motorista")
        km_atual = self.criar_campo(frame, "KM atual")
        litros = self.criar_campo(frame, "Litros")
        valor_litro = self.criar_campo(frame, "Valor por litro")
        posto = self.criar_campo(frame, "Posto")
        observacao = self.criar_campo(frame, "Observação")

        if dados:
            data.delete(0, "end")
            data.insert(0, dados[1] or "")
            veiculo.set(dados[2] or "")
            motorista.insert(0, dados[3] or "")
            km_atual.insert(0, str(dados[4] or "").replace(".", ","))
            litros.insert(0, str(dados[5] or "").replace(".", ","))
            valor_litro.insert(0, str(dados[6] or "").replace(".", ","))
            posto.insert(0, dados[10] or "")
            observacao.insert(0, dados[11] or "")

        label_total = ctk.CTkLabel(
            frame,
            text="",
            font=("Arial", 17, "bold"),
            text_color="#111827"
        )
        label_total.pack(pady=10)

        def atualizar_previa(event=None):
            km = self.numero(km_atual.get())
            lts = self.numero(litros.get())
            vl = self.numero(valor_litro.get())
            total = lts * vl

            media, custo_km = frota_service.calcular_media_e_custo(
                veiculo.get(),
                km,
                lts,
                total,
                abastecimento_id
            )

            label_total.configure(
                text=(
                    f"Total: {self.moeda(total)}\n"
                    f"Média: {self.formatar_numero(media)} km/L  •  "
                    f"Custo/KM: {self.moeda(custo_km)}"
                )
            )

        for campo in [km_atual, litros, valor_litro]:
            campo.bind("<KeyRelease>", atualizar_previa)

        veiculo.configure(command=lambda e: atualizar_previa())
        atualizar_previa()

        def salvar():
            km = self.numero(km_atual.get())
            lts = self.numero(litros.get())
            vl = self.numero(valor_litro.get())
            total = lts * vl

            if not data.get().strip():
                messagebox.showwarning("Atenção", "Informe a data.")
                return

            if not veiculo.get().strip():
                messagebox.showwarning("Atenção", "Informe o veículo.")
                return

            if km <= 0 or lts <= 0 or vl <= 0:
                messagebox.showwarning("Atenção", "Informe KM, litros e valor por litro.")
                return

            media, custo_km = frota_service.calcular_media_e_custo(
                veiculo.get(),
                km,
                lts,
                total,
                abastecimento_id
            )

            valores = (
                data.get().strip(),
                veiculo.get().strip(),
                motorista.get().strip(),
                km,
                lts,
                vl,
                total,
                media,
                custo_km,
                posto.get().strip(),
                observacao.get().strip()
            )

            frota_service.salvar_abastecimento(abastecimento_id, valores)

            janela.destroy()
            self.carregar_abastecimentos()
            messagebox.showinfo("Sucesso", "Abastecimento salvo com sucesso!")

        ctk.CTkButton(
            frame,
            text="Salvar Abastecimento",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=42,
            command=salvar
        ).pack(fill="x", padx=20, pady=18)

    def criar_campo(self, frame, label):
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))

        campo = ctk.CTkEntry(frame, height=40)
        campo.pack(fill="x", padx=20, pady=(0, 8))

        return campo

    def carregar_abastecimentos(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        tipo = self.tipo_periodo.get()
        mes = self.mes.get()
        ano = self.ano.get().strip()
        busca = self.busca.get().strip()

        dados = frota_service.listar_abastecimentos(tipo, mes, ano, busca)

        total_litros = 0
        total_gasto = 0
        medias = []

        for linha in dados:
            total_litros += float(linha[5] or 0)
            total_gasto += float(linha[7] or 0)

            if float(linha[8] or 0) > 0:
                medias.append(float(linha[8] or 0))

            status = self.status_media(linha[8])

            self.tabela.insert("", "end", values=(
                linha[0],
                linha[1],
                linha[2] or "",
                linha[3] or "",
                self.formatar_numero(linha[4]),
                f"{self.formatar_numero(linha[5])} L",
                self.moeda(linha[6]),
                self.moeda(linha[7]),
                f"{self.formatar_numero(linha[8])} km/L" if linha[8] else "-",
                self.moeda(linha[9]),
                linha[10] or "",
                status
            ))

        media_geral = sum(medias) / len(medias) if medias else 0

        self.card_qtd.configure(text=str(len(dados)))
        self.card_litros.configure(text=f"{self.formatar_numero(total_litros)} L")
        self.card_gasto.configure(text=self.moeda(total_gasto))
        self.card_media.configure(text=f"{self.formatar_numero(media_geral)} km/L")

    def editar_abastecimento(self, event=None):
        selecionado = self.tabela.selection()

        if not selecionado:
            return

        abastecimento_id = self.tabela.item(selecionado[0], "values")[0]

        dados = frota_service.obter_abastecimento(abastecimento_id)

        if dados:
            self.abrir_modal_abastecimento(dados)

    def excluir_abastecimento(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um abastecimento.")
            return

        valores = self.tabela.item(selecionado[0], "values")
        abastecimento_id = valores[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "Deseja excluir este abastecimento?"
        )

        if not confirmar:
            return

        frota_service.excluir_abastecimento(abastecimento_id)

        self.carregar_abastecimentos()

    def buscar_veiculos(self):
        return frota_service.listar_veiculos_disponiveis("abastecimentos")

    def status_media(self, media):
        media = float(media or 0)

        if media <= 0:
            return "1º registro"

        if media < 5:
            return "⚠ Baixa"

        if media > 14:
            return "⚠ Conferir"

        return "✅ OK"

    def numero(self, valor):
        if not valor:
            return 0.0

        valor = str(valor).replace("R$", "").replace(" ", "").strip()

        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")

        try:
            return float(valor)
        except:
            return 0.0

    def moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_numero(self, valor):
        valor = float(valor or 0)

        if valor.is_integer():
            return str(int(valor))

        return f"{valor:.2f}".replace(".", ",")
