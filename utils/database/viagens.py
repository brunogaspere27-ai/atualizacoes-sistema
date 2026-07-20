"""Ciclo de vida das viagens: criacao, finalizacao, consulta, exclusao."""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

from utils.logger import get_logger
from ._conexao import conectar, get_connection, registrar_sync

logger = get_logger(__name__)


def criar_viagem(caminhao_id, notas_ids, data_saida, motorista):

    if not notas_ids:
        raise ValueError("Nenhuma nota selecionada.")

    placeholders = ",".join(["?"] * len(notas_ids))

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, status
            FROM notas
            WHERE id IN ({placeholders})
        """, notas_ids)

        for nota_id, status in cursor.fetchall():
            if status != "Disponível":
                raise ValueError(
                    f"A nota #{nota_id} não está disponível (status: {status})."
                )

        cursor.execute(f"""
            SELECT
                COALESCE(SUM(peso), 0),
                COALESCE(SUM(valor_frete), 0)
            FROM notas
            WHERE id IN ({placeholders})
        """, notas_ids)

        peso_total, frete_total = cursor.fetchone()

        cursor.execute("""
            INSERT INTO viagens (
                caminhao_id,
                data_saida,
                motorista,
                status,
                peso_total,
                frete_total,
                custo_total,
                lucro_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            caminhao_id,
            data_saida,
            motorista,
            "Em viagem",
            peso_total,
            frete_total,
            0,
            frete_total
        ))

        viagem_id = cursor.lastrowid
        registrar_sync(cursor, "viagens", viagem_id)

        for nota_id in notas_ids:
            cursor.execute("""
                INSERT INTO viagem_notas (viagem_id, nota_id)
                VALUES (?, ?)
            """, (viagem_id, nota_id))

            viagem_nota_id = cursor.lastrowid
            registrar_sync(cursor, "viagem_notas", viagem_nota_id)

            cursor.execute("""
                UPDATE notas
                SET status = 'Em viagem'
                WHERE id = ?
            """, (nota_id,))

            registrar_sync(cursor, "notas", nota_id)

        conn.commit()

    return viagem_id


def apagar_viagem(viagem_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM viagens WHERE id = ?",
            (viagem_id,)
        )

        if not cursor.fetchone():
            raise Exception("Viagem não encontrada.")

        cursor.execute(
            "SELECT id, nota_id FROM viagem_notas WHERE viagem_id = ?",
            (viagem_id,)
        )

        viagem_notas = cursor.fetchall()
        notas_ids = [nota_id for _, nota_id in viagem_notas]

        for viagem_nota_id, nota_id in viagem_notas:
            if viagem_nota_id:
                registrar_sync(cursor, "viagem_notas", viagem_nota_id, "DELETE")

        for nota_id in notas_ids:
            cursor.execute("""
                UPDATE notas
                SET status = 'Disponível'
                WHERE id = ?
            """, (nota_id,))

            registrar_sync(cursor, "notas", nota_id)

        cursor.execute(
            "DELETE FROM viagem_notas WHERE viagem_id = ?",
            (viagem_id,)
        )

        registrar_sync(cursor, "viagens", viagem_id, "DELETE")

        cursor.execute(
            "DELETE FROM viagens WHERE id = ?",
            (viagem_id,)
        )

        conn.commit()

        return len(notas_ids)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def listar_viagens():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            viagens.id,
            viagens.data_saida,
            caminhoes.modelo,
            caminhoes.placa,
            viagens.motorista,
            viagens.status,
            viagens.peso_total,
            viagens.frete_total,
            COUNT(viagem_notas.nota_id) as total_notas
        FROM viagens
        LEFT JOIN caminhoes ON caminhoes.id = viagens.caminhao_id
        LEFT JOIN viagem_notas ON viagem_notas.viagem_id = viagens.id
        GROUP BY viagens.id
        ORDER BY viagens.id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    return dados


def listar_notas_da_viagem(viagem_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM viagem_notas
        INNER JOIN notas ON notas.id = viagem_notas.nota_id
        LEFT JOIN clientes remetente ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario ON destinatario.id = notas.destinatario_id
        WHERE viagem_notas.viagem_id = ?
        ORDER BY notas.id DESC
    """, (viagem_id,))

    dados = cursor.fetchall()
    conn.close()

    return dados


def finalizar_viagem(viagem_id, data_retorno):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE viagens
        SET status = 'Finalizada',
            data_retorno = ?
        WHERE id = ?
    """, (data_retorno, viagem_id))

    cursor.execute("""
        UPDATE notas
        SET status = 'Entregue'
        WHERE id IN (
            SELECT nota_id
            FROM viagem_notas
            WHERE viagem_id = ?
        )
    """, (viagem_id,))

    registrar_sync(cursor, "viagens", viagem_id)

    cursor.execute(
        "SELECT nota_id FROM viagem_notas WHERE viagem_id = ?",
        (viagem_id,)
    )

    for (nota_id,) in cursor.fetchall():
        registrar_sync(cursor, "notas", nota_id)

    conn.commit()
    conn.close()

    return True


def buscar_detalhes_viagem(viagem_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            viagens.id,
            viagens.data_saida,
            viagens.data_retorno,
            viagens.motorista,
            viagens.status,
            viagens.peso_total,
            viagens.frete_total,
            caminhoes.modelo,
            caminhoes.placa,
            caminhoes.capacidade_kg
        FROM viagens
        LEFT JOIN caminhoes ON caminhoes.id = viagens.caminhao_id
        WHERE viagens.id = ?
    """, (viagem_id,))

    dados = cursor.fetchone()
    conn.close()

    return dados


