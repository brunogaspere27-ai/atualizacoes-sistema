# -*- coding: utf-8 -*-
"""Verifica imports de todos os módulos do projeto e reporta erros."""
import importlib
import sys
import traceback

MODULOS = [
    "config.settings",
    "utils.database",
    "utils.logger",
    "utils.helpers",
    "utils.validators",
    "utils.cache",
    "utils.performance",
    "utils.supabase_db",
    "utils.sync",
    "utils.importador_txt",
    "utils.calculos_operacao",
    "utils.preparar_distribuicao",
    "utils.env_check",
    "utils.branding",
    "utils.avatar",
    "utils.command_palette",
    "services.auth_service",
    "services.sync_service",
    "services.update_service",
    "services.github_update_service",
    "services.github_release_service",
    "services.release_service",
    "services.dashboard_service",
    "services.financeiro_service",
    "services.frota_service",
    "services.funcionarios_service",
    "services.historico_service",
    "services.notas_service",
    "services.operacoes_service",
    "services.perfil_service",
    "services.ranking_service",
    "services.rascunho_viagem_service",
    "services.relatorios_service",
    "services.search_service",
    "services.usuario_service",
    "services.viagem_service",
    "services.auditoria_service",
    "services.config_service",
    "ui.theme.cw_theme",
    "ui.theme.compat",
    "ui.components",
    "telas.login_aurora",
    "telas.dashboard_cw",
    "telas.notas_pyside6",
    "telas.operacoes_pyside6",
    "telas.ranking_pyside6",
    "telas.historico_versoes_pyside6",
    "telas.criar_viagem_pyside6",
    "telas.historico_pyside6",
    "telas.combustivel_pyside6",
    "telas.manutencao_pyside6",
    "telas.contas_pyside6",
    "telas.relatorios_pyside6",
    "telas.funcionarios_pyside6",
    "telas.configuracoes_pyside6",
    "telas.gerenciar_usuarios_pyside6",
    "telas.perfil_pyside6",
    "telas.auditoria_pyside6",
    "utils.components",
    "utils.search_widget",
    "utils.icons",
]

falhas = []
ok = 0
for nome in MODULOS:
    try:
        importlib.import_module(nome)
        ok += 1
    except Exception as exc:
        falhas.append((nome, exc))
        print(f"FALHA  {nome}: {type(exc).__name__}: {exc}")

print(f"\n=== OK: {ok} | FALHAS: {len(falhas)} ===")
for nome, exc in falhas:
    print(f"  - {nome}")
