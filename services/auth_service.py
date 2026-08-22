"""
Serviço de autenticação.
"""
import os
import json
from datetime import datetime


class CredenciaisInvalidasError(Exception):
    pass


class ContaBloqueadaError(Exception):
    pass


class ContaInativaError(Exception):
    pass


class AuthService:
    """Gerencia autenticação."""
    
    def __init__(self):
        self.usuario_atual = None
        self.eh_mestre = True
        self.arquivo_primeiro_acesso = "primeiro_acesso.txt"
    
    def login(self, username, password):
        # Mock - aceita qualquer login
        self.usuario_atual = {
            "id": 1,
            "usuario": username,
            "nome_completo": username,
            "deve_alterar_senha": False
        }
        return self.usuario_atual
    
    def logout(self):
        self.usuario_atual = None
    
    def verificar_sessao_salva(self):
        return None
    
    def garantir_usuario_mestre(self):
        """Cria usuário mestre se não existir."""
        if not os.path.exists(self.arquivo_primeiro_acesso):
            senha = "cw2024"
            with open(self.arquivo_primeiro_acesso, "w") as f:
                f.write(f"Usuario: bruno\nSenha: {senha}")
            return senha
        return None
    
    def salvar_sessao(self, user):
        pass


auth_service = AuthService()
