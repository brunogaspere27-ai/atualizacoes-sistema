"""
Serviço de Atualização Automática via GitHub - CW Transportadora

Gerencia o processo de verificação e instalação de atualizações do GitHub.
Fluxo Cliente: verifica automaticamente novas versões e baixa via HTTPS.

Features:
- Verificação de atualizações via API do GitHub
- Download de instaladores via HTTPS
- Autenticação via Personal Access Token (repositórios privados)
- Verificação de integridade SHA-256
- Backup pré-instalação
- Rollback automático em caso de falha
- Resiliência a falhas de rede
- Suporte a múltiplos canais (stable, beta, dev)
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from config.settings import settings
from services.github_release_service import GitHubChannel
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger(__name__)


class UpdateStatus(Enum):
    """Status do processo de atualização."""
    IDLE = "idle"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class GitHubUpdateService:
    """Serviço para gerenciar atualizações automáticas do GitHub."""
    
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
    
    def __init__(self):
        self.repo_owner = settings.github_repo_owner
        self.repo_name = settings.github_repo_name
        self.token = settings.github_token
        self.use_cdn = settings.github_use_cdn
        self.channel = GitHubChannel.STABLE
        
        self.version_file = settings.project_dir / "versao.json"
        self.current_version = self._load_current_version()
        self.timeout_seconds = settings.update_timeout
        self.enabled = settings.enable_auto_update
        
        # Estado do download para cálculo de velocidade
        self._download_start_time: Optional[float] = None
        self._download_last_time: Optional[float] = None
        
        # Status atual
        self._status = UpdateStatus.IDLE
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições à API do GitHub."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
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
    
    def _get_installed_version_info(self) -> Dict[str, str]:
        """Retorna informações da versão instalada."""
        try:
            if self.version_file.exists():
                with open(self.version_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"versao": self.current_version, "nome": "CW Transportadora", "data": ""}
    
    def set_channel(self, channel: GitHubChannel) -> None:
        """Define o canal de atualização (stable, beta, dev)."""
        self.channel = channel
        logger.info(f"Canal de atualização alterado para: {channel.value}")
    
    def _get_api_url(self, endpoint: str) -> str:
        """Constrói URL completa para endpoint da API."""
        return f"{self.GITHUB_API_BASE}/repos/{self.repo_owner}/{self.repo_name}/{endpoint}"
    
    def _get_raw_url(self, path: str) -> str:
        """Constrói URL para arquivo raw no GitHub."""
        branch = settings.github_release_branch
        return f"{self.GITHUB_RAW_BASE}/{self.repo_owner}/{self.repo_name}/{branch}/{path}"
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compara duas versões X.Y.Z. Returns -1, 0, 1."""
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
    
    @retry(max_attempts=3, delay=2, exceptions=(requests.RequestException,))
    def _fetch_release_json(self) -> Optional[Dict[str, Any]]:
        """Busca o arquivo release.json via URL raw do GitHub."""
        try:
            url = self._get_raw_url("release.json")
            
            logger.info(f"Buscando release.json: {url}")
            
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout_seconds)
            
            if response.status_code == 404:
                logger.info("release.json não encontrado no repositório")
                return None
            
            response.raise_for_status()
            
            release_data = response.json()
            logger.info(f"release.json obtido: versão {release_data.get('versao', 'unknown')}")
            
            return release_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar release.json: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao processar release.json: {e}")
            return None
    
    def check_for_updates(self, channel: Optional[GitHubChannel] = None) -> Dict[str, Any]:
        """
        Verifica se existe uma nova versão disponível no GitHub.
        
        Returns:
            Dict: has_update, current_version, latest_version, download_url,
                  release_notes, release_size, release_date, error, channel
        """
        self._status = UpdateStatus.CHECKING
        
        ch = channel or self.channel
        result = {
            "has_update": False,
            "current_version": self.current_version,
            "latest_version": self.current_version,
            "download_url": None,
            "release_notes": "",
            "release_size": 0,
            "release_date": "",
            "sha256": "",
            "error": None,
            "channel": ch.value,
        }
        
        if not self.enabled:
            result["error"] = "Atualizações automáticas desabilitadas"
            self._status = UpdateStatus.IDLE
            return result
        
        if not self.repo_owner or not self.repo_name:
            result["error"] = "Configuração do GitHub incompleta"
            self._status = UpdateStatus.IDLE
            return result
        
        try:
            # Buscar release.json
            release_data = self._fetch_release_json()
            
            if not release_data:
                result["error"] = "Não foi possível obter informações de release"
                self._status = UpdateStatus.IDLE
                return result
            
            # Verificar se o canal corresponde
            release_channel = release_data.get("canal", "stable")
            if release_channel != ch.value and ch != GitHubChannel.STABLE:
                logger.info(f"Release do canal {release_channel} não corresponde ao canal solicitado {ch.value}")
            
            latest_version = release_data.get("versao", self.current_version)
            result["latest_version"] = latest_version
            result["release_notes"] = release_data.get("release_notes", "")
            result["release_date"] = release_data.get("data", "")
            result["release_size"] = release_data.get("installer_size", 0)
            result["sha256"] = release_data.get("sha256", "")
            result["download_url"] = release_data.get("github_download_url", "")
            
            # Verificar se há atualização
            if self._compare_versions(latest_version, self.current_version) > 0:
                result["has_update"] = True
                logger.info(f"Nova versão disponível: {self.current_version} → {latest_version}")
            else:
                logger.info(f"Sistema atualizado: {self.current_version}")
            
            self._status = UpdateStatus.IDLE
            return result
            
        except Exception as e:
            result["error"] = f"Erro ao verificar atualizações: {e}"
            logger.error(result["error"])
            self._status = UpdateStatus.FAILED
            return result
    
    def download_update(
        self,
        download_url: str,
        expected_sha256: str = "",
        progress_callback: Optional[Callable[[int, int, float, float], None]] = None
    ) -> Tuple[bool, str]:
        """
        Baixa o instalador com callback de progresso detalhado.
        Suporta HTTPS com autenticação via token.
        
        Args:
            download_url: URL do instalador
            expected_sha256: Hash SHA-256 esperado para validação
            progress_callback: função(downloaded, total, speed_bps, eta_seconds)
        
        Returns:
            Tuple (success, file_path ou error_message)
        """
        self._status = UpdateStatus.DOWNLOADING
        
        try:
            downloads_dir = settings.dados_dir / "downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
            file_path = downloads_dir / filename
            
            logger.info(f"Iniciando download: {download_url}")
            
            # Preparar headers com autenticação se necessário
            headers = {}
            if self.token:
                headers["Authorization"] = f"token {self.token}"
            
            response = requests.get(
                download_url,
                stream=True,
                timeout=self.timeout_seconds * 3,
                headers=headers
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
            
            logger.info(f"Download concluído: {file_path} ({downloaded} bytes)")
            
            # Validar integridade se SHA-256 fornecido
            if expected_sha256:
                self._status = UpdateStatus.VERIFYING
                if not self._verify_integrity(file_path, expected_sha256):
                    file_path.unlink()  # Remover arquivo corrompido
                    self._status = UpdateStatus.FAILED
                    return False, "Arquivo corrompido: SHA-256 mismatch"
            
            self._status = UpdateStatus.IDLE
            return True, str(file_path)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão no download: {e}"
            logger.error(error_msg)
            self._status = UpdateStatus.FAILED
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro ao baixar atualização: {e}"
            logger.error(error_msg)
            self._status = UpdateStatus.FAILED
            return False, error_msg
    
    def _verify_integrity(self, file_path: Path, expected_sha256: str) -> bool:
        """Verifica integridade do arquivo baixado via SHA-256."""
        try:
            if not file_path.exists() or file_path.stat().st_size == 0:
                return False
            
            sha256 = self._calculate_sha256(file_path)
            if sha256.lower() != expected_sha256.lower():
                logger.error(f"SHA256 mismatch: esperado={expected_sha256}, obtido={sha256}")
                return False
            
            logger.info(f"Integridade verificada: SHA-256 correto")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            return False
    
    def _calculate_sha256(self, file_path: Path) -> str:
        """Calcula hash SHA-256 de um arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def create_pre_update_backup(self) -> Tuple[bool, str]:
        """Cria backup do banco e configurações antes de instalar."""
        try:
            backup_dir = settings.dados_dir / "backups_pre_update"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = backup_dir / f"pre_update_{timestamp}"
            backup_subdir.mkdir(parents=True, exist_ok=True)
            
            # Backup do banco
            db_path = settings.db_path
            if db_path.exists():
                shutil.copy2(str(db_path), str(backup_subdir / db_path.name))
            
            # Backup das configurações
            config_path = settings.config_path
            if config_path.exists():
                shutil.copy2(str(config_path), str(backup_subdir / config_path.name))
            
            # Backup do versao.json
            if self.version_file.exists():
                shutil.copy2(str(self.version_file), str(backup_subdir / "versao.json"))
            
            logger.info(f"Backup pré-update criado em: {backup_subdir}")
            return True, str(backup_subdir)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup pré-update: {e}")
            return False, str(e)
    
    def rollback_update(self, backup_path: str) -> Tuple[bool, str]:
        """Restaura backup em caso de falha na atualização."""
        self._status = UpdateStatus.ROLLBACK
        
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False, "Backup não encontrado"
            
            logger.info(f"Iniciando rollback de: {backup_dir}")
            
            # Restaurar banco
            db_backup = backup_dir / settings.db_path.name
            if db_backup.exists():
                shutil.copy2(str(db_backup), str(settings.db_path))
                logger.info("Banco de dados restaurado")
            
            # Restaurar configurações
            config_backup = backup_dir / settings.config_path.name
            if config_backup.exists():
                shutil.copy2(str(config_backup), str(settings.config_path))
                logger.info("Configurações restauradas")
            
            # Restaurar versao.json
            version_backup = backup_dir / "versao.json"
            if version_backup.exists():
                shutil.copy2(str(version_backup), str(self.version_file))
                logger.info("Versão restaurada")
            
            self._status = UpdateStatus.IDLE
            logger.info("Rollback concluído com sucesso")
            return True, "Rollback concluído com sucesso"
            
        except Exception as e:
            error_msg = f"Erro no rollback: {e}"
            logger.error(error_msg)
            self._status = UpdateStatus.FAILED
            return False, error_msg
    
    def install_update(self, installer_path: str) -> Tuple[bool, str]:
        """
        Instala a atualização com backup de segurança e rollback automático.
        
        Args:
            installer_path: Caminho do instalador .exe
        
        Returns:
            Tuple (success, message)
        """
        self._status = UpdateStatus.INSTALLING
        
        try:
            installer_file = Path(installer_path)
            if not installer_file.exists():
                return False, "Instalador não encontrado"
            
            # Criar backup pré-instalação
            backup_ok, backup_path = self.create_pre_update_backup()
            if not backup_ok:
                logger.warning(f"Backup falhou: {backup_path}")
                # Continuar mesmo sem backup
            
            logger.info(f"Iniciando instalação: {installer_path}")
            
            if sys.platform == "win32":
                # Iniciar instalador de forma assíncrona
                subprocess.Popen([str(installer_file)], shell=False)
                
                self._status = UpdateStatus.SUCCESS
                return True, "Instalador iniciado. O aplicativo será fechado."
            else:
                self._status = UpdateStatus.FAILED
                return False, "Sistema de atualização disponível apenas para Windows."
            
        except Exception as e:
            error_msg = f"Erro ao instalar atualização: {e}"
            logger.error(error_msg)
            
            # Tentar rollback
            if backup_ok:
                logger.info("Tentando rollback após falha...")
                rollback_ok, rollback_msg = self.rollback_update(backup_path)
                if not rollback_ok:
                    logger.error(f"Rollback falhou: {rollback_msg}")
            
            self._status = UpdateStatus.FAILED
            return False, error_msg
    
    def get_status(self) -> UpdateStatus:
        """Retorna o status atual do serviço de atualização."""
        return self._status
    
    def get_update_history(self, limit: int = 20) -> List[Dict[str, str]]:
        """Retorna histórico de atualizações do GitHub."""
        try:
            history_dir = settings.dados_dir / "github_releases_history"
            if not history_dir.exists():
                return []
            
            history = []
            for file_path in sorted(history_dir.glob("release_*.json"), reverse=True)[:limit]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        history.append({
                            "versao": data.get("version", ""),
                            "data": data.get("release_date", ""),
                            "notas": data.get("release_notes", ""),
                            "canal": data.get("channel", ""),
                            "status": data.get("status", ""),
                        })
                except Exception as e:
                    logger.error(f"Erro ao ler arquivo de histórico {file_path}: {e}")
            
            return history
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []


# Instância singleton do serviço
github_update_service = GitHubUpdateService()
