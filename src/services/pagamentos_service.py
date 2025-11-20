"""
PagamentosService - Gerenciamento de pagamentos mensais
Integração com Firestore para collection /pagamentos/{alunoId_YYYY_MM}
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from src.utils.firebase_config import get_firestore_client

class PagamentosService:
    """Serviço para gerenciamento de pagamentos mensais"""
    
    # Constantes para dias de vencimento válidos
    VENCIMENTOS_VALIDOS = [10, 15, 25]
    CARENCIA_PADRAO = 3  # Dias de carência para inadimplência
    
    # Mapeamento de vencimento para dia de cobrança (devedor)
    DIAS_COBRANCA = {
        10: 1,   # Vencimento dia 10 → entra como devedor dia 01
        15: 5,   # Vencimento dia 15 → entra como devedor dia 05
        25: 15   # Vencimento dia 25 → entra como devedor dia 15
    }
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.db = get_firestore_client()
        self.collection_name = 'pagamentos'
    
    def calcular_status_pagamento(self, ano: int, mes: int, data_vencimento: int = 15, 
                                   carencia_dias: int = None, data_referencia: date = None) -> str:
        """
        Calcula o status de um pagamento baseado nas regras de negócio
        
        Regras:
        - Devedor (a cobrar): Entra no dia de cobrança conforme vencimento
          - Vencimento dia 10 → devedor a partir do dia 01
          - Vencimento dia 15 → devedor a partir do dia 05
          - Vencimento dia 25 → devedor a partir do dia 15
        
        - Inadimplente (em atraso): Após vencimento + carência
          - Carência padrão: 3 dias
        
        Args:
            ano: Ano do pagamento
            mes: Mês do pagamento
            data_vencimento: Dia do vencimento (10, 15 ou 25)
            carencia_dias: Dias de carência (padrão: 3)
            data_referencia: Data para cálculo (padrão: hoje)
        
        Returns:
            str: Status calculado ('devedor', 'inadimplente' ou 'pendente')
        """
        if carencia_dias is None:
            carencia_dias = self.CARENCIA_PADRAO
        
        if data_referencia is None:
            data_referencia = date.today()
        
        # Validar vencimento
        if data_vencimento not in self.VENCIMENTOS_VALIDOS:
            data_vencimento = 15  # Usar padrão se inválido
        
        # Data do vencimento
        data_venc = date(ano, mes, data_vencimento)
        
        # Data de início da cobrança (quando vira devedor)
        dia_cobranca = self.DIAS_COBRANCA.get(data_vencimento, 5)
        data_cobranca = date(ano, mes, dia_cobranca)
        
        # Data de inadimplência (vencimento + carência)
        data_inadimplencia = data_venc + timedelta(days=carencia_dias)
        
        # Calcular status
        if data_referencia >= data_inadimplencia:
            return 'inadimplente'
        elif data_referencia >= data_cobranca:
            return 'devedor'
        else:
            return 'pendente'  # Ainda não entrou em cobrança
    
    def criar_pagamento(self, dados_pagamento: Dict[str, Any]) -> str:
        """
        Cria um novo pagamento mensal
        
        Args:
            dados_pagamento: Dados do pagamento com campos obrigatórios:
                - alunoId: ID do aluno
                - ano: Ano do pagamento 
                - mes: Mês do pagamento (1-12)
                - valor: Valor do pagamento
                - status: "pago" | "devedor" | "inadimplente" | "ausente"
                - dataVencimento: Dia do vencimento (10, 15 ou 25) - opcional, padrão 15
                - carenciaDias: Dias de carência - opcional, padrão 3
                - exigivel: boolean (DEPRECATED - usar status ao invés)
                - alunoNome: nome do aluno (denormalizado)
        
        Returns:
            str: ID do documento criado (alunoId_YYYY_MM)
        
        Raises:
            ValueError: Se dados obrigatórios estão ausentes
            Exception: Se erro ao criar no Firestore
        """
        # Validar dados obrigatórios (exigivel agora é opcional para compatibilidade)
        campos_obrigatorios = ['alunoId', 'ano', 'mes', 'valor', 'status']
        for campo in campos_obrigatorios:
            if campo not in dados_pagamento or dados_pagamento[campo] is None:
                raise ValueError(f"Campo obrigatório ausente: {campo}")
        
        # Validar valores
        if dados_pagamento['mes'] < 1 or dados_pagamento['mes'] > 12:
            raise ValueError("Mês deve estar entre 1 e 12")
        
        if dados_pagamento['valor'] <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        if dados_pagamento['status'] not in ['pago', 'devedor', 'inadimplente', 'ausente']:
            raise ValueError("Status deve ser: pago, devedor, inadimplente ou ausente")
        
        # Validar dia de vencimento se fornecido
        data_vencimento = dados_pagamento.get('dataVencimento', 15)
        if data_vencimento not in self.VENCIMENTOS_VALIDOS:
            raise ValueError(f"Data de vencimento deve ser: {self.VENCIMENTOS_VALIDOS}")
        
        # Carência padrão se não fornecida
        carencia_dias = dados_pagamento.get('carenciaDias', self.CARENCIA_PADRAO)
        
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
            'dataVencimento': data_vencimento,
            'carenciaDias': carencia_dias,
            'createdAt': agora,
            'updatedAt': agora
        }
        
        # Manter campo exigivel para compatibilidade retroativa
        if 'exigivel' in dados_pagamento:
            documento['exigivel'] = dados_pagamento['exigivel']
        else:
            # Auto-calcular exigivel baseado no status (para compatibilidade)
            documento['exigivel'] = dados_pagamento['status'] in ['devedor', 'inadimplente']
        
        # Adicionar campos opcionais
        if 'alunoNome' in dados_pagamento:
            documento['alunoNome'] = dados_pagamento['alunoNome']
        
        # Calcular e adicionar data de atraso (quando deve entrar em inadimplência)
        if dados_pagamento['status'] in ['devedor', 'inadimplente']:
            data_atraso = date(ano, mes, data_vencimento) + timedelta(days=carencia_dias)
            documento['dataAtraso'] = data_atraso.strftime('%Y-%m-%d')
        
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
    
    def marcar_como_devedor(self, pagamento_id: str) -> bool:
        """
        Marca um pagamento como devedor (a cobrar)
        
        Args:
            pagamento_id: ID do pagamento
        
        Returns:
            bool: True se marcado como devedor
        """
        return self.atualizar_pagamento(pagamento_id, {'status': 'devedor'})
    
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
    
    def obter_devedores(self, ym: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de pagamentos em status devedor (a cobrar)
        
        Args:
            ym: Filtrar por mês específico (YYYY-MM), se None pega todos
        
        Returns:
            Lista de pagamentos em status devedor
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
            
            devedores = []
            for doc in docs:
                pagamento = doc.to_dict()
                pagamento['id'] = doc.id
                
                # Filtrar apenas status devedor
                if pagamento.get('status') == 'devedor':
                    devedores.append(pagamento)
            
            # Ordenar por ym (mais recente primeiro)
            devedores.sort(key=lambda x: x.get('ym', ''), reverse=True)
            
            return devedores
            
        except Exception as e:
            raise Exception(f"Erro ao obter devedores: {str(e)}")
    
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
            devedores = [p for p in pagamentos_mes if p['status'] == 'devedor']
            inadimplentes = [p for p in pagamentos_mes if p['status'] == 'inadimplente']
            ausentes = [p for p in pagamentos_mes if p['status'] == 'ausente']
            
            receita_total = sum(p['valor'] for p in pagos)
            valor_devedores = sum(p['valor'] for p in devedores)
            valor_inadimplencia = sum(p['valor'] for p in inadimplentes)
            
            # Total exigível = devedores + inadimplentes
            total_exigivel = len(devedores) + len(inadimplentes)
            valor_total_exigivel = valor_devedores + valor_inadimplencia
            
            return {
                'ym': ym,
                'total_pagamentos': total_pagamentos,
                'total_pagos': len(pagos),
                'total_devedores': len(devedores),
                'total_inadimplentes': len(inadimplentes),
                'total_ausentes': len(ausentes),
                'total_exigivel': total_exigivel,
                'receita_total': receita_total,
                'valor_devedores': valor_devedores,
                'valor_inadimplencia': valor_inadimplencia,
                'valor_total_exigivel': valor_total_exigivel,
                'taxa_inadimplencia': (len(inadimplentes) / max(1, total_pagamentos - len(ausentes))) * 100,
                'taxa_cobranca': (total_exigivel / max(1, total_pagamentos - len(ausentes))) * 100,
                'detalhes': {
                    'pagos': pagos,
                    'devedores': devedores,
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
                - Cada aluno pode ter 'dataVencimento' (10, 15 ou 25)
        
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
                    # Obter dia de vencimento do aluno (padrão: 15)
                    data_vencimento = aluno.get('dataVencimento', 15)
                    
                    # Calcular status inicial baseado na data atual
                    status_inicial = self.calcular_status_pagamento(ano, mes, data_vencimento)
                    
                    # Se ainda está 'pendente', criar como 'devedor' (será atualizado depois)
                    if status_inicial == 'pendente':
                        status_inicial = 'devedor'
                    
                    # Criar pagamento automático
                    dados_pagamento = {
                        'alunoId': aluno['id'],
                        'alunoNome': aluno.get('nome', 'N/A'),
                        'ano': ano,
                        'mes': mes,
                        'valor': aluno.get('valor_plano', 150.0),
                        'status': status_inicial,
                        'dataVencimento': data_vencimento,
                        'carenciaDias': self.CARENCIA_PADRAO
                    }
                    
                    pagamento_id = self.criar_pagamento(dados_pagamento)
                    pagamentos_criados.append(pagamento_id)
            
            return pagamentos_criados
            
        except Exception as e:
            raise Exception(f"Erro ao gerar pagamentos do mês: {str(e)}")
    
    def listar_pagamentos_por_aluno(self, aluno_id: str) -> list:
        """
        Lista todos os pagamentos de um aluno específico
        
        Args:
            aluno_id: ID do aluno
            
        Returns:
            Lista de pagamentos do aluno ordenados por data (mais recente primeiro)
        """
        try:
            if not aluno_id:
                return []
            
            # Buscar todos os pagamentos do aluno
            query = self.db.collection(self.collection_name).where(
                filter=FieldFilter('alunoId', '==', aluno_id)
            )
            
            docs = query.stream()
            
            pagamentos = []
            for doc in docs:
                pagamento = doc.to_dict()
                pagamento['id'] = doc.id
                pagamentos.append(pagamento)
            
            # Ordenar por ym (mais recente primeiro)
            pagamentos.sort(key=lambda x: x.get('ym', ''), reverse=True)
            
            return pagamentos
            
        except Exception as e:
            raise Exception(f"Erro ao buscar pagamentos do aluno: {str(e)}")