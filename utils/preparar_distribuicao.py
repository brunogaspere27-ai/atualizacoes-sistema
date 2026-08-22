"""
Prepara base para distribuição.
"""
import os
import shutil
from datetime import datetime


def preparar_base_para_distribuicao(criar_backup=True):
    """Prepara base zerada para distribuição."""
    if criar_backup:
        backup_dir = "backups/dist"
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(backup_dir, f"backup_{timestamp}.db")
    return None
