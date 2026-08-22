"""
Sistema de logging.
"""
import os
import logging
from datetime import datetime


class Logger:
    """Logger customizado."""
    
    def __init__(self, name="SistemaAtualizacoes", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            # File handler
            fh = logging.FileHandler(
                os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log"),
                encoding="utf-8"
            )
            fh.setLevel(logging.DEBUG)
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
    
    def log(self, message, level="info"):
        """Registra mensagem."""
        levels = {
            "debug": self.logger.debug,
            "info": self.logger.info,
            "success": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error
        }
        levels.get(level, self.logger.info)(message)