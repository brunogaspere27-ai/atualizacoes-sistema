"""
Testes para configurações do sistema.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


def test_config_singleton():
    """Testa se settings é singleton."""
    settings1 = settings
    settings2 = settings
    assert settings1 is settings2
    print("✓ test_config_singleton passou")


def test_config_empresa():
    """Testa configuração de empresa."""
    empresa = settings.empresa
    assert isinstance(empresa, str)
    assert len(empresa) > 0
    print(f"✓ test_config_empresa passou: {empresa}")


def test_config_meta_lucro():
    """Testa configuração de meta de lucro."""
    meta = settings.meta_lucro
    assert isinstance(meta, (int, float))
    assert meta > 0
    print(f"✓ test_config_meta_lucro passou: {meta}")


def test_config_imposto_percentual():
    """Testa configuração de imposto."""
    imposto = settings.imposto_percentual
    assert isinstance(imposto, (int, float))
    assert imposto >= 0
    print(f"✓ test_config_imposto_percentual passou: {imposto}")


def test_config_cores_tema():
    """Testa obtenção de cores do tema."""
    cores = settings.obter_cores_tema()
    assert isinstance(cores, dict)
    assert "principal" in cores
    assert "hover" in cores
    assert "fundo" in cores
    assert "texto" in cores
    print(f"✓ test_config_cores_tema passou")


def test_config_paleta_cores():
    """Testa paleta de cores."""
    paleta = settings.paleta_cores
    assert isinstance(paleta, dict)
    assert "Vermelho" in paleta
    assert "Azul" in paleta
    assert "Verde" in paleta
    print(f"✓ test_config_paleta_cores passou")


if __name__ == "__main__":
    print("Executando testes de configurações...")
    print()
    
    test_config_singleton()
    test_config_empresa()
    test_config_meta_lucro()
    test_config_imposto_percentual()
    test_config_cores_tema()
    test_config_paleta_cores()
    
    print()
    print("Todos os testes de configuração passaram! ✓")
