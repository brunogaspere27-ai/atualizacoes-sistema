"""
Serviço de auditoria de integridade.
"""
import re
import threading
from datetime import datetime
from utils.logger import Logger


class AuditoriaService:
    """Audita integridade dos dados."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = Logger()
        self._lock = threading.Lock()
        self._integrity_rules = {
            "usuarios": {
                "email": {"required": True, "type": "email", "description": "Email válido obrigatório"},
                "nome": {"required": True, "description": "Nome obrigatório"}
            }
        }
    
    def run_full_audit(self):
        """Executa auditoria completa."""
        try:
            with self._lock:
                results = {}
                for table in self._integrity_rules:
                    records = self._get_table_records(table)
                    issues = self._check_integrity(table, records)
                    results[table] = issues
                return results
        except Exception as e:
            self.logger.log(f"Erro na auditoria: {e}", "error")
            return {}
    
    def _get_table_records(self, table):
        try:
            return self.db.query_all(table)
        except Exception:
            return []
    
    def _check_integrity(self, table, records):
        issues = []
        for record in records:
            for field, rules in self._integrity_rules.get(table, {}).items():
                value = record.get(field)
                if rules.get("required") and (value is None or value == ""):
                    issues.append({
                        "tipo": "campo_obrigatorio",
                        "tabela": table,
                        "campo": field,
                        "registro_id": record.get("id"),
                        "valor": value,
                        "regra": rules.get("description", "Campo obrigatório")
                    })
                if rules.get("type") == "email" and value:
                    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                        issues.append({
                            "tipo": "email_invalido",
                            "tabela": table,
                            "campo": field,
                            "registro_id": record.get("id"),
                            "valor": value,
                            "regra": "Email inválido"
                        })
        return issues