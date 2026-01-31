"""
Sistema de Gestão para Academia - MVP
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
logger.info("🚀 INICIANDO APLICAÇÃO SPIRITH MUAY THAI")
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
    from utils.ui import render_brand_header
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
            page_title="Spirith Muay thai",
            page_icon="elefantecontorno.png",
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
            background: linear-gradient(90deg, #282828 0%, #000000 100%);
            padding: 1rem;
            border-radius: 10px;
            color: #F8F8F8;
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 3px solid #881818;
        }
        .metric-card {
            background-color: #FFFFFF;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #D8D8D8;
            border-left: 4px solid #881818;
        }
        </style>
        """, unsafe_allow_html=True)
        log_step("Aplicação de CSS customizado", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao aplicar CSS: {str(e)}")
        # Continuar mesmo com erro de CSS
    
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
        # Verificar se ainda está carregando cookie (evita flash da tela de login)
        if auth_manager.is_checking_auth():
            logger.info("⏳ Aguardando carregamento do cookie de autenticação...")
            auth_manager.show_loading()
            return
        
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

    # Header principal (somente após login)
    step_start = log_step("Renderização do header")
    try:
        root_dir = Path(__file__).parent
        pranch_path = root_dir / "pranch.png"
        render_brand_header(
            title="Spirith Muay thai",
            subtitle="Gestão para academia de Muay Thai",
            logo_path=pranch_path if pranch_path.exists() else (root_dir / "elefantecontorno.png"),
            logo_width_px=480,
            container_class="brand-header-main",
        )
        log_step("Renderização do header", step_start)
    except Exception as e:
        logger.error(f"❌ ERRO ao renderizar header: {str(e)}")
    
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
        # Inicializar página padrão se não existir
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Dashboard"

        # Modo de dados (operacional vs histórico)
        if 'data_mode' not in st.session_state:
            st.session_state.data_mode = 'operacional'

        # Guard rail: histórico é somente dashboard
        if st.session_state.data_mode == 'historico' and st.session_state.current_page != "🏠 Dashboard":
            st.session_state.current_page = "🏠 Dashboard"
        
        with st.sidebar:
            st.markdown("### 📋 Navegação")
            
            # Logout
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logger.info("👤 Usuário fez logout")
                auth_manager.logout()
                st.rerun()
            
            st.divider()
            
            # Página principal - sempre visível
            st.markdown("#### Principal")
            if st.button("🏠 Dashboard (2026+)", use_container_width=True, 
                        type="primary" if st.session_state.current_page == "🏠 Dashboard" else "secondary"):
                st.session_state.current_page = "🏠 Dashboard"
                st.session_state.data_mode = 'operacional'
                st.rerun()
            
            st.divider()
            
            # Páginas mais utilizadas
            if st.session_state.data_mode != 'historico':
                st.markdown("#### Mais Utilizados")
                
                if st.button("👥 Alunos", use_container_width=True,
                            type="primary" if st.session_state.current_page == "👥 Alunos" else "secondary"):
                    st.session_state.current_page = "👥 Alunos"
                    st.rerun()
                
                if st.button("✅ Presenças", use_container_width=True,
                            type="primary" if st.session_state.current_page == "✅ Presenças" else "secondary"):
                    st.session_state.current_page = "✅ Presenças"
                    st.rerun()
                
                if st.button("💰 Pagamentos", use_container_width=True,
                            type="primary" if st.session_state.current_page == "💰 Pagamentos" else "secondary"):
                    st.session_state.current_page = "💰 Pagamentos"
                    st.rerun()
                
                st.divider()
                
                # Páginas auxiliares
                st.markdown("#### Outros")
                
                if st.button("👨‍👩‍👧‍👦 Turmas", use_container_width=True,
                            type="primary" if st.session_state.current_page == "👨‍👩‍👧‍👦 Turmas" else "secondary"):
                    st.session_state.current_page = "👨‍👩‍👧‍👦 Turmas"
                    st.rerun()
                
                if st.button("🥋 Graduações", use_container_width=True,
                            type="primary" if st.session_state.current_page == "🥋 Graduações" else "secondary"):
                    st.session_state.current_page = "🥋 Graduações"
                    st.rerun()
            else:
                st.info("Modo histórico ativo: apenas consulta")

            st.divider()

            # Histórico - somente leitura (menos usado, fica no final)
            with st.expander("📚 Histórico (somente leitura)", expanded=False):
                st.caption("Dashboard de 2024/2025 para consulta")
                if st.button("Abrir histórico", use_container_width=True):
                    st.session_state.current_page = "🏠 Dashboard"
                    st.session_state.data_mode = 'historico'
                    st.rerun()
        
        page = st.session_state.current_page
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
            mode = st.session_state.get('data_mode', 'operacional')
            show_dashboard(mode=mode)
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
        elif page == "👨‍👩‍👧‍👦 Turmas":
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