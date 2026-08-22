# -*- coding: utf-8 -*-
"""Instancia as telas PySide6 em modo offscreen para reproduzir NameError/ImportError reais."""
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication

app = QApplication([])

CASOS = [
    ("telas.login_aurora", None),
    ("telas.dashboard_cw", "DashboardCW"),
    ("telas.combustivel_pyside6", "TelaCombustivel"),
    ("telas.contas_pyside6", "TelaContas"),
    ("telas.manutencao_pyside6", "TelaManutencao"),
    ("telas.historico_pyside6", "TelaHistorico"),
    ("telas.funcionarios_pyside6", "TelaFuncionarios"),
    ("telas.auditoria_pyside6", "TelaAuditoria"),
    ("telas.gerenciar_usuarios_pyside6", "TelaGerenciarUsuarios"),
    ("telas.perfil_pyside6", "TelaPerfil"),
    ("telas.operacoes_pyside6", "TelaOperacoes"),
    ("telas.notas_pyside6", "TelaNotas"),
    ("telas.relatorios_pyside6", "TelaRelatorios"),
    ("telas.configuracoes_pyside6", "TelaConfiguracoes"),
    ("telas.ranking_pyside6", "TelaRanking"),
    ("telas.historico_versoes_pyside6", "TelaHistoricoVersoes"),
    ("telas.criar_viagem_pyside6", "TelaCriarViagem"),
]

for modulo_nome, classe_nome in CASOS:
    try:
        mod = __import__(modulo_nome, fromlist=[classe_nome or "x"])
        if classe_nome is None:
            print(f"OK(import)  {modulo_nome}")
            continue
        classe = getattr(mod, classe_nome)
        instancia = classe()
        print(f"OK       {modulo_nome}.{classe_nome}")
        instancia.deleteLater()
    except Exception as exc:
        import traceback
        print(f"FALHA    {modulo_nome}.{classe_nome}: {type(exc).__name__}: {exc}")
        traceback.print_exc()

print("FIM")
