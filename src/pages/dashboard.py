"""
Página Dashboard - KPIs e visão geral
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Any
import plotly.express as px
import pandas as pd
from src.utils.notifications import NotificationService

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
    
    # Placeholder para dados reais (será implementado com Firestore)
    dados_mock = _get_mock_data(ym)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Receita do Mês</h3>
            <h2 style="color: #28a745;">R$ {:.2f}</h2>
            <small>📈 +12% vs mês anterior</small>
        </div>
        """.format(dados_mock['receita']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Inadimplentes</h3>
            <h2 style="color: #dc3545;">{}</h2>
            <small>🎯 Meta: ≤ 5%</small>
        </div>
        """.format(dados_mock['inadimplentes']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Alunos Ativos</h3>
            <h2 style="color: #007bff;">{}</h2>
            <small>📊 {}% do total</small>
        </div>
        """.format(
            dados_mock['ativos'], 
            dados_mock['percentual_ativos']
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Presenças</h3>
            <h2 style="color: #17a2b8;">{}</h2>
            <small>📅 Média: {:.1f}/dia</small>
        </div>
        """.format(
            dados_mock['total_presencas'],
            dados_mock['media_presencas_dia']
        ), unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Evolução de Receita (6 meses)")
        
        # Dados mock para gráfico
        df_receita = pd.DataFrame({
            'Mês': ['08/24', '09/24', '10/24', '11/24', '12/24', '01/25'],
            'Receita': [3200, 3450, 3800, 3600, 4200, dados_mock['receita']]
        })
        
        fig_receita = px.line(
            df_receita, 
            x='Mês', 
            y='Receita',
            title="Receita Mensal",
            markers=True
        )
        fig_receita.update_layout(height=300)
        st.plotly_chart(fig_receita, use_container_width=True)
    
    with col2:
        st.markdown("#### 🥋 Status dos Alunos")
        
        # Dados mock para gráfico de pizza
        df_status = pd.DataFrame({
            'Status': ['Ativos', 'Inativos'],
            'Quantidade': [dados_mock['ativos'], dados_mock['inativos']]
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
    
    # Ações rápidas
    st.markdown("#### ⚡ Ações Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👥 Novo Aluno", use_container_width=True):
            st.info("🚧 Será implementado na Sprint 1")
    
    with col2:
        if st.button("💰 Registrar Pagamento", use_container_width=True):
            st.info("🚧 Será implementado na Sprint 2")
    
    with col3:
        if st.button("✅ Marcar Presença", use_container_width=True):
            st.info("🚧 Será implementado na Sprint 3")
    
    with col4:
        if st.button("🥋 Nova Graduação", use_container_width=True):
            st.info("🚧 Será implementado na Sprint 3")
    
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
                    # Redirecionar para página de pagamentos
                    st.session_state.pagamentos_modo = 'inadimplentes'
                    st.switch_page("src/pages/pagamentos.py")
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
    
    # Informações de desenvolvimento
    if st.secrets.get("environment", {}).get("debug", False):
        with st.expander("🔧 Debug - Dados Mock"):
            st.json(dados_mock)

def _get_mock_data(ym: str) -> Dict[str, Any]:
    """Gera dados mock para o dashboard (será substituído por dados reais)"""
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