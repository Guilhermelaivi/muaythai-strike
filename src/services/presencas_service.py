"""
PresencasService - Gerenciamento de presenças e check-ins
Integração com Firestore para collection /presencas/{presencaId}
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from src.utils.firebase_config import get_firestore_client
import uuid

class PresencasService:
    """Serviço para gerenciamento de presenças e check-ins"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.db = get_firestore_client()
        self.collection_name = 'presencas'
    
    def registrar_presenca(self, aluno_id: str, data_presenca: Optional[date] = None, 
                          presente: bool = True) -> str:
        """
        Registra presença de um aluno
        
        Args:
            aluno_id: ID do aluno
            data_presenca: Data da presença (default: hoje)
            presente: True para presente, False para falta
        
        Returns:
            str: ID do documento criado
        
        Raises:
            ValueError: Se dados obrigatórios estão ausentes
            Exception: Se erro ao registrar no Firestore
        """
        if not aluno_id or not aluno_id.strip():
            raise ValueError("ID do aluno é obrigatório")
        
        # Usar data atual se não especificada
        if data_presenca is None:
            data_presenca = date.today()
        
        # Gerar ID único para presença
        presenca_id = str(uuid.uuid4())
        
        # Formatar campos
        data_str = data_presenca.strftime('%Y-%m-%d')
        ym = data_presenca.strftime('%Y-%m')
        
        # Preparar documento
        agora = firestore.SERVER_TIMESTAMP
        documento = {
            'alunoId': aluno_id.strip(),
            'data': data_str,
            'ym': ym,
            'presente': presente,
            'createdAt': agora,
            'updatedAt': agora
        }
        
        try:
            # Verificar se já existe presença para este aluno na mesma data
            presenca_existente = self.buscar_presenca_por_aluno_data(aluno_id, data_presenca)
            
            if presenca_existente:
                # Atualizar presença existente
                return self.atualizar_presenca(presenca_existente['id'], {'presente': presente})
            else:
                # Criar nova presença
                doc_ref = self.db.collection(self.collection_name).document(presenca_id)
                doc_ref.set(documento)
                return presenca_id
            
        except Exception as e:
            raise Exception(f"Erro ao registrar presença: {str(e)}")
    
    def buscar_presenca(self, presenca_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma presença por ID
        
        Args:
            presenca_id: ID da presença
        
        Returns:
            Dict com dados da presença ou None se não encontrado
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(presenca_id)
            doc = doc_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                dados['id'] = doc.id
                return dados
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar presença: {str(e)}")
    
    def buscar_presenca_por_aluno_data(self, aluno_id: str, data_presenca: date) -> Optional[Dict[str, Any]]:
        """
        Busca presença de um aluno em uma data específica
        
        Args:
            aluno_id: ID do aluno
            data_presenca: Data da presença
        
        Returns:
            Dict com dados da presença ou None se não encontrado
        """
        try:
            data_str = data_presenca.strftime('%Y-%m-%d')
            
            # Consulta simples para evitar índices compostos
            query = (self.db.collection(self.collection_name)
                    .where('alunoId', '==', aluno_id)
                    .limit(100))
            
            docs = query.stream()
            
            # Filtrar por data no cliente
            for doc in docs:
                presenca = doc.to_dict()
                if presenca.get('data') == data_str:
                    presenca['id'] = doc.id
                    return presenca
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar presença por aluno/data: {str(e)}")
    
    def listar_presencas(self, filtros: Optional[Dict[str, Any]] = None, 
                        limite: int = 1000) -> List[Dict[str, Any]]:
        """
        Lista presenças com filtros simples
        
        Args:
            filtros: Dicionário com UM filtro por vez (alunoId OU ym OU data)
            limite: Número máximo de resultados
        
        Returns:
            Lista de presenças
        """
        try:
            query = self.db.collection(self.collection_name)
            
            # Aplicar apenas UM filtro por vez para evitar índices compostos
            if filtros:
                if 'alunoId' in filtros:
                    query = query.where('alunoId', '==', filtros['alunoId'])
                elif 'ym' in filtros:
                    query = query.where('ym', '==', filtros['ym'])
                elif 'data' in filtros:
                    query = query.where('data', '==', filtros['data'])
                elif 'presente' in filtros:
                    query = query.where('presente', '==', filtros['presente'])
            
            # Limitar resultados
            query = query.limit(limite)
            docs = query.stream()
            
            presencas = []
            for doc in docs:
                presenca = doc.to_dict()
                presenca['id'] = doc.id
                
                # Aplicar filtros adicionais no cliente se necessário
                incluir = True
                if filtros:
                    for key, value in filtros.items():
                        if key not in ['alunoId', 'ym', 'data', 'presente']:
                            continue
                        # Se já foi filtrado na query, pular
                        if len([k for k in filtros.keys() if k in ['alunoId', 'ym', 'data', 'presente']]) == 1:
                            continue
                        # Filtros adicionais no cliente
                        if presenca.get(key) != value:
                            incluir = False
                            break
                
                if incluir:
                    presencas.append(presenca)
            
            # Ordenar por data (mais recente primeiro)
            presencas.sort(key=lambda x: x.get('data', ''), reverse=True)
            
            return presencas
            
        except Exception as e:
            raise Exception(f"Erro ao listar presenças: {str(e)}")
    
    def atualizar_presenca(self, presenca_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza uma presença existente
        
        Args:
            presenca_id: ID da presença
            dados_atualizacao: Dados para atualizar
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Verificar se presença existe
            if not self.buscar_presenca(presenca_id):
                raise ValueError(f"Presença não encontrada: {presenca_id}")
            
            # Preparar dados de atualização
            dados_atualizacao['updatedAt'] = firestore.SERVER_TIMESTAMP
            
            # Atualizar documento
            doc_ref = self.db.collection(self.collection_name).document(presenca_id)
            doc_ref.update(dados_atualizacao)
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar presença: {str(e)}")
    
    def marcar_presente(self, aluno_id: str, data_presenca: Optional[date] = None) -> str:
        """
        Marca um aluno como presente em uma data
        
        Args:
            aluno_id: ID do aluno
            data_presenca: Data da presença (default: hoje)
        
        Returns:
            str: ID da presença registrada
        """
        return self.registrar_presenca(aluno_id, data_presenca, presente=True)
    
    def marcar_falta(self, aluno_id: str, data_presenca: Optional[date] = None) -> str:
        """
        Marca um aluno como ausente em uma data
        
        Args:
            aluno_id: ID do aluno
            data_presenca: Data da falta (default: hoje)
        
        Returns:
            str: ID da presença registrada
        """
        return self.registrar_presenca(aluno_id, data_presenca, presente=False)
    
    def obter_presencas_aluno(self, aluno_id: str, limite_dias: int = 30) -> List[Dict[str, Any]]:
        """
        Obtém histórico de presenças de um aluno
        
        Args:
            aluno_id: ID do aluno
            limite_dias: Número de dias para incluir no histórico
        
        Returns:
            Lista de presenças do aluno ordenadas por data (mais recente primeiro)
        """
        try:
            presencas = self.listar_presencas(filtros={'alunoId': aluno_id}, limite=limite_dias * 2)
            
            # Limitar ao número de dias solicitado
            return presencas[:limite_dias]
            
        except Exception as e:
            raise Exception(f"Erro ao obter presenças do aluno: {str(e)}")
    
    def obter_relatorio_mensal(self, ym: str) -> Dict[str, Any]:
        """
        Obtém relatório de presenças de um mês
        
        Args:
            ym: Mês no formato YYYY-MM
        
        Returns:
            Dict com relatório mensal de presenças
        """
        try:
            presencas_mes = self.listar_presencas(filtros={'ym': ym})
            
            # Separar presenças e faltas
            presentes = [p for p in presencas_mes if p.get('presente', False)]
            faltas = [p for p in presencas_mes if not p.get('presente', True)]
            
            # Contar alunos únicos
            alunos_presentes = set(p.get('alunoId') for p in presentes)
            alunos_faltosos = set(p.get('alunoId') for p in faltas)
            todos_alunos = alunos_presentes.union(alunos_faltosos)
            
            # Estatísticas por dia
            presencas_por_dia = {}
            for presenca in presencas_mes:
                data = presenca.get('data', '')
                if data not in presencas_por_dia:
                    presencas_por_dia[data] = {'presentes': 0, 'faltas': 0}
                
                if presenca.get('presente', False):
                    presencas_por_dia[data]['presentes'] += 1
                else:
                    presencas_por_dia[data]['faltas'] += 1
            
            # Calcular médias
            total_dias_com_treino = len(presencas_por_dia)
            media_presencas_dia = len(presentes) / max(1, total_dias_com_treino)
            
            return {
                'ym': ym,
                'total_presencas': len(presentes),
                'total_faltas': len(faltas),
                'total_registros': len(presencas_mes),
                'alunos_ativos': len(todos_alunos),
                'alunos_presentes': len(alunos_presentes),
                'alunos_faltosos': len(alunos_faltosos),
                'dias_com_treino': total_dias_com_treino,
                'media_presencas_dia': round(media_presencas_dia, 1),
                'taxa_presenca': (len(presentes) / max(1, len(presencas_mes))) * 100,
                'presencas_por_dia': presencas_por_dia,
                'detalhes': {
                    'presentes': presentes,
                    'faltas': faltas
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter relatório mensal: {str(e)}")
    
    def obter_frequencia_aluno(self, aluno_id: str, ym: str) -> Dict[str, Any]:
        """
        Obtém frequência específica de um aluno em um mês
        
        Args:
            aluno_id: ID do aluno
            ym: Mês no formato YYYY-MM
        
        Returns:
            Dict com frequência do aluno no mês
        """
        try:
            # Buscar presenças do aluno no mês
            presencas_mes = self.listar_presencas(filtros={'alunoId': aluno_id}, limite=50)
            
            # Filtrar pelo mês específico no cliente
            presencas_aluno_mes = [p for p in presencas_mes if p.get('ym') == ym]
            
            # Separar presenças e faltas
            presentes = [p for p in presencas_aluno_mes if p.get('presente', False)]
            faltas = [p for p in presencas_aluno_mes if not p.get('presente', True)]
            
            total_registros = len(presencas_aluno_mes)
            taxa_presenca = (len(presentes) / max(1, total_registros)) * 100
            
            return {
                'aluno_id': aluno_id,
                'ym': ym,
                'total_presencas': len(presentes),
                'total_faltas': len(faltas),
                'total_registros': total_registros,
                'taxa_presenca': round(taxa_presenca, 1),
                'dias_presente': [p.get('data') for p in presentes],
                'dias_ausente': [p.get('data') for p in faltas]
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter frequência do aluno: {str(e)}")
    
    def check_in_rapido(self, aluno_id: str) -> Dict[str, Any]:
        """
        Check-in rápido de um aluno na data atual
        
        Args:
            aluno_id: ID do aluno
        
        Returns:
            Dict com resultado do check-in
        """
        try:
            hoje = date.today()
            
            # Verificar se já fez check-in hoje
            presenca_hoje = self.buscar_presenca_por_aluno_data(aluno_id, hoje)
            
            if presenca_hoje:
                # Já fez check-in hoje
                status_atual = "presente" if presenca_hoje.get('presente', False) else "ausente"
                return {
                    'sucesso': False,
                    'mensagem': f"Aluno já registrado como {status_atual} hoje",
                    'presenca_id': presenca_hoje['id'],
                    'status_atual': status_atual,
                    'data': hoje.strftime('%Y-%m-%d')
                }
            else:
                # Fazer check-in como presente
                presenca_id = self.marcar_presente(aluno_id, hoje)
                return {
                    'sucesso': True,
                    'mensagem': "Check-in realizado com sucesso!",
                    'presenca_id': presenca_id,
                    'status_atual': "presente",
                    'data': hoje.strftime('%Y-%m-%d')
                }
                
        except Exception as e:
            raise Exception(f"Erro no check-in rápido: {str(e)}")
    
    def deletar_presenca(self, presenca_id: str) -> bool:
        """
        Deleta uma presença (usar com cuidado!)
        
        Args:
            presenca_id: ID da presença
        
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            # Verificar se existe
            if not self.buscar_presenca(presenca_id):
                raise ValueError(f"Presença não encontrada: {presenca_id}")
            
            # Deletar documento
            doc_ref = self.db.collection(self.collection_name).document(presenca_id)
            doc_ref.delete()
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao deletar presença: {str(e)}")
    
    def obter_estatisticas_gerais(self, ym_inicio: str, ym_fim: str) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais de presenças em um período
        
        Args:
            ym_inicio: Mês inicial (YYYY-MM)
            ym_fim: Mês final (YYYY-MM)
        
        Returns:
            Dict com estatísticas gerais
        """
        try:
            # Por simplicidade, buscar todas as presenças e filtrar no cliente
            todas_presencas = self.listar_presencas(limite=5000)
            
            # Filtrar por período
            presencas_periodo = []
            for presenca in todas_presencas:
                ym = presenca.get('ym', '')
                if ym_inicio <= ym <= ym_fim:
                    presencas_periodo.append(presenca)
            
            # Calcular estatísticas
            total_presencas = len([p for p in presencas_periodo if p.get('presente', False)])
            total_faltas = len([p for p in presencas_periodo if not p.get('presente', True)])
            
            alunos_unicos = set(p.get('alunoId') for p in presencas_periodo)
            
            # Agrupar por mês
            por_mes = {}
            for presenca in presencas_periodo:
                ym = presenca.get('ym', '')
                if ym not in por_mes:
                    por_mes[ym] = {'presentes': 0, 'faltas': 0}
                
                if presenca.get('presente', False):
                    por_mes[ym]['presentes'] += 1
                else:
                    por_mes[ym]['faltas'] += 1
            
            return {
                'periodo': f"{ym_inicio} a {ym_fim}",
                'total_presencas': total_presencas,
                'total_faltas': total_faltas,
                'total_registros': len(presencas_periodo),
                'alunos_unicos': len(alunos_unicos),
                'taxa_presenca_geral': (total_presencas / max(1, len(presencas_periodo))) * 100,
                'estatisticas_por_mes': por_mes
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas gerais: {str(e)}")