"""
Serviço de notas/manifestos.
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from utils.database.notas import (
    listar_manifestos as db_listar_manifestos,
    listar_notas_por_manifesto as db_listar_notas_por_manifesto,
    criar_manifesto as db_criar_manifesto,
    apagar_manifesto as db_apagar_manifesto,
    salvar_nota,
    nota_existe,
)
from utils.database.viagens import apagar_viagem
from utils.database import calcular_resumo_notas


class NotasService:
    def listar_manifestos(self, tipo_periodo="Geral", mes=None, ano=None):
        return db_listar_manifestos(tipo_periodo, mes, ano)
    
    def listar_notas_por_manifesto(self, manifesto_id):
        return db_listar_notas_por_manifesto(manifesto_id)
    
    def importar_manifesto(self, caminho: str) -> Dict[str, Any]:
        """
        Importa um arquivo TXT de manifesto.
        Formato esperado: linhas com dados separados por tabulação ou pipe.
        """
        encontradas = 0
        salvas = 0
        duplicadas = 0
        
        # Criar manifesto no banco
        nome_arquivo = os.path.basename(caminho)
        manifesto_id = db_criar_manifesto(nome_arquivo)
        
        with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            encontradas += 1
            
            # Tenta parsear linha com campos separados por | ou tab
            campos = linha.split('|') if '|' in linha else linha.split('\t')
            
            if len(campos) < 3:
                continue
            
            nota = {
                "manifesto_id": manifesto_id,
                "chave_nfe": campos[0].strip() if len(campos) > 0 else "",
                "numero_cte": campos[1].strip() if len(campos) > 1 else "",
                "remetente_nome": campos[2].strip() if len(campos) > 2 else "",
                "destinatario_nome": campos[3].strip() if len(campos) > 3 else "",
                "origem": campos[4].strip() if len(campos) > 4 else "",
                "destino": campos[5].strip() if len(campos) > 5 else "",
                "valor_mercadoria": float(campos[6]) if len(campos) > 6 and campos[6].strip() else 0,
                "valor_frete": float(campos[7]) if len(campos) > 7 and campos[7].strip() else 0,
                "peso": float(campos[8]) if len(campos) > 8 and campos[8].strip() else 0,
                "uf_origem": "",
                "uf_destino": "",
                "status": "Disponível"
            }
            
            chave = nota.get("chave_nfe") or nota.get("numero_cte")
            if nota_existe(chave):
                duplicadas += 1
                continue
            
            if salvar_nota(nota):
                salvas += 1
        
        return {
            "arquivo": nome_arquivo,
            "encontradas": encontradas,
            "salvas": salvas,
            "duplicadas": duplicadas
        }
    
    def exportar_manifesto_xml(self, manifesto_id: int, caminho_destino: str) -> bool:
        """
        Exporta um manifesto e suas notas para XML no formato padrão de transporte.
        """
        try:
            notas = db_listar_notas_por_manifesto(manifesto_id)
            if not notas:
                return False
            
            # Buscar info do manifesto
            from utils.database._conexao import conectar
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT nome_arquivo, data_importacao FROM manifestos WHERE id = ?", (manifesto_id,))
            manifesto_row = cursor.fetchone()
            conn.close()
            
            manifesto_nome = manifesto_row[0] if manifesto_row else f"MANIFESTO_{manifesto_id}"
            data_manifesto = manifesto_row[1] if manifesto_row else datetime.now().isoformat()
            
            root = ET.Element("manifesto")
            ET.SubElement(root, "id").text = str(manifesto_id)
            ET.SubElement(root, "nome_arquivo").text = manifesto_nome
            ET.SubElement(root, "data_geracao").text = datetime.now().isoformat()
            ET.SubElement(root, "data_importacao").text = str(data_manifesto)
            
            notas_elem = ET.SubElement(root, "notas")
            
            for nota in notas:
                # nota: (id, chave_nfe, numero_cte, remetente, destinatario, origem, destino, valor_mercadoria, valor_frete, peso, status)
                n_elem = ET.SubElement(notas_elem, "nota")
                ET.SubElement(n_elem, "id").text = str(nota[0])
                ET.SubElement(n_elem, "chave_nfe").text = str(nota[1] or "")
                ET.SubElement(n_elem, "numero_cte").text = str(nota[2] or "")
                ET.SubElement(n_elem, "remetente").text = str(nota[3] or "")
                ET.SubElement(n_elem, "destinatario").text = str(nota[4] or "")
                ET.SubElement(n_elem, "origem").text = str(nota[5] or "")
                ET.SubElement(n_elem, "destino").text = str(nota[6] or "")
                ET.SubElement(n_elem, "valor_mercadoria").text = str(nota[7] or 0)
                ET.SubElement(n_elem, "valor_frete").text = str(nota[8] or 0)
                ET.SubElement(n_elem, "peso").text = str(nota[9] or 0)
                ET.SubElement(n_elem, "status").text = str(nota[10] or "")
            
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(caminho_destino, encoding='utf-8', xml_declaration=True)
            return True
            
        except Exception as e:
            print(f"[notas_service] Erro ao exportar XML: {e}")
            return False
    
    def apagar_manifesto(self, manifesto_id):
        return db_apagar_manifesto(manifesto_id)
    
    def apagar_viagem(self, viagem_id):
        return apagar_viagem(viagem_id)
    
    def cadastrar_caminhao(self, placa, modelo, motorista, capacidade, media):
        from utils.database import cadastrar_caminhao
        cadastrar_caminhao(placa, modelo, motorista, capacidade, media)
    
    def calcular_resumo_notas(self, notas_ids):
        return calcular_resumo_notas(notas_ids)


notas_service = NotasService()
