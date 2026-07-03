from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import Dict, Any

from config.settings import settings
from utils.database import conectar


class ConfigService:
    def carregar_configuracoes(self) -> Dict[str, Any]:
        settings.reload()
        return settings.configuracoes

    def salvar_configuracoes(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        return settings.salvar_configuracoes(dados)

    def restaurar_padrao(self) -> Dict[str, Any]:
        return settings.restaurar_padrao()

    def abrir_pasta_sistema(self) -> str:
        return str(settings.project_dir)

    def abrir_pasta_relatorios(self, pasta_relatorios: str | None = None) -> str:
        pasta = settings.project_dir / (pasta_relatorios or settings.pasta_relatorios)
        pasta.mkdir(parents=True, exist_ok=True)
        return str(pasta)

    def fazer_backup(self, pasta_relatorios: str | None = None) -> str:
        destino = settings.backup_dir / datetime.now().strftime("%d%m%Y_%H%M%S")
        destino.mkdir(parents=True, exist_ok=True)

        itens = [settings.db_path, settings.config_path]
        for origem in itens:
            if origem.exists():
                shutil.copy2(origem, destino / origem.name)

        origem_relatorios = settings.project_dir / (pasta_relatorios or settings.pasta_relatorios)
        if origem_relatorios.exists():
            shutil.copytree(
                origem_relatorios,
                destino / origem_relatorios.name,
                dirs_exist_ok=True
            )

        return str(destino)

    def info_banco(self) -> Dict[str, Any]:
        tamanho = "Não encontrado"
        tabelas = 0
        registros = 0

        if settings.db_path.exists():
            tamanho_bytes = settings.db_path.stat().st_size
            tamanho = f"{tamanho_bytes / 1024 / 1024:.2f} MB"

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            lista_tabelas = cursor.fetchall()
            tabelas = len(lista_tabelas)

            tabelas_principais = [
                "notas",
                "viagens",
                "funcionarios",
                "folha_funcionarios",
                "abastecimentos",
                "manutencoes",
                "contas",
            ]

            for tabela in tabelas_principais:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                    registros += cursor.fetchone()[0]
                except Exception:
                    pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

        ultimo_backup = "Nenhum"
        if settings.backup_dir.exists():
            backups = sorted(os.listdir(settings.backup_dir), reverse=True)
            if backups:
                ultimo_backup = backups[0]

        return {
            "tamanho": tamanho,
            "tabelas": tabelas,
            "registros": registros,
            "ultimo_backup": ultimo_backup,
        }


config_service = ConfigService()
