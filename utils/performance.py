"""
Monitoramento de performance.
"""
import os
import time
import sqlite3
from contextlib import contextmanager


def performance_diagnostics_enabled():
    return os.getenv("DIAGNOSTICO_PERFORMANCE", "").lower() in {"1", "true", "on", "yes"}


@contextmanager
def timed_block(nome, extra=""):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        if performance_diagnostics_enabled():
            print(f"[perf] {nome}: {elapsed:.2f} ms")


def safe_after(widget, delay_ms, callback):
    """Versão segura de after para PySide6."""
    try:
        # PySide6 não tem winfo_exists (é Tkinter)
        if widget and not widget.isVisible():
            return False
        from PySide6.QtCore import QTimer
        QTimer.singleShot(delay_ms, callback)
        return True
    except Exception:
        return False


def sqlite_connection_factory(db_path):
    """Factory para criar conexões SQLite com configurações otimizadas."""
    def connect():
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        return conn
    return connect
