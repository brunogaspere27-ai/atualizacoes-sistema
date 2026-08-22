"""
Sistema de logging.
"""
import os
import logging
import sys
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
            fh = logging.FileHandler(
                os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log"),
                encoding="utf-8"
            )
            fh.setLevel(logging.DEBUG)

            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def log(self, message, level="info"):
        levels = {
            "debug": self.logger.debug,
            "info": self.logger.info,
            "success": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error
        }
        levels.get(level, self.logger.info)(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)


# Função get_logger para compatibilidade com main_pyside6.py
_loggers = {}

def get_logger(name="SistemaAtualizacoes"):
    """Retorna um logger configurado."""
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name].logger
