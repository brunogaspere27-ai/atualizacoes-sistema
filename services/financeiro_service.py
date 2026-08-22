"""
Serviço financeiro.
"""
from utils.logger import get_logger

logger = get_logger(__name__)


class FinanceiroService:
    def listar_contas(self, tipo=None, status=None, mes=None, ano=None, pagina=1, por_pagina=50):
        return []
    
    def criar_conta(self, dados):
        return 1
    
    def atualizar_conta(self, conta_id, dados):
        return True
    
    def excluir_conta(self, conta_id):
        return True
    
    def resumo_financeiro(self, mes=None, ano=None):
        return {"receitas": 0.0, "despesas": 0.0, "saldo": 0.0}


financeiro_service = FinanceiroService()
