from __future__ import annotations

from datetime import date
from typing import Any, List, Optional, Sequence

from utils.database import conectar, registrar_sync


class FinanceiroService:

    def contar_contas_vencidas(self) -> int:
        """
        Retorna o número de contas Pendentes com vencimento anterior a hoje.
        Usado pelo sidebar para exibir badge de alerta.
        """
        hoje = date.today().strftime("%d/%m/%Y")
        conn = conectar()
        cursor = conn.cursor()
        try:
            # Compara strings DD/MM/YYYY usando substr para extrair ano, mês, dia
            # de forma que a ordenação lexicográfica seja correta (YYYY + MM + DD)
            cursor.execute("""
                SELECT COUNT(*)
                FROM contas
                WHERE status = 'Pendente'
                  AND vencimento IS NOT NULL
                  AND vencimento != ''
                  AND (
                      substr(vencimento,7,4) || substr(vencimento,4,2) || substr(vencimento,1,2)
                      < substr(?,7,4) || substr(?,4,2) || substr(?,1,2)
                  )
            """, (hoje, hoje, hoje))
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()

    def listar_contas(
        self,
        tipo_periodo: str,
        mes: str,
        ano: str,
        filtro_tipo: str,
        busca: str,
    ) -> List[Sequence[Any]]:
        where = []
        params = []

        if tipo_periodo == "Mês":
            where.append("substr(vencimento, 4, 2) = ? AND substr(vencimento, 7, 4) = ?")
            params.extend([mes, ano])
        elif tipo_periodo == "Ano":
            where.append("substr(vencimento, 7, 4) = ?")
            params.append(ano)

        if filtro_tipo != "Todos":
            where.append("tipo = ?")
            params.append(filtro_tipo)

        if busca:
            where.append("(descricao LIKE ? OR pessoa LIKE ? OR categoria LIKE ?)")
            params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT
                    id,
                    tipo,
                    descricao,
                    pessoa,
                    categoria,
                    valor,
                    vencimento,
                    pagamento,
                    status,
                    observacao
                FROM contas
                {where_sql}
                ORDER BY id DESC
            """, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def obter_conta(self, conta_id: Any) -> Optional[Sequence[Any]]:
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id,
                    tipo,
                    descricao,
                    pessoa,
                    categoria,
                    valor,
                    vencimento,
                    pagamento,
                    status,
                    observacao
                FROM contas
                WHERE id = ?
            """, (conta_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def salvar_conta(self, conta_id: Any, valores: Sequence[Any]) -> Any:
        conn = conectar()
        cursor = conn.cursor()
        try:
            if conta_id:
                cursor.execute("""
                    UPDATE contas
                    SET tipo = ?,
                        descricao = ?,
                        pessoa = ?,
                        categoria = ?,
                        valor = ?,
                        vencimento = ?,
                        pagamento = ?,
                        status = ?,
                        observacao = ?
                    WHERE id = ?
                """, tuple(valores) + (conta_id,))
                registrar_sync(cursor, "contas", conta_id)
                registro_id = conta_id
            else:
                cursor.execute("""
                    INSERT INTO contas (
                        tipo,
                        descricao,
                        pessoa,
                        categoria,
                        valor,
                        vencimento,
                        pagamento,
                        status,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(valores))
                registro_id = cursor.lastrowid
                registrar_sync(cursor, "contas", registro_id)

            conn.commit()
            return registro_id
        finally:
            conn.close()

    def marcar_pago(self, conta_id: Any, tipo: str, data_pagamento: str) -> None:
        novo_status = "Recebido" if tipo == "Receber" else "Pago"
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE contas
                SET status = ?,
                    pagamento = ?
                WHERE id = ?
            """, (novo_status, data_pagamento, conta_id))
            registrar_sync(cursor, "contas", conta_id)
            conn.commit()
        finally:
            conn.close()

    def excluir_conta(self, conta_id: Any) -> None:
        conn = conectar()
        cursor = conn.cursor()
        try:
            registrar_sync(cursor, "contas", conta_id, "DELETE")
            cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
            conn.commit()
        finally:
            conn.close()


financeiro_service = FinanceiroService()
