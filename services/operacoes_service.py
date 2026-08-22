"""
Serviço de operações.
"""


class OperacoesService:
    def criar_operacao(self, dados):
        print(f"[OPERACAO] Criada: {dados.get('nome_caminhao')}")
    
    def listar_operacoes(self):
        return []


operacoes_service = OperacoesService()
