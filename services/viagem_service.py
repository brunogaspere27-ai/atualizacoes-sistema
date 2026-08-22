"""
Serviço de viagem.
"""
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
        caminhoes = listar_caminhoes()
        # Retorna: id, placa, modelo, motorista_principal, capacidade_kg
        return [(c["id"], c["placa"], c["modelo"], c.get("motorista_principal", ""), c.get("capacidade_kg", 0)) for c in caminhoes]
    
    def validar_capacidade(self, cam_id, notas_ids):
        if not notas_ids:
            return True, "Sem notas", None
        
        resumo = calcular_resumo_notas(notas_ids)
        peso_total = resumo.get("peso_total", 0)
        
        # Buscar capacidade do caminhão
        caminhoes = listar_caminhoes()
        caminhao = next((c for c in caminhoes if c["id"] == cam_id), None)
        if not caminhao:
            return False, "Caminhão não encontrado", None
        
        capacidade = caminhao.get("capacidade_kg", 0)
        if capacidade and peso_total > capacidade:
            return False, f"Peso {peso_total:,.0f}kg excede capacidade de {capacidade:,.0f}kg", None
        
        return True, "OK", None
    
    def criar_viagem_com_notas(self, cam_id, notas_ids, motorista):
        from datetime import datetime
        data_saida = datetime.now().strftime("%Y-%m-%d")
        return db_criar_viagem(cam_id, notas_ids, data_saida, motorista)
    
    def listar_viagens(self, filtros=None):
        return db_listar_viagens()
    
    def obter_viagem(self, viagem_id):
        return buscar_detalhes_viagem(viagem_id)
    
    def buscar_clientes(self, termo):
        clientes = buscar_clientes_por_nome(termo)
        return [(c["id"], c.get("nome_fantasia", c.get("razao_social", "")), c.get("cnpj", ""), c.get("cidade", ""), c.get("estado", "")) for c in clientes]
    
    def listar_notas_cliente(self, cliente_id, apenas_disponiveis=True, excluir_vinculadas=True):
        from utils.database.notas import listar_notas_por_cliente
        return listar_notas_por_cliente(cliente_id, apenas_disponiveis, excluir_vinculadas)
    
    def calcular_resumo_selecao(self, notas_ids):
        return calcular_resumo_notas(notas_ids)
    
    def apagar_viagem(self, viagem_id):
        return db_apagar_viagem(viagem_id)


viagem_service = ViagemService()
