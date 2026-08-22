"""
Serviço de atualização.
"""
import json
import os

CANAL_ESTAVEL = "estavel"
CANAL_BETA = "beta"
CANAL_DEV = "dev"


class UpdateService:
    def __init__(self):
        self.channel = CANAL_ESTAVEL
    
    def check_for_updates(self):
        return {"has_update": False, "version": "2.0.0"}
    
    def obter_versao_instalada(self):
        versao = "2.0.0"
        data = "01/01/2024"
        if os.path.exists("versao.json"):
            try:
                with open("versao.json", "r") as f:
                    data_json = json.load(f)
                    versao = data_json.get("versao", versao)
                    data = data_json.get("data", data)
            except Exception:
                pass
        return {"versao": versao, "data": data, "nome": "CW Transportadora"}
    
    def obter_historico_versoes(self, limit=20):
        return [
            {"versao": "2.0.0", "data": "01/01/2024", "notas": "Versão inicial", "prerelease": False}
        ]
    
    def download_and_install(self, version, canal=CANAL_ESTAVEL):
        return True


update_service = UpdateService()
