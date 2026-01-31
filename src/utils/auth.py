"""
Gerenciador de Autenticação simples e funcional
Com persistência de sessão via cookie HMAC-SHA256
"""

import streamlit as st
from typing import Optional, Dict, Any
import bcrypt
import hmac
import hashlib
import time
from pathlib import Path

from utils.ui import render_brand_header

# Importar CookieManager para persistência
try:
    from extra_streamlit_components import CookieManager
    COOKIE_MANAGER_AVAILABLE = True
except ImportError:
    COOKIE_MANAGER_AVAILABLE = False


class AuthManager:
    """Classe simples para gerenciar autenticação com persistência via cookie"""
    
    # Controle de tentativas de reidratação (evita loop infinito)
    _REHYDRATION_KEY = '_auth_rehydration_attempted'
    _REHYDRATION_MAX_ATTEMPTS = 2
    
    def __init__(self):
        """Inicializa o gerenciador de autenticação"""
        self._load_config()
        self._init_cookie_manager()
        # Tentar reidratar sessão do cookie no início
        self._rehydrate_session_from_cookie()
    
    def _init_cookie_manager(self) -> None:
        """Inicializa o gerenciador de cookies"""
        if COOKIE_MANAGER_AVAILABLE:
            # Usar key única para evitar conflitos
            self.cookie_manager = CookieManager(key="dojo_cookie_manager")
        else:
            self.cookie_manager = None
    
    def _create_auth_token(self, username: str) -> str:
        """
        Cria token de autenticação HMAC-SHA256
        Formato: username:expiry_timestamp:signature
        """
        secret_key = self.cookie_config.get('key', 'default_secret_key')
        expiry_days = self.cookie_config.get('expiry_days', 7)
        
        # Calcular timestamp de expiração
        expiry_timestamp = int(time.time()) + (expiry_days * 24 * 60 * 60)
        
        # Criar payload
        payload = f"{username}:{expiry_timestamp}"
        
        # Criar assinatura HMAC-SHA256
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Token final: payload:signature
        return f"{payload}:{signature}"
    
    def _validate_auth_token(self, token: str) -> Optional[str]:
        """
        Valida token de autenticação e retorna username se válido
        Retorna None se inválido ou expirado
        """
        try:
            if not token:
                return None
            
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            username, expiry_str, provided_signature = parts
            
            # Verificar expiração
            expiry_timestamp = int(expiry_str)
            if time.time() > expiry_timestamp:
                return None  # Token expirado
            
            # Verificar se usuário existe
            if username not in self.credentials.get('usernames', {}):
                return None
            
            # Recalcular assinatura para verificar
            secret_key = self.cookie_config.get('key', 'default_secret_key')
            payload = f"{username}:{expiry_str}"
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Comparação segura contra timing attacks
            if hmac.compare_digest(provided_signature, expected_signature):
                return username
            
            return None
            
        except Exception:
            return None
    
    def _save_auth_cookie(self, username: str) -> None:
        """Salva cookie de autenticação"""
        if not self.cookie_manager:
            return
        
        try:
            token = self._create_auth_token(username)
            cookie_name = self.cookie_config.get('name', 'dojo_auth_cookie')
            expiry_days = self.cookie_config.get('expiry_days', 7)
            
            # Salvar cookie
            self.cookie_manager.set(
                cookie_name,
                token,
                expires_at=None,  # Gerenciado pelo próprio token
                key=f"set_{cookie_name}"
            )
        except Exception as e:
            # Log silencioso - não quebrar o fluxo
            import logging
            logging.getLogger('AuthManager').warning(f"Erro ao salvar cookie: {e}")
    
    def _get_auth_cookie(self) -> Optional[str]:
        """Recupera cookie de autenticação"""
        if not self.cookie_manager:
            return None
        
        try:
            cookie_name = self.cookie_config.get('name', 'dojo_auth_cookie')
            return self.cookie_manager.get(cookie_name)
        except Exception:
            return None
    
    def _delete_auth_cookie(self) -> None:
        """Remove cookie de autenticação"""
        if not self.cookie_manager:
            return
        
        try:
            cookie_name = self.cookie_config.get('name', 'dojo_auth_cookie')
            self.cookie_manager.delete(cookie_name, key=f"delete_{cookie_name}")
        except Exception:
            pass
    
    def _rehydrate_session_from_cookie(self) -> bool:
        """
        Tenta restaurar sessão a partir do cookie (reidratação)
        Retorna True se conseguiu restaurar, False caso contrário
        """
        # Se logout foi solicitado, não reidratar (limpar flag após verificar)
        if st.session_state.get('_logout_requested', False):
            # Manter a flag por mais um ciclo para garantir que cookie foi deletado
            logout_cycles = st.session_state.get('_logout_cycles', 0)
            if logout_cycles >= 1:
                # Limpar flags de logout após cookie ser deletado
                st.session_state.pop('_logout_requested', None)
                st.session_state.pop('_logout_cycles', None)
            else:
                st.session_state['_logout_cycles'] = logout_cycles + 1
            return False
        
        # Se já está autenticado no session_state, não precisa reidratar
        if st.session_state.get('authentication_status', False):
            return True
        
        # Tentar ler cookie
        token = self._get_auth_cookie()
        if not token:
            return False
        
        # Validar token
        username = self._validate_auth_token(token)
        if not username:
            # Token inválido ou expirado - limpar cookie
            self._delete_auth_cookie()
            return False
        
        # Restaurar sessão
        user_data = self.credentials.get('usernames', {}).get(username, {})
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.session_state['name'] = user_data.get('name', username)
        
        # Marcar que reidratação foi bem sucedida
        st.session_state['_auth_rehydrated'] = True
        
        return True
    
    def is_checking_auth(self) -> bool:
        """
        Verifica se ainda está no processo de checar autenticação via cookie.
        O CookieManager precisa de 1-2 renders para carregar o cookie.
        Retorna True se deve aguardar, False se já pode decidir.
        """
        # Se já está autenticado, não está mais checando
        if st.session_state.get('authentication_status', False):
            return False
        
        # Se já reidratou com sucesso antes, não está checando
        if st.session_state.get('_auth_rehydrated', False):
            return False
        
        # Controlar tentativas de reidratação
        attempts = st.session_state.get(self._REHYDRATION_KEY, 0)
        
        # Se ainda não tentou o suficiente e tem cookie manager, aguardar
        if attempts < self._REHYDRATION_MAX_ATTEMPTS and self.cookie_manager:
            st.session_state[self._REHYDRATION_KEY] = attempts + 1
            return True
        
        return False
    
    def show_loading(self) -> None:
        """
        Exibe tela de carregamento enquanto verifica autenticação.
        Evita o 'flash' da tela de login durante reidratação.
        """
        # Esconder sidebar durante loading
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"], div[data-testid="collapsedControl"] { display: none !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        # Centralizar loading
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.spinner("Verificando autenticação...")
            # Forçar rerun para tentar novamente
            time.sleep(0.1)
            st.rerun()
    
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
                            # Salvar no session_state
                            st.session_state['authentication_status'] = True
                            st.session_state['name'] = self.credentials['usernames'][username]['name']
                            st.session_state['username'] = username
                            
                            # Definir Dashboard como página padrão após login
                            st.session_state['current_page'] = "🏠 Dashboard"
                            st.session_state['data_mode'] = 'operacional'
                            
                            # Persistir em cookie para sobreviver ao F5
                            self._save_auth_cookie(username)
                            
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
        # Marcar que logout foi solicitado (impede reidratação)
        st.session_state['_logout_requested'] = True
        
        # Limpar cookie de autenticação
        self._delete_auth_cookie()
        
        # Limpar session state (exceto a flag de logout)
        for key in list(st.session_state.keys()):
            if key == '_logout_requested':
                continue
            if key.startswith('authentication') or key.startswith('_auth'):
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