"""
Configurações do sistema.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.configuracoes = {
            "tema": "Aurora Dark",
            "supabase_url": os.getenv("SUPABASE_URL", ""),
            "supabase_key": os.getenv("SUPABASE_KEY", ""),
            "github_token": os.getenv("GITHUB_TOKEN", ""),
            "github_repo_owner": os.getenv("GITHUB_REPO_OWNER", ""),
            "github_repo_name": os.getenv("GITHUB_REPO_NAME", ""),
        }
        self.supabase_enabled = bool(self.configuracoes.get("supabase_url"))
        self.intervalo_sync_ms = 300000  # 5 minutos
        self.github_use_cdn = False
        self.enable_auto_update = False
        self.db_path = Path("data/cw_transportadora.db")
        self.dados_dir = Path("data")
        self.backup_auto_dir = Path("backups/auto")
        self.backup_dir = Path("backups")
        self.logs_dir = Path("logs")
    
    def reload(self):
        load_dotenv(override=True)
        self.configuracoes["supabase_url"] = os.getenv("SUPABASE_URL", "")
        self.configuracoes["supabase_key"] = os.getenv("SUPABASE_KEY", "")
        self.configuracoes["github_token"] = os.getenv("GITHUB_TOKEN", "")
        self.supabase_enabled = bool(self.configuracoes.get("supabase_url"))
    
    def resource_path(self, relative_path):
        base_path = Path(__file__).parent.parent
        return base_path / relative_path


settings = Settings()
