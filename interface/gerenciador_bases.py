import json
import os
from typing import List, Dict, Optional

class GerenciadorBases:
    """Classe para gerenciar as bases do sistema"""
    
    def __init__(self, arquivo_bases: str = "bases.json"):
        self.arquivo_bases = arquivo_bases
        self.bases = self.carregar_bases()
    
    def carregar_bases(self) -> List[Dict]:
        """Carrega as bases do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_bases):
                with open(self.arquivo_bases, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('bases', [])
            else:
                # Criar arquivo padrão se não existir
                bases_padrao = [
                    {
                        "nome": "RIOENERGY",
                        "url": "https://mxmhml-rioenergy.rsmbrasil.com.br/?grupo=RIOENERGYHOM",
                        "descricao": "Base Rio Energy"
                    },
                    {
                        "nome": "ACAL003",
                        "url": "https://mxmhml-acal003.rsmbrasil.com.br/?grupo=ACAL003HOM",
                        "descricao": "Base Acal 003"
                    }
                ]
                self.salvar_bases(bases_padrao)
                return bases_padrao
        except Exception as e:
            print(f"Erro ao carregar bases: {str(e)}")
            return []
    
    def salvar_bases(self, bases: List[Dict]) -> bool:
        """Salva as bases no arquivo JSON"""
        try:
            data = {"bases": bases}
            with open(self.arquivo_bases, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.bases = bases
            return True
        except Exception as e:
            print(f"Erro ao salvar bases: {str(e)}")
            return False
    
    def obter_bases(self) -> List[Dict]:
        """Retorna a lista de bases"""
        return self.bases
    
    def obter_base_por_nome(self, nome: str) -> Optional[Dict]:
        """Retorna uma base específica pelo nome"""
        for base in self.bases:
            if base['nome'].upper() == nome.upper():
                return base
        return None
    
    def adicionar_base(self, nome: str, url: str, descricao: str = "") -> bool:
        """Adiciona uma nova base"""
        # Verificar se a base já existe
        if self.obter_base_por_nome(nome):
            return False
        
        nova_base = {
            "nome": nome.upper(),
            "url": url,
            "descricao": descricao
        }
        
        self.bases.append(nova_base)
        return self.salvar_bases(self.bases)
    
    def remover_base(self, nome: str) -> bool:
        """Remove uma base pelo nome"""
        base_original = len(self.bases)
        self.bases = [base for base in self.bases if base['nome'].upper() != nome.upper()]
        
        if len(self.bases) < base_original:
            return self.salvar_bases(self.bases)
        return False
    
    def editar_base(self, nome_original: str, novo_nome: str, nova_url: str, nova_descricao: str) -> bool:
        """Edita uma base existente"""
        for base in self.bases:
            if base['nome'].upper() == nome_original.upper():
                base['nome'] = novo_nome.upper()
                base['url'] = nova_url
                base['descricao'] = nova_descricao
                return self.salvar_bases(self.bases)
        return False
    
    def obter_nomes_bases(self) -> List[str]:
        """Retorna apenas os nomes das bases"""
        return [base['nome'] for base in self.bases] 