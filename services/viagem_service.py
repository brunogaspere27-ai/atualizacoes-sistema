"""
Servico de viagem.
"""
from datetime import datetime
from utils.database.viagens import (
    criar_viagem as db_criar_viagem,
    listar_viagens as db_listar_viagens,
    listar_notas_da_viagem,
    buscar_detalhes_viagem,
    finalizar_viagem,
    apagar_viagem as db_apagar_viagem,
)
from utils.database.notas import calcular_resumo_notas
from utils.database.caminhoes import listar_caminhoes
from utils.database.clientes import buscar_clientes_por_nome


class ViagemService:
    def listar_caminhoes_disponiveis(self):
        """
        Retorna lista de tuplas:
        [(id, placa, modelo, motorista, capacidade_kg), ...]
        """
        caminhoes = listar_caminhoes()
        resultado = []
        for c in caminhoes:
            # O banco retorna tupla: (id, placa, modelo, motorista, capacidade_kg)
            if isinstance(c, (list, tuple)) and len(c) >= 5:
                resultado.append((
                    c[0],           # id
                    c[1] or "",     # placa
                    c[2] or "",     # modelo
                    c[3] or "",     # motorista
                    c[4] or 0,      # capacidade_kg
                ))
        return resultado

    def validar_capacidade(self, cam_id, notas_ids):
        if not notas_ids:
            return True, "Sem notas", None

        resumo = calcular_resumo_notas(notas_ids)
        peso_total = resumo.get("peso_total", 0)

        caminhoes = self.listar_caminhoes_disponiveis()
        caminhao = next((c for c in caminhoes if c[0] == cam_id), None)
        if not caminhao:
            return False, "Caminhão não encontrado", None

        capacidade = caminhao[4]
        if capacidade and peso_total > capacidade:
            return False, f"Peso {peso_total:,.0f}kg excede capacidade de {capacidade:,.0f}kg", None

        return True, "OK", None

    def criar_viagem_com_notas(self, cam_id, notas_ids, motorista):
        data_saida = datetime.now().strftime("%Y-%m-%d")
        return db_criar_viagem(cam_id, notas_ids, data_saida, motorista)

    def listar_viagens(self, filtros=None):
        return db_listar_viagens()

    def obter_viagem(self, viagem_id):
        return buscar_detalhes_viagem(viagem_id)

    def buscar_clientes(self, termo):
        """
        Retorna lista de tuplas:
        [(id, nome, cnpj, cidade, uf), ...]
        """
        clientes = buscar_clientes_por_nome(termo)
        resultado = []
        for c in clientes:
            if isinstance(c, dict):
                resultado.append((
                    c.get("id"),
                    c.get("nome", ""),
                    c.get("cnpj", ""),
                    c.get("cidade", ""),
                    c.get("uf", ""),
                ))
            elif isinstance(c, (list, tuple)) and len(c) >= 5:
                resultado.append((c[0], c[1] or "", c[2] or "", c[3] or "", c[4] or ""))
        return resultado

    def listar_notas_cliente(self, cliente_id, apenas_disponiveis=True, excluir_vinculadas=True):
        from utils.database.notas import listar_notas_por_cliente
        return listar_notas_por_cliente(cliente_id, apenas_disponiveis, excluir_vinculadas)

    def calcular_resumo_selecao(self, notas_ids):
        return calcular_resumo_notas(notas_ids)

    def apagar_viagem(self, viagem_id):
        return db_apagar_viagem(viagem_id)


viagem_service = ViagemService()
