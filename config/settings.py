"""
Configurações centralizadas - versão simplificada.
"""
import json
import os
import sys
from pathlib import Path


class Settings:
    def __init__(self):
        self._project_dir = Path(__file__).parent.parent
        self.dados_dir = self._project_dir / "dados"
        self.dados_dir.mkdir(exist_ok=True)
        self.db_path = self.dados_dir / "cw_transportadora.db"
        self.config_path = self._project_dir / "configuracoes.json"
        self.sync_config_path = self.dados_dir / "sync_config.json"
        self.backup_dir = self.dados_dir / "backup_dados"
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_auto_dir = self.backup_dir / "automatico"
        self.backup_auto_dir.mkdir(exist_ok=True)
        self.backup_distribuicao_dir = self.backup_dir / "distribuicao"
        self.backup_distribuicao_dir.mkdir(exist_ok=True)
        self.logs_dir = self.dados_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.assets_dir = self._project_dir / "assets"
        self.pasta_relatorios = "relatorios_gerados"
        self.reports_dir = self._project_dir / self.pasta_relatorios
        self.reports_dir.mkdir(exist_ok=True)
        self.reload()

    def reload(self):
        self._config_json = self._carregar_config_json()

    def resource_path(self, caminho_relativo):
        """Retorna o caminho absoluto para um recurso."""
        try:
            base_path = Path(sys._MEIPASS)
        except Exception:
            base_path = self._project_dir
        return base_path / Path(caminho_relativo)

    def _carregar_config_json(self):
        padrao = {
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
            "tema": "Premium Escuro",
            "cor_tema": "Vermelho",
            "update_server_type": "http",
            "update_server_path": "",
            "update_server_username": "",
            "update_server_password": "",
            "update_channel": "stable",
            "enable_auto_update": True,
            "update_url": "",
            "update_timeout": 10,
            "github_repo_owner": "",
            "github_repo_name": "",
            "github_token": "",
            "github_use_cdn": True,
            "github_release_branch": "main",
        }
        if not self.config_path.exists():
            return padrao.copy()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for chave, valor in padrao.items():
                dados.setdefault(chave, valor)
            return dados
        except Exception:
            return padrao.copy()

    def salvar_configuracoes(self, dados):
        padrao = self._carregar_config_json()
        for chave, valor in dados.items():
            padrao[chave] = valor
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(padrao, f, ensure_ascii=False, indent=4)
        self.reload()
        return padrao

    @property
    def configuracoes(self):
        return self._config_json.copy()

    @property
    def empresa(self):
        return self._config_json.get("empresa", "CW TRANSPORTADORA")

    @property
    def cnpj(self):
        return self._config_json.get("cnpj", "")

    @property
    def cidade(self):
        return self._config_json.get("cidade", "Cascavel")

    @property
    def tema(self):
        return self._config_json.get("tema", "Vermelho CW")

    @property
    def cor_tema(self):
        return self._config_json.get("cor_tema", "Vermelho")

    @property
    def meta_lucro(self):
        try:
            return float(self._config_json.get("meta_lucro", "10000"))
        except (ValueError, TypeError):
            return 10000.0

    @property
    def imposto_percentual(self):
        try:
            return float(self._config_json.get("imposto_percentual", "3"))
        except (ValueError, TypeError):
            return 3.0

    @property
    def alerta_revisao(self):
        try:
            return int(self._config_json.get("alerta_revisao", "8000"))
        except (ValueError, TypeError):
            return 8000

    @property
    def revisao_obrigatoria(self):
        try:
            return int(self._config_json.get("revisao_obrigatoria", "10000"))
        except (ValueError, TypeError):
            return 10000

    @property
    def update_url(self):
        return self._config_json.get("update_url", "")

    @property
    def update_timeout(self):
        return self._config_json.get("update_timeout", 10)

    @property
    def enable_auto_update(self):
        return self._config_json.get("enable_auto_update", True)

    @property
    def github_repo_owner(self):
        return self._config_json.get("github_repo_owner", "")

    @property
    def github_repo_name(self):
        return self._config_json.get("github_repo_name", "")

    @property
    def github_token(self):
        return self._config_json.get("github_token", "")

    @property
    def github_use_cdn(self):
        return self._config_json.get("github_use_cdn", True)

    @property
    def github_release_branch(self):
        return self._config_json.get("github_release_branch", "main")

    @property
    def supabase_enabled(self):
        return False


settings = Settings()
