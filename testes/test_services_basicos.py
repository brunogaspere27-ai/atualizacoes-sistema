"""
Testes básicos para services principais.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.config_service import config_service
from services.sync_service import sync_service
from services.dashboard_service import dashboard_service
from services.financeiro_service import financeiro_service
from services.frota_service import frota_service
from services.funcionarios_service import funcionarios_service


def test_config_service():
    dados = config_service.carregar_configuracoes()
    assert isinstance(dados, dict)
    assert "tema" in dados
    assert "empresa" in dados
    print("✓ test_config_service passou")


def test_sync_service():
    resultado = sync_service.executar()
    assert isinstance(resultado, dict)
    assert "status" in resultado
    assert "pendencias" in resultado
    print("✓ test_sync_service passou")


def test_dashboard_service():
    payload = dashboard_service.carregar_dashboard("Geral", "01", "2026")
    assert isinstance(payload, dict)
    assert "dados" in payload
    assert "extras" in payload
    print("✓ test_dashboard_service passou")


def test_financeiro_service():
    dados = financeiro_service.listar_contas("Geral", "01", "2026", "Todos", "")
    assert isinstance(dados, list)
    print("✓ test_financeiro_service passou")


def test_frota_service():
    abastecimentos = frota_service.listar_abastecimentos("Geral", "01", "2026", "")
    manutencoes = frota_service.listar_manutencoes("Geral", "01", "2026", "")
    assert isinstance(abastecimentos, list)
    assert isinstance(manutencoes, list)
    print("✓ test_frota_service passou")


def test_funcionarios_service():
    funcionarios = funcionarios_service.listar_funcionarios("")
    folha = funcionarios_service.listar_folha_mes("01", "2026", "")
    assert isinstance(funcionarios, list)
    assert isinstance(folha, list)
    print("✓ test_funcionarios_service passou")


if __name__ == "__main__":
    print("Executando testes de services...")
    print()

    test_config_service()
    test_sync_service()
    test_dashboard_service()
    test_financeiro_service()
    test_frota_service()
    test_funcionarios_service()

    print()
    print("Todos os testes de services passaram! ✓")
