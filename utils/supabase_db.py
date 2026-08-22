"""
Gerenciador Supabase.
"""
import os
from supabase import create_client


class SupabaseManager:
    """Interface com Supabase."""
    
    def __init__(self, url=None, key=None):
        self.supabase_url = url or os.getenv("SUPABASE_URL")
        self.supabase_key = key or os.getenv("SUPABASE_KEY")
        self._client = None
    
    def _get_client(self):
        if not self._client:
            self._client = create_client(self.supabase_url, self.supabase_key)
        return self._client
    
    def check_connection(self):
        try:
            client = self._get_client()
            return client is not None
        except Exception:
            return False
    
    @property
    def auth(self):
        return self._get_client().auth
    
    @property
    def table(self, name):
        return self._get_client().table(name)