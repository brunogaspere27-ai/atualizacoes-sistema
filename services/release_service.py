"""
Serviço de gerenciamento de releases.
"""
import os
import requests
from utils.logger import Logger


class ReleaseService:
    """Gerencia releases do sistema."""
    
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({"Authorization": f"token {self.github_token}"})
        self.logger = Logger()
    
    def create_release(self, repo, tag, name, body):
        """Cria uma release no GitHub."""
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            data = {"tag_name": tag, "name": name, "body": body}
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            self.logger.log(f"Release {tag} criada", "success")
            return response.json()
        except Exception as e:
            self.logger.log(f"Erro ao criar release: {e}", "error")
            return None