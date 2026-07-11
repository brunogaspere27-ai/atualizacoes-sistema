import threading                                    # ← adicionar linha 1
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime

from services.notas_service import notas_service
from services.viagem_service import viagem_service
from utils.loading_overlay import LoadingOverlay   # ← adicionar esta linha
from utils.logger import get_logger
from config.settings import settings
from telas.theme import setup_theme, criar_header

logger = get_logger(__name__)


class TelaNotas(ctk.CTkFrame):

    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self.notas_ids = {}
        self.caminhoes_map = {}
        self.notas_marcadas = set()

        criar_header(
            self,
            tag="NOTAS FISCAIS",
            titulo="Notas Importadas",
            subtitulo="Gerenciamento de manifestos, notas fiscais e criação de viagens.",
            cores=self.cores,
        )

        self.resumo = ctk.CTkLabel(
            self,
            text="Selecione um manifesto para visualizar as notas.",
            font=(self.cores["font_family"], 14, "bold"),
            text_color="#374151"
        )
        self.resumo.pack(anchor="w", padx=25, pady=(0, 10))

        self.criar_tabela_manifestos()
        self.criar_barra_viagem()
        self.criar_tabela_notas()

        self.carregar_caminhoes()
        self.carregar_manifestos()


    def importar_manifesto(self):

        caminho = filedialog.askopenfilename(
            title="Selecionar Manifesto TXT",
            filetypes=[
                ("Arquivos TXT", "*.txt"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            resultado = notas_service.importar_manifesto(caminho)

            messagebox.showinfo(
                "Importação concluída",
                f"Arquivo: {resultado['arquivo']}\n\n"
                f"Notas encontradas: {resultado['encontradas']}\n"
                f"Notas salvas: {resultado['salvas']}\n"
                f"Notas duplicadas: {resultado['duplicadas']}"
            )

            self.carregar_manifestos()

        except Exception as erro:
            messagebox.showerror(
                "Erro ao importar manifesto",
                str(erro)
            )

    def apagar_manifesto_selecionado(self):

        selecionado = self.tree_manifestos.focus()

        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione um manifesto para apagar."
            )
            return

        valores = self.tree_manifestos.item(selecionado, "values")

        if not valores:
            return

        manifesto_id = valores[0]
        nome_arquivo = valores[1]

        confirmar = messagebox.askyesno(
            "Apagar manifesto",
            f"Deseja apagar este manifesto?\n\n{nome_arquivo}\n\n"
            "Todas as notas desse manifesto também serão apagadas."
        )

        if not confirmar:
            return

        try:
            ids_manifesto = {nota[0] for nota in notas_service.listar_notas_por_manifesto(manifesto_id)}
            notas_service.apagar_manifesto(manifesto_id)

            messagebox.showinfo(
                "Sucesso",
                "Manifesto apagado com sucesso!"
            )

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.resumo.configure(
                text="Selecione um manifesto para visualizar as notas."
            )

            self.notas_ids = {}
            self.notas_marcadas -= ids_manifesto
            self.atualizar_selecao()
            self.carregar_manifestos()

        except Exception as erro:
            messagebox.showerror(
                "Erro ao apagar manifesto",
                str(erro)
            )        

    def criar_tabela_manifestos(self):

        frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        frame.pack(fill="x", padx=10, pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="📁 MANIFESTOS / ARQUIVOS TXT",
            font=(self.cores["font_family"], 16, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=15, pady=(12, 6))

        linha_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        linha_botoes.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkButton(
            linha_botoes,
            text="Importar Manifesto TXT",
            height=38,
            fg_color="#15803d",
            hover_color="#166534",
            font=(self.cores["font_family"], 13, "bold"),
            command=self.importar_manifesto
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            linha_botoes,
            text="Apagar",
            height=38,
            fg_color="#b91c1c",
            hover_color="#7f1d1d",
            font=(self.cores["font_family"], 13, "bold"),
            command=self.apagar_manifesto_selecionado
        ).pack(side="left")

        linha_filtros = ctk.CTkFrame(frame, fg_color="transparent")
        linha_filtros.pack(anchor="w", padx=15, pady=(0, 10))

        self.combo_periodo_manifestos = ctk.CTkComboBox(
            linha_filtros,
            width=130,
            values=["Geral", "Mês", "Ano"],
            command=lambda _: self.atualizar_filtro_manifestos()
        )
        self.combo_periodo_manifestos.pack(side="left", padx=(0, 8))
        self.combo_periodo_manifestos.set("Geral")

        self.combo_mes_manifestos = ctk.CTkComboBox(
            linha_filtros,
            width=90,
            values=[f"{i:02d}" for i in range(1, 13)],
            command=lambda _: self.atualizar_filtro_manifestos()
        )
        self.combo_mes_manifestos.pack(side="left", padx=(0, 8))
        self.combo_mes_manifestos.set(datetime.now().strftime("%m"))

        ano_atual = datetime.now().year
        self.combo_ano_manifestos = ctk.CTkComboBox(
            linha_filtros,
            width=100,
            values=[str(ano) for ano in range(ano_atual - 5, ano_atual + 2)],
            command=lambda _: self.atualizar_filtro_manifestos()
        )
        self.combo_ano_manifestos.pack(side="left", padx=(0, 8))
        self.combo_ano_manifestos.set(str(ano_atual))

        colunas = ("id", "arquivo", "data", "notas", "valor_notas", "frete", "peso")

        self.tree_manifestos = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=5
        )

        titulos = {
            "id": "ID",
            "arquivo": "Arquivo TXT",
            "data": "Importado em",
            "valor_notas": "Valor Notas",
            "notas": "Notas",
            "frete": "Frete Total",
            "peso": "Peso Total"
        }

        larguras = {
            "id": 50,
            "arquivo": 330,
            "data": 160,
            "valor_notas": 150,
            "notas": 80,
            "frete": 140,
            "peso": 140
        }

        for col in colunas:
            self.tree_manifestos.heading(col, text=titulos[col])
            self.tree_manifestos.column(col, width=larguras[col], anchor="w")

        self.tree_manifestos.column("id", anchor="center")
        self.tree_manifestos.column("valor_notas", anchor="e")
        self.tree_manifestos.column("notas", anchor="center")
        self.tree_manifestos.column("frete", anchor="e")
        self.tree_manifestos.column("peso", anchor="e")

        self.tree_manifestos.pack(fill="x", padx=12, pady=(0, 12))
        self.tree_manifestos.bind("<<TreeviewSelect>>", self.selecionar_manifesto)

    def criar_barra_viagem(self):

        frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        frame.pack(fill="x", padx=10, pady=(0, 12))

        ctk.CTkLabel(
            frame,
            text="🚚 CRIAR VIAGEM COM NOTAS SELECIONADAS",
            font=(self.cores["font_family"], 15, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=15, pady=(12, 8))

        linha = ctk.CTkFrame(frame, fg_color="transparent")
        linha.pack(fill="x", padx=15, pady=(0, 12))

        self.combo_caminhoes = ctk.CTkComboBox(
            linha,
            width=330,
            values=["Nenhum caminhão cadastrado"]
        )
        self.combo_caminhoes.pack(side="left", padx=(0, 10))

        self.entrada_motorista_viagem = ctk.CTkEntry(
            linha,
            width=210,
            placeholder_text="Motorista da viagem"
        )
        self.entrada_motorista_viagem.pack(side="left", padx=5)

        ctk.CTkButton(
            linha,
            text="+ Novo Veículo",
            width=140,
            fg_color="#374151",
            hover_color="#111827",
            command=self.abrir_novo_veiculo
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            linha,
            text="✅ Criar Viagem",
            width=150,
            fg_color="#15803d",
            hover_color="#166534",
            command=self.criar_viagem_selecionadas
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            linha,
            text="🗑 Apagar Viagem",
            width=150,
            fg_color="#b91c1c",
            hover_color="#7f1d1d",
            command=self.apagar_viagem_selecionada
        ).pack(side="left", padx=5)

        self.label_selecao = ctk.CTkLabel(
            linha,
            text="Notas selecionadas: 0",
            font=(self.cores["font_family"], 13, "bold"),
            text_color="#374151"
        )
        self.label_selecao.pack(side="left", padx=18)

    def criar_tabela_notas(self):

        frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text="📄 NOTAS DO MANIFESTO SELECIONADO",
            font=(self.cores["font_family"], 16, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=15, pady=(12, 6))

        tabela_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        tabela_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        colunas = (
            "selecionar", "cte", "remetente", "cliente", "origem",
            "destino", "frete", "peso", "status"
        )

        self.tree = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            height=16,
            selectmode="browse"
        )

        titulos = {
            "selecionar": "Sel.",
            "cte": "CT-e / Chave",
            "remetente": "Remetente",
            "cliente": "Cliente / Destinatário",
            "origem": "Origem",
            "destino": "Destino",
            "frete": "Frete",
            "peso": "Peso",
            "status": "Status"
        }

        larguras = {
            "selecionar": 55,
            "cte": 180,
            "remetente": 280,
            "cliente": 300,
            "origem": 160,
            "destino": 180,
            "frete": 130,
            "peso": 120,
            "status": 120
        }

        for col in colunas:
            self.tree.heading(col, text=titulos[col])
            self.tree.column(col, width=larguras[col], anchor="w")

        self.tree.column("selecionar", anchor="center")
        self.tree.column("frete", anchor="e")
        self.tree.column("peso", anchor="e")
        self.tree.column("status", anchor="center")

        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tabela_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tabela_frame.grid_columnconfigure(0, weight=1)
        tabela_frame.grid_rowconfigure(0, weight=1)

        self.tree.bind("<ButtonRelease-1>", self.clicar_na_nota)

    def carregar_caminhoes(self):

        self.caminhoes_map = {}
        caminhoes = viagem_service.listar_caminhoes_disponiveis()
        valores = []

        for caminhao in caminhoes:
            caminhao_id, placa, modelo, motorista, capacidade = caminhao
            texto = f"{modelo} | {placa} | {capacidade:,.0f} kg"
            self.caminhoes_map[texto] = caminhao_id
            valores.append(texto)

        if not valores:
            valores = ["Nenhum caminhão cadastrado"]

        self.combo_caminhoes.configure(values=valores)
        self.combo_caminhoes.set(valores[0])

    def obter_filtro_manifestos(self):

        tipo_periodo = self.combo_periodo_manifestos.get()
        mes = self.combo_mes_manifestos.get()
        ano = self.combo_ano_manifestos.get()

        if tipo_periodo == "Geral":
            return "Geral", None, None

        if tipo_periodo == "Mês":
            return "Mês", mes, ano

        if tipo_periodo == "Ano":
            return "Ano", None, ano

        return "Geral", None, None

    def atualizar_filtro_manifestos(self):
        try:
            self.carregar_manifestos()
        except Exception as erro:
            logger.error(f"Erro ao atualizar filtro de manifestos: {erro}")

    def carregar_manifestos(self):

        for item in self.tree_manifestos.get_children():
            self.tree_manifestos.delete(item)

        tipo_periodo, mes, ano = self.obter_filtro_manifestos()
        manifestos = notas_service.listar_manifestos(tipo_periodo, mes, ano)

        for manifesto in manifestos:
            manifesto_id, nome_arquivo, data_importacao, total_notas, valor_notas, frete_total, peso_total = manifesto

            self.tree_manifestos.insert("", "end", values=(
                manifesto_id,
                f"📁 {nome_arquivo}",
                data_importacao,
                total_notas,
                f"R$ {valor_notas:,.2f}",
                f"R$ {frete_total:,.2f}",
                f"{peso_total:,.2f} kg"
            ))

        if manifestos:
            primeiro = self.tree_manifestos.get_children()[0]
            self.tree_manifestos.selection_set(primeiro)
            self.tree_manifestos.focus(primeiro)
            self.selecionar_manifesto()

        else:
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.resumo.configure(
                text="Nenhum manifesto encontrado para o período selecionado."
            )

            self.notas_ids = {}
            self.atualizar_selecao()

    def selecionar_manifesto(self, event=None):

        selecionado = self.tree_manifestos.focus()

        if not selecionado:
            return

        valores = self.tree_manifestos.item(selecionado, "values")

        if not valores:
            return

        manifesto_id = valores[0]
        nome_arquivo = valores[1]

        self.carregar_notas_manifesto(manifesto_id, nome_arquivo)

    def carregar_notas_manifesto(self, manifesto_id, nome_arquivo):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.notas_ids = {}

        dados = notas_service.listar_notas_por_manifesto(manifesto_id)

        total_frete = 0
        total_valor_notas = 0
        total_peso = 0

        for linha in dados:
            (
                id_nota,
                chave_nfe,
                numero_cte,
                remetente,
                destinatario,
                origem,
                destino,
                valor_mercadoria,
                frete,
                peso,
                status
            ) = linha

            frete = frete or 0
            valor_mercadoria = valor_mercadoria or 0
            total_valor_notas += valor_mercadoria
            peso = peso or 0

            total_frete += frete
            total_peso += peso

            cte = numero_cte if numero_cte else chave_nfe

            if status != "Disponível":
                marcador = "—"
            elif id_nota in self.notas_marcadas:
                marcador = "☑"
            else:
                marcador = "☐"

            item_id = self.tree.insert("", "end", values=(
                marcador,
                cte,
                remetente,
                destinatario,
                origem,
                destino,
                f"R$ {frete:,.2f}",
                f"{peso:,.2f} kg",
                status
            ))

            self.notas_ids[item_id] = id_nota

        self.resumo.configure(
                text=f"{nome_arquivo}   |   Notas: {len(dados)}   |   Valor Notas: R$ {total_valor_notas:,.2f}   |   Frete Total: R$ {total_frete:,.2f}   |   Peso Total: {total_peso:,.2f} kg"
        )

        self.atualizar_selecao()

    def clicar_na_nota(self, event=None):

        item = self.tree.identify_row(event.y)

        if not item:
            return

        valores = list(self.tree.item(item, "values"))

        if not valores:
            return

        status = valores[-1]
        id_nota = self.notas_ids.get(item)

        if not id_nota:
            return

        if status != "Disponível":
            messagebox.showwarning(
                "Atenção",
                f"Essa nota não está disponível (status: {status}).\n"
                "Notas em viagem ou entregues não podem ser selecionadas."
            )
            return

        if id_nota in self.notas_marcadas:
            self.notas_marcadas.remove(id_nota)
            valores[0] = "☐"
        else:
            self.notas_marcadas.add(id_nota)
            valores[0] = "☑"

        self.tree.item(item, values=valores)
        self.atualizar_selecao()

    def atualizar_selecao(self):

        self.label_selecao.configure(
            text=f"Notas selecionadas: {len(self.notas_marcadas)}"
        )

    def criar_viagem_selecionadas(self):

        if not self.notas_marcadas:
            messagebox.showwarning("Atenção", "Selecione pelo menos uma nota.")
            return

        caminhao_texto = self.combo_caminhoes.get()
        caminhao_id = self.caminhoes_map.get(caminhao_texto)

        if not caminhao_id or "Nenhum" in caminhao_texto:
            messagebox.showwarning("Atenção", "Selecione um caminhão válido.")
            return

        motorista = self.entrada_motorista_viagem.get().strip()

        if not motorista:
            messagebox.showwarning("Atenção", "Informe o motorista da viagem.")
            return

        notas_ids = list(self.notas_marcadas)

        valido, mensagem, _ = viagem_service.validar_capacidade(caminhao_id, notas_ids)
        if not valido:
            if not messagebox.askyesno(
                "Aviso de Capacidade",
                f"{mensagem}\n\nDeseja continuar mesmo assim?"
            ):
                return

        try:
            viagem_id = viagem_service.criar_viagem_com_notas(
                caminhao_id,
                notas_ids,
                motorista
            )
        except Exception as erro:
            messagebox.showerror("Erro ao criar viagem", str(erro))
            self.selecionar_manifesto()
            return

        messagebox.showinfo(
            "Viagem criada",
            f"Viagem #{viagem_id} criada com sucesso!\n"
            f"{len(notas_ids)} nota(s) adicionada(s)."
        )

        self.entrada_motorista_viagem.delete(0, "end")
        self.notas_marcadas.clear()
        self.selecionar_manifesto()

    def apagar_viagem_selecionada(self):

        viagem_id = simpledialog.askinteger(
            "Apagar Viagem",
            "Informe o número da viagem que deseja apagar:",
            minvalue=1,
            parent=self
        )

        if not viagem_id:
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja apagar a viagem #{viagem_id}?\n\n"
            "As notas dessa viagem voltarão a ficar disponíveis "
            "para serem adicionadas em outra viagem."
        )

        if not confirmar:
            return

        try:
            total_notas = notas_service.apagar_viagem(viagem_id)

            messagebox.showinfo(
                "Viagem apagada",
                f"Viagem #{viagem_id} apagada com sucesso!\n"
                f"{total_notas} nota(s) liberada(s)."
            )

            self.selecionar_manifesto()

        except Exception as erro:
            messagebox.showerror(
                "Erro ao apagar viagem",
                str(erro)
            )

    def abrir_novo_veiculo(self):

        janela = ctk.CTkToplevel(self)
        janela.title("Cadastrar Novo Veículo")
        janela.geometry("420x420")
        janela.resizable(False, False)
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="🚚 Novo Veículo",
            font=(self.cores["font_family"], 22, "bold")
        ).pack(pady=(20, 10))

        entrada_placa = ctk.CTkEntry(janela, placeholder_text="Placa ou nome")
        entrada_placa.pack(fill="x", padx=25, pady=8)

        entrada_modelo = ctk.CTkEntry(janela, placeholder_text="Modelo")
        entrada_modelo.pack(fill="x", padx=25, pady=8)

        entrada_motorista = ctk.CTkEntry(janela, placeholder_text="Motorista padrão")
        entrada_motorista.pack(fill="x", padx=25, pady=8)

        entrada_capacidade = ctk.CTkEntry(janela, placeholder_text="Capacidade em kg")
        entrada_capacidade.pack(fill="x", padx=25, pady=8)

        entrada_media = ctk.CTkEntry(janela, placeholder_text="Média km/L")
        entrada_media.pack(fill="x", padx=25, pady=8)

        def salvar():

            try:
                placa = entrada_placa.get().strip()
                modelo = entrada_modelo.get().strip()
                motorista = entrada_motorista.get().strip()
                capacidade = float(entrada_capacidade.get().replace(",", "."))
                media = float(entrada_media.get().replace(",", "."))

                if not placa or not modelo:
                    messagebox.showwarning("Atenção", "Informe placa/nome e modelo.")
                    return

                notas_service.cadastrar_caminhao(placa, modelo, motorista, capacidade, media)

                messagebox.showinfo("Sucesso", "Veículo cadastrado com sucesso!")

                janela.destroy()
                self.carregar_caminhoes()

            except Exception as erro:
                logger.error(f"Erro ao cadastrar veículo: {erro}")
                messagebox.showerror("Erro", "Verifique os dados informados.")

        ctk.CTkButton(
            janela,
            text="Salvar Veículo",
            fg_color="#15803d",
            hover_color="#166534",
            command=salvar
        ).pack(fill="x", padx=25, pady=20)
