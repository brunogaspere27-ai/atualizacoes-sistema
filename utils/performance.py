from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterable, Optional

from utils.logger import get_logger

logger = get_logger("performance")

_ENV_KEYS = ("DIAGNOSTICO_PERFORMANCE", "CW_DIAGNOSTICO_PERFORMANCE")
_thread_local = threading.local()


def performance_diagnostics_enabled() -> bool:
    return any(os.getenv(key, "").strip().lower() in {"1", "true", "on", "yes"} for key in _ENV_KEYS)


def _safe_params_preview(params: Any) -> str:
    if params in (None, (), [], {}):
        return ""
    try:
        text = repr(params)
    except Exception:
        return ""
    return text if len(text) <= 240 else f"{text[:237]}..."


def log_timing(nome: str, elapsed_ms: float, extra: str = "") -> None:
    if not performance_diagnostics_enabled():
        return
    complemento = f" | {extra}" if extra else ""
    logger.info(f"[perf] {nome}: {elapsed_ms:.2f} ms{complemento}")


@contextmanager
def timed_block(nome: str, extra: str = ""):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        log_timing(nome, elapsed_ms, extra=extra)


def mark_ui_event(widget: Any, nome: str) -> None:
    if not performance_diagnostics_enabled():
        return
    if not hasattr(widget, "_perf_marks"):
        widget._perf_marks = {}
    widget._perf_marks[nome] = time.perf_counter()


def log_ui_event(widget: Any, inicio: str, nome: str, extra: str = "") -> None:
    if not performance_diagnostics_enabled():
        return
    start = getattr(widget, "_perf_marks", {}).get(inicio)
    if start is None:
        return
    elapsed_ms = (time.perf_counter() - start) * 1000
    log_timing(nome, elapsed_ms, extra=extra)


def safe_after(widget: Any, delay_ms: int, callback) -> bool:
    try:
        if not widget.winfo_exists():
            return False
        widget.after(delay_ms, callback)
        return True
    except Exception:
        return False


def _sql_depth() -> int:
    return getattr(_thread_local, "sql_depth", 0)


def _set_sql_depth(depth: int) -> None:
    _thread_local.sql_depth = depth


class LoggingCursor(sqlite3.Cursor):
    def execute(self, sql: str, parameters: Iterable[Any] = ()):
        if not performance_diagnostics_enabled():
            return super().execute(sql, parameters)

        start = time.perf_counter()
        depth = _sql_depth()
        _set_sql_depth(depth + 1)
        try:
            return super().execute(sql, parameters)
        finally:
            _set_sql_depth(depth)
            elapsed_ms = (time.perf_counter() - start) * 1000
            sql_preview = " ".join(str(sql).split())
            if len(sql_preview) > 220:
                sql_preview = f"{sql_preview[:217]}..."
            params_preview = _safe_params_preview(parameters)
            extra = sql_preview if not params_preview else f"{sql_preview} | params={params_preview}"
            log_timing("sql.execute", elapsed_ms, extra=extra)

    def executemany(self, sql: str, seq_of_parameters):
        if not performance_diagnostics_enabled():
            return super().executemany(sql, seq_of_parameters)

        start = time.perf_counter()
        try:
            return super().executemany(sql, seq_of_parameters)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            sql_preview = " ".join(str(sql).split())
            if len(sql_preview) > 220:
                sql_preview = f"{sql_preview[:217]}..."
            log_timing("sql.executemany", elapsed_ms, extra=sql_preview)

    def executescript(self, sql_script: str):
        if not performance_diagnostics_enabled():
            return super().executescript(sql_script)

        start = time.perf_counter()
        try:
            return super().executescript(sql_script)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            script_preview = " ".join(str(sql_script).split())
            if len(script_preview) > 220:
                script_preview = f"{script_preview[:217]}..."
            log_timing("sql.executescript", elapsed_ms, extra=script_preview)


class LoggingConnection(sqlite3.Connection):
    def cursor(self, factory: Optional[type] = None):
        return super().cursor(factory=factory or LoggingCursor)


def sqlite_connection_factory():
    return LoggingConnection if performance_diagnostics_enabled() else sqlite3.Connection
