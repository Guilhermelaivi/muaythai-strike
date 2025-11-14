"""
Sistema de Gestão para Academia/Dojo - MVP
Streamlit + Firestore + streamlit-authenticator

Author: GitHub Copilot
Version: 1.0.0-MVP
"""

import streamlit as st
import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/dojo_app.log', mode='a') if os.path.exists('/tmp') else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('DojojApp')

def log_step(step_name, start_time=None):
    """Log de cada etapa com timing"""
    current_time = time.time()
    if start_time:
        duration = current_time - start_time
        logger.info(f"✅ {step_name} - CONCLUÍDO em {duration:.2f}s")
    else:
        logger.info(f"🔄 {step_name} - INICIANDO...")
    return current_time

# Adicionar src ao path para imports
logger.info("🚀 INICIANDO APLICAÇÃO DOJO MANAGEMENT SYSTEM")
start_total = time.time()

step_start = log_step("Configuração de imports")
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
log_step("Configuração de imports", step_start)

# Imports locais
step_start = log_step("Imports de módulos locais")
try:
    from utils.auth import AuthManager
    from utils.firebase_config import FirebaseConfig
    log_step("Imports de módulos locais", step_start)
except Exception as e:
    logger.error(f"❌ ERRO nos imports: {str(e)}")
    raise e

def main():
    """Função principal da aplicação"""
    
    logger.info("📱 FUNÇÃO MAIN INICIADA")
    step_start = log_step("Verificação de ambiente Streamlit")
    
    # Verificar se está rodando corretamente
    if 'streamlit' not in sys.modules:
        logger.error("❌ Aplicação NÃO está sendo executada com streamlit run")
        st.error("Aplicação deve ser executada com 'streamlit run app.py'")
        return
    
    log_step("Verificação de ambiente Streamlit", step_start)
    
    # Configuração da página
    step_start = log_step("Configuração da página Streamlit")
    try:
        st.set_page_config(
            page_title="Dojo Management System",
            page_icon="🥋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        log_step("Configuração da página Streamlit", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao configurar página: {str(e)}")
        raise e
    
    # CSS customizado
    step_start = log_step("Aplicação de CSS customizado")
    try:
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
        log_step("Aplicação de CSS customizado", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao aplicar CSS: {str(e)}")
        # Continuar mesmo com erro de CSS
    
    # Header principal
    step_start = log_step("Renderização do header")
    try:
        st.markdown("""
        <div class="main-header">
            <h1>🥋 Sistema de Gestão - Dojo</h1>
            <p>MVP - Academia de Muay Thai - v1.1</p>
        </div>
        """, unsafe_allow_html=True)
        log_step("Renderização do header", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao renderizar header: {str(e)}")
    
    # Inicializar autenticação
    step_start = log_step("Inicialização do sistema de autenticação")
    try:
        auth_manager = AuthManager()
        log_step("Inicialização do sistema de autenticação", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao inicializar autenticação: {str(e)}")
        st.error("Erro crítico na autenticação")
        return
    
    # Verificar autenticação
    step_start = log_step("Verificação de autenticação do usuário")
    try:
        if not auth_manager.is_authenticated():
            logger.info("👤 Usuário não autenticado - mostrando tela de login")
            auth_manager.show_login()
            return
        logger.info("✅ Usuário autenticado com sucesso")
        log_step("Verificação de autenticação do usuário", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao verificar autenticação: {str(e)}")
        st.error("Erro ao verificar autenticação")
        return
    
    # Inicializar Firebase com timeout
    firebase_config = None
    step_start = log_step("Inicialização do Firebase")
    try:
        logger.info("🔄 Verificando configuração do Firebase...")
        
        # Verificar se as configurações existem (env vars OU secrets.toml)
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        firebase_project = os.getenv("FIREBASE_PROJECT_ID")
        
        # Verificar secrets.toml com tratamento de erro
        has_secrets = False
        try:
            has_secrets = "firebase" in st.secrets
        except Exception:
            pass  # secrets.toml não existe (produção)
        
        # Ambiente local usa secrets.toml, produção usa env vars
        if not google_creds and not has_secrets:
            logger.error("❌ Credenciais Firebase não encontradas (nem env vars nem secrets.toml)")
            st.error("❌ Credenciais Firebase não configuradas")
            st.info("🔄 Continuando em modo degradado...")
        elif not firebase_project and not has_secrets:
            logger.error("❌ FIREBASE_PROJECT_ID não encontrada")
            st.error("❌ Project ID Firebase não configurado")
            st.info("🔄 Continuando em modo degradado...")
        else:
            # Log apropriado baseado na fonte
            if has_secrets:
                logger.info(f"✅ Configuração encontrada em secrets.toml - Project: {st.secrets['firebase'].get('project_id', 'N/A')}")
            else:
                logger.info(f"✅ Variáveis de ambiente encontradas - Project: {firebase_project}")
            
            logger.info("🔄 Conectando ao Firebase...")
            
            firebase_config = FirebaseConfig()
            
            if firebase_config.is_connected():
                logger.info("✅ Firebase conectado com sucesso!")
                log_step("Inicialização do Firebase", step_start)
            else:
                logger.warning("⚠️ Firebase não conectou - modo degradado")
                st.error("❌ Erro na conexão com Firebase. Verifique as configurações.")
                st.info("Trabalhando em modo offline...")
                
    except Exception as e:
        logger.error(f"❌ EXCEÇÃO ao conectar Firebase: {str(e)}")
        st.error(f"❌ Erro ao conectar com Firebase: {str(e)}")
        st.error("Verifique as variáveis de ambiente FIREBASE_PROJECT_ID e GOOGLE_APPLICATION_CREDENTIALS")
        st.info("🔄 Continuando em modo degradado...")
        # Não retornar - continuar mesmo com erro do Firebase
    
    # Sidebar com navegação
    step_start = log_step("Construção da sidebar e navegação")
    try:
        with st.sidebar:
            st.markdown("### 📋 Navegação")
            
            # Logout
            if st.button("🚪 Logout", type="secondary"):
                logger.info("👤 Usuário fez logout")
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
                    "🥋 Turmas"
                ]
            )
        log_step("Construção da sidebar e navegação", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao construir sidebar: {str(e)}")
        st.error("Erro na navegação")
        return
    
    # Roteamento de páginas
    step_start = log_step(f"Carregamento da página: {page}")
    try:
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
        elif page == "🥋 Turmas":
            from pages.turmas import show_turmas
            show_turmas()
        
        log_step(f"Carregamento da página: {page}", step_start)
        
        # Log final
        total_time = time.time() - start_total
        logger.info(f"🎉 APLICAÇÃO CARREGADA COM SUCESSO em {total_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ ERRO ao carregar página {page}: {str(e)}")
        st.error(f"Erro ao carregar página: {str(e)}")
        return

if __name__ == "__main__":
    main()