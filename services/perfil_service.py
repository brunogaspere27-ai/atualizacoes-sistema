"""
Perfil Service - CW Transportadora

Gerenciamento de perfil de usuário: foto, nome, senha.
Avatares armazenados em assets/avatars/ com resize automático 256x256.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple

from config.settings import settings
from utils.database._conexao import conectar
from utils.logger import get_logger

logger = get_logger(__name__)

# Avatar directory
AVATARS_DIR = Path(settings.resource_path("assets/avatars"))
AVATAR_SIZE = 256

# Predefined avatar background colors (deterministic from name hash)
AVATAR_COLORS = [
    "#E5484D", "#3FB950", "#58A6FF", "#BC8CFF",
    "#D29922", "#39C5CF", "#FB7185", "#818CF8",
    "#F97316", "#14B8A6", "#EC4899", "#6366F1",
]


def _get_avatar_color(name: str) -> str:
    """Deterministic color from name hash."""
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return AVATAR_COLORS[h % len(AVATAR_COLORS)]


def _ensure_column():
    """Ensure foto_path column exists in usuarios table."""
    try:
        with conectar() as conn:
            cursor = conn.execute("PRAGMA table_info(usuarios)")
            cols = [row[1] for row in cursor.fetchall()]
            if "foto_path" not in cols:
                conn.execute("ALTER TABLE usuarios ADD COLUMN foto_path TEXT DEFAULT NULL")
                conn.commit()
                logger.info("Added foto_path column to usuarios table")
    except Exception as e:
        logger.warning(f"Could not ensure foto_path column: {e}")


# Run on import
_ensure_column()


def get_avatar_path(usuario_id: int) -> Optional[str]:
    """Get the avatar file path for a user. Returns None if no photo."""
    try:
        with conectar() as conn:
            row = conn.execute(
                "SELECT foto_path FROM usuarios WHERE id = ?", (usuario_id,)
            ).fetchone()
            if row and row[0]:
                path = Path(row[0])
                if path.exists():
                    return str(path)
    except Exception as e:
        logger.warning(f"Error getting avatar path: {e}")
    return None


def save_avatar(usuario_id: int, image_path: str) -> bool:
    """
    Save avatar for a user.
    - Resize to 256x256
    - Compress as JPEG
    - Store in assets/avatars/
    - Update DB path
    """
    try:
        from PIL import Image
    except ImportError:
        logger.error("PIL/Pillow not installed - cannot process avatar images")
        return False

    try:
        AVATARS_DIR.mkdir(parents=True, exist_ok=True)

        # Open and resize
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)

        # Save as compressed JPEG
        filename = f"avatar_{usuario_id}.jpg"
        dest = AVATARS_DIR / filename
        img.save(str(dest), "JPEG", quality=85, optimize=True)

        # Update DB
        with conectar() as conn:
            conn.execute(
                "UPDATE usuarios SET foto_path = ? WHERE id = ?",
                (str(dest), usuario_id)
            )
            conn.commit()

        logger.info(f"Avatar saved for user {usuario_id}: {dest}")
        return True

    except Exception as e:
        logger.error(f"Error saving avatar: {e}")
        return False


def remove_avatar(usuario_id: int) -> bool:
    """Remove avatar file and clear DB path."""
    try:
        path = get_avatar_path(usuario_id)
        if path and os.path.exists(path):
            os.remove(path)

        with conectar() as conn:
            conn.execute(
                "UPDATE usuarios SET foto_path = NULL WHERE id = ?", (usuario_id,)
            )
            conn.commit()

        logger.info(f"Avatar removed for user {usuario_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing avatar: {e}")
        return False


def get_initials(nome: str) -> str:
    """Generate initials from full name."""
    parts = nome.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif parts:
        return parts[0][0].upper()
    return "U"


def get_avatar_color_for_name(nome: str) -> str:
    """Get deterministic avatar color for a name."""
    return _get_avatar_color(nome)


def update_nome(usuario_id: int, novo_nome: str) -> bool:
    """Update user's full name."""
    try:
        with conectar() as conn:
            conn.execute(
                "UPDATE usuarios SET nome_completo = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (novo_nome, usuario_id)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating name: {e}")
        return False


def get_user_info(usuario_id: int) -> Optional[dict]:
    """Get user info for profile screen."""
    try:
        with conectar() as conn:
            row = conn.execute(
                "SELECT id, nome_completo, usuario, nivel_acesso, criado_em, foto_path "
                "FROM usuarios WHERE id = ?", (usuario_id,)
            ).fetchone()
            if row:
                return {
                    "id": row[0],
                    "nome_completo": row[1],
                    "usuario": row[2],
                    "nivel": row[3],
                    "criado_em": row[4],
                    "foto_path": row[5],
                }
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
    return None


# Singleton-like service instance
class PerfilService:
    """Service facade for profile operations."""

    def get_avatar_path(self, usuario_id: int) -> Optional[str]:
        return get_avatar_path(usuario_id)

    def save_avatar(self, usuario_id: int, image_path: str) -> bool:
        return save_avatar(usuario_id, image_path)

    def remove_avatar(self, usuario_id: int) -> bool:
        return remove_avatar(usuario_id)

    def get_initials(self, nome: str) -> str:
        return get_initials(nome)

    def get_avatar_color(self, nome: str) -> str:
        return get_avatar_color_for_name(nome)

    def update_nome(self, usuario_id: int, novo_nome: str) -> bool:
        return update_nome(usuario_id, novo_nome)

    def get_user_info(self, usuario_id: int) -> Optional[dict]:
        return get_user_info(usuario_id)


perfil_service = PerfilService()
