from __future__ import annotations

from utils.importador_txt import importar_manifesto_txt
from utils.database import (
    listar_manifestos,
    listar_notas_por_manifesto,
    listar_caminhoes,
    criar_viagem,
    apagar_viagem,
    cadastrar_caminhao,
    apagar_manifesto,
)


class NotasService:
    def importar_manifesto(self, caminho: str):
        return importar_manifesto_txt(caminho)

    def listar_manifestos(self, tipo_periodo: str, mes: str | None, ano: str | None):
        return listar_manifestos(tipo_periodo, mes, ano)

    def listar_notas_por_manifesto(self, manifesto_id):
        return listar_notas_por_manifesto(manifesto_id)

    def listar_caminhoes(self):
        return listar_caminhoes()

    def criar_viagem(self, caminhao_id, notas_ids, data_saida, motorista):
        return criar_viagem(caminhao_id, notas_ids, data_saida, motorista)

    def apagar_viagem(self, viagem_id):
        return apagar_viagem(viagem_id)

    def cadastrar_caminhao(self, placa, modelo, motorista, capacidade_kg, media_km_l):
        return cadastrar_caminhao(placa, modelo, motorista, capacidade_kg, media_km_l)

    def apagar_manifesto(self, manifesto_id):
        return apagar_manifesto(manifesto_id)


notas_service = NotasService()
