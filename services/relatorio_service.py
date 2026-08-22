"""
Serviço de relatórios.
"""


class RelatorioService:
    def gerar_relatorio(self, tipo, filtros):
        return b""
    
    def exportar_excel(self, dados, caminho):
        return True
    
    def exportar_pdf(self, dados, caminho):
        return True


relatorio_service = RelatorioService()
