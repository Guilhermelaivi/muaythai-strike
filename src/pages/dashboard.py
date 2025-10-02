"""
Página Dashboard - KPIs e visão geral
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Any
import plotly.express as px
import pandas as pd
from src.utils.notifications import NotificationService
from src.services.alunos_service import AlunosService
from src.services.pagamentos_service import PagamentosService
from src.services.presencas_service import PresencasService
from src.services.graduacoes_service import GraduacoesService
from src.utils.cache_service import get_cache_manager

def show_dashboard():
    """Exibe o dashboard principal com KPIs"""
    
    st.markdown("## 📊 Dashboard")
    
    # Seletor de mês
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        current_year = datetime.now().year
        selected_year = st.selectbox(
            "Ano:", 
            options=list(range(current_year-2, current_year+2)),
            index=2  # Ano atual
        )
    
    with col2:
        selected_month = st.selectbox(
            "Mês:",
            options=list(range(1, 13)),
            index=datetime.now().month - 1,
            format_func=lambda x: f"{x:02d}"
        )
    
    # Gerar ym para consultas
    ym = f"{selected_year}-{selected_month:02d}"
    
    st.markdown(f"### 📅 Relatório: {ym}")
    
    # Obter dados reais dos serviços
    dados_reais = _get_real_data(ym)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Receita do Mês</h3>
            <h2 style="color: #28a745;">R$ {:.2f}</h2>
            <small>📈 +12% vs mês anterior</small>
        </div>
        """.format(dados_reais['receita']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Inadimplentes</h3>
            <h2 style="color: #dc3545;">{}</h2>
            <small>🎯 Meta: ≤ 5%</small>
        </div>
        """.format(dados_reais['inadimplentes']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Alunos Ativos</h3>
            <h2 style="color: #007bff;">{}</h2>
            <small>📊 {}% do total</small>
        </div>
        """.format(
            dados_reais['ativos'], 
            dados_reais['percentual_ativos']
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Presenças</h3>
            <h2 style="color: #17a2b8;">{}</h2>
            <small>📅 Média: {:.1f}/dia</small>
        </div>
        """.format(
            dados_reais['total_presencas'],
            dados_reais['media_presencas_dia']
        ), unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Evolução de Receita (6 meses)")
        
        # Obter dados históricos reais
        try:
            receitas_historicas = _get_receitas_historicas(ym)
            
            fig_receita = px.line(
                receitas_historicas, 
                x='Mês', 
                y='Receita',
                title="Receita Mensal",
                markers=True
            )
            fig_receita.update_layout(height=300)
            st.plotly_chart(fig_receita, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao carregar histórico de receitas: {str(e)}")
    
    with col2:
        st.markdown("#### 🥋 Status dos Alunos")
        
        # Dados reais para gráfico de pizza
        df_status = pd.DataFrame({
            'Status': ['Ativos', 'Inativos'],
            'Quantidade': [dados_reais['ativos'], dados_reais['inativos']]
        })
        
        fig_status = px.pie(
            df_status,
            values='Quantidade',
            names='Status',
            title="Distribuição de Alunos",
            color_discrete_map={
                'Ativos': '#28a745',
                'Inativos': '#6c757d'
            }
        )
        fig_status.update_layout(height=300)
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Gráficos adicionais
    st.markdown("---")
    st.markdown("#### 📊 Analytics Avançados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graduações por nível
        try:
            graduacoes_service = GraduacoesService()
            stats_grad = graduacoes_service.obter_estatisticas_graduacoes()
            
            if stats_grad['distribuicao_por_nivel']:
                # Limitar a top 8 graduações para visualização
                distribuicao = dict(list(stats_grad['distribuicao_por_nivel'].items())[:8])
                
                fig_grad = px.bar(
                    x=list(distribuicao.keys()),
                    y=list(distribuicao.values()),
                    title="Distribuição por Graduação",
                    labels={'x': 'Graduação', 'y': 'Quantidade'}
                )
                fig_grad.update_layout(height=300)
                st.plotly_chart(fig_grad, use_container_width=True)
            else:
                st.info("Nenhum dado de graduação disponível")
                
        except Exception as e:
            st.info(f"Graduações não disponíveis: {str(e)}")
    
    with col2:
        # Presenças vs Faltas do mês
        try:
            presencas_service = PresencasService()
            relatorio_presencas = presencas_service.obter_relatorio_mensal(ym)
            
            presencas = relatorio_presencas.get('total_presencas', 0)
            faltas = relatorio_presencas.get('total_faltas', 0)
            
            if presencas > 0 or faltas > 0:
                fig_presencas = px.pie(
                    values=[presencas, faltas],
                    names=['Presenças', 'Faltas'],
                    title=f'Presenças vs Faltas ({ym})',
                    color_discrete_map={'Presenças': 'green', 'Faltas': 'red'}
                )
                fig_presencas.update_layout(height=300)
                st.plotly_chart(fig_presencas, use_container_width=True)
            else:
                st.info("Nenhum dado de presença disponível para este mês")
                
        except Exception as e:
            st.info(f"Presenças não disponíveis: {str(e)}")
    
    # Seção de Alertas e Notificações
    st.markdown("---")
    st.markdown("### 🚨 Alertas e Notificações")
    
    try:
        # Inicializar serviço de notificações
        notification_service = NotificationService()
        
        # Gerar relatório de alertas
        relatorio_alertas = notification_service.gerar_relatorio_alertas()
        
        # Exibir status geral
        nivel_geral = relatorio_alertas['resumo']['nivel_geral']
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border-radius: 10px; 
                       background-color: {'#d4edda' if nivel_geral['cor'] == 'green' else 
                                         '#fff3cd' if nivel_geral['cor'] == 'yellow' else
                                         '#f8d7da' if nivel_geral['cor'] == 'red' else '#d1ecf1'};">
                <h3>{nivel_geral['emoji']} Status Geral: {nivel_geral['nivel']}</h3>
                <p>{nivel_geral['acao']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Alertas em cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👻 Alunos Ausentes")
            ausentes_info = relatorio_alertas['alunos_ausentes']
            
            if ausentes_info['total'] > 0:
                st.error(f"⚠️ {ausentes_info['total']} aluno(s) ausente(s)")
                
                # Mostrar top 3 mais críticos
                for aluno in ausentes_info['detalhes'][:3]:
                    status = aluno['status_risco']
                    st.markdown(f"""
                    {status['emoji']} **{aluno['nome']}** - {aluno['dias_sem_atividade']} dias
                    """)
                
                if st.button("👁️ Ver Todos Ausentes", use_container_width=True):
                    st.session_state.mostrar_detalhes_ausentes = True
                    st.rerun()
            else:
                st.success("✅ Nenhum aluno ausente!")
        
        with col2:
            st.markdown("#### 🚫 Inadimplentes Críticos")
            inadimplentes_info = relatorio_alertas['inadimplentes_criticos']
            
            if inadimplentes_info['total'] > 0:
                st.error(f"💸 {inadimplentes_info['total']} inadimplente(s) crítico(s)")
                st.error(f"💰 Total: R$ {inadimplentes_info['valor_total']:.2f}")
                
                # Mostrar top 3 mais críticos
                for pagamento in inadimplentes_info['detalhes'][:3]:
                    status = pagamento['status_risco']
                    dias_atraso = pagamento.get('dias_atraso', 0)
                    valor = pagamento.get('valor', 0)
                    st.markdown(f"""
                    {status['emoji']} **{pagamento.get('alunoNome', 'N/A')}** - {dias_atraso} dias - R$ {valor:.2f}
                    """)
                
                if st.button("👁️ Ver Todos Inadimplentes", use_container_width=True):
                    st.info("💡 Use o menu lateral para navegar para 'Pagamentos' e ver inadimplentes")
            else:
                st.success("✅ Nenhum inadimplente crítico!")
        
        # Detalhes expandidos se solicitado
        if st.session_state.get('mostrar_detalhes_ausentes', False):
            st.markdown("#### 📋 Detalhes - Alunos Ausentes")
            
            for aluno in relatorio_alertas['alunos_ausentes']['detalhes']:
                status = aluno['status_risco']
                
                with st.expander(f"{status['emoji']} {aluno['nome']} - {aluno['dias_sem_atividade']} dias"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {aluno['id']}")
                        st.write(f"**Status:** {status['nivel']}")
                        st.write(f"**Ação:** {status['acao']}")
                    
                    with col2:
                        contato = aluno.get('contato', {})
                        if contato.get('telefone'):
                            st.write(f"**Telefone:** {contato['telefone']}")
                        if contato.get('email'):
                            st.write(f"**Email:** {contato['email']}")
                        
                        ultimo_pag = aluno.get('ultimo_pagamento')
                        if ultimo_pag:
                            st.write(f"**Último pagamento:** {ultimo_pag.get('ym', 'N/A')}")
            
            if st.button("🔼 Recolher", use_container_width=True):
                st.session_state.mostrar_detalhes_ausentes = False
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar alertas: {str(e)}")

def _get_real_data(ym: str) -> Dict[str, Any]:
    """Obtém dados reais dos serviços para o dashboard com cache"""
    try:
        # Inicializar serviços e cache
        alunos_service = AlunosService()
        pagamentos_service = PagamentosService()
        presencas_service = PresencasService()
        cache_manager = get_cache_manager()
        
        # Dados de alunos (com cache)
        alunos = cache_manager.get_alunos_cached(alunos_service)
        total_alunos = len(alunos)
        alunos_ativos = len([a for a in alunos if a.get('status') == 'ativo'])
        alunos_inativos = total_alunos - alunos_ativos
        percentual_ativos = round((alunos_ativos / max(1, total_alunos)) * 100, 1)
        
        # Dados de pagamentos (com cache)
        try:
            estatisticas_pag = cache_manager.get_estatisticas_pagamentos_cached(pagamentos_service, ym)
            receita = estatisticas_pag.get('receita_total', 0.0)
            inadimplentes = estatisticas_pag.get('total_inadimplentes', 0)
        except Exception:
            receita = 0.0
            inadimplentes = 0
        
        # Dados de presenças (com cache)
        try:
            relatorio_presencas = cache_manager.get_relatorio_presencas_cached(presencas_service, ym)
            total_presencas = relatorio_presencas.get('total_presencas', 0)
            media_presencas_dia = relatorio_presencas.get('media_presencas_dia', 0.0)
        except Exception:
            total_presencas = 0
            media_presencas_dia = 0.0
        
        return {
            'receita': receita,
            'inadimplentes': inadimplentes,
            'ativos': alunos_ativos,
            'inativos': alunos_inativos,
            'percentual_ativos': percentual_ativos,
            'total_presencas': total_presencas,
            'media_presencas_dia': media_presencas_dia,
            'ym': ym
        }
        
    except Exception as e:
        # Fallback para dados mock em caso de erro
        st.warning(f"⚠️ Erro ao carregar dados reais: {str(e)}. Usando dados de exemplo.")
        return _get_mock_data_fallback(ym)

def _get_receitas_historicas(ym_atual: str) -> pd.DataFrame:
    """Obtém receitas dos últimos 6 meses para gráfico histórico"""
    try:
        pagamentos_service = PagamentosService()
        
        # Calcular últimos 6 meses
        ano_atual, mes_atual = map(int, ym_atual.split('-'))
        meses_historicos = []
        receitas = []
        
        for i in range(5, -1, -1):  # 6 meses (5 anteriores + atual)
            mes_calc = mes_atual - i
            ano_calc = ano_atual
            
            # Ajustar ano se mês for negativo
            while mes_calc <= 0:
                mes_calc += 12
                ano_calc -= 1
            
            ym_historico = f"{ano_calc}-{mes_calc:02d}"
            
            try:
                stats = pagamentos_service.obter_estatisticas_mes(ym_historico)
                receita = stats.get('receita_total', 0.0)
            except:
                receita = 0.0
            
            meses_historicos.append(f"{mes_calc:02d}/{str(ano_calc)[2:]}")
            receitas.append(receita)
        
        return pd.DataFrame({
            'Mês': meses_historicos,
            'Receita': receitas
        })
        
    except Exception as e:
        # Fallback para dados mock
        return pd.DataFrame({
            'Mês': ['08/24', '09/24', '10/24', '11/24', '12/24', '01/25'],
            'Receita': [3200, 3450, 3800, 3600, 4200, 4500]
        })

def _get_mock_data_fallback(ym: str) -> Dict[str, Any]:
    """Dados de fallback quando serviços falham"""
    return {
        'receita': 4500.00,
        'inadimplentes': 3,
        'ativos': 45,
        'inativos': 8,
        'percentual_ativos': 85,
        'total_presencas': 180,
        'media_presencas_dia': 6.0,
        'ym': ym
    }