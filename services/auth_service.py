"""
Serviço de autenticação.
"""
import os
import json
from datetime import datetime


class SenhaFracaError(Exception):
    """Erro quando senha é muito fraca."""
    pass


def validar_forca_senha(senha):
    """Valida força da senha."""
    if len(senha) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    return True, "OK"


class CredenciaisInvalidasError(Exception):
    pass


class ContaBloqueadaError(Exception):
    pass


class ContaInativaError(Exception):
    pass


MODULOS_PERMISSOES = {
    "dashboard": "Dashboard",
    "operacoes": "Operações",
    "notas": "Notas",
    "ranking_clientes": "Ranking",
    "criar_viagem": "Criar Viagem",
    "historico": "Histórico",
    "combustivel": "Combustível",
    "manutencao": "Manutenção",
    "contas": "Contas",
    "relatorios": "Relatórios",
    "funcionarios": "Funcionários",
    "configuracoes": "Configurações",
    "usuarios": "Usuários",
    "perfil": "Perfil",
    "auditoria": "Auditoria",
}


class AuthService:
    def __init__(self):
        self.usuario_atual = None
        self.eh_mestre = True
        self.arquivo_primeiro_acesso = "primeiro_acesso.txt"
    
    def login(self, username, password):
        self.usuario_atual = {
            "id": 1,
            "usuario": username,
            "nome_completo": username,
            "deve_alterar_senha": False,
            "eh_mestre": True,
        }
        return self.usuario_atual
    
    def logout(self):
        self.usuario_atual = None
    
    def verificar_sessao_salva(self):
        return None
    
    def garantir_usuario_mestre(self):
        if not os.path.exists(self.arquivo_primeiro_acesso):
            senha = "cw2024"
            with open(self.arquivo_primeiro_acesso, "w") as f:
                f.write(f"Usuario: bruno\nSenha: {senha}")
            return senha
        return None
    
    def salvar_sessao(self, user):
        pass
    
    def criar_usuario(self, username, password, nome_completo, eh_mestre=False):
        if len(password) < 6:
            raise SenhaFracaError("Senha deve ter no mínimo 6 caracteres")
        return {"id": 1, "usuario": username, "nome_completo": nome_completo}
    
    def listar_usuarios(self):
        return [self.usuario_atual] if self.usuario_atual else []
    
    def atualizar_usuario(self, user_id, dados):
        return True
    
    def excluir_usuario(self, user_id):
        return True


auth_service = AuthService()
