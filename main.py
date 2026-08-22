"""
Entry point alternativo (CLI).
"""
import sys
from utils.logger import Logger


def main():
    logger = Logger()
    logger.log("Sistema iniciado (CLI mode)", "info")
    print("Sistema de Atualizações v2.0")
    print("Use main_pyside6.py para interface gráfica")


if __name__ == "__main__":
    main()