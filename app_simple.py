"""
Sistema de Gestão para Academia/Dojo - Versão Simplificada para Deploy
"""

import streamlit as st
import sys
import os
import time
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

# Adicionar favicon
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
    <p>MVP - Academia de Muay Thai - v1.2 (Railway Deploy)</p>
</div>
""", unsafe_allow_html=True)

# Verificar se é primeira execução
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sistema de autenticação simples
if not st.session_state.authenticated:
    st.subheader("🔐 Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
                    
        st.info("💡 **Credenciais de teste:**\n- Usuário: admin\n- Senha: admin123")

else:
    # Aplicação principal
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Navegação")
        
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.authenticated = False
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
                "📋 Planos"
            ]
        )
    
    # Conteúdo das páginas
    if page == "🏠 Dashboard":
        st.header("📊 Dashboard")
        
        # Métricas de exemplo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Alunos", "140", "5")
            
        with col2:
            st.metric("💰 Receita Mensal", "R$ 15.280", "12%")
            
        with col3:
            st.metric("✅ Presença Hoje", "85%", "3%")
            
        with col4:
            st.metric("🥋 Graduações", "12", "2")
        
        st.divider()
        
        # Status da aplicação
        st.subheader("🚀 Status da Aplicação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Deploy realizado com sucesso!")
            st.info(f"🕐 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.success("✅ Favicon configurado")
            st.success("✅ Sistema de autenticação ativo")
            
        with col2:
            # Verificações do sistema
            st.write("**🔧 Verificações do Sistema:**")
            
            # Verificar variáveis de ambiente
            firebase_project = os.getenv("FIREBASE_PROJECT_ID")
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if firebase_project:
                st.success(f"✅ Firebase Project ID: {firebase_project}")
            else:
                st.warning("⚠️ Firebase Project ID não configurado")
                
            if google_creds:
                st.success("✅ Google Credentials configuradas")
            else:
                st.warning("⚠️ Google Credentials não configuradas")
                
            if favicon_path.exists():
                st.success("✅ Favicon.ico encontrado")
            else:
                st.error("❌ Favicon.ico não encontrado")
    
    elif page == "👥 Alunos":
        st.header("👥 Gestão de Alunos")
        st.info("🔄 Módulo em desenvolvimento - conectar com Firebase")
        
        # Exemplo de dados
        st.subheader("📋 Lista de Alunos (Exemplo)")
        import pandas as pd
        
        alunos_exemplo = pd.DataFrame({
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Costa'],
            'Graduação': ['Faixa Branca', 'Faixa Azul', 'Faixa Vermelha'],
            'Plano': ['Mensal', 'Trimestral', 'Anual'],
            'Status': ['Ativo', 'Ativo', 'Pendente']
        })
        
        st.dataframe(alunos_exemplo, use_container_width=True)
    
    elif page == "💰 Pagamentos":
        st.header("💰 Gestão de Pagamentos")
        st.info("🔄 Módulo em desenvolvimento - conectar com Firebase")
        
        # Gráfico de exemplo
        import pandas as pd
        import numpy as np
        
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Janeiro', 'Fevereiro', 'Março']
        )
        st.line_chart(chart_data)
    
    elif page == "✅ Presenças":
        st.header("✅ Controle de Presenças")
        st.info("🔄 Módulo em desenvolvimento - conectar com Firebase")
        
        # Interface de exemplo
        col1, col2 = st.columns(2)
        
        with col1:
            st.date_input("Data da aula")
            st.selectbox("Turma", ["Iniciante", "Intermediário", "Avançado"])
            
        with col2:
            st.time_input("Horário")
            st.multiselect("Alunos presentes", ["João", "Maria", "Pedro"])
    
    elif page == "🥋 Graduações":
        st.header("🥋 Sistema de Graduações")
        st.info("🔄 Módulo em desenvolvimento - conectar com Firebase")
        
        # Sistema de graduação
        graduacoes = [
            "🤍 Faixa Branca (Iniciante)",
            "🔵 Faixa Azul (Básico)",
            "🟢 Faixa Verde (Intermediário)",
            "🟡 Faixa Amarela (Avançado)",
            "🟠 Faixa Laranja (Expert)",
            "🔴 Faixa Vermelha (Mestre)"
        ]
        
        for graduacao in graduacoes:
            st.write(f"- {graduacao}")
    
    elif page == "📋 Planos":
        st.header("📋 Gestão de Planos")
        st.info("🔄 Módulo em desenvolvimento - conectar com Firebase")
        
        # Planos disponíveis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **💎 Plano Mensal**
            - R$ 120/mês
            - 3x por semana
            - Acesso livre aos treinos
            """)
            
        with col2:
            st.markdown("""
            **💎 Plano Trimestral**
            - R$ 300/trimestre
            - 3x por semana
            - Desconto de 17%
            """)
            
        with col3:
            st.markdown("""
            **💎 Plano Anual**
            - R$ 1000/ano
            - Ilimitado
            - Desconto de 31%
            """)

# Footer
st.markdown("---")
st.markdown("🥋 **Dojo Management System** - Desenvolvido com Streamlit | Railway Deploy ✅")