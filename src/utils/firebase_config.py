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
        """Configura as credenciais do Firebase - híbrido: secrets.toml ou env vars"""
        import json
        
        try:
            # Tentar carregar de secrets primeiro (desenvolvimento)
            if "firebase" in st.secrets:
                if "credentials_path" in st.secrets["firebase"]:
                    cred_path = st.secrets["firebase"]["credentials_path"]
                    if os.path.exists(cred_path):
                        self.cred = credentials.Certificate(cred_path)
                        return
                else:
                    # Usando credenciais diretamente do secrets
                    firebase_secrets = dict(st.secrets["firebase"])
                    self.cred = credentials.Certificate(firebase_secrets)
                    return
                    
        except (KeyError, FileNotFoundError):
            pass
        
        # Fallback para variáveis de ambiente (produção)
        try:
            # Método 1: GOOGLE_APPLICATION_CREDENTIALS como JSON string
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if google_creds:
                # Se é um caminho de arquivo
                if os.path.exists(google_creds):
                    self.cred = credentials.Certificate(google_creds)
                else:
                    # Se é o JSON como string (Render)
                    cred_dict = json.loads(google_creds)
                    self.cred = credentials.Certificate(cred_dict)
                return
            
            # Método 2: Usando project_id separadamente
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            if project_id and google_creds:
                cred_dict = json.loads(google_creds)
                # Garantir que project_id está correto
                cred_dict["project_id"] = project_id
                self.cred = credentials.Certificate(cred_dict)
                return
                
            raise ValueError("Credenciais do Firebase não encontradas nas variáveis de ambiente")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar credenciais JSON: {e}")
        except Exception as e:
            raise ValueError(f"Erro ao configurar credenciais Firebase: {e}")
        
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

# Instância global para reutilização
_firebase_instance: Optional[FirebaseConfig] = None

def get_firestore_client() -> firestore.Client:
    """
    Função utilitária para obter cliente Firestore
    Reutiliza instância existente ou cria nova
    """
    global _firebase_instance
    
    if _firebase_instance is None:
        _firebase_instance = FirebaseConfig()
    
    return _firebase_instance.get_db()