"""
Serviço de atualização GitHub.
"""


class GitHubUpdateService:
    def check_for_updates(self):
        return {"has_update": False, "version": "2.0.0", "download_url": None}


github_update_service = GitHubUpdateService()
