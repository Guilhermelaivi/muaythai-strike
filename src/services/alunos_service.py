"""
Serviço de gerenciamento de Alunos com CRUD completo
Baseado no FIRESTORE_SCHEMA.md
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import streamlit as st
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from src.utils.firebase_config import FirebaseConfig

class AlunosService:
    """Serviço para operações CRUD de Alunos"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.firebase_config = FirebaseConfig()
        self.db = self.firebase_config.db
        self.collection = self.db.collection('alunos')
    
    def criar_aluno(self, dados_aluno: Dict[str, Any]) -> str:
        """
        Cria um novo aluno no Firestore
        
        Args:
            dados_aluno: Dicionário com dados do aluno conforme schema
            
        Returns:
            str: ID do documento criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            # Validar dados obrigatórios
            self._validar_dados_obrigatorios(dados_aluno)
            
            # Preparar dados para criação
            aluno_data = self._preparar_dados_aluno(dados_aluno)
            
            # Adicionar timestamps
            aluno_data.update({
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            })
            
            # Criar documento no Firestore
            doc_ref = self.collection.add(aluno_data)[1]
            
            return doc_ref.id
            
        except Exception as e:
            st.error(f"❌ Erro ao criar aluno: {str(e)}")
            raise e
    
    def buscar_aluno(self, aluno_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um aluno por ID
        
        Args:
            aluno_id: ID do aluno
            
        Returns:
            Dict com dados do aluno ou None se não encontrado
        """
        try:
            doc = self.collection.document(aluno_id).get()
            
            if doc.exists:
                aluno_data = doc.to_dict()
                aluno_data['id'] = doc.id
                return aluno_data
            
            return None
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar aluno: {str(e)}")
            raise e
    
    def listar_alunos(self, status: Optional[str] = None, ordenar_por: str = 'nome') -> List[Dict[str, Any]]:
        """
        Lista alunos com filtros opcionais
        
        Args:
            status: Filtrar por status ('ativo', 'inativo') ou None para todos
            ordenar_por: Campo para ordenação (padrão: 'nome')
            
        Returns:
            Lista de dicionários com dados dos alunos
        """
        try:
            # Para evitar problemas de índices compostos, fazer filtro e ordenação separadamente
            if status:
                # Consulta apenas com filtro
                query = self.collection.where('status', '==', status)
                docs = query.stream()
            else:
                # Consulta apenas com ordenação
                query = self.collection.order_by(ordenar_por)
                docs = query.stream()
            
            alunos = []
            for doc in docs:
                aluno_data = doc.to_dict()
                aluno_data['id'] = doc.id
                alunos.append(aluno_data)
            
            # Se não houve filtro de status mas queremos ordenar, ordenar no cliente
            if not status:
                alunos.sort(key=lambda x: x.get(ordenar_por, ''))
            elif status and ordenar_por != 'nome':
                # Se houve filtro E queremos ordenar por outro campo, ordenar no cliente
                alunos.sort(key=lambda x: x.get(ordenar_por, ''))
            
            return alunos
            
        except Exception as e:
            st.error(f"❌ Erro ao listar alunos: {str(e)}")
            raise e
    
    def atualizar_aluno(self, aluno_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza dados de um aluno
        
        Args:
            aluno_id: ID do aluno
            dados_atualizacao: Dados a serem atualizados
            
        Returns:
            bool: True se atualização foi bem-sucedida
        """
        try:
            # Preparar dados para atualização
            update_data = self._preparar_dados_atualizacao(dados_atualizacao)
            
            # Adicionar timestamp de atualização
            update_data['updatedAt'] = SERVER_TIMESTAMP
            
            # Atualizar documento
            self.collection.document(aluno_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar aluno: {str(e)}")
            raise e
    
    def inativar_aluno(self, aluno_id: str, data_inativacao: Optional[str] = None) -> bool:
        """
        Marca um aluno como inativo
        
        Args:
            aluno_id: ID do aluno
            data_inativacao: Data de inativação (YYYY-MM-DD) ou None para hoje
            
        Returns:
            bool: True se inativação foi bem-sucedida
        """
        try:
            if not data_inativacao:
                data_inativacao = date.today().strftime('%Y-%m-%d')
            
            update_data = {
                'status': 'inativo',
                'inativoDesde': data_inativacao,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            self.collection.document(aluno_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao inativar aluno: {str(e)}")
            raise e
    
    def reativar_aluno(self, aluno_id: str, data_reativacao: Optional[str] = None) -> bool:
        """
        Reativa um aluno inativo
        
        Args:
            aluno_id: ID do aluno
            data_reativacao: Data de reativação (YYYY-MM-DD) ou None para hoje
            
        Returns:
            bool: True se reativação foi bem-sucedida
        """
        try:
            if not data_reativacao:
                data_reativacao = date.today().strftime('%Y-%m-%d')
            
            update_data = {
                'status': 'ativo',
                'ativoDesde': data_reativacao,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            # Remover data de inativação
            self.collection.document(aluno_id).update({
                **update_data,
                'inativoDesde': None
            })
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao reativar aluno: {str(e)}")
            raise e
    
    def buscar_por_nome(self, termo_busca: str) -> List[Dict[str, Any]]:
        """
        Busca alunos por nome (busca parcial)
        
        Args:
            termo_busca: Termo para buscar no nome
            
        Returns:
            Lista de alunos que contêm o termo no nome
        """
        try:
            # Firestore não suporta busca LIKE nativamente
            # Vamos fazer busca por prefix e filtrar no cliente
            # Para busca mais sofisticada, seria necessário usar Algolia ou similar
            
            alunos = self.listar_alunos()
            termo_lower = termo_busca.lower()
            
            resultados = [
                aluno for aluno in alunos 
                if termo_lower in aluno.get('nome', '').lower()
            ]
            
            return resultados
            
        except Exception as e:
            st.error(f"❌ Erro na busca por nome: {str(e)}")
            raise e
    
    def _validar_dados_obrigatorios(self, dados: Dict[str, Any]) -> None:
        """Valida se campos obrigatórios estão presentes"""
        campos_obrigatorios = ['nome', 'status', 'vencimentoDia', 'ativoDesde']
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                raise ValueError(f"Campo obrigatório ausente: {campo}")
        
        # Validações específicas
        if dados['status'] not in ['ativo', 'inativo']:
            raise ValueError("Status deve ser 'ativo' ou 'inativo'")
        
        if not (1 <= dados['vencimentoDia'] <= 28):
            raise ValueError("Dia de vencimento deve estar entre 1 e 28")
    
    def _preparar_dados_aluno(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados do aluno seguindo o schema"""
        aluno_data = {
            'nome': dados['nome'],
            'status': dados['status'],
            'vencimentoDia': int(dados['vencimentoDia']),
            'ativoDesde': dados['ativoDesde']
        }
        
        # Campos opcionais
        if 'contato' in dados:
            aluno_data['contato'] = dados['contato']
        
        if 'endereco' in dados:
            aluno_data['endereco'] = dados['endereco']
        
        if 'turma' in dados:
            aluno_data['turma'] = dados['turma']
        
        if 'inativoDesde' in dados:
            aluno_data['inativoDesde'] = dados['inativoDesde']
        
        if 'ultimoPagamentoYm' in dados:
            aluno_data['ultimoPagamentoYm'] = dados['ultimoPagamentoYm']
        
        return aluno_data
    
    def _preparar_dados_atualizacao(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados para atualização (remove campos não permitidos)"""
        campos_permitidos = [
            'nome', 'contato', 'endereco', 'status', 'vencimentoDia',
            'turma', 'ativoDesde', 'inativoDesde', 'ultimoPagamentoYm'
        ]
        
        return {k: v for k, v in dados.items() if k in campos_permitidos}
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais dos alunos
        
        Returns:
            Dict com estatísticas dos alunos
        """
        try:
            alunos = self.listar_alunos()
            
            total = len(alunos)
            ativos = len([a for a in alunos if a.get('status') == 'ativo'])
            inativos = total - ativos
            
            # Análise por turma
            turmas = {}
            for aluno in alunos:
                turma = aluno.get('turma', 'Sem turma')
                turmas[turma] = turmas.get(turma, 0) + 1
            
            return {
                'total': total,
                'ativos': ativos,
                'inativos': inativos,
                'por_turma': turmas
            }
            
        except Exception as e:
            st.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            raise e