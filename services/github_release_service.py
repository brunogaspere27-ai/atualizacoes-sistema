"""
Serviço de releases do GitHub (alternativo).
"""
import os
import requests
from utils.logger import Logger


class GitHubReleaseService:
    """Busca informações de releases."""
    
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({"Authorization": f"token {self.github_token}"})
        self.logger = Logger()
    
    def get_releases(self, owner, repo):
        """Lista releases."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.log(f"Erro ao listar releases: {e}", "error")
            return []