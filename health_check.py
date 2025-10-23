"""
Health Check simples para teste de deploy
"""
import streamlit as st
import os
import sys
import time
from datetime import datetime

st.set_page_config(
    page_title="Health Check",
    page_icon="✅",
    layout="wide"
)

st.title("🔍 Health Check - Dojo System")
st.write(f"⏰ Timestamp: {datetime.now()}")

# Verificar variáveis de ambiente
st.subheader("🔧 Variáveis de Ambiente")
env_vars = {
    "PORT": os.getenv("PORT"),
    "FIREBASE_PROJECT_ID": os.getenv("FIREBASE_PROJECT_ID"),
    "GOOGLE_APPLICATION_CREDENTIALS": "CONFIGURADO" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else "NÃO CONFIGURADO"
}

for key, value in env_vars.items():
    st.write(f"- **{key}**: {value}")

# Teste de imports
st.subheader("📦 Teste de Imports")
try:
    import firebase_admin
    st.success("✅ firebase_admin importado com sucesso")
except Exception as e:
    st.error(f"❌ Erro ao importar firebase_admin: {e}")

try:
    from pathlib import Path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    from utils.firebase_config import FirebaseConfig
    st.success("✅ FirebaseConfig importado com sucesso")
except Exception as e:
    st.error(f"❌ Erro ao importar FirebaseConfig: {e}")

try:
    from utils.auth import AuthManager
    st.success("✅ AuthManager importado com sucesso")
except Exception as e:
    st.error(f"❌ Erro ao importar AuthManager: {e}")

# Teste básico de funcionamento
st.subheader("🎯 Teste Básico")
if st.button("Testar Botão"):
    st.balloons()
    st.success("✅ Aplicação funcionando!")

st.write("---")
st.info("✅ Se você está vendo esta página, o Streamlit está funcionando!")