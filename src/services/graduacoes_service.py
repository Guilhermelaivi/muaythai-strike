"""
GraduacoesService - Gerenciamento de graduações e promoções
Subcoleção /alunos/{alunoId}/graduacoes/{gradId}
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from src.utils.firebase_config import get_firestore_client
import uuid

class GraduacoesService:
    """Serviço para gerenciamento de graduações e promoções"""
    
    def __init__(self):
        """Inicializa o serviço com conexão Firestore"""
        self.db = get_firestore_client()
        self.alunos_collection = 'alunos'
        self.graduacoes_subcollection = 'graduacoes'
    
    def registrar_graduacao(self, aluno_id: str, nivel: str, data_graduacao: Optional[date] = None, 
                           obs: Optional[str] = None) -> str:
        """
        Registra uma nova graduação para um aluno
        
        Args:
            aluno_id: ID do aluno
            nivel: Nível da graduação (ex.: "Khan Amarelo")
            data_graduacao: Data da graduação (default: hoje)
            obs: Observações sobre a graduação
        
        Returns:
            str: ID do documento de graduação criado
        
        Raises:
            ValueError: Se dados obrigatórios estão ausentes
            Exception: Se erro ao registrar no Firestore
        """
        if not aluno_id or not aluno_id.strip():
            raise ValueError("ID do aluno é obrigatório")
        
        if not nivel or not nivel.strip():
            raise ValueError("Nível da graduação é obrigatório")
        
        # Usar data atual se não especificada
        if data_graduacao is None:
            data_graduacao = date.today()
        
        # Gerar ID único para graduação
        grad_id = str(uuid.uuid4())
        
        # Formatar data
        data_str = data_graduacao.strftime('%Y-%m-%d')
        
        # Preparar documento
        agora = firestore.SERVER_TIMESTAMP
        documento = {
            'nivel': nivel.strip(),
            'data': data_str,
            'createdAt': agora,
            'updatedAt': agora
        }
        
        # Adicionar observações se fornecidas
        if obs and obs.strip():
            documento['obs'] = obs.strip()
        
        try:
            # Verificar se aluno existe
            aluno_ref = self.db.collection(self.alunos_collection).document(aluno_id)
            aluno_doc = aluno_ref.get()
            
            if not aluno_doc.exists:
                raise ValueError(f"Aluno não encontrado: {aluno_id}")
            
            # Criar documento na subcoleção
            grad_ref = aluno_ref.collection(self.graduacoes_subcollection).document(grad_id)
            grad_ref.set(documento)
            
            # Atualizar graduação atual do aluno
            aluno_ref.update({
                'graduacao': nivel.strip(),
                'updatedAt': agora
            })
            
            return grad_id
            
        except Exception as e:
            raise Exception(f"Erro ao registrar graduação: {str(e)}")
    
    def buscar_graduacao(self, aluno_id: str, grad_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma graduação específica
        
        Args:
            aluno_id: ID do aluno
            grad_id: ID da graduação
        
        Returns:
            Dict com dados da graduação ou None se não encontrado
        """
        try:
            grad_ref = (self.db.collection(self.alunos_collection)
                       .document(aluno_id)
                       .collection(self.graduacoes_subcollection)
                       .document(grad_id))
            
            doc = grad_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                dados['id'] = doc.id
                dados['alunoId'] = aluno_id
                return dados
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar graduação: {str(e)}")
    
    def listar_graduacoes_aluno(self, aluno_id: str, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Lista todas as graduações de um aluno ordenadas por data (mais recente primeiro)
        
        Args:
            aluno_id: ID do aluno
            limite: Número máximo de graduações a retornar
        
        Returns:
            Lista de graduações do aluno
        """
        try:
            # Buscar graduações na subcoleção
            query = (self.db.collection(self.alunos_collection)
                    .document(aluno_id)
                    .collection(self.graduacoes_subcollection)
                    .limit(limite))
            
            docs = query.stream()
            
            graduacoes = []
            for doc in docs:
                graduacao = doc.to_dict()
                graduacao['id'] = doc.id
                graduacao['alunoId'] = aluno_id
                graduacoes.append(graduacao)
            
            # Ordenar por data (mais recente primeiro)
            graduacoes.sort(key=lambda x: x.get('data', ''), reverse=True)
            
            return graduacoes
            
        except Exception as e:
            raise Exception(f"Erro ao listar graduações do aluno: {str(e)}")
    
    def obter_timeline_aluno(self, aluno_id: str) -> Dict[str, Any]:
        """
        Obtém timeline completo de graduações de um aluno
        
        Args:
            aluno_id: ID do aluno
        
        Returns:
            Dict com timeline e estatísticas
        """
        try:
            graduacoes = self.listar_graduacoes_aluno(aluno_id)
            
            if not graduacoes:
                return {
                    'aluno_id': aluno_id,
                    'total_graduacoes': 0,
                    'graduacao_atual': None,
                    'primeira_graduacao': None,
                    'ultima_graduacao': None,
                    'timeline': [],
                    'progressao': []
                }
            
            # Ordenar por data (cronológica para timeline)
            # Filtrar graduações válidas antes de ordenar
            graduacoes_validas = [g for g in graduacoes if g and g.get('data')]
            timeline = sorted(graduacoes_validas, key=lambda x: x.get('data', ''))
            
            # Calcular progressão (intervalos entre graduações)
            progressao = []
            for i in range(1, len(timeline)):
                grad_anterior = timeline[i-1]
                grad_atual = timeline[i]
                
                # Verificar se as graduações têm dados válidos
                if not grad_anterior or not grad_atual:
                    continue
                
                data_anterior_str = grad_anterior.get('data', '')
                data_atual_str = grad_atual.get('data', '')
                
                if not data_anterior_str or not data_atual_str:
                    continue
                
                try:
                    data_anterior = datetime.strptime(data_anterior_str, '%Y-%m-%d').date()
                    data_atual = datetime.strptime(data_atual_str, '%Y-%m-%d').date()
                    
                    dias_entre = (data_atual - data_anterior).days
                    
                    progressao.append({
                        'de': grad_anterior.get('nivel', ''),
                        'para': grad_atual.get('nivel', ''),
                        'data_inicial': data_anterior_str,
                        'data_final': data_atual_str,
                        'dias_entre': dias_entre,
                        'meses_aproximados': round(dias_entre / 30.44, 1)
                    })
                except (ValueError, TypeError):
                    # Ignorar datas inválidas
                    continue
            
            # Calcular tempo total com verificações de segurança
            tempo_total_dias = 0
            if len(timeline) >= 2 and timeline[0] and timeline[-1]:
                data_primeira_str = timeline[0].get('data', '')
                data_ultima_str = timeline[-1].get('data', '')
                
                if data_primeira_str and data_ultima_str:
                    try:
                        data_primeira = datetime.strptime(data_primeira_str, '%Y-%m-%d').date()
                        data_ultima = datetime.strptime(data_ultima_str, '%Y-%m-%d').date()
                        tempo_total_dias = (data_ultima - data_primeira).days
                    except (ValueError, TypeError):
                        tempo_total_dias = 0
            
            return {
                'aluno_id': aluno_id,
                'total_graduacoes': len(graduacoes),
                'graduacao_atual': timeline[-1] if timeline else None,
                'primeira_graduacao': timeline[0] if timeline else None,
                'ultima_graduacao': timeline[-1] if timeline else None,
                'timeline': timeline,
                'progressao': progressao,
                'tempo_total_dias': tempo_total_dias
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter timeline do aluno: {str(e)}")
    
    def atualizar_graduacao(self, aluno_id: str, grad_id: str, dados_atualizacao: Dict[str, Any]) -> bool:
        """
        Atualiza uma graduação existente
        
        Args:
            aluno_id: ID do aluno
            grad_id: ID da graduação
            dados_atualizacao: Dados para atualizar
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            # Verificar se graduação existe
            if not self.buscar_graduacao(aluno_id, grad_id):
                raise ValueError(f"Graduação não encontrada: {grad_id}")
            
            # Preparar dados de atualização
            dados_atualizacao['updatedAt'] = firestore.SERVER_TIMESTAMP
            
            # Atualizar documento
            grad_ref = (self.db.collection(self.alunos_collection)
                       .document(aluno_id)
                       .collection(self.graduacoes_subcollection)
                       .document(grad_id))
            
            grad_ref.update(dados_atualizacao)
            
            # Se atualizou o nível da graduação mais recente, atualizar no aluno também
            if 'nivel' in dados_atualizacao:
                graduacoes = self.listar_graduacoes_aluno(aluno_id)
                if graduacoes and graduacoes[0]['id'] == grad_id:  # É a mais recente
                    aluno_ref = self.db.collection(self.alunos_collection).document(aluno_id)
                    aluno_ref.update({
                        'graduacao': dados_atualizacao['nivel'],
                        'updatedAt': firestore.SERVER_TIMESTAMP
                    })
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar graduação: {str(e)}")
    
    def deletar_graduacao(self, aluno_id: str, grad_id: str) -> bool:
        """
        Deleta uma graduação (usar com cuidado!)
        
        Args:
            aluno_id: ID do aluno
            grad_id: ID da graduação
        
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            # Verificar se existe
            graduacao = self.buscar_graduacao(aluno_id, grad_id)
            if not graduacao:
                raise ValueError(f"Graduação não encontrada: {grad_id}")
            
            # Deletar documento
            grad_ref = (self.db.collection(self.alunos_collection)
                       .document(aluno_id)
                       .collection(self.graduacoes_subcollection)
                       .document(grad_id))
            
            grad_ref.delete()
            
            # Reprocessar graduação atual do aluno
            graduacoes_restantes = self.listar_graduacoes_aluno(aluno_id)
            
            aluno_ref = self.db.collection(self.alunos_collection).document(aluno_id)
            
            if graduacoes_restantes:
                # Atualizar com a graduação mais recente
                graduacao_atual = graduacoes_restantes[0]  # Já vem ordenada por data desc
                aluno_ref.update({
                    'graduacao': graduacao_atual.get('nivel', 'Sem graduação'),
                    'updatedAt': firestore.SERVER_TIMESTAMP
                })
            else:
                # Sem graduações, resetar para "Sem graduação"
                aluno_ref.update({
                    'graduacao': 'Sem graduação',
                    'updatedAt': firestore.SERVER_TIMESTAMP
                })
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao deletar graduação: {str(e)}")
    
    def obter_estatisticas_graduacoes(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais sobre graduações no sistema
        
        Returns:
            Dict com estatísticas gerais
        """
        try:
            # Buscar todos os alunos
            alunos_query = self.db.collection(self.alunos_collection).stream()
            
            total_alunos = 0
            graduacoes_por_nivel = {}
            alunos_com_graduacoes = 0
            total_promocoes = 0
            
            for aluno_doc in alunos_query:
                total_alunos += 1
                aluno_id = aluno_doc.id
                aluno_data = aluno_doc.to_dict()
                
                # Contar graduação atual
                graduacao_atual = aluno_data.get('graduacao', 'Sem graduação')
                if graduacao_atual not in graduacoes_por_nivel:
                    graduacoes_por_nivel[graduacao_atual] = 0
                graduacoes_por_nivel[graduacao_atual] += 1
                
                # Contar total de promoções do aluno
                graduacoes_aluno = self.listar_graduacoes_aluno(aluno_id)
                if graduacoes_aluno:
                    alunos_com_graduacoes += 1
                    total_promocoes += len(graduacoes_aluno)
            
            # Calcular médias
            media_promocoes_por_aluno = total_promocoes / max(1, total_alunos)
            taxa_alunos_graduados = (alunos_com_graduacoes / max(1, total_alunos)) * 100
            
            return {
                'total_alunos': total_alunos,
                'alunos_com_graduacoes': alunos_com_graduacoes,
                'total_promocoes': total_promocoes,
                'media_promocoes_por_aluno': round(media_promocoes_por_aluno, 1),
                'taxa_alunos_graduados': round(taxa_alunos_graduados, 1),
                'distribuicao_por_nivel': graduacoes_por_nivel,
                'nivel_mais_comum': max(graduacoes_por_nivel, key=graduacoes_por_nivel.get) if graduacoes_por_nivel else None
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter estatísticas de graduações: {str(e)}")
    
    def listar_candidatos_promocao(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista alunos candidatos à promoção baseado em critérios
        
        Args:
            filtros: Critérios de filtragem (ex.: 'meses_minimos_graduacao')
        
        Returns:
            Lista de alunos candidatos à promoção
        """
        try:
            # Buscar todos os alunos ativos
            alunos_query = self.db.collection(self.alunos_collection).where('status', '==', 'ativo').stream()
            
            candidatos = []
            meses_minimos = filtros.get('meses_minimos_graduacao', 6) if filtros else 6
            
            for aluno_doc in alunos_query:
                aluno_id = aluno_doc.id
                aluno_data = aluno_doc.to_dict()
                
                # Buscar última graduação
                graduacoes = self.listar_graduacoes_aluno(aluno_id, limite=1)
                
                if graduacoes:
                    ultima_graduacao = graduacoes[0]
                    data_ultima = datetime.strptime(ultima_graduacao.get('data', ''), '%Y-%m-%d').date()
                    hoje = date.today()
                    
                    dias_desde_ultima = (hoje - data_ultima).days
                    meses_desde_ultima = dias_desde_ultima / 30.44
                    
                    # Verificar se atende critério de tempo mínimo
                    if meses_desde_ultima >= meses_minimos:
                        candidatos.append({
                            'aluno_id': aluno_id,
                            'nome': aluno_data.get('nome', 'Desconhecido'),
                            'graduacao_atual': aluno_data.get('graduacao', 'Sem graduação'),
                            'data_ultima_graduacao': ultima_graduacao.get('data', ''),
                            'dias_desde_ultima': int(dias_desde_ultima),
                            'meses_desde_ultima': round(meses_desde_ultima, 1),
                            'total_graduacoes': len(self.listar_graduacoes_aluno(aluno_id))
                        })
                else:
                    # Aluno sem graduações - candidato automaticamente
                    candidatos.append({
                        'aluno_id': aluno_id,
                        'nome': aluno_data.get('nome', 'Desconhecido'),
                        'graduacao_atual': 'Sem graduação',
                        'data_ultima_graduacao': None,
                        'dias_desde_ultima': None,
                        'meses_desde_ultima': None,
                        'total_graduacoes': 0
                    })
            
            # Ordenar por tempo desde última graduação (mais tempo primeiro)
            # Tratar None values na ordenação de forma mais robusta
            def sort_key(candidato):
                meses = candidato.get('meses_desde_ultima')
                if meses is None:
                    return 999  # Colocar alunos sem graduação no final
                return meses
            
            candidatos.sort(key=sort_key, reverse=True)
            
            return candidatos
            
        except Exception as e:
            raise Exception(f"Erro ao listar candidatos à promoção: {str(e)}")
    
    def obter_niveis_graduacao_disponiveis(self) -> List[str]:
        """
        Retorna lista de níveis de graduação disponíveis
        
        Returns:
            Lista de níveis ordenados por progressão
        """
        # Níveis típicos de arte marcial em ordem de progressão
        return [
            "Branca",
            "Cinza",
            "Amarela", 
            "Laranja",
            "Verde",
            "Azul",
            "Roxa", 
            "Marrom",
            "Preta 1º Dan",
            "Preta 2º Dan",
            "Preta 3º Dan",
            "Preta 4º Dan",
            "Preta 5º Dan",
            "Khan Amarelo",
            "Khan Verde",
            "Khan Azul",
            "Khan Roxo",
            "Khan Marrom",
            "Khan Preto"
        ]