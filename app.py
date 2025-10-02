"""
Sistema de Gestão para Academia/Dojo - MVP
Streamlit + Firestore + streamlit-authenticator

Author: GitHub Copilot
Version: 1.0.0-MVP
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Imports locais
from utils.auth import AuthManager
from utils.firebase_config import FirebaseConfig

def main():
    """Função principal da aplicação"""
    
    # Configuração da página
    st.set_page_config(
        page_title="Dojo Management System",
        page_icon="🥋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
        <p>MVP - Academia de Muay Thai</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar autenticação
    auth_manager = AuthManager()
    
    # Verificar autenticação
    if not auth_manager.is_authenticated():
        auth_manager.show_login()
        return
    
    # Inicializar Firebase
    try:
        firebase_config = FirebaseConfig()
        if not firebase_config.is_connected():
            st.error("❌ Erro na conexão com Firebase. Verifique as configurações.")
            return
    except Exception as e:
        st.error(f"❌ Erro ao conectar com Firebase: {str(e)}")
        st.error("Verifique as variáveis de ambiente FIREBASE_PROJECT_ID e GOOGLE_APPLICATION_CREDENTIALS")
        return
    
    # Sidebar com navegação
    with st.sidebar:
        st.markdown("### 📋 Navegação")
        
        # Logout
        if st.button("🚪 Logout", type="secondary"):
            auth_manager.logout()
            st.rerun()
        
        st.divider()
        
        # Menu de navegação
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
    
    # Roteamento de páginas
    if page == "🏠 Dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "👥 Alunos":
        from pages.alunos import show_alunos
        show_alunos()
    elif page == "💰 Pagamentos":
        from pages.pagamentos import show_pagamentos
        show_pagamentos()
    elif page == "✅ Presenças":
        from pages.presencas import show_presencas
        show_presencas()
    elif page == "🥋 Graduações":
        from pages.graduacoes import show_graduacoes
        show_graduacoes()
    elif page == "📋 Planos":
        from pages.planos import show_planos
        show_planos()

if __name__ == "__main__":
    main()