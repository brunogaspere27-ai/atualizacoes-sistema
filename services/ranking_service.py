from __future__ import annotations

from utils.cache import runtime_cache
from utils.database import gerar_ranking_clientes_v6


class RankingService:
    def carregar_ranking(self, tipo_periodo: str, mes: str, ano: str):
        cache_key = (tipo_periodo, mes, ano)
        return runtime_cache.get_or_set(
            "ranking_clientes",
            cache_key,
            lambda: gerar_ranking_clientes_v6(tipo_periodo, mes, ano),
            ttl_seconds=15,
        )


ranking_service = RankingService()
