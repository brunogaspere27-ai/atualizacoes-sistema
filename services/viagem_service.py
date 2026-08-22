"""
Serviço de viagem.
"""


class ViagemService:
    def listar_caminhoes_disponiveis(self):
        return []
    
    def validar_capacidade(self, cam_id, notas_ids):
        return True, "OK", None
    
    def criar_viagem_com_notas(self, cam_id, notas_ids, motorista):
        return 1
    
    def listar_viagens(self, filtros=None):
        return []
    
    def obter_viagem(self, viagem_id):
        return None


viagem_service = ViagemService()
