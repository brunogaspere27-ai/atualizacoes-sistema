"""
Serviço de funcionários.
"""


class FuncionarioService:
    def listar_funcionarios(self):
        return []
    
    def criar_funcionario(self, dados):
        return 1
    
    def atualizar_funcionario(self, func_id, dados):
        return True
    
    def excluir_funcionario(self, func_id):
        return True


funcionario_service = FuncionarioService()
