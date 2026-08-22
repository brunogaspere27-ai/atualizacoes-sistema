"""
Serviço de notas/manifestos.
"""


class NotasService:
    def listar_manifestos(self, tipo=None, mes=None, ano=None):
        return []
    
    def listar_notas_por_manifesto(self, manifesto_id):
        return []
    
    def importar_manifesto(self, caminho):
        return {"arquivo": caminho, "encontradas": 0, "salvas": 0, "duplicadas": 0}
    
    def apagar_manifesto(self, manifesto_id):
        return True
    
    def apagar_viagem(self, viagem_id):
        return 0
    
    def cadastrar_caminhao(self, placa, modelo, motorista, capacidade, media):
        pass


notas_service = NotasService()
