"""
Serviço de gerenciamento de Alunos com CRUD completo
Baseado no FIRESTORE_SCHEMA.md
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import streamlit as st
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from src.utils.firebase_config import FirebaseConfig
from src.utils.readonly_guard import ensure_writable
from src.utils.operational_scope import should_apply_operational_scope, aluno_is_operational

class AlunosService:
    """Serviço para operações CRUD de Alunos"""

    @staticmethod
    def _normalize_nome(nome: Any) -> str:
        """Normaliza nome para sempre persistir algo não-vazio."""
        value = str(nome).strip() if nome is not None else ""
        return value if value else "(Sem nome)"
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.firebase_config = FirebaseConfig()
        self.db = self.firebase_config.db
        self.collection = self.db.collection('alunos')
    
    def criar_aluno(self, dados_aluno_ou_nome, telefone: str = "", email: str = "", 
                   endereco: str = "", vencimento_dia: int = 5, turma: str = "",
                   plano_id: str = "") -> str:
        """
        Cria um novo aluno no Firestore
        
        Args:
            dados_aluno_ou_nome: Dict com dados do aluno OU string com nome
            telefone: Telefone de contato (se usar método antigo)
            email: Email de contato (se usar método antigo)
            endereco: Endereço completo (se usar método antigo)
            vencimento_dia: Dia do vencimento (1-28)
            turma: Turma/horário do aluno (se usar método antigo)
            plano_id: ID do plano vinculado (se usar método antigo)
            
        Returns:
            str: ID do documento criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            ensure_writable("criar aluno")

            # Se recebeu um dicionário, extrair os dados
            if isinstance(dados_aluno_ou_nome, dict):
                dados = dados_aluno_ou_nome
                nome = self._normalize_nome(dados.get('nome', ''))
                telefone = dados.get('contato', {}).get('telefone', '') if isinstance(dados.get('contato'), dict) else ''
                email = dados.get('contato', {}).get('email', '') if isinstance(dados.get('contato'), dict) else ''
                endereco = dados.get('endereco', '')
                vencimento_dia = dados.get('vencimentoDia', 5)
                turma = dados.get('turma', '')
                plano_id = dados.get('planoId', '')
                status = dados.get('status', 'ativo')
                ativo_desde = dados.get('ativoDesde', date.today().strftime('%Y-%m-%d'))
            else:
                # Método antigo - dados_aluno_ou_nome é o nome
                nome = self._normalize_nome(dados_aluno_ou_nome)
                status = 'ativo'
                ativo_desde = date.today().strftime('%Y-%m-%d')
            
            if not (1 <= vencimento_dia <= 28):
                raise ValueError("Dia de vencimento deve estar entre 1 e 28")
            
            # Preparar dados do aluno
            aluno_data = {
                'nome': nome,
                'contato': {
                    'telefone': telefone.strip() if telefone else "",
                    'email': email.strip() if email else ""
                },
                'endereco': endereco.strip() if endereco else "",
                'status': status if status in ['ativo', 'inativo'] else 'ativo',
                'vencimentoDia': vencimento_dia,
                'ativoDesde': ativo_desde if ativo_desde else date.today().strftime('%Y-%m-%d'),
                'turma': turma.strip() if turma else "",
                'graduacao': 'Sem graduação',
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            # Adicionar plano se especificado
            if plano_id and plano_id.strip():
                aluno_data['planoId'] = plano_id.strip()
            
            # Adicionar observações se especificado (quando dados vêm como dict)
            if isinstance(dados_aluno_ou_nome, dict):
                if 'observacoes' in dados_aluno_ou_nome and dados_aluno_ou_nome['observacoes']:
                    aluno_data['observacoes'] = dados_aluno_ou_nome['observacoes'].strip()
                
                # Adicionar responsável legal se especificado
                if 'responsavel' in dados_aluno_ou_nome and dados_aluno_ou_nome['responsavel']:
                    aluno_data['responsavel'] = dados_aluno_ou_nome['responsavel']
            
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

                # In operational UI, hide legacy students entirely.
                if should_apply_operational_scope() and not aluno_is_operational(aluno_data):
                    return None

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

                if should_apply_operational_scope() and not aluno_is_operational(aluno_data):
                    continue

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
            ensure_writable("atualizar aluno")

            # Preparar dados para atualização
            update_data = self._preparar_dados_atualizacao(dados_atualizacao)

            if 'nome' in update_data:
                update_data['nome'] = self._normalize_nome(update_data.get('nome'))
            
            # Adicionar timestamp de atualização
            update_data['updatedAt'] = SERVER_TIMESTAMP
            
            # Atualizar documento
            self.collection.document(aluno_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar aluno: {str(e)}")
            raise e
    
    def vincular_plano(self, aluno_id: str, plano_id: str) -> bool:
        """
        Vincula um aluno a um plano
        
        Args:
            aluno_id: ID do aluno
            plano_id: ID do plano
            
        Returns:
            bool: True se vinculação foi bem-sucedida
        """
        try:
            ensure_writable("vincular plano")
            self.collection.document(aluno_id).update({
                'planoId': plano_id,
                'updatedAt': SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            st.error(f"❌ Erro ao vincular plano: {str(e)}")
            return False
    
    def obter_plano_aluno(self, aluno_id: str) -> Optional[str]:
        """
        Obtém o ID do plano do aluno
        
        Args:
            aluno_id: ID do aluno
            
        Returns:
            Optional[str]: ID do plano ou None se não vinculado
        """
        try:
            aluno = self.buscar_aluno(aluno_id)
            if aluno:
                return aluno.get('planoId')
            return None
        except Exception as e:
            st.error(f"❌ Erro ao obter plano do aluno: {str(e)}")
            return None
    
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
            ensure_writable("inativar aluno")
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
            ensure_writable("reativar aluno")
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
            'turma', 'ativoDesde', 'inativoDesde', 'ultimoPagamentoYm',
            'observacoes', 'responsavel'  # Adicionados campos de observações e responsável legal
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
    
    def buscar_alunos_por_nome(self, termo_busca: str) -> list:
        """
        Busca alunos pelo nome (busca parcial, insensível a maiúsculas)
        
        Args:
            termo_busca: Termo a ser buscado no nome
            
        Returns:
            Lista de alunos que correspondem ao termo de busca
        """
        try:
            if not termo_busca or len(termo_busca.strip()) < 2:
                return []
            
            # Normalizar termo de busca
            termo_normalizado = termo_busca.strip().lower()
            
            # Buscar todos os alunos e filtrar no cliente
            # (Firestore não tem busca full-text nativa)
            todos_alunos = self.listar_alunos()
            
            # Filtrar alunos que contêm o termo no nome
            alunos_encontrados = []
            for aluno in todos_alunos:
                nome = aluno.get('nome', '').lower()
                if termo_normalizado in nome:
                    alunos_encontrados.append(aluno)
            
            # Ordenar por relevância (nomes que começam com o termo primeiro)
            def relevancia(aluno):
                nome = aluno.get('nome', '').lower()
                if nome.startswith(termo_normalizado):
                    return 0  # Maior relevância
                else:
                    return 1  # Menor relevância
            
            alunos_encontrados.sort(key=relevancia)
            
            return alunos_encontrados
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar alunos: {str(e)}")
            return []