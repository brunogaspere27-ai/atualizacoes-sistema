"""
Serviço de auditoria.
"""

ACAO_LOGOUT = "LOGOUT"
ACAO_LOGIN = "LOGIN"
ACAO_LOGIN_FALHOU = "LOGIN_FALHOU"


class AuditoriaService:
    def registrar(self, acao, modulo, usuario, **kwargs):
        print(f"[AUDITORIA] {acao} | {modulo} | {usuario}")
    
    def registrar_acao(self, acao, descricao, usuario_id=None):
        print(f"[AUDITORIA] {acao}: {descricao}")


auditoria_service = AuditoriaService()
