"""
Serviço de gerenciamento de Turmas com CRUD completo
Gerencia turmas de treino com horários
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from src.utils.firebase_config import FirebaseConfig
from src.utils.readonly_guard import ensure_writable

class TurmasService:
    """Serviço para operações CRUD de Turmas"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.firebase_config = FirebaseConfig()
        self.db = self.firebase_config.db
        self.collection = self.db.collection('turmas')
    
    def criar_turma(self, dados_turma: Dict[str, Any]) -> str:
        """
        Cria uma nova turma no Firestore
        
        Args:
            dados_turma: Dicionário com dados da turma
            {
                'nome': str (obrigatório) - Ex: "KIDS", "ADULTA (Matutino)"
                'horarioInicio': str (obrigatório) - Ex: "18:00"
                'horarioFim': str (obrigatório) - Ex: "19:10"
                'diasSemana': list (opcional) - Ex: ["segunda", "quarta", "sexta"]
                'descricao': str (opcional)
                'ativo': bool (opcional, padrão True)
            }
            
        Returns:
            str: ID do documento criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            ensure_writable("criar turma")

            # Validar dados obrigatórios
            if 'nome' not in dados_turma or not dados_turma['nome'].strip():
                raise ValueError("Nome da turma é obrigatório")
            
            if 'horarioInicio' not in dados_turma or not dados_turma['horarioInicio'].strip():
                raise ValueError("Horário de início é obrigatório")
            
            if 'horarioFim' not in dados_turma or not dados_turma['horarioFim'].strip():
                raise ValueError("Horário de término é obrigatório")
            
            # Preparar dados para criação
            turma_data = {
                'nome': dados_turma['nome'].strip(),
                'horarioInicio': dados_turma['horarioInicio'].strip(),
                'horarioFim': dados_turma['horarioFim'].strip(),
                'ativo': dados_turma.get('ativo', True)
            }
            
            # Adicionar campos opcionais
            if 'diasSemana' in dados_turma and dados_turma['diasSemana']:
                turma_data['diasSemana'] = dados_turma['diasSemana']
            
            if 'descricao' in dados_turma and dados_turma['descricao'].strip():
                turma_data['descricao'] = dados_turma['descricao'].strip()
            
            # Adicionar timestamps
            turma_data.update({
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            })
            
            # Criar documento no Firestore
            doc_ref = self.collection.add(turma_data)[1]
            
            return doc_ref.id
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"Erro ao criar turma: {str(e)}")
    
    def listar_turmas(self, apenas_ativas: bool = True) -> List[Dict[str, Any]]:
        """
        Lista todas as turmas
        
        Args:
            apenas_ativas: Se True, retorna apenas turmas ativas
            
        Returns:
            List[Dict]: Lista de turmas com seus dados e IDs
        """
        try:
            # Buscar todas as turmas e filtrar/ordenar em memória
            # para evitar necessidade de índice composto no Firestore
            turmas = []
            for doc in self.collection.stream():
                turma_data = doc.to_dict()
                turma_data['id'] = doc.id
                
                # Filtrar turmas ativas se necessário
                if apenas_ativas and not turma_data.get('ativo', True):
                    continue
                    
                turmas.append(turma_data)
            
            # Ordenar por nome em memória
            turmas.sort(key=lambda x: x.get('nome', ''))
            
            return turmas
            
        except Exception as e:
            raise Exception(f"Erro ao listar turmas: {str(e)}")
    
    def buscar_turma(self, turma_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma turma específica por ID
        
        Args:
            turma_id: ID da turma
            
        Returns:
            Dict com dados da turma ou None se não encontrada
        """
        try:
            doc = self.collection.document(turma_id).get()
            
            if doc.exists:
                turma_data = doc.to_dict()
                turma_data['id'] = doc.id
                return turma_data
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar turma: {str(e)}")
    
    def atualizar_turma(self, turma_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza uma turma existente
        
        Args:
            turma_id: ID da turma
            dados_atualizacao: Dados para atualizar
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            ensure_writable("atualizar turma")
            # Adicionar timestamp de atualização
            dados_atualizacao['updatedAt'] = SERVER_TIMESTAMP
            
            # Atualizar documento
            self.collection.document(turma_id).update(dados_atualizacao)
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar turma: {str(e)}")
    
    def excluir_turma(self, turma_id: str, exclusao_logica: bool = True) -> bool:
        """
        Exclui uma turma (física ou logicamente)
        
        Args:
            turma_id: ID da turma
            exclusao_logica: Se True, apenas marca como inativa
            
        Returns:
            bool: True se excluído com sucesso
        """
        try:
            ensure_writable("excluir turma")
            if exclusao_logica:
                # Exclusão lógica - apenas desativa
                self.collection.document(turma_id).update({
                    'ativo': False,
                    'updatedAt': SERVER_TIMESTAMP
                })
            else:
                # Exclusão física - remove do banco
                self.collection.document(turma_id).delete()
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao excluir turma: {str(e)}")
    
    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        """
        Busca turmas por nome (parcial)
        
        Args:
            nome: Nome ou parte do nome para buscar
            
        Returns:
            List[Dict]: Lista de turmas encontradas
        """
        try:
            # Buscar todas as turmas e filtrar no client-side
            # (Firestore não suporta LIKE nativo)
            todas_turmas = self.listar_turmas(apenas_ativas=False)
            
            nome_lower = nome.lower().strip()
            turmas_encontradas = [
                turma for turma in todas_turmas
                if nome_lower in turma.get('nome', '').lower()
            ]
            
            return turmas_encontradas
            
        except Exception as e:
            raise Exception(f"Erro ao buscar turmas: {str(e)}")
    
    def obter_nomes_turmas(self) -> List[str]:
        """
        Retorna apenas os nomes das turmas ativas
        
        Returns:
            List[str]: Lista de nomes de turmas
        """
        try:
            turmas = self.listar_turmas(apenas_ativas=True)
            return [turma['nome'] for turma in turmas]
            
        except Exception as e:
            raise Exception(f"Erro ao obter nomes de turmas: {str(e)}")
