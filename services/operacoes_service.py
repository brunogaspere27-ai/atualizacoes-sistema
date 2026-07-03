from __future__ import annotations

from utils.database import criar_operacao_sp, listar_operacoes_sp


class OperacoesService:
    def criar_operacao(self, dados):
        return criar_operacao_sp(dados)

    def listar_operacoes(self):
        return listar_operacoes_sp()


operacoes_service = OperacoesService()
