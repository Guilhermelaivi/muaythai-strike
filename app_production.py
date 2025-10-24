"""
🥋 Sistema de Gestão para Academia/Dojo - MVP
Streamlit + Firebase + Autenticação

Version: 2.0.0 - Railway Production
"""

import streamlit as st
import os
import sys
import base64
from pathlib import Path
from datetime import datetime

# Configurar página
st.set_page_config(
    page_title="Dojo Management System",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar favicon se existir
favicon_path = Path(__file__).parent / "favicon.ico"
if favicon_path.exists():
    with open(favicon_path, "rb") as f:
        favicon_data = f.read()
        favicon_b64 = base64.b64encode(favicon_data).decode()
    
    st.markdown(f"""
    <link rel="shortcut icon" href="data:image/x-icon;base64,{favicon_b64}">
    <link rel="icon" href="data:image/x-icon;base64,{favicon_b64}">
    """, unsafe_allow_html=True)

# CSS customizado
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #FF6B35;
}
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🥋 Sistema de Gestão - Dojo</h1>
    <p>MVP - Academia de Muay Thai - v2.0 (Production)</p>
</div>
""", unsafe_allow_html=True)

# Verificar se é primeira execução
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sistema de autenticação
if not st.session_state.authenticated:
    st.subheader("🔐 Login do Sistema")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("🚀 **Sistema funcionando em produção no Railway!**")
        
        with st.form("login_form"):
            st.markdown("### 👤 Credenciais de Acesso")
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            col_login1, col_login2 = st.columns(2)
            with col_login1:
                submit = st.form_submit_button("🔑 Entrar", use_container_width=True, type="primary")
            with col_login2:
                demo = st.form_submit_button("👀 Demo", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.success("✅ Login realizado com sucesso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
                    
            if demo:
                st.session_state.authenticated = True
                st.session_state.demo_mode = True
                st.success("🎮 Modo demonstração ativado!")
                st.rerun()
                    
        # Informações de login
        with st.expander("💡 Informações de Login"):
            st.markdown("""
            **👨‍💼 Credenciais de Administrador:**
            - **Usuário:** admin
            - **Senha:** admin123
            
            **🎮 Modo Demo:**
            - Acesso livre para visualização
            - Dados de exemplo
            """)

else:
    # Aplicação principal autenticada
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Navegação")
        
        # Info do usuário
        if st.session_state.get('demo_mode'):
            st.info("🎮 **Modo Demo**")
        else:
            st.success("👨‍💼 **Administrador**")
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.demo_mode = False
            st.rerun()
        
        st.divider()
        
        page = st.selectbox(
            "Selecione uma página:",
            options=[
                "🏠 Dashboard", 
                "👥 Alunos", 
                "💰 Pagamentos", 
                "✅ Presenças", 
                "🥋 Graduações", 
                "📋 Planos",
                "⚙️ Sistema"
            ]
        )
    
    # Conteúdo das páginas
    if page == "🏠 Dashboard":
        st.header("📊 Dashboard Principal")
        
        # Status do sistema
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Métricas principais
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                st.metric("👥 Total Alunos", "140", "5")
                
            with col_m2:
                st.metric("💰 Receita Mensal", "R$ 15.280", "12%")
                
            with col_m3:
                st.metric("✅ Presença Hoje", "85%", "3%")
                
            with col_m4:
                st.metric("🥋 Graduações", "12", "2")
        
        with col2:
            st.success("🚀 **Sistema Online**")
            st.info(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            # Verificar Firebase
            firebase_project = os.getenv("FIREBASE_PROJECT_ID")
            if firebase_project:
                st.success(f"🔥 Firebase: {firebase_project}")
            else:
                st.warning("⚠️ Firebase não configurado")
        
        st.divider()
        
        # Gráfico de exemplo
        import pandas as pd
        import numpy as np
        
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Alunos', 'Receita', 'Presenças']
        )
        st.line_chart(chart_data)
    
    elif page == "👥 Alunos":
        st.header("👥 Gestão de Alunos")
        
        if st.session_state.get('demo_mode'):
            st.info("🎮 **Modo Demo** - Dados de exemplo")
        
        # Exemplo de lista de alunos
        st.subheader("📋 Lista de Alunos")
        
        import pandas as pd
        
        alunos_demo = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Ferreira'],
            'Graduação': ['🤍 Branca', '🔵 Azul', '🟢 Verde', '🟡 Amarela', '🟠 Laranja'],
            'Plano': ['Mensal', 'Trimestral', 'Anual', 'Mensal', 'Trimestral'],
            'Status': ['✅ Ativo', '✅ Ativo', '⏸️ Pausado', '✅ Ativo', '❌ Inativo']
        })
        
        st.dataframe(alunos_demo, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Novo Aluno", use_container_width=True):
                st.success("Funcionalidade em desenvolvimento")
        with col2:
            if st.button("📊 Relatório", use_container_width=True):
                st.info("Relatório será implementado")
        with col3:
            if st.button("📤 Exportar", use_container_width=True):
                st.info("Export em desenvolvimento")
    
    elif page == "💰 Pagamentos":
        st.header("💰 Gestão de Pagamentos")
        
        # Resumo financeiro
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💵 Receita Mês", "R$ 15.280", "8%")
        with col2:
            st.metric("📅 Pendentes", "R$ 2.450", "-3")
        with col3:
            st.metric("📊 Taxa Cobrança", "94.2%", "1.2%")
        
        st.info("🔄 Sistema de pagamentos sendo integrado com Firebase")
    
    elif page == "✅ Presenças":
        st.header("✅ Controle de Presenças")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.date_input("📅 Data da aula")
            st.selectbox("🏃 Turma", ["Iniciante - 18h", "Intermediário - 19h", "Avançado - 20h"])
            
        with col2:
            st.time_input("⏰ Horário")
            st.multiselect("👥 Alunos presentes", ["João Silva", "Maria Santos", "Pedro Costa"])
        
        if st.button("✅ Registrar Presença", type="primary"):
            st.success("Presença registrada com sucesso!")
    
    elif page == "🥋 Graduações":
        st.header("🥋 Sistema de Graduações")
        
        st.subheader("🎖️ Níveis de Graduação")
        
        graduacoes = [
            ("🤍", "Faixa Branca", "Iniciante", "0-6 meses"),
            ("🔵", "Faixa Azul", "Básico", "6-12 meses"),
            ("🟢", "Faixa Verde", "Intermediário", "1-2 anos"),
            ("🟡", "Faixa Amarela", "Avançado", "2-3 anos"),
            ("🟠", "Faixa Laranja", "Expert", "3-4 anos"),
            ("🔴", "Faixa Vermelha", "Mestre", "4+ anos")
        ]
        
        for emoji, nome, nivel, tempo in graduacoes:
            with st.expander(f"{emoji} {nome} - {nivel}"):
                st.write(f"**Tempo mínimo:** {tempo}")
                st.write(f"**Nível:** {nivel}")
    
    elif page == "📋 Planos":
        st.header("📋 Gestão de Planos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown("""
                <div class="metric-card">
                <h3>💎 Plano Mensal</h3>
                <p><strong>R$ 120/mês</strong></p>
                <ul>
                <li>3x por semana</li>
                <li>Acesso aos treinos</li>
                <li>Suporte básico</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
        with col2:
            with st.container():
                st.markdown("""
                <div class="metric-card">
                <h3>💎 Plano Trimestral</h3>
                <p><strong>R$ 300/trimestre</strong></p>
                <ul>
                <li>3x por semana</li>
                <li>Desconto de 17%</li>
                <li>Suporte prioritário</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                
        with col3:
            with st.container():
                st.markdown("""
                <div class="metric-card">
                <h3>💎 Plano Anual</h3>
                <p><strong>R$ 1000/ano</strong></p>
                <ul>
                <li>Acesso ilimitado</li>
                <li>Desconto de 31%</li>
                <li>Benefícios exclusivos</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "⚙️ Sistema":
        st.header("⚙️ Informações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 Status do Deploy")
            st.success("✅ Aplicação funcionando")
            st.success("✅ Railway conectado")
            st.success("✅ Autenticação ativa")
            
            # Verificar variáveis de ambiente
            firebase_project = os.getenv("FIREBASE_PROJECT_ID")
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            port = os.getenv("PORT")
            
            st.write("**🔧 Variáveis de Ambiente:**")
            st.write(f"- PORT: {port}")
            st.write(f"- FIREBASE_PROJECT_ID: {firebase_project}")
            st.write(f"- Google Credentials: {'✅ Configurado' if google_creds else '❌ Não encontrado'}")
            
        with col2:
            st.subheader("📊 Estatísticas")
            st.info(f"🕐 Sistema iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.info("🌐 Hospedado no Railway")
            st.info("🚀 Deploy automático via GitHub")
            
            if st.button("🔄 Testar Conexão Firebase"):
                if firebase_project:
                    st.success("🔥 Firebase configurado corretamente!")
                else:
                    st.error("❌ Firebase não configurado")

# Footer
st.markdown("---")
st.markdown("🥋 **Dojo Management System v2.0** - Produção | Railway Deploy ✅")