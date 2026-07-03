"""
Serviço de atualização automática do sistema.
Desacoplado da interface, verifica, baixa e instala atualizações.
"""

from __future__ import annotations

import json
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

from config.settings import settings
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger(__name__)


class UpdateService:
    """Serviço para gerenciar atualizações automáticas do sistema."""

    def __init__(self):
        self.version_file = settings.project_dir / "versao.json"
        self.update_url = settings.update_url
        self.current_version = self._load_current_version()
        self.timeout_seconds = settings.update_timeout
        self.enabled = settings.enable_auto_update

    def _load_current_version(self) -> str:
        """Carrega a versão atual do arquivo versao.json."""
        try:
            if self.version_file.exists():
                with open(self.version_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("versao", "0.0.0")
        except Exception as e:
            logger.error(f"Erro ao carregar versão atual: {e}")
        return "0.0.0"

    @retry(max_attempts=3, delay=1, exceptions=(requests.RequestException,))
    def _fetch_release_info(self) -> dict:
        """Busca informações de release da API com retry."""
        response = requests.get(self.update_url, timeout=self.timeout_seconds)

        if response.status_code == 404:
            logger.info("Nenhuma release pública encontrada para o repositório configurado.")
            return {}

        response.raise_for_status()
        return response.json()

    def check_for_updates(self) -> Dict[str, any]:
        """
        Verifica se existe uma nova versão disponível.

        Returns:
            Dict com informações sobre a atualização:
            - has_update: bool se existe atualização
            - current_version: str versão atual
            - latest_version: str versão mais recente
            - download_url: str URL para download
            - release_notes: str notas da versão
            - error: str mensagem de erro (se houver)
        """
        result = {
            "has_update": False,
            "current_version": self.current_version,
            "latest_version": self.current_version,
            "download_url": None,
            "release_notes": "",
            "error": None
        }

        if not self.enabled:
            result["error"] = "Atualizações automáticas desabilitadas"
            return result

        try:
            release_data = self._fetch_release_info()

            latest_version = release_data.get("tag_name", "").lstrip("v") or self.current_version
            
            result["latest_version"] = latest_version
            result["release_notes"] = release_data.get("body", "")

            # Verificar se existe atualização disponível
            if self._compare_versions(latest_version, self.current_version) > 0:
                result["has_update"] = True
                
                # Buscar URL do asset para Windows
                assets = release_data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if "exe" in name or "msi" in name or "windows" in name:
                        result["download_url"] = asset.get("browser_download_url")
                        break
                
                if not result["download_url"] and assets:
                    # Fallback para o primeiro asset
                    result["download_url"] = assets[0].get("browser_download_url")

            logger.info(f"Verificação de atualização: atual={self.current_version}, latest={latest_version}")

        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão ao verificar atualizações: {e}"
            logger.error(error_msg)
            result["error"] = error_msg
        except Exception as e:
            error_msg = f"Erro ao verificar atualizações: {e}"
            logger.error(error_msg)
            result["error"] = error_msg

        return result

    def download_update(self, download_url: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Baixa o instalador da atualização.
        
        Args:
            download_url: URL do instalador
            progress_callback: função callback para progresso (bytes_downloaded, total_bytes)
            
        Returns:
            Tuple (success: bool, file_path: str ou error_message: str)
        """
        try:
            downloads_dir = settings.dados_dir / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
            file_path = downloads_dir / filename

            logger.info(f"Iniciando download de: {download_url}")
            
            response = requests.get(download_url, stream=True, timeout=self.timeout_seconds * 3)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Download concluído: {file_path}")
            return True, str(file_path)

        except Exception as e:
            error_msg = f"Erro ao baixar atualização: {e}"
            logger.error(error_msg)
            return False, error_msg

    def install_update(self, installer_path: str) -> Tuple[bool, str]:
        """
        Instala a atualização no Windows.
        
        Args:
            installer_path: Caminho do instalador
            
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            import subprocess
            import sys
            
            logger.info(f"Iniciando instalação: {installer_path}")
            
            # No Windows, usa subprocess para executar o instalador
            # O instalador deve ser executado de forma assíncrona
            # para que o aplicativo possa ser fechado
            
            if sys.platform == "win32":
                subprocess.Popen(
                    [installer_path],
                    shell=False,
                )
                return True, "Instalador iniciado. O aplicativo será fechado."
            else:
                return False, "Sistema de atualização disponível apenas para Windows."

        except Exception as e:
            error_msg = f"Erro ao instalar atualização: {e}"
            logger.error(error_msg)
            return False, error_msg

    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compara duas versões no formato X.Y.Z.
        
        Returns:
            -1 se version1 < version2
            0 se version1 == version2
            1 se version1 > version2
        """
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]
            
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            
            # Se as partes principais são iguais, verifica se há mais partes
            if len(v1_parts) < len(v2_parts):
                return -1
            elif len(v1_parts) > len(v2_parts):
                return 1
                
            return 0
        except Exception:
            return 0


update_service = UpdateService()
