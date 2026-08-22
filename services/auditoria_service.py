"""
Serviço de auditoria.
"""
from datetime import datetime

ACAO_LOGIN = "LOGIN"
ACAO_LOGOUT = "LOGOUT"
ACAO_LOGIN_FALHOU = "LOGIN_FALHOU"
ACAO_PERMISSAO_ALTERADA = "PERMISSAO_ALTERADA"
ACAO_USUARIO_CRIADO = "USUARIO_CRIADO"
ACAO_USUARIO_ATUALIZADO = "USUARIO_ATUALIZADO"
ACAO_USUARIO_EXCLUIDO = "USUARIO_EXCLUIDO"
ACAO_USUARIO_ATIVADO = "USUARIO_ATIVADO"
ACAO_USUARIO_DESATIVADO = "USUARIO_DESATIVADO"
ACAO_SYNC = "SYNC"
ACAO_BACKUP = "BACKUP"
ACAO_UPDATE = "UPDATE"
ACAO_CONFIG_ALTERADA = "CONFIG_ALTERADA"


class AuditoriaService:
    def __init__(self):
        self._registros = []
    
    def registrar(self, acao, modulo, usuario=None, **kwargs):
        user = usuario or "Sistema"
        registro = {
            "id": len(self._registros) + 1,
            "acao": acao,
            "modulo": modulo,
            "usuario": user,
            "data_hora": datetime.now().isoformat(),
            "detalhes": kwargs
        }
        self._registros.append(registro)
        print(f"[AUDITORIA] {acao} | {modulo} | {user}")
    
    def registrar_acao(self, acao, descricao, usuario_id=None):
        user = usuario_id or "Sistema"
        self.registrar(acao, "Geral", usuario=user, descricao=descricao)
    
    def listar(self, filtros=None, data_inicio=None, data_fim=None, pagina=1, por_pagina=50, acao=None, modulo=None):
        """Lista registros de auditoria com filtros opcionais."""
        resultado = self._registros.copy()
        
        if filtros:
            for chave, valor in filtros.items():
                resultado = [r for r in resultado if r.get(chave) == valor]
        
        if data_inicio:
            resultado = [r for r in resultado if r.get("data_hora", "") >= data_inicio]
        
        if data_fim:
            resultado = [r for r in resultado if r.get("data_hora", "") <= data_fim]
        
        if acao:
            resultado = [r for r in resultado if r.get("acao") == acao]
        
        if modulo:
            resultado = [r for r in resultado if r.get("modulo") == modulo]
        
        # Paginação
        total = len(resultado)
        inicio = (pagina - 1) * por_pagina
        fim = inicio + por_pagina
        resultado = resultado[inicio:fim]
        
        return {
            "registros": resultado,
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina
        }
    
    def listar_registros(self, filtros=None, pagina=1, por_pagina=50):
        return self.listar(filtros=filtros, pagina=pagina, por_pagina=por_pagina)
    
    def exportar_csv(self, caminho):
        return True
    
    def exportar_pdf(self, caminho):
        return True


auditoria_service = AuditoriaService()
