"""
Gerenciador de Autenticação simples e funcional
"""

import streamlit as st
from typing import Optional, Dict, Any
import bcrypt
from pathlib import Path

from utils.ui import render_brand_header

class AuthManager:
    """Classe simples para gerenciar autenticação"""
    
    def __init__(self):
        """Inicializa o gerenciador de autenticação"""
        self._load_config()
    
    def _load_config(self) -> None:
        """Carrega configurações de autenticação - híbrido: secrets.toml ou env vars"""
        import os
        
        try:
            # Tentar carregar do secrets.toml primeiro (desenvolvimento)
            if "credentials" in st.secrets:
                self.credentials = dict(st.secrets["credentials"])
                self.roles = dict(st.secrets["roles"])
                self.cookie_config = dict(st.secrets["cookie"]) if "cookie" in st.secrets else {}
                return
                
        except (KeyError, FileNotFoundError):
            pass
        
        # Fallback para variáveis de ambiente (produção)
        try:
            # Configurar credenciais do admin a partir de env vars
            admin_email = os.getenv("STREAMLIT_ADMIN_EMAIL", "admin@spirith.com")
            admin_name = os.getenv("STREAMLIT_ADMIN_NAME", "Administrador")
            admin_password = os.getenv("STREAMLIT_ADMIN_PASSWORD_HASH", "$2b$12$O1V01ndVPyE4mEXcDG3QqeIaIKLh5WG.9dxzCiPZ1uKJe41H9VxkC")
            
            self.credentials = {
                "usernames": {
                    "admin": {
                        "email": admin_email,
                        "name": admin_name,
                        "password": admin_password
                    }
                }
            }
            
            # Configurar roles
            self.roles = {
                "admin": os.getenv("STREAMLIT_ROLES_ADMIN", "admin")
            }
            
            # Configurar cookie
            self.cookie_config = {
                "name": os.getenv("STREAMLIT_COOKIE_NAME", "dojo_auth_cookie"),
                "key": os.getenv("STREAMLIT_COOKIE_KEY", "dojo_secret_key_2025_streamlit_firebase_mvp_academia_muay_thai_64chars"),
                "expiry_days": int(os.getenv("STREAMLIT_COOKIE_EXPIRY_DAYS", "7"))
            }
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar configuração de autenticação: {e}")
            st.error("Verifique as variáveis de ambiente ou o arquivo .streamlit/secrets.toml")
            st.stop()
    
    def show_login(self) -> None:
        """Exibe o formulário de login"""
        # Centralizar o login e evitar “peças soltas”
        st.markdown(
            """
            <style>
            /* Login: esconder sidebar antes do auth */
            section[data-testid="stSidebar"], div[data-testid="collapsedControl"] { display: none !important; }

            /* Ajustes de espaçamento do topo */
            .block-container { padding-top: 2rem; }

            /* Botão de submit mais consistente */
            div.stButton > button, div.stFormSubmitButton > button {
                border-radius: 10px;
                padding: 0.75rem 1rem;
                font-weight: 600;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1.1, 1.3, 1.1])

        with col2:
            # Branding: usar pranch.png (mais “hero”) no login
            root_dir = Path(__file__).resolve().parents[2]
            pranch_path = root_dir / "pranch.png"

            render_brand_header(
                title="Spirith Muay thai",
                subtitle="Faça login para acessar o sistema",
                logo_path=pranch_path if pranch_path.exists() else (root_dir / "elefantecontorno.png"),
                logo_width_px=640,
                container_class="brand-header-login",
            )

            st.markdown("### 🔐 Acesso ao Sistema")
            st.caption("Use seu usuário e senha para entrar")

            # Formulário simples e funcional
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Usuário", placeholder="Digite seu usuário")
                password = st.text_input("Senha", type="password", placeholder="Digite sua senha")

                submit = st.form_submit_button(
                    "Entrar",
                    use_container_width=True,
                    type="primary",
                )

                if submit:
                    if not username or not password:
                        st.error("❌ Por favor, preencha usuário e senha")
                    else:
                        if self._validate_credentials(username, password):
                            st.session_state['authentication_status'] = True
                            st.session_state['name'] = self.credentials['usernames'][username]['name']
                            st.session_state['username'] = username
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos")
        
        # Informações de desenvolvimento - apenas em ambiente local
        import os
        debug_mode = os.getenv("STREAMLIT_DEBUG", "false").lower() == "true"
            
        if debug_mode:
            with st.expander("ℹ️ Informações de Desenvolvimento"):
                st.info("""
                **Credenciais (modo dev):**
                - Usuário: `admin`

                **Senha**
                - A senha não é exibida aqui (usa bcrypt).
                - Configure via `.streamlit/secrets.toml` (chave `credentials.usernames.admin.password`) ou via env `STREAMLIT_ADMIN_PASSWORD_HASH`.
                """)
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Valida credenciais do usuário"""
        try:
            if username in self.credentials.get('usernames', {}):
                stored_password = self.credentials['usernames'][username]['password']
                # Usar bcrypt para verificar a senha
                return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            return False
        except Exception as e:
            st.error(f"Erro na validação: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Verifica se o usuário está autenticado"""
        return st.session_state.get('authentication_status', False)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna informações do usuário atual"""
        if self.is_authenticated():
            return {
                'name': st.session_state.get('name'),
                'username': st.session_state.get('username'),
                'role': self.get_user_role()
            }
        return None
    
    def get_user_role(self) -> Optional[str]:
        """Retorna o papel do usuário atual"""
        username = st.session_state.get('username')
        if username:
            return self.roles.get(username, 'user')
        return None
    
    def is_admin(self) -> bool:
        """Verifica se o usuário atual é admin"""
        return self.get_user_role() == 'admin'
    
    def logout(self) -> None:
        """Realiza logout do usuário"""
        # Limpar session state
        for key in list(st.session_state.keys()):
            if key.startswith('authentication'):
                del st.session_state[key]
            if key in ['name', 'username']:
                del st.session_state[key]
    
    def show_user_info(self) -> None:
        """Exibe informações do usuário na sidebar"""
        user = self.get_current_user()
        if user:
            st.sidebar.markdown(f"""
            **👤 Usuário:** {user['name']}  
            **🔑 Papel:** {user['role']}
            """)