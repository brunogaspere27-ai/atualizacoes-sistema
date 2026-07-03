from __future__ import annotations

from utils.database import (
    listar_viagens,
    listar_notas_da_viagem,
    finalizar_viagem,
    buscar_detalhes_viagem,
)


class HistoricoService:
    def listar_viagens(self):
        return listar_viagens()

    def listar_notas_da_viagem(self, viagem_id):
        return listar_notas_da_viagem(viagem_id)

    def finalizar_viagem(self, viagem_id, data_retorno):
        return finalizar_viagem(viagem_id, data_retorno)

    def buscar_detalhes_viagem(self, viagem_id):
        return buscar_detalhes_viagem(viagem_id)


historico_service = HistoricoService()
