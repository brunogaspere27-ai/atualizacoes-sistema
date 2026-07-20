"""
Servico de auditoria do sistema CW Transportadora.

Registra e consulta eventos importantes do sistema:
- Logins / logouts
- Tentativas invalidas
- Criacao / exclusao / alteracao de usuarios
- Alteracoes de permissoes e senhas
- Operacoes criticas do sistema
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from utils.database import conectar
from utils.logger import get_logger

logger = get_logger(__name__)

# Acoes padronizadas
ACAO_LOGIN = "LOGIN"
ACAO_LOGOUT = "LOGOUT"
ACAO_LOGIN_FALHOU = "LOGIN_FALHOU"
ACAO_USUARIO_CRIADO = "USUARIO_CRIADO"
ACAO_USUARIO_EXCLUIDO = "USUARIO_EXCLUIDO"
ACAO_USUARIO_ATIVADO = "USUARIO_ATIVADO"
ACAO_USUARIO_DESATIVADO = "USUARIO_DESATIVADO"
ACAO_PERMISSAO_ALTERADA = "PERMISSAO_ALTERADA"
ACAO_NIVEL_ALTERADO = "NIVEL_ALTERADO"
ACAO_SENHA_ALTERADA = "SENHA_ALTERADA"
ACAO_SENHA_REDEFINIDA = "SENHA_REDEFINIDA"
ACAO_REGISTRO_EXCLUIDO = "REGISTRO_EXCLUIDO"
ACAO_REGISTRO_ALTERADO = "REGISTRO_ALTERADO"
ACAO_SINCRONIZACAO = "SINCRONIZACAO"
ACAO_CONFIG_ALTERADA = "CONFIG_ALTERADA"
ACAO_PUBLICAR_VERSAO = "PUBLICAR_VERSAO"


class AuditoriaService:
    """Servico singleton para registro e consulta de auditoria."""

    def registrar(
        self,
        acao: str,
        modulo: str = "",
        registro_afetado: str = "",
        detalhes: str = "",
        usuario_id: Optional[int] = None,
        usuario_nome: str = "",
    ) -> None:
        """
        Registra um evento de auditoria.

        Se usuario_id/nome nao forem informados, tenta usar o usuario logado
        via auth_service (importacao tardia para evitar ciclo).
        """
        if usuario_id is None:
            try:
                from services.auth_service import auth_service
                u = auth_service.usuario_atual
                if u:
                    usuario_id = u["id"]
                    usuario_nome = u.get("nome_completo", "")
            except Exception:
                pass  # auth_service pode nao estar disponivel ainda

        try:
            conn = conectar()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO auditoria
                        (usuario_id, usuario_nome, acao, modulo,
                         registro_afetado, detalhes, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        usuario_id,
                        usuario_nome,
                        acao,
                        modulo,
                        registro_afetado,
                        detalhes,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception as erro:
            # Auditoria nao deve quebrar o fluxo principal
            logger.error(f"Erro ao registrar auditoria ({acao}): {erro}")

    # Alias para compatibilidade
    registrar_acao = registrar

    def listar(
        self,
        usuario_id: Optional[int] = None,
        acao: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        modulo: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Consulta registros de auditoria com filtros e paginacao.

        Args:
            usuario_id: Filtrar por usuario especifico.
            acao: Filtrar por tipo de acao.
            data_inicio: Data inicial (YYYY-MM-DD).
            data_fim: Data final (YYYY-MM-DD).
            modulo: Filtrar por modulo.
            limite: Quantidade maxima de registros.
            offset: Posicao inicial (para paginacao).

        Returns:
            Lista de dicts com registros de auditoria.
        """
        where_clauses = []
        params: list = []

        if usuario_id is not None:
            where_clauses.append("usuario_id = ?")
            params.append(usuario_id)

        if acao:
            where_clauses.append("acao = ?")
            params.append(acao)

        if modulo:
            where_clauses.append("modulo = ?")
            params.append(modulo)

        if data_inicio:
            where_clauses.append("criado_em >= ?")
            params.append(f"{data_inicio} 00:00:00")

        if data_fim:
            where_clauses.append("criado_em <= ?")
            params.append(f"{data_fim} 23:59:59")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                SELECT id, usuario_id, usuario_nome, acao, modulo,
                       registro_afetado, detalhes, criado_em
                FROM auditoria
                {where_sql}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                [*params, limite, offset],
            )

            resultado = []
            for row in cursor.fetchall():
                resultado.append(
                    {
                        "id": row[0],
                        "usuario_id": row[1],
                        "usuario_nome": row[2] or "Sistema",
                        "acao": row[3],
                        "modulo": row[4] or "",
                        "registro_afetado": row[5] or "",
                        "detalhes": row[6] or "",
                        "criado_em": row[7],
                    }
                )
            return resultado
        finally:
            conn.close()

    def contar_total(
        self,
        usuario_id: Optional[int] = None,
        acao: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        modulo: Optional[str] = None,
    ) -> int:
        """Conta total de registros com os mesmos filtros de listar()."""
        where_clauses = []
        params: list = []

        if usuario_id is not None:
            where_clauses.append("usuario_id = ?")
            params.append(usuario_id)
        if acao:
            where_clauses.append("acao = ?")
            params.append(acao)
        if modulo:
            where_clauses.append("modulo = ?")
            params.append(modulo)
        if data_inicio:
            where_clauses.append("criado_em >= ?")
            params.append(f"{data_inicio} 00:00:00")
        if data_fim:
            where_clauses.append("criado_em <= ?")
            params.append(f"{data_fim} 23:59:59")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM auditoria {where_sql}", params
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def estatisticas_hoje(self) -> Dict[str, int]:
        """Retorna contadores de eventos do dia atual."""
        hoje = datetime.now().strftime("%Y-%m-%d")
        conn = conectar()
        cursor = conn.cursor()
        try:
            stats: Dict[str, int] = {
                "logins": 0,
                "tentativas_falhas": 0,
                "alteracoes": 0,
            }

            cursor.execute(
                """
                SELECT acao, COUNT(*)
                FROM auditoria
                WHERE criado_em >= ? AND criado_em <= ?
                GROUP BY acao
                """,
                (f"{hoje} 00:00:00", f"{hoje} 23:59:59"),
            )

            for acao, total in cursor.fetchall():
                if acao == ACAO_LOGIN:
                    stats["logins"] = total
                elif acao == ACAO_LOGIN_FALHOU:
                    stats["tentativas_falhas"] = total
                elif acao in (
                    ACAO_REGISTRO_ALTERADO,
                    ACAO_REGISTRO_EXCLUIDO,
                    ACAO_SENHA_ALTERADA,
                    ACAO_PERMISSAO_ALTERADA,
                    ACAO_CONFIG_ALTERADA,
                ):
                    stats["alteracoes"] += total

            return stats
        finally:
            conn.close()

    def listar_acoes_distintas(self) -> List[str]:
        """Retorna lista de acoes distintas ja registradas."""
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT acao FROM auditoria ORDER BY acao")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()


auditoria_service = AuditoriaService()
