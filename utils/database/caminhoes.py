"""Cadastro e consulta de caminhoes da frota."""

import sqlite3
from typing import Optional

from utils.logger import get_logger
from ._conexao import conectar, registrar_sync

logger = get_logger(__name__)


def listar_caminhoes(conn: Optional[sqlite3.Connection] = None):
    """
    Args:
        conn: conexão opcional já aberta (ver `dados_dashboard`).
    """
    conexao_propria = conn is None
    if conexao_propria:
        conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, placa, modelo, motorista, capacidade_kg
        FROM caminhoes
        ORDER BY modelo
    """)

    dados = cursor.fetchall()
    if conexao_propria:
        conn.close()

    return dados


def apagar_todos_caminhoes():
    """Remove todos os caminhões da tabela."""
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM caminhoes")
        conn.commit()
        conn.close()

        logger.info("Todos os caminhões foram apagados")
        return True

    except Exception as erro:
        logger.error(f"Erro ao apagar caminhões: {erro}")
        return False


def criar_caminhoes_padrao():

    conn = conectar()
    cursor = conn.cursor()

    caminhoes = [
        ("Renault Master", "Renault Master", "Motorista Master", 1500, 9),
        ("3/4 Branco", "Caminhão 3/4 Branco", "Motorista Branco", 3500, 7),
        ("3/4 Preto", "Caminhão 3/4 Preto", "Motorista Preto", 3500, 7),
        ("Toco", "Caminhão Toco", "Motorista Toco", 6000, 5),
    ]

    for placa, modelo, motorista, capacidade, media in caminhoes:
        cursor.execute("SELECT id FROM caminhoes WHERE placa = ?", (placa,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("""
                INSERT INTO caminhoes
                (placa, modelo, motorista, capacidade_kg, media_km_l)
                VALUES (?, ?, ?, ?, ?)
            """, (placa, modelo, motorista, capacidade, media))

            registrar_sync(cursor, "caminhoes", cursor.lastrowid)

    conn.commit()
    conn.close()


def cadastrar_caminhao(placa, modelo, motorista, capacidade_kg, media_km_l):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO caminhoes (
            placa,
            modelo,
            motorista,
            capacidade_kg,
            media_km_l
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        placa,
        modelo,
        motorista,
        capacidade_kg,
        media_km_l
    ))

    registrar_sync(cursor, "caminhoes", cursor.lastrowid)

    conn.commit()
    conn.close()


