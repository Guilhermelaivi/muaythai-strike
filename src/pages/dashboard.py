"""
Página Dashboard - KPIs e visão geral
"""

import streamlit as st
from datetime import datetime, date
from typing import Dict, Any
import plotly.express as px
import pandas as pd

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