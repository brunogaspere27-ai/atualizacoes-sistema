"""
Configurações centralizadas do sistema CW Transportadora.
Gerencia ambiente, paths, tema e persistência do JSON de configuração.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


class Settings:
    """Classe singleton para gerenciar configurações do sistema."""

    def __init__(self):
        if getattr(sys, "frozen", False):
            # Executável PyInstaller: usar a pasta onde o .exe está,
            # não o diretório temporário de extração (_MEIPASS), para
            # que configuracoes.json, relatórios e backups persistam
            # entre execuções.
            self._project_dir = Path(sys.executable).resolve().parent
        else:
            self._project_dir = Path(__file__).resolve().parent.parent

        load_dotenv(self._project_dir / ".env")
        self.reload()

    def reload(self) -> None:
        self._env_vars = self._carregar_env_vars()
        self._config_json = self._carregar_config_json()

    @property
    def project_dir(self) -> Path:
        return self._project_dir

    @property
    def base_dir(self) -> Path:
        return self.project_dir

    @property
    def local_app_dir(self) -> Path:
        base = os.getenv("LOCALAPPDATA")
        if base:
            return Path(base)
        return self.project_dir / ".localappdata"

    @property
    def dados_dir(self) -> Path:
        path = self.local_app_dir / "CW Transportadora"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def db_path(self) -> Path:
        return self.dados_dir / "cw_transportadora.db"

    @property
    def config_path(self) -> Path:
        return self.project_dir / "configuracoes.json"

    @property
    def sync_config_path(self) -> Path:
        return self.dados_dir / "sync_config.json"

    @property
    def backup_dir(self) -> Path:
        path = self.dados_dir / "backup_dados"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def backup_auto_dir(self) -> Path:
        path = self.backup_dir / "automatico"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def backup_distribuicao_dir(self) -> Path:
        path = self.backup_dir / "distribuicao"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        path = self.dados_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def assets_dir(self) -> Path:
        return self.project_dir / "assets"

    @property
    def reports_dir(self) -> Path:
        path = self.project_dir / self.pasta_relatorios
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resource_path(self, caminho_relativo: str | os.PathLike[str]) -> Path:
        try:
            base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        except Exception:
            base_path = self.project_dir
        return base_path / Path(caminho_relativo)

    def _config_padrao(self) -> Dict[str, Any]:
        return {
            "empresa": "CW TRANSPORTADORA",
            "cnpj": "",
            "telefone": "",
            "email": "",
            "cidade": "Cascavel",
            "uf": "PR",
            "meta_lucro": "10000",
            "imposto_percentual": "3",
            "pasta_relatorios": "relatorios_gerados",
            "alerta_revisao": "8000",
            "revisao_obrigatoria": "10000",
            "tema": "Vermelho CW",
            "cor_tema": "Vermelho",
        }

    def _carregar_config_json(self) -> Dict[str, Any]:
        padrao = self._config_padrao()
        config_path = self.config_path

        if not config_path.exists():
            return padrao.copy()

        try:
            with open(config_path, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except Exception:
            return padrao.copy()

        for chave, valor in padrao.items():
            dados.setdefault(chave, valor)
        return dados

    def _carregar_env_vars(self) -> Dict[str, str]:
        return {
            "SUPABASE_URL": os.getenv("SUPABASE_URL", "").strip(),
            "EMPRESA": os.getenv("EMPRESA", "CW TRANSPORTADORA"),
            "CNPJ": os.getenv("CNPJ", ""),
            "TELEFONE": os.getenv("TELEFONE", ""),
            "EMAIL": os.getenv("EMAIL", ""),
            "CIDADE": os.getenv("CIDADE", "Cascavel"),
            "UF": os.getenv("UF", "PR"),
            "META_LUCRO": os.getenv("META_LUCRO", "10000"),
            "IMPOSTO_PERCENTUAL": os.getenv("IMPOSTO_PERCENTUAL", "3"),
            "ALERTA_REVISAO": os.getenv("ALERTA_REVISAO", "8000"),
            "REVISAO_OBRIGATORIA": os.getenv("REVISAO_OBRIGATORIA", "10000"),
            "PASTA_RELATORIOS": os.getenv("PASTA_RELATORIOS", "relatorios_gerados"),
            "INTERVALO_SYNC_SEGUNDOS": os.getenv("INTERVALO_SYNC_SEGUNDOS", "60"),
        }

    def salvar_configuracoes(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        config_final = self._config_padrao()
        for chave, valor in dados.items():
            config_final[chave] = valor

        with open(self.config_path, "w", encoding="utf-8") as arquivo:
            json.dump(config_final, arquivo, ensure_ascii=False, indent=4)

        self.reload()
        return config_final

    def restaurar_padrao(self) -> Dict[str, Any]:
        return self.salvar_configuracoes(self._config_padrao())

    @property
    def configuracoes(self) -> Dict[str, Any]:
        return self._config_json.copy()

    @property
    def supabase_url(self) -> str:
        return self._env_vars["SUPABASE_URL"]

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url)

    @property
    def empresa(self) -> str:
        return self._config_json.get("empresa", self._env_vars["EMPRESA"])

    @property
    def cnpj(self) -> str:
        return self._config_json.get("cnpj", self._env_vars["CNPJ"])

    @property
    def telefone(self) -> str:
        return self._config_json.get("telefone", self._env_vars["TELEFONE"])

    @property
    def email(self) -> str:
        return self._config_json.get("email", self._env_vars["EMAIL"])

    @property
    def cidade(self) -> str:
        return self._config_json.get("cidade", self._env_vars["CIDADE"])

    @property
    def uf(self) -> str:
        return self._config_json.get("uf", self._env_vars["UF"])

    @property
    def meta_lucro(self) -> float:
        try:
            return float(self._config_json.get("meta_lucro", self._env_vars["META_LUCRO"]))
        except (ValueError, TypeError):
            return 10000.0

    @property
    def imposto_percentual(self) -> float:
        try:
            return float(self._config_json.get("imposto_percentual", self._env_vars["IMPOSTO_PERCENTUAL"]))
        except (ValueError, TypeError):
            return 3.0

    @property
    def alerta_revisao(self) -> int:
        try:
            return int(self._config_json.get("alerta_revisao", self._env_vars["ALERTA_REVISAO"]))
        except (ValueError, TypeError):
            return 8000

    @property
    def revisao_obrigatoria(self) -> int:
        try:
            return int(self._config_json.get("revisao_obrigatoria", self._env_vars["REVISAO_OBRIGATORIA"]))
        except (ValueError, TypeError):
            return 10000

    @property
    def pasta_relatorios(self) -> str:
        return self._config_json.get("pasta_relatorios", self._env_vars["PASTA_RELATORIOS"])

    @property
    def intervalo_sync_segundos(self) -> int:
        try:
            return max(10, int(self._env_vars["INTERVALO_SYNC_SEGUNDOS"]))
        except (ValueError, TypeError):
            return 60

    @property
    def intervalo_sync_ms(self) -> int:
        return self.intervalo_sync_segundos * 1000

    @property
    def tema(self) -> str:
        return self._config_json.get("tema", "Vermelho CW")

    @property
    def cor_tema(self) -> str:
        return self._config_json.get("cor_tema", "Vermelho")

    @property
    def paleta_cores(self) -> Dict[str, Dict[str, str]]:
        return {
            "Vermelho": {
                "principal": "#DC2626",
                "hover": "#B91C1C",
                "sidebar": "#020617",
                "sidebar_card": "#0F172A",
                "fundo": "#F3F4F6",
                "header": "#FFFFFF",
                "texto": "#111827",
                "texto_suave": "#6B7280",
            },
            "Azul": {
                "principal": "#2563EB",
                "hover": "#1D4ED8",
                "sidebar": "#020617",
                "sidebar_card": "#0F172A",
                "fundo": "#F3F4F6",
                "header": "#FFFFFF",
                "texto": "#111827",
                "texto_suave": "#6B7280",
            },
            "Verde": {
                "principal": "#16A34A",
                "hover": "#15803D",
                "sidebar": "#020617",
                "sidebar_card": "#0F172A",
                "fundo": "#F3F4F6",
                "header": "#FFFFFF",
                "texto": "#111827",
                "texto_suave": "#6B7280",
            },
            "Roxo": {
                "principal": "#7C3AED",
                "hover": "#6D28D9",
                "sidebar": "#020617",
                "sidebar_card": "#0F172A",
                "fundo": "#F3F4F6",
                "header": "#FFFFFF",
                "texto": "#111827",
                "texto_suave": "#6B7280",
            },
            "Preto": {
                "principal": "#111827",
                "hover": "#374151",
                "sidebar": "#020617",
                "sidebar_card": "#111827",
                "fundo": "#F3F4F6",
                "header": "#FFFFFF",
                "texto": "#111827",
                "texto_suave": "#6B7280",
            },
        }

    def obter_cores_tema(self) -> Dict[str, str]:
        tema = self.tema
        cor_tema = self.cor_tema
        cores = self.paleta_cores.get(cor_tema, self.paleta_cores["Vermelho"]).copy()

        if tema == "Premium Escuro":
            cores["fundo"] = "#111827"
            cores["header"] = "#1F2937"
            cores["texto"] = "#FFFFFF"
            cores["texto_suave"] = "#D1D5DB"
        elif tema == "Claro":
            cores["fundo"] = "#F8FAFC"
            cores["header"] = "#FFFFFF"
            cores["texto"] = "#111827"
            cores["texto_suave"] = "#6B7280"
        elif tema == "Vermelho CW":
            cores["principal"] = "#DC2626"
            cores["hover"] = "#B91C1C"
            cores["fundo"] = "#F3F4F6"
            cores["header"] = "#FFFFFF"
            cores["texto"] = "#111827"
            cores["texto_suave"] = "#6B7280"

        return cores

    @property
    def update_url(self) -> str:
        """URL para verificação de atualizações."""
        return self._config_json.get("update_url",
            "https://api.github.com/repos/brunogaspere27-ai/bruno/releases/latest")

    @property
    def update_timeout(self) -> int:
        """Timeout em segundos para requisições de atualização."""
        return self._config_json.get("update_timeout", 10)

    @property
    def enable_auto_update(self) -> bool:
        """Habilita verificação automática de atualizações."""
        return self._config_json.get("enable_auto_update", True)


settings = Settings()
