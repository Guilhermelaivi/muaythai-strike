"""
Serviço de gerenciamento de Planos com CRUD completo
Baseado no FIRESTORE_SCHEMA.md
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from src.utils.firebase_config import FirebaseConfig

class PlanosService:
    """Serviço para operações CRUD de Planos"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.firebase_config = FirebaseConfig()
        self.db = self.firebase_config.db
        self.collection = self.db.collection('planos')
    
    def criar_plano(self, dados_plano: Dict[str, Any]) -> str:
        """
        Cria um novo plano no Firestore
        
        Args:
            dados_plano: Dicionário com dados do plano conforme schema
            
        Returns:
            str: ID do documento criado
            
        Raises:
            Exception: Se houver erro na criação
        """
        try:
            # Validar dados obrigatórios
            self._validar_dados_obrigatorios(dados_plano)
            
            # Preparar dados para criação
            plano_data = self._preparar_dados_plano(dados_plano)
            
            # Adicionar timestamps
            plano_data.update({
                'createdAt': SERVER_TIMESTAMP,
                'updatedAt': SERVER_TIMESTAMP
            })
            
            # Criar documento no Firestore
            doc_ref = self.collection.add(plano_data)[1]
            
            return doc_ref.id
            
        except Exception as e:
            st.error(f"❌ Erro ao criar plano: {str(e)}")
            raise e
    
    def buscar_plano(self, plano_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um plano por ID
        
        Args:
            plano_id: ID do plano
            
        Returns:
            Dict com dados do plano ou None se não encontrado
        """
        try:
            doc = self.collection.document(plano_id).get()
            
            if doc.exists:
                plano_data = doc.to_dict()
                plano_data['id'] = doc.id
                return plano_data
            
            return None
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar plano: {str(e)}")
            raise e
    
    def listar_planos(self, apenas_ativos: Optional[bool] = None, ordenar_por: str = 'nome') -> List[Dict[str, Any]]:
        """
        Lista planos com filtros opcionais
        
        Args:
            apenas_ativos: Filtrar apenas planos ativos (True), inativos (False) ou todos (None)
            ordenar_por: Campo para ordenação (padrão: 'nome')
            
        Returns:
            Lista de dicionários com dados dos planos
        """
        try:
            # Para evitar problemas de índices compostos, fazer filtro e ordenação separadamente
            if apenas_ativos is not None:
                # Consulta apenas com filtro
                query = self.collection.where('ativo', '==', apenas_ativos)
                docs = query.stream()
            else:
                # Consulta apenas com ordenação
                query = self.collection.order_by(ordenar_por)
                docs = query.stream()
            
            planos = []
            for doc in docs:
                plano_data = doc.to_dict()
                plano_data['id'] = doc.id
                planos.append(plano_data)
            
            # Se não houve filtro mas queremos ordenar, ordenar no cliente
            if apenas_ativos is None:
                planos.sort(key=lambda x: x.get(ordenar_por, ''))
            elif apenas_ativos is not None and ordenar_por != 'nome':
                # Se houve filtro E queremos ordenar por outro campo, ordenar no cliente
                planos.sort(key=lambda x: x.get(ordenar_por, ''))
            
            return planos
            
        except Exception as e:
            st.error(f"❌ Erro ao listar planos: {str(e)}")
            raise e
    
    def atualizar_plano(self, plano_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza dados de um plano
        
        Args:
            plano_id: ID do plano
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
            self.collection.document(plano_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar plano: {str(e)}")
            raise e
    
    def inativar_plano(self, plano_id: str) -> bool:
        """
        Marca um plano como inativo
        
        Args:
            plano_id: ID do plano
            
        Returns:
            bool: True se inativação foi bem-sucedida
        """
        try:
            update_data = {
                'ativo': False,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            self.collection.document(plano_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao inativar plano: {str(e)}")
            raise e
    
    def ativar_plano(self, plano_id: str) -> bool:
        """
        Marca um plano como ativo
        
        Args:
            plano_id: ID do plano
            
        Returns:
            bool: True se ativação foi bem-sucedida
        """
        try:
            update_data = {
                'ativo': True,
                'updatedAt': SERVER_TIMESTAMP
            }
            
            self.collection.document(plano_id).update(update_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao ativar plano: {str(e)}")
            raise e
    
    def buscar_por_nome(self, termo_busca: str) -> List[Dict[str, Any]]:
        """
        Busca planos por nome (busca parcial)
        
        Args:
            termo_busca: Termo para buscar no nome
            
        Returns:
            Lista de planos que contêm o termo no nome
        """
        try:
            # Firestore não suporta busca LIKE nativamente
            # Fazer busca no cliente como no AlunosService
            
            planos = self.listar_planos()
            termo_lower = termo_busca.lower()
            
            resultados = [
                plano for plano in planos 
                if termo_lower in plano.get('nome', '').lower()
            ]
            
            return resultados
            
        except Exception as e:
            st.error(f"❌ Erro na busca por nome: {str(e)}")
            raise e
    
    def obter_planos_ativos(self) -> List[Dict[str, Any]]:
        """
        Obtém apenas planos ativos (útil para formulários de seleção)
        
        Returns:
            Lista de planos ativos ordenados por nome
        """
        try:
            return self.listar_planos(apenas_ativos=True, ordenar_por='nome')
        except Exception as e:
            st.error(f"❌ Erro ao obter planos ativos: {str(e)}")
            raise e
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais dos planos
        
        Returns:
            Dict com estatísticas dos planos
        """
        try:
            planos = self.listar_planos()
            
            total = len(planos)
            ativos = len([p for p in planos if p.get('ativo', False)])
            inativos = total - ativos
            
            # Análise de valores
            valores = [p.get('valor', 0) for p in planos if p.get('ativo', False)]
            valor_medio = sum(valores) / len(valores) if valores else 0
            valor_min = min(valores) if valores else 0
            valor_max = max(valores) if valores else 0
            
            # Análise por faixa de preço
            faixas_preco = {
                'Até R$ 50': len([v for v in valores if v <= 50]),
                'R$ 51 - R$ 100': len([v for v in valores if 51 <= v <= 100]),
                'R$ 101 - R$ 200': len([v for v in valores if 101 <= v <= 200]),
                'Acima R$ 200': len([v for v in valores if v > 200])
            }
            
            return {
                'total': total,
                'ativos': ativos,
                'inativos': inativos,
                'valor_medio': valor_medio,
                'valor_min': valor_min,
                'valor_max': valor_max,
                'faixas_preco': faixas_preco
            }
            
        except Exception as e:
            st.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            raise e
    
    def _validar_dados_obrigatorios(self, dados: Dict[str, Any]) -> None:
        """Valida se campos obrigatórios estão presentes"""
        campos_obrigatorios = ['nome', 'valor', 'ativo']
        
        for campo in campos_obrigatorios:
            if campo not in dados or dados[campo] is None:
                raise ValueError(f"Campo obrigatório ausente: {campo}")
        
        # Validações específicas
        if not isinstance(dados['ativo'], bool):
            raise ValueError("Campo 'ativo' deve ser True ou False")
        
        if not isinstance(dados['valor'], (int, float)) or dados['valor'] <= 0:
            raise ValueError("Valor deve ser um número positivo")
        
        if not dados['nome'] or not dados['nome'].strip():
            raise ValueError("Nome do plano não pode estar vazio")
    
    def _preparar_dados_plano(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados do plano seguindo o schema"""
        plano_data = {
            'nome': dados['nome'].strip(),
            'periodicidade': 'mensal',  # Fixo no MVP conforme schema
            'valor': float(dados['valor']),
            'ativo': bool(dados['ativo'])
        }
        
        # Campo opcional
        if 'diaPadraoVencimento' in dados and dados['diaPadraoVencimento']:
            # Validar dia de vencimento
            dia = int(dados['diaPadraoVencimento'])
            if 1 <= dia <= 28:
                plano_data['diaPadraoVencimento'] = dia
            else:
                raise ValueError("Dia padrão de vencimento deve estar entre 1 e 28")
        
        return plano_data
    
    def _preparar_dados_atualizacao(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados para atualização (remove campos não permitidos)"""
        campos_permitidos = [
            'nome', 'valor', 'ativo', 'diaPadraoVencimento'
        ]
        
        update_data = {}
        
        for k, v in dados.items():
            if k in campos_permitidos:
                if k == 'nome' and v:
                    update_data[k] = v.strip()
                elif k == 'valor' and v is not None:
                    update_data[k] = float(v)
                elif k == 'ativo' and v is not None:
                    update_data[k] = bool(v)
                elif k == 'diaPadraoVencimento' and v is not None:
                    dia = int(v)
                    if 1 <= dia <= 28:
                        update_data[k] = dia
                    else:
                        raise ValueError("Dia padrão de vencimento deve estar entre 1 e 28")
        
        # Sempre manter periodicidade como mensal (schema fixo)
        update_data['periodicidade'] = 'mensal'
        
        return update_data