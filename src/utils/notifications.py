"""
Utilitário para notificações e alertas do sistema
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from src.services.alunos_service import AlunosService
from src.services.pagamentos_service import PagamentosService

class NotificationService:
    """Serviço para gerenciar notificações e alertas do sistema"""
    
    def __init__(self):
        """Inicializa o serviço de notificações"""
        self.alunos_service = AlunosService()
        self.pagamentos_service = PagamentosService()
    
    def verificar_alunos_ausentes(self, dias_limite: int = 7) -> List[Dict[str, Any]]:
        """
        Verifica alunos que estão ausentes há mais de X dias
        
        Args:
            dias_limite: Número de dias sem presença para considerar ausente
        
        Returns:
            Lista de alunos ausentes com informações relevantes
        """
        try:
            # Por enquanto, vamos simular baseado na ausência de pagamentos recentes
            # Na Sprint 3 será baseado em presenças reais
            
            hoje = date.today()
            limite_data = hoje - timedelta(days=dias_limite)
            
            # Buscar alunos ativos
            alunos_ativos = self.alunos_service.listar_alunos(status='ativo')
            
            alunos_ausentes = []
            
            for aluno in alunos_ativos:
                # Verificar pagamentos recentes como proxy para atividade
                extrato = self.pagamentos_service.obter_extrato_aluno(aluno['id'], limite_meses=2)
                
                # Se não tem pagamentos ou último pagamento é muito antigo
                if not extrato:
                    dias_sem_atividade = 30  # Assumir 30 dias se não há histórico
                else:
                    ultimo_pagamento = extrato[0]
                    try:
                        ultimo_ym = ultimo_pagamento.get('ym', '')
                        if ultimo_ym:
                            ano, mes = map(int, ultimo_ym.split('-'))
                            ultima_data = date(ano, mes, 1)
                            dias_sem_atividade = (hoje - ultima_data).days
                        else:
                            dias_sem_atividade = 30
                    except:
                        dias_sem_atividade = 30
                
                # Se está ausente há mais que o limite
                if dias_sem_atividade > dias_limite:
                    aluno_info = {
                        'id': aluno['id'],
                        'nome': aluno.get('nome', 'N/A'),
                        'dias_sem_atividade': dias_sem_atividade,
                        'ultimo_pagamento': extrato[0] if extrato else None,
                        'contato': aluno.get('contato', {}),
                        'status_risco': self._calcular_status_risco(dias_sem_atividade)
                    }
                    alunos_ausentes.append(aluno_info)
            
            # Ordenar por dias sem atividade (mais críticos primeiro)
            alunos_ausentes.sort(key=lambda x: x['dias_sem_atividade'], reverse=True)
            
            return alunos_ausentes
            
        except Exception as e:
            raise Exception(f"Erro ao verificar alunos ausentes: {str(e)}")
    
    def _calcular_status_risco(self, dias_sem_atividade: int) -> Dict[str, str]:
        """
        Calcula o status de risco baseado nos dias sem atividade
        
        Args:
            dias_sem_atividade: Dias sem atividade
        
        Returns:
            Dict com status, cor e emoji
        """
        if dias_sem_atividade >= 30:
            return {
                'nivel': 'CRÍTICO',
                'cor': 'red',
                'emoji': '🔴',
                'acao': 'Contato imediato necessário'
            }
        elif dias_sem_atividade >= 14:
            return {
                'nivel': 'ALTO',
                'cor': 'orange', 
                'emoji': '🟠',
                'acao': 'Entrar em contato'
            }
        elif dias_sem_atividade >= 7:
            return {
                'nivel': 'MÉDIO',
                'cor': 'yellow',
                'emoji': '🟡',
                'acao': 'Monitorar'
            }
        else:
            return {
                'nivel': 'BAIXO',
                'cor': 'green',
                'emoji': '🟢',
                'acao': 'Normal'
            }
    
    def verificar_inadimplentes_criticos(self, dias_atraso_limite: int = 30) -> List[Dict[str, Any]]:
        """
        Verifica inadimplentes com mais de X dias de atraso
        
        Args:
            dias_atraso_limite: Dias de atraso para considerar crítico
        
        Returns:
            Lista de inadimplentes críticos
        """
        try:
            # Buscar todos os inadimplentes
            inadimplentes = self.pagamentos_service.obter_inadimplentes()
            
            inadimplentes_criticos = []
            hoje = date.today()
            
            for pagamento in inadimplentes:
                try:
                    # Calcular dias de atraso usando dados REAIS do pagamento
                    ym = pagamento.get('ym', '')
                    if ym:
                        ano, mes = map(int, ym.split('-'))
                        # Usar dia de vencimento REAL do pagamento
                        dia_vencimento = pagamento.get('dataVencimento', 15)
                        data_vencimento = date(ano, mes, dia_vencimento)
                        
                        # SEM carência - passou 1 dia = inadimplente
                        dias_atraso = (hoje - data_vencimento).days
                        
                        if dias_atraso >= dias_atraso_limite:
                            pagamento['dias_atraso'] = dias_atraso
                            pagamento['status_risco'] = self._calcular_status_risco_inadimplencia(dias_atraso)
                            inadimplentes_criticos.append(pagamento)
                except:
                    continue
            
            # Ordenar por dias de atraso
            inadimplentes_criticos.sort(key=lambda x: x.get('dias_atraso', 0), reverse=True)
            
            return inadimplentes_criticos
            
        except Exception as e:
            raise Exception(f"Erro ao verificar inadimplentes críticos: {str(e)}")
    
    def verificar_devedores(self, ym: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Verifica devedores (pagamentos a cobrar) - alerta para gestão
        
        Devedores são pagamentos que entraram no período de cobrança
        (~10 dias antes do vencimento) mas ainda não venceram.
        
        Args:
            ym: Filtrar por mês específico (YYYY-MM), se None pega mês atual
        
        Returns:
            Lista de pagamentos com status devedor e informações de vencimento
        """
        try:
            # Usar mês atual se não especificado
            if not ym:
                hoje = date.today()
                ym = f"{hoje.year:04d}-{hoje.month:02d}"
            
            # Buscar devedores do mês
            devedores = self.pagamentos_service.obter_devedores(ym=ym)
            
            hoje = date.today()
            devedores_info = []
            
            for pagamento in devedores:
                try:
                    # Calcular dias até o vencimento
                    ym_pag = pagamento.get('ym', '')
                    if ym_pag:
                        ano, mes = map(int, ym_pag.split('-'))
                        dia_vencimento = pagamento.get('dataVencimento', 15)
                        data_vencimento = date(ano, mes, dia_vencimento)
                        dias_ate_vencer = (data_vencimento - hoje).days
                        
                        pagamento_info = {
                            'id': pagamento.get('id'),
                            'alunoId': pagamento.get('alunoId'),
                            'alunoNome': pagamento.get('alunoNome', 'N/A'),
                            'valor': pagamento.get('valor', 0),
                            'ym': ym_pag,
                            'dataVencimento': dia_vencimento,
                            'data_vencimento_completa': data_vencimento.strftime('%Y-%m-%d'),
                            'dias_ate_vencer': dias_ate_vencer,
                            'status_alerta': self._calcular_status_alerta_cobranca(dias_ate_vencer)
                        }
                        devedores_info.append(pagamento_info)
                except:
                    continue
            
            # Ordenar por dias até vencer (mais urgentes primeiro)
            devedores_info.sort(key=lambda x: x.get('dias_ate_vencer', 999))
            
            return devedores_info
            
        except Exception as e:
            raise Exception(f"Erro ao verificar devedores: {str(e)}")
    
    def _calcular_status_alerta_cobranca(self, dias_ate_vencer: int) -> Dict[str, str]:
        """
        Calcula status de alerta para cobrança (devedores)
        
        Args:
            dias_ate_vencer: Dias até o vencimento
        
        Returns:
            Dict com informações do alerta
        """
        if dias_ate_vencer <= 0:
            # Já venceu (provavelmente está virando inadimplente)
            return {
                'nivel': 'CRÍTICO',
                'cor': 'red',
                'emoji': '🔴',
                'acao': 'Vencimento hoje ou passou - verificar urgente'
            }
        elif dias_ate_vencer <= 3:
            return {
                'nivel': 'URGENTE',
                'cor': 'orange',
                'emoji': '🟠',
                'acao': 'Vence em poucos dias - contato imediato'
            }
        elif dias_ate_vencer <= 7:
            return {
                'nivel': 'ATENÇÃO',
                'cor': 'yellow',
                'emoji': '🟡',
                'acao': 'Vence na próxima semana - lembrete'
            }
        else:
            return {
                'nivel': 'NORMAL',
                'cor': 'blue',
                'emoji': '🔔',
                'acao': 'Monitorar'
            }
    
    def _calcular_status_risco_inadimplencia(self, dias_atraso: int) -> Dict[str, str]:
        """
        Calcula status de risco para inadimplência
        
        Args:
            dias_atraso: Dias de atraso no pagamento
        
        Returns:
            Dict com informações do status
        """
        if dias_atraso >= 60:
            return {
                'nivel': 'CRÍTICO',
                'cor': 'red',
                'emoji': '🔴',
                'acao': 'Considerar suspensão'
            }
        elif dias_atraso >= 30:
            return {
                'nivel': 'ALTO',
                'cor': 'orange',
                'emoji': '🟠', 
                'acao': 'Negociação urgente'
            }
        else:
            return {
                'nivel': 'MÉDIO',
                'cor': 'yellow',
                'emoji': '🟡',
                'acao': 'Cobrança de rotina'
            }
    
    def gerar_relatorio_alertas(self) -> Dict[str, Any]:
        """
        Gera um relatório completo com todos os alertas do sistema
        
        Returns:
            Dict com relatório de alertas
        """
        try:
            hoje = date.today()
            
            # Verificar alertas
            alunos_ausentes = self.verificar_alunos_ausentes(dias_limite=7)
            inadimplentes_criticos = self.verificar_inadimplentes_criticos(dias_atraso_limite=30)
            
            # Contar por nível de risco
            ausentes_por_risco = {}
            for aluno in alunos_ausentes:
                nivel = aluno['status_risco']['nivel']
                ausentes_por_risco[nivel] = ausentes_por_risco.get(nivel, 0) + 1
            
            inadimplentes_por_risco = {}
            for pagamento in inadimplentes_criticos:
                nivel = pagamento['status_risco']['nivel']
                inadimplentes_por_risco[nivel] = inadimplentes_por_risco.get(nivel, 0) + 1
            
            # Calcular valor total em risco
            valor_total_inadimplencia = sum(p.get('valor', 0) for p in inadimplentes_criticos)
            
            relatorio = {
                'data_relatorio': hoje.strftime('%d/%m/%Y'),
                'alunos_ausentes': {
                    'total': len(alunos_ausentes),
                    'por_risco': ausentes_por_risco,
                    'detalhes': alunos_ausentes[:10]  # Top 10 mais críticos
                },
                'inadimplentes_criticos': {
                    'total': len(inadimplentes_criticos),
                    'por_risco': inadimplentes_por_risco,
                    'valor_total': valor_total_inadimplencia,
                    'detalhes': inadimplentes_criticos[:10]  # Top 10 mais críticos
                },
                'resumo': {
                    'total_alertas': len(alunos_ausentes) + len(inadimplentes_criticos),
                    'nivel_geral': self._calcular_nivel_geral_risco(
                        len(alunos_ausentes), 
                        len(inadimplentes_criticos),
                        valor_total_inadimplencia
                    )
                }
            }
            
            return relatorio
            
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório de alertas: {str(e)}")
    
    def _calcular_nivel_geral_risco(self, ausentes: int, inadimplentes: int, valor_inadimplencia: float) -> Dict[str, str]:
        """
        Calcula o nível geral de risco do negócio
        
        Args:
            ausentes: Número de alunos ausentes
            inadimplentes: Número de inadimplentes
            valor_inadimplencia: Valor total da inadimplência
        
        Returns:
            Dict com nível geral de risco
        """
        score_risco = 0
        
        # Pontuação baseada em ausentes
        if ausentes >= 10:
            score_risco += 3
        elif ausentes >= 5:
            score_risco += 2
        elif ausentes >= 2:
            score_risco += 1
        
        # Pontuação baseada em inadimplentes
        if inadimplentes >= 10:
            score_risco += 3
        elif inadimplentes >= 5:
            score_risco += 2
        elif inadimplentes >= 2:
            score_risco += 1
        
        # Pontuação baseada em valor
        if valor_inadimplencia >= 3000:
            score_risco += 3
        elif valor_inadimplencia >= 1500:
            score_risco += 2
        elif valor_inadimplencia >= 500:
            score_risco += 1
        
        # Determinar nível
        if score_risco >= 7:
            return {
                'nivel': 'CRÍTICO',
                'cor': 'red',
                'emoji': '🚨',
                'acao': 'Ação imediata necessária'
            }
        elif score_risco >= 4:
            return {
                'nivel': 'ALTO',
                'cor': 'orange',
                'emoji': '⚠️',
                'acao': 'Monitoramento ativo necessário'
            }
        elif score_risco >= 2:
            return {
                'nivel': 'MÉDIO',
                'cor': 'yellow',
                'emoji': '⚡',
                'acao': 'Monitoramento de rotina'
            }
        else:
            return {
                'nivel': 'BAIXO',
                'cor': 'green',
                'emoji': '✅',
                'acao': 'Situação sob controle'
            }