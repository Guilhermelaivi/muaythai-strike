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
                    # Suporta caminho relativo (raiz do projeto) e absoluto
                    cred_candidates = [
                        cred_path,
                        str((Path(__file__).resolve().parents[2] / cred_path).resolve()),
                    ]

                    for candidate in cred_candidates:
                        if candidate and os.path.exists(candidate):
                            self.cred = credentials.Certificate(candidate)
                            return

                    raise ValueError(
                        f"Arquivo de credenciais não encontrado. credentials_path='{cred_path}'. "
                        f"Tentativas: {cred_candidates}"
                    )
                else:
                    # Usando credenciais diretamente do secrets
                    firebase_secrets = dict(st.secrets["firebase"])
                    self.cred = credentials.Certificate(firebase_secrets)
                    return
                    
        except (KeyError, FileNotFoundError):
            pass
        
        # Fallback para variáveis de ambiente (produção)
        try:
            # Debug das credenciais
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            project_id = os.getenv("FIREBASE_PROJECT_ID")

            if not google_creds:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS não encontrada")

            # Log de debug (sem expor credenciais)
            print(f"🔧 Tamanho das credenciais: {len(google_creds)} chars")
            print(f"🔧 Project ID: {project_id}")

            # Método 1: Se é um caminho de arquivo
            if os.path.exists(google_creds):
                self.cred = credentials.Certificate(google_creds)
                return

            # Método 2: JSON string - com validação robusta
            google_creds_clean = google_creds.strip()
            try:
                cred_dict = json.loads(google_creds_clean)
            except json.JSONDecodeError as e:
                # Diagnóstico detalhado do erro JSON
                error_context = ""
                if e.pos < len(google_creds_clean):
                    start = max(0, e.pos - 30)
                    end = min(len(google_creds_clean), e.pos + 30)
                    error_context = google_creds_clean[start:end]

                raise ValueError(
                    f"JSON inválido na posição {e.pos}: {e.msg}. Contexto: {error_context}"
                )

            # Validar keys obrigatórias
            required_keys = ["type", "project_id", "private_key_id", "private_key", "client_email"]
            missing_keys = [key for key in required_keys if key not in cred_dict]

            if missing_keys:
                raise ValueError(f"Chaves obrigatórias ausentes no JSON: {missing_keys}")

            # Garantir project_id consistente
            if project_id and cred_dict.get("project_id") != project_id:
                print(f"⚠️ Project ID inconsistente. Usando: {project_id}")
                cred_dict["project_id"] = project_id

            self.cred = credentials.Certificate(cred_dict)
            print("✅ Credenciais Firebase carregadas com sucesso!")
            return

        except Exception as e:
            st.error(f"❌ Erro ao configurar credenciais: {str(e)}")
            st.error(
                """
            **Configuração necessária:**
            1. Adicione as credenciais em `.streamlit/secrets.toml`
            2. Ou configure GOOGLE_APPLICATION_CREDENTIALS

            Exemplo secrets.toml:
            ```toml
            [firebase]
            credentials_path = "caminho/para/service-account-key.json"
            project_id = "seu-project-id"
            ```
            """
            )
            raise
    
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
            
            # Informações de debug - apenas em ambiente local
            import os
            debug_mode = os.getenv("STREAMLIT_DEBUG", "false").lower() == "true"
            if debug_mode:
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