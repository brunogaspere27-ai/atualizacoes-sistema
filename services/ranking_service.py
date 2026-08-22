"""
Serviço de ranking.
"""


class RankingService:
    def carregar_ranking(self, tipo="faturamento", mes=None, ano=None):
        return []
    
    def exportar_ranking(self, tipo, formato, caminho):
        return True


ranking_service = RankingService()
