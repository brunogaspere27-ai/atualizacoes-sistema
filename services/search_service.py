"""
Serviço de busca e indexação.
"""
import threading
import re
from utils.logger import Logger


class SearchService:
    """Indexa e busca registros."""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.logger = Logger()
        self._index = {}
        self._index_lock = threading.Lock()
        self._stop_words = {
            "de", "da", "do", "dos", "das", "a", "o", "as", "os", "e", "em",
            "no", "na", "nos", "nas", "por", "para", "com", "sem", "sobre"
        }
    
    def index_records(self, table, records, fields):
        """Indexa registros para busca."""
        try:
            with self._index_lock:
                if table not in self._index:
                    self._index[table] = {}
                
                for record in records:
                    doc_id = str(record.get("id", ""))
                    text = " ".join(str(record.get(f, "")) for f in fields)
                    tokens = self._tokenize(text)
                    self._index[table][doc_id] = tokens
        except Exception as e:
            self.logger.log(f"Erro na indexação: {e}", "error")
    
    def search(self, table, query):
        """Busca registros indexados."""
        try:
            with self._index_lock:
                if table not in self._index:
                    return []
                
                query_tokens = self._tokenize(query)
                results = []
                
                for doc_id, tokens in self._index[table].items():
                    score = sum(1 for t in query_tokens if t in tokens)
                    if score > 0:
                        results.append({"id": doc_id, "score": score})
                
                return sorted(results, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            self.logger.log(f"Erro na busca: {e}", "error")
            return []
    
    def _tokenize(self, text):
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if t not in self._stop_words and len(t) > 2]