from __future__ import annotations

from utils.database import gerar_ranking_clientes_v6


class RankingService:
    def carregar_ranking(self, tipo_periodo: str, mes: str, ano: str):
        return gerar_ranking_clientes_v6(tipo_periodo, mes, ano)


ranking_service = RankingService()
