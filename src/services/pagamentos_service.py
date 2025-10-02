"""
PagamentosService - Gerenciamento de pagamentos mensais
Integração com Firestore para collection /pagamentos/{alunoId_YYYY_MM}
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from src.utils.firebase_config import get_firestore_client

class PagamentosService:
    """Serviço para gerenciamento de pagamentos mensais"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.db = get_firestore_client()
        self.collection_name = 'pagamentos'
    
    def criar_pagamento(self, dados_pagamento: Dict[str, Any]) -> str:
        """
        Cria um novo pagamento mensal
        
        Args:
            dados_pagamento: Dados do pagamento com campos obrigatórios:
                - alunoId: ID do aluno
                - ano: Ano do pagamento 
                - mes: Mês do pagamento (1-12)
                - valor: Valor do pagamento
                - status: "pago" | "inadimplente" | "ausente"
                - exigivel: boolean (se conta para cobrança)
                - alunoNome: nome do aluno (denormalizado)
        
        Returns:
            str: ID do documento criado (alunoId_YYYY_MM)
        
        Raises:
            ValueError: Se dados obrigatórios estão ausentes
            Exception: Se erro ao criar no Firestore
        """
        # Validar dados obrigatórios
        campos_obrigatorios = ['alunoId', 'ano', 'mes', 'valor', 'status', 'exigivel']
        for campo in campos_obrigatorios:
            if campo not in dados_pagamento or dados_pagamento[campo] is None:
                raise ValueError(f"Campo obrigatório ausente: {campo}")
        
        # Validar valores
        if dados_pagamento['mes'] < 1 or dados_pagamento['mes'] > 12:
            raise ValueError("Mês deve estar entre 1 e 12")
        
        if dados_pagamento['valor'] <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if dados_pagamento['status'] not in ['pago', 'inadimplente', 'ausente']:
            raise ValueError("Status deve ser: pago, inadimplente ou ausente")
        
        # Gerar ID estável e campo ym
        aluno_id = dados_pagamento['alunoId']
        ano = dados_pagamento['ano']
        mes = dados_pagamento['mes']
        pagamento_id = f"{aluno_id}_{ano:04d}_{mes:02d}"
        ym = f"{ano:04d}-{mes:02d}"
        
        # Preparar documento
        agora = firestore.SERVER_TIMESTAMP
        documento = {
            'alunoId': aluno_id,
            'ano': ano,
            'mes': mes,
            'ym': ym,
            'valor': dados_pagamento['valor'],
            'status': dados_pagamento['status'],
            'exigivel': dados_pagamento['exigivel'],
            'createdAt': agora,
            'updatedAt': agora
        }
        
        # Adicionar campos opcionais
        if 'alunoNome' in dados_pagamento:
            documento['alunoNome'] = dados_pagamento['alunoNome']
        
        # Se status é "pago", adicionar paidAt
        if dados_pagamento['status'] == 'pago':
            documento['paidAt'] = agora
        
        try:
            # Criar documento com merge para permitir upsert
            doc_ref = self.db.collection(self.collection_name).document(pagamento_id)
            doc_ref.set(documento, merge=True)
            return pagamento_id
            
        except Exception as e:
            raise Exception(f"Erro ao criar pagamento: {str(e)}")
    
    def buscar_pagamento(self, pagamento_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um pagamento por ID
        
        Args:
            pagamento_id: ID do pagamento (alunoId_YYYY_MM)
        
        Returns:
            Dict com dados do pagamento ou None se não encontrado
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(pagamento_id)
            doc = doc_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                dados['id'] = doc.id
                return dados
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar pagamento: {str(e)}")
    
    def buscar_pagamento_por_aluno_mes(self, aluno_id: str, ano: int, mes: int) -> Optional[Dict[str, Any]]:
        """
        Busca pagamento de um aluno em um mês específico
        
        Args:
            aluno_id: ID do aluno
            ano: Ano do pagamento
            mes: Mês do pagamento (1-12)
        
        Returns:
            Dict com dados do pagamento ou None se não encontrado
        """
        pagamento_id = f"{aluno_id}_{ano:04d}_{mes:02d}"
        return self.buscar_pagamento(pagamento_id)
    
    def listar_pagamentos(self, filtros: Optional[Dict[str, Any]] = None, 
                         ordenar_por: str = 'ym', ordem: str = 'desc') -> List[Dict[str, Any]]:
        """
        Lista pagamentos com filtros simples (um por vez para evitar índices compostos)
        
        Args:
            filtros: Dicionário com UM filtro por vez (status OU ym OU alunoId, etc.)
            ordenar_por: Campo para ordenação (padrão: ym) 
            ordem: 'asc' ou 'desc' (padrão: desc)
        
        Returns:
            Lista de pagamentos
        """
        try:
            query = self.db.collection(self.collection_name)
            
            # Aplicar apenas UM filtro por vez para evitar índices compostos
            if filtros:
                if 'ym' in filtros:
                    query = query.where(filter=FieldFilter('ym', '==', filtros['ym']))
                elif 'status' in filtros:
                    query = query.where(filter=FieldFilter('status', '==', filtros['status']))
                elif 'alunoId' in filtros:
                    query = query.where(filter=FieldFilter('alunoId', '==', filtros['alunoId']))
                elif 'ano' in filtros:
                    query = query.where(filter=FieldFilter('ano', '==', filtros['ano']))
                elif 'mes' in filtros:
                    query = query.where(filter=FieldFilter('mes', '==', filtros['mes']))
                elif 'exigivel' in filtros:
                    query = query.where(filter=FieldFilter('exigivel', '==', filtros['exigivel']))
            
            # Sem ordenação na query para evitar índices - faremos no cliente
            docs = query.limit(1000).stream()
            
            pagamentos = []
            for doc in docs:
                pagamento = doc.to_dict()
                pagamento['id'] = doc.id
                
                # Aplicar filtros adicionais no cliente se necessário
                incluir = True
                if filtros:
                    for key, value in filtros.items():
                        if key not in ['ym', 'status', 'alunoId', 'ano', 'mes', 'exigivel']:
                            continue
                        # Se já foi filtrado na query, pular
                        if (key in ['ym', 'status', 'alunoId', 'ano', 'mes', 'exigivel'] and 
                            len([k for k in filtros.keys() if k in ['ym', 'status', 'alunoId', 'ano', 'mes', 'exigivel']]) == 1):
                            continue
                        # Filtros adicionais no cliente
                        if pagamento.get(key) != value:
                            incluir = False
                            break
                
                if incluir:
                    pagamentos.append(pagamento)
            
            # Ordenação no cliente
            reverse_order = (ordem == 'desc')
            pagamentos.sort(key=lambda x: x.get(ordenar_por, ''), reverse=reverse_order)
            
            return pagamentos
            
        except Exception as e:
            raise Exception(f"Erro ao listar pagamentos: {str(e)}")
    
    def atualizar_pagamento(self, pagamento_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza um pagamento existente
        
        Args:
            pagamento_id: ID do pagamento
            dados_atualizacao: Dados para atualizar
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Verificar se pagamento existe
            if not self.buscar_pagamento(pagamento_id):
                raise ValueError(f"Pagamento não encontrado: {pagamento_id}")
            
            # Preparar dados de atualização
            dados_atualizacao['updatedAt'] = firestore.SERVER_TIMESTAMP
            
            # Se mudando status para "pago", adicionar paidAt
            if 'status' in dados_atualizacao and dados_atualizacao['status'] == 'pago':
                dados_atualizacao['paidAt'] = firestore.SERVER_TIMESTAMP
            
            # Se mudando status para algo diferente de "pago", remover paidAt
            elif 'status' in dados_atualizacao and dados_atualizacao['status'] != 'pago':
                dados_atualizacao['paidAt'] = firestore.DELETE_FIELD
            
            # Atualizar documento
            doc_ref = self.db.collection(self.collection_name).document(pagamento_id)
            doc_ref.update(dados_atualizacao)
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar pagamento: {str(e)}")
    
    def marcar_como_pago(self, pagamento_id: str, valor_pago: Optional[float] = None) -> bool:
        """
        Marca um pagamento como pago
        
        Args:
            pagamento_id: ID do pagamento
            valor_pago: Valor pago (opcional, se diferente do valor original)
        
        Returns:
            bool: True se marcado como pago
        """
        dados_atualizacao = {
            'status': 'pago',
            'paidAt': firestore.SERVER_TIMESTAMP
        }
        
        if valor_pago is not None:
            dados_atualizacao['valor'] = valor_pago
        
        return self.atualizar_pagamento(pagamento_id, dados_atualizacao)
    
    def marcar_como_inadimplente(self, pagamento_id: str) -> bool:
        """
        Marca um pagamento como inadimplente
        
        Args:
            pagamento_id: ID do pagamento
        
        Returns:
            bool: True se marcado como inadimplente
        """
        return self.atualizar_pagamento(pagamento_id, {'status': 'inadimplente'})
    
    def marcar_como_ausente(self, pagamento_id: str, exigivel: bool = False) -> bool:
        """
        Marca um pagamento como ausente (aluno não veio)
        
        Args:
            pagamento_id: ID do pagamento
            exigivel: Se deve ser cobrado mesmo ausente (padrão: False)
        
        Returns:
            bool: True se marcado como ausente
        """
        return self.atualizar_pagamento(pagamento_id, {
            'status': 'ausente',
            'exigivel': exigivel
        })
    
    def obter_extrato_aluno(self, aluno_id: str, limite_meses: int = 12) -> List[Dict[str, Any]]:
        """
        Obtém extrato de pagamentos de um aluno
        
        Args:
            aluno_id: ID do aluno
            limite_meses: Quantos meses incluir (padrão: 12)
        
        Returns:
            Lista de pagamentos do aluno ordenados por data (mais recente primeiro)
        """
        try:
            # Consulta simples apenas por alunoId para evitar índice composto
            query = (self.db.collection(self.collection_name)
                    .where(filter=FieldFilter('alunoId', '==', aluno_id))
                    .limit(limite_meses * 2))  # Buscar mais para garantir que temos suficientes
            
            docs = query.stream()
            
            extrato = []
            for doc in docs:
                pagamento = doc.to_dict()
                pagamento['id'] = doc.id
                extrato.append(pagamento)
            
            # Ordenar no cliente por ym (mais recente primeiro)
            extrato.sort(key=lambda x: x.get('ym', ''), reverse=True)
            
            # Limitar ao número solicitado
            return extrato[:limite_meses]
            
        except Exception as e:
            raise Exception(f"Erro ao obter extrato: {str(e)}")
    
    def obter_inadimplentes(self, ym: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de pagamentos inadimplentes
        
        Args:
            ym: Filtrar por mês específico (YYYY-MM), se None pega todos
        
        Returns:
            Lista de pagamentos inadimplentes
        """
        try:
            # Para evitar índice composto, fazer consulta simples e filtrar no cliente
            if ym:
                # Consulta apenas por ym
                query = self.db.collection(self.collection_name).where(filter=FieldFilter('ym', '==', ym))
            else:
                # Consulta todos os documentos dos últimos 6 meses
                query = self.db.collection(self.collection_name).limit(1000)
            
            docs = query.stream()
            
            inadimplentes = []
            for doc in docs:
                pagamento = doc.to_dict()
                pagamento['id'] = doc.id
                
                # Filtrar no cliente para evitar índices compostos
                if (pagamento.get('status') == 'inadimplente' and 
                    pagamento.get('exigivel', True)):
                    inadimplentes.append(pagamento)
            
            # Ordenar por ym (mais recente primeiro)
            inadimplentes.sort(key=lambda x: x.get('ym', ''), reverse=True)
            
            return inadimplentes
            
        except Exception as e:
            raise Exception(f"Erro ao obter inadimplentes: {str(e)}")
    
    def obter_estatisticas_mes(self, ym: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de pagamentos de um mês
        
        Args:
            ym: Mês no formato YYYY-MM
        
        Returns:
            Dict com estatísticas do mês
        """
        try:
            # Usar método simplificado de listagem
            pagamentos_mes = self.listar_pagamentos(filtros={'ym': ym})
            
            total_pagamentos = len(pagamentos_mes)
            pagos = [p for p in pagamentos_mes if p['status'] == 'pago']
            inadimplentes = [p for p in pagamentos_mes if p['status'] == 'inadimplente' and p.get('exigivel', True)]
            ausentes = [p for p in pagamentos_mes if p['status'] == 'ausente']
            
            receita_total = sum(p['valor'] for p in pagos)
            valor_inadimplencia = sum(p['valor'] for p in inadimplentes)
            
            return {
                'ym': ym,
                'total_pagamentos': total_pagamentos,
                'total_pagos': len(pagos),
                'total_inadimplentes': len(inadimplentes),
                'total_ausentes': len(ausentes),
                'receita_total': receita_total,
                'valor_inadimplencia': valor_inadimplencia,
                'taxa_inadimplencia': (len(inadimplentes) / max(1, total_pagamentos - len(ausentes))) * 100,
                'detalhes': {
                    'pagos': pagos,
                    'inadimplentes': inadimplentes,
                    'ausentes': ausentes
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas: {str(e)}")
    
    def deletar_pagamento(self, pagamento_id: str) -> bool:
        """
        Deleta um pagamento (usar com cuidado!)
        
        Args:
            pagamento_id: ID do pagamento
        
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            # Verificar se existe
            if not self.buscar_pagamento(pagamento_id):
                raise ValueError(f"Pagamento não encontrado: {pagamento_id}")
            
            # Deletar documento
            doc_ref = self.db.collection(self.collection_name).document(pagamento_id)
            doc_ref.delete()
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao deletar pagamento: {str(e)}")
    
    def gerar_pagamentos_mes(self, ym: str, alunos_ativos: List[Dict[str, Any]]) -> List[str]:
        """
        Gera pagamentos automáticos para um mês baseado nos alunos ativos
        
        Args:
            ym: Mês no formato YYYY-MM
            alunos_ativos: Lista de alunos ativos com dados necessários
        
        Returns:
            Lista de IDs dos pagamentos criados
        """
        try:
            ano, mes = map(int, ym.split('-'))
            pagamentos_criados = []
            
            for aluno in alunos_ativos:
                # Verificar se já existe pagamento para este aluno/mês
                pagamento_existente = self.buscar_pagamento_por_aluno_mes(
                    aluno['id'], ano, mes
                )
                
                if not pagamento_existente:
                    # Criar pagamento automático como inadimplente
                    dados_pagamento = {
                        'alunoId': aluno['id'],
                        'alunoNome': aluno.get('nome', 'N/A'),
                        'ano': ano,
                        'mes': mes,
                        'valor': aluno.get('valor_plano', 150.0),  # Valor padrão se não especificado
                        'status': 'inadimplente',
                        'exigivel': True
                    }
                    
                    pagamento_id = self.criar_pagamento(dados_pagamento)
                    pagamentos_criados.append(pagamento_id)
            
            return pagamentos_criados
            
        except Exception as e:
            raise Exception(f"Erro ao gerar pagamentos do mês: {str(e)}")