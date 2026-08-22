"""
Serviço de perfil do usuário.
"""
import os
from pathlib import Path


class PerfilService:
    def __init__(self):
        self.avatar_dir = Path("assets/avatars")
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
    
    def get_avatar_path(self, user_id):
        """Retorna caminho do avatar do usuário."""
        try:
            avatar_path = self.avatar_dir / f"user_{user_id}.png"
            if avatar_path.exists():
                return str(avatar_path)
            return None
        except Exception as e:
            print(f"[perfil_service] Erro ao obter avatar: {e}")
            return None
    
    def _ensure_column(self):
        """Garante que coluna foto_path existe."""
        pass  # SQLite local não precisa disso
    
    def salvar_avatar(self, user_id, caminho_origem):
        """Salva avatar do usuário."""
        try:
            import shutil
            destino = self.avatar_dir / f"user_{user_id}.png"
            shutil.copy2(caminho_origem, destino)
            return str(destino)
        except Exception as e:
            print(f"[perfil_service] Erro ao salvar avatar: {e}")
            return None


perfil_service = PerfilService()
