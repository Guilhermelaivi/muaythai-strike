"""
Configuração e conexão com Firebase/Firestore
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
import os
from pathlib import Path

class FirebaseConfig:
    """Classe para gerenciar configuração e conexão com Firebase"""
    
    def __init__(self):
        """Inicializa a configuração do Firebase"""
        self.db: Optional[firestore.Client] = None
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Inicializa a conexão com Firebase"""
        try:
            # Verificar se já foi inicializado
            if not firebase_admin._apps:
                self._setup_credentials()
                
                # Inicializar Firebase Admin
                firebase_admin.initialize_app(self.cred)
            
            # Obter cliente Firestore
            self.db = firestore.client()
            
        except Exception as e:
            st.error(f"❌ Erro ao inicializar Firebase: {str(e)}")
            raise e
    
    def _setup_credentials(self) -> None:
        """Configura as credenciais do Firebase"""
        try:
            # Tentar carregar de secrets primeiro
            if "firebase" in st.secrets:
                # Usando service account key do secrets
                if "credentials_path" in st.secrets["firebase"]:
                    cred_path = st.secrets["firebase"]["credentials_path"]
                    if os.path.exists(cred_path):
                        self.cred = credentials.Certificate(cred_path)
                    else:
                        raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {cred_path}")
                else:
                    # Usando credenciais diretamente do secrets (para Streamlit Cloud)
                    firebase_secrets = dict(st.secrets["firebase"])
                    self.cred = credentials.Certificate(firebase_secrets)
            else:
                # Fallback para variável de ambiente
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path and os.path.exists(cred_path):
                    self.cred = credentials.Certificate(cred_path)
                else:
                    raise ValueError("Credenciais do Firebase não configuradas")
        
        except Exception as e:
            st.error(f"❌ Erro ao configurar credenciais: {str(e)}")
            st.error("""
            **Configuração necessária:**
            1. Adicione as credenciais em `.streamlit/secrets.toml`
            2. Ou configure GOOGLE_APPLICATION_CREDENTIALS
            
            Exemplo secrets.toml:
            ```toml
            [firebase]
            credentials_path = "caminho/para/service-account-key.json"
            project_id = "seu-project-id"
            ```
            """)
            raise e
    
    def is_connected(self) -> bool:
        """Verifica se a conexão com Firestore está ativa"""
        try:
            if self.db is None:
                return False
            
            # Teste simples de conexão
            collections = list(self.db.collections())
            return True
        except Exception:
            return False
    
    def get_db(self) -> firestore.Client:
        """Retorna o cliente Firestore"""
        if self.db is None:
            raise ValueError("Firestore não está conectado")
        return self.db
    
    def test_connection(self) -> bool:
        """Testa a conexão e exibe informações"""
        try:
            if not self.is_connected():
                return False
            
            # Informações de debug
            if st.secrets.get("environment", {}).get("debug", False):
                st.success("✅ Conexão com Firestore estabelecida!")
                
                # Listar coleções existentes
                collections = [coll.id for coll in self.db.collections()]
                if collections:
                    st.info(f"📂 Coleções encontradas: {', '.join(collections)}")
                else:
                    st.info("📂 Nenhuma coleção encontrada (banco vazio)")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro no teste de conexão: {str(e)}")
            return False