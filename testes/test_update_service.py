"""
Testes para o serviço de atualização automática.
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from main import App
from services.update_service import UpdateService


@pytest.fixture
def update_service():
    """Fixture para criar instância do UpdateService."""
    return UpdateService()


def test_load_current_version(update_service):
    """Testa carregamento da versão atual."""
    version = update_service._load_current_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_compare_versions(update_service):
    """Testa comparação de versões."""
    # Versão maior
    assert update_service._compare_versions("1.2.0", "1.1.0") == 1
    # Versão menor
    assert update_service._compare_versions("1.1.0", "1.2.0") == -1
    # Versão igual
    assert update_service._compare_versions("1.1.0", "1.1.0") == 0
    # Versão com mais partes
    assert update_service._compare_versions("1.1.1", "1.1.0") == 1


@patch('services.update_service.requests.get')
def test_check_for_updates_success(mock_get, update_service):
    """Testa verificação de atualizações com sucesso."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "tag_name": "v1.0.1",
        "body": "Nova versão com correções",
        "assets": [
            {
                "name": "installer.exe",
                "browser_download_url": "https://example.com/installer.exe"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    # Simular versão atual menor
    update_service.current_version = "1.0.0"
    
    result = update_service.check_for_updates()
    
    assert result["has_update"] is True
    assert result["latest_version"] == "1.0.1"
    assert result["download_url"] == "https://example.com/installer.exe"
    assert result["error"] is None


@patch('services.update_service.requests.get')
def test_check_for_updates_no_update(mock_get, update_service):
    """Testa verificação quando não há atualização."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "tag_name": "v1.0.0",
        "body": "Versão atual",
        "assets": []
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    update_service.current_version = "1.0.0"
    
    result = update_service.check_for_updates()
    
    assert result["has_update"] is False
    assert result["latest_version"] == "1.0.0"


@patch('services.update_service.requests.get')
def test_check_for_updates_error(mock_get, update_service):
    """Testa verificação com erro de conexão."""
    mock_get.side_effect = Exception("Connection error")
    
    result = update_service.check_for_updates()
    
    assert result["has_update"] is False
    assert result["error"] is not None
    assert "Connection error" in result["error"]


@patch('services.update_service.requests.get')
def test_check_for_updates_without_releases(mock_get, update_service):
    """Testa verificação quando o repositório não possui releases publicadas."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
    mock_get.return_value = mock_response

    result = update_service.check_for_updates()

    assert result["has_update"] is False
    assert result["latest_version"] == update_service.current_version
    assert result["error"] is None


@patch('services.update_service.requests.get')
def test_download_update_success(mock_get, update_service, tmp_path):
    """Testa download de atualização com sucesso."""
    mock_response = Mock()
    mock_response.iter_content = Mock(return_value=[b"data"])
    mock_response.headers = {'content-length': '100'}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    with patch.object(update_service, 'version_file', tmp_path / "versao.json"):
        success, result = update_service.download_update(
            "https://example.com/update.exe"
        )
    
    assert success is True
    assert "update" in result


@patch('subprocess.Popen')
def test_install_update_windows(mock_popen, update_service):
    """Testa instalação no Windows."""
    mock_popen.return_value = Mock()
    
    with patch('sys.platform', 'win32'):
        success, message = update_service.install_update("path/to/installer.exe")
    
    assert success is True
    assert "Instalador iniciado" in message
    mock_popen.assert_called_once()


def test_install_update_not_windows(update_service):
    """Testa instalação em sistema não-Windows."""
    with patch('sys.platform', 'linux'):
        success, message = update_service.install_update("path/to/installer.exe")
    
    assert success is False
    assert "apenas para Windows" in message
