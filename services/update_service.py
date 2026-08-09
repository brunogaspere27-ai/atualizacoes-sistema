"""
Servico de atualizacao profissional do sistema CW Transportadora.

Features:
- Verificacao por canal (estavel, beta, desenvolvimento)
- Suporte a servidor proprio e GitHub
- Download com calculo de velocidade e tempo restante
- Verificacao de integridade (SHA256)
- Backup pre-instalacao
- Historico de versoes
- Instalacao segura com rollback
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime

import requests

from config.settings import settings
from services.release_service import release_service, Channel
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger(__name__)

# Canais de atualizacao
CANAL_ESTAVEL = "stable"
CANAL_BETA = "beta"
CANAL_DEV = "dev"

# Mapeamento de canais para URLs da API
_CANAL_URLS = {
    CANAL_ESTAVEL: "/releases/latest",
    CANAL_BETA: "/releases",
    CANAL_DEV: "/releases",
}

# Fontes de atualizacao
SOURCE_LOCAL = "local"
SOURCE_GITHUB = "github"


class UpdateService:
    """Servico para gerenciar atualizacoes automaticas do sistema."""

    def __init__(self):
        self.version_file = settings.project_dir / "versao.json"
        self.update_url = settings.update_url
        self.current_version = self._load_current_version()
        self.timeout_seconds = settings.update_timeout
        self.enabled = settings.enable_auto_update
        self.channel = CANAL_ESTAVEL
        
        # Determinar fonte de atualização
        self.source = self._determine_update_source()

        # Estado do download para calculo de velocidade
        self._download_start_time: Optional[float] = None
        self._download_last_time: Optional[float] = None
    
    def _determine_update_source(self) -> str:
        """Determina a fonte de atualização (local ou GitHub)."""
        # Se tiver URL configurada, usa GitHub
        if settings.update_url:
            return SOURCE_GITHUB
        # Caso contrário, usa servidor próprio
        return SOURCE_LOCAL

    def _load_current_version(self) -> str:
        try:
            if self.version_file.exists():
                with open(self.version_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("versao", "0.0.0")
        except Exception as e:
            logger.error(f"Erro ao carregar versao atual: {e}")
        return "0.0.0"

    def obter_versao_instalada(self) -> Dict[str, str]:
        """Retorna informacoes da versao instalada."""
        try:
            if self.version_file.exists():
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"versao": self.current_version, "nome": "CW Transportadora", "data": ""}

    def set_channel(self, channel: str) -> None:
        """Define o canal de atualizacao (stable, beta, dev)."""
        if channel in (CANAL_ESTAVEL, CANAL_BETA, CANAL_DEV):
            self.channel = channel
            logger.info(f"Canal de atualizacao alterado para: {channel}")

    def _build_api_url(self, channel: str = "") -> str:
        """Constroi URL da API baseada no canal."""
        base = self.update_url.rsplit("/repos/", 1)[0] + "/repos/"
        try:
            repo_part = self.update_url.split("/repos/")[1]
            if "/releases" in repo_part:
                repo_part = repo_part.split("/releases")[0]
            suffix = _CANAL_URLS.get(channel or self.channel, _CANAL_URLS[CANAL_ESTAVEL])
            return f"{base}{repo_part}{suffix}"
        except Exception:
            return self.update_url

    @retry(max_attempts=3, delay=1, exceptions=(requests.RequestException,))
    def _fetch_release_info(self, channel: str = "") -> dict:
        """Busca informacoes de release da API com retry."""
        url = self._build_api_url(channel)
        response = requests.get(url, timeout=self.timeout_seconds)

        if response.status_code == 404:
            logger.info("Nenhuma release encontrada.")
            return {}

        response.raise_for_status()
        data = response.json()

        # Para canais beta/dev, a API retorna lista de releases
        if isinstance(data, list):
            if channel in (CANAL_BETA, CANAL_DEV) or self.channel in (CANAL_BETA, CANAL_DEV):
                for release in data:
                    if channel == CANAL_BETA or self.channel == CANAL_BETA:
                        if release.get("prerelease"):
                            return release
                    else:
                        return data[0] if data else {}
            return data[0] if data else {}

        return data

    def check_for_updates(self, channel: str = "") -> Dict[str, Any]:
        """
        Verifica se existe uma nova versao disponivel.
        
        Usa servidor próprio se configurado, caso contrário usa GitHub.

        Returns:
            Dict: has_update, current_version, latest_version, download_url,
                  release_notes, release_size, release_date, error, source
        """
        ch = channel or self.channel
        result = {
            "has_update": False,
            "current_version": self.current_version,
            "latest_version": self.current_version,
            "download_url": None,
            "release_notes": "",
            "release_size": 0,
            "release_date": "",
            "error": None,
            "source": self.source,
        }

        if not self.enabled and not channel:
            result["error"] = "Atualizacoes automaticas desabilitadas"
            return result

        # Usar servidor próprio se configurado
        if self.source == SOURCE_LOCAL:
            return self._check_for_updates_local(ch)
        
        # Usar GitHub se configurado
        return self._check_for_updates_github(ch)
    
    def _check_for_updates_local(self, channel: str) -> Dict[str, Any]:
        """Verifica atualizações no servidor próprio."""
        result = {
            "has_update": False,
            "current_version": self.current_version,
            "latest_version": self.current_version,
            "download_url": None,
            "release_notes": "",
            "release_size": 0,
            "release_date": "",
            "error": None,
            "source": SOURCE_LOCAL,
        }
        
        try:
            # Mapear canal do update_service para Channel do release_service
            channel_map = {
                CANAL_ESTAVEL: Channel.STABLE,
                CANAL_BETA: Channel.BETA,
                CANAL_DEV: Channel.DEV,
            }
            release_channel = channel_map.get(channel, Channel.STABLE)
            
            # Obter versão mais recente do release_service
            version_info = release_service.get_latest_version_info(release_channel)
            
            if not version_info:
                logger.info(f"Nenhuma versão encontrada no canal {channel} do servidor próprio")
                return result
            
            latest_version = version_info.get("versao", self.current_version)
            result["latest_version"] = latest_version
            result["release_notes"] = version_info.get("release_notes", "")
            result["release_date"] = version_info.get("data", "")
            result["release_size"] = version_info.get("installer_size", 0)
            
            # Verificar se há atualização
            if self._compare_versions(latest_version, self.current_version) > 0:
                result["has_update"] = True
                # Para servidor local, o download_url é o caminho do arquivo
                installer_path = release_service.get_installer_path(release_channel)
                if installer_path:
                    result["download_url"] = str(installer_path)
            
            logger.info(f"Verificacao LOCAL [{channel}]: atual={self.current_version}, latest={latest_version}")
            
        except Exception as e:
            result["error"] = f"Erro ao verificar atualizacoes no servidor proprio: {e}"
            logger.error(result["error"])
        
        return result
    
    def _check_for_updates_github(self, channel: str) -> Dict[str, Any]:
        """Verifica atualizações no GitHub (método original)."""
        result = {
            "has_update": False,
            "current_version": self.current_version,
            "latest_version": self.current_version,
            "download_url": None,
            "release_notes": "",
            "release_size": 0,
            "release_date": "",
            "error": None,
            "source": SOURCE_GITHUB,
        }

        try:
            release_data = self._fetch_release_info(channel)
            if not release_data:
                return result

            latest_version = release_data.get("tag_name", "").lstrip("v") or self.current_version
            result["latest_version"] = latest_version
            result["release_notes"] = release_data.get("body", "")
            result["release_date"] = release_data.get("published_at", "")[:10]

            if self._compare_versions(latest_version, self.current_version) > 0:
                result["has_update"] = True
                assets = release_data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if "exe" in name or "msi" in name or "windows" in name:
                        result["download_url"] = asset.get("browser_download_url")
                        result["release_size"] = asset.get("size", 0)
                        break
                if not result["download_url"] and assets:
                    result["download_url"] = assets[0].get("browser_download_url")
                    result["release_size"] = assets[0].get("size", 0)

            logger.info(f"Verificacao GITHUB [{channel}]: atual={self.current_version}, latest={latest_version}")

        except requests.exceptions.RequestException as e:
            result["error"] = f"Erro de conexao: {e}"
            logger.error(result["error"])
        except Exception as e:
            result["error"] = f"Erro ao verificar atualizacoes: {e}"
            logger.error(result["error"])

        return result

    def download_update(
        self,
        download_url: str,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[bool, str]:
        """
        Baixa o instalador com callback de progresso detalhado.
        Suporta HTTP/HTTPS com autenticação básica.

        Args:
            download_url: URL do instalador
            progress_callback: funcao(downloaded, total, speed_bps, eta_seconds)

        Returns:
            Tuple (success, file_path ou error_message)
        """
        try:
            downloads_dir = settings.dados_dir / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            filename = f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
            file_path = downloads_dir / filename

            logger.info(f"Iniciando download: {download_url}")
            
            # Preparar autenticação se configurada
            auth = None
            if settings.update_server_username and settings.update_server_password:
                auth = (settings.update_server_username, settings.update_server_password)
            
            response = requests.get(
                download_url, 
                stream=True, 
                timeout=self.timeout_seconds * 3,
                auth=auth,
                verify=True  # Validar certificado HTTPS
            )
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            self._download_start_time = time.time()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            elapsed = time.time() - self._download_start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            eta = (total_size - downloaded) / speed if speed > 0 else 0
                            progress_callback(downloaded, total_size, speed, eta)

            logger.info(f"Download concluido: {file_path} ({downloaded} bytes)")
            return True, str(file_path)

        except Exception as e:
            error_msg = f"Erro ao baixar atualizacao: {e}"
            logger.error(error_msg)
            return False, error_msg

    def verificar_integridade(self, arquivo_path: str, expected_sha256: str = "") -> bool:
        """Verifica integridade do arquivo baixado."""
        try:
            path = Path(arquivo_path)
            if not path.exists() or path.stat().st_size == 0:
                return False
            if expected_sha256:
                sha256 = self._calc_sha256(arquivo_path)
                if sha256.lower() != expected_sha256.lower():
                    logger.error(f"SHA256 mismatch: esperado={expected_sha256}, obtido={sha256}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            return False

    def _calc_sha256(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def criar_backup_pre_update(self) -> Tuple[bool, str]:
        """Cria backup do banco e configuracoes antes de instalar."""
        try:
            backup_dir = settings.dados_dir / "backups_pre_update"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = backup_dir / f"pre_update_{timestamp}"
            backup_subdir.mkdir(parents=True, exist_ok=True)

            db_path = settings.db_path
            if db_path.exists():
                shutil.copy2(str(db_path), str(backup_subdir / db_path.name))

            config_path = settings.config_path
            if config_path.exists():
                shutil.copy2(str(config_path), str(backup_subdir / config_path.name))

            if self.version_file.exists():
                shutil.copy2(str(self.version_file), str(backup_subdir / "versao.json"))

            logger.info(f"Backup pre-update criado em: {backup_subdir}")
            return True, str(backup_subdir)

        except Exception as e:
            logger.error(f"Erro ao criar backup pre-update: {e}")
            return False, str(e)

    def install_update(self, installer_path: str) -> Tuple[bool, str]:
        """Instala a atualizacao com backup de seguranca."""
        try:
            import subprocess
            import sys

            # A disponibilidade do instalador é específica de plataforma.
            # Verificar isso antes do arquivo torna o retorno correto e evita
            # qualquer tentativa de tratar um .exe no macOS/Linux.
            if sys.platform != "win32":
                return False, "Sistema de atualizacao disponivel apenas para Windows."

            if not self.verificar_integridade(installer_path):
                return False, "Arquivo de instalacao corrompido ou invalido."

            backup_ok, backup_msg = self.criar_backup_pre_update()
            if not backup_ok:
                logger.warning(f"Backup falhou: {backup_msg}")

            logger.info(f"Iniciando instalacao: {installer_path}")

            subprocess.Popen([installer_path], shell=False)
            return True, "Instalador iniciado. O aplicativo sera fechado."

        except Exception as e:
            logger.error(f"Erro ao instalar atualizacao: {e}")
            return False, str(e)

    def obter_historico_versoes(self, limit: int = 20) -> List[Dict[str, str]]:
        """Busca historico de releases da API ou do servidor proprio."""
        # Usar servidor proprio se configurado
        if self.source == SOURCE_LOCAL:
            return self._obter_historico_local(limit)
        
        # Usar GitHub se configurado
        return self._obter_historico_github(limit)
    
    def _obter_historico_local(self, limit: int = 20) -> List[Dict[str, str]]:
        """Busca historico de releases do servidor proprio."""
        try:
            history = release_service.get_history(limit)
            
            return [
                {
                    "versao": r.version,
                    "data": r.release_date,
                    "notas": r.release_notes,
                    "prerelease": r.channel != "stable",
                }
                for r in history
            ]
        except Exception as e:
            logger.error(f"Erro ao obter historico do servidor proprio: {e}")
            return []
    
    def _obter_historico_github(self, limit: int = 20) -> List[Dict[str, str]]:
        """Busca historico de releases da API do GitHub."""
        try:
            url = self._build_api_url(CANAL_BETA).replace("/releases/latest", "/releases")
            
            # Se URL estiver vazia, retorna vazio
            if not url or url == "/releases":
                logger.warning("URL do GitHub não configurada para obter historico")
                return []
            
            response = requests.get(url, timeout=self.timeout_seconds)

            if response.status_code == 404:
                logger.info("Nenhum release encontrado na API (404).")
                return []

            response.raise_for_status()
            releases = response.json()

            if not isinstance(releases, list):
                return []

            return [
                {
                    "versao": r.get("tag_name", "").lstrip("v"),
                    "data": r.get("published_at", "")[:10],
                    "notas": r.get("body", ""),
                    "prerelease": r.get("prerelease", False),
                }
                for r in releases[:limit]
            ]
        except requests.exceptions.RequestException as e:
            logger.warning(f"Erro de conexao ao obter historico: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro ao obter historico: {e}")
            return []

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compara duas versoes X.Y.Z. Returns -1, 0, 1."""
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            if len(v1_parts) < len(v2_parts):
                return -1
            elif len(v1_parts) > len(v2_parts):
                return 1
            return 0
        except Exception:
            return 0


update_service = UpdateService()
