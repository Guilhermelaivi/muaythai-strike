"""
App Ultra-Simples para teste - ZERO dependências
"""
import streamlit as st
import os

# Configurar página básica
st.set_page_config(
    page_title="Dojo Test", 
    page_icon="🥋"
)

# Mostrar informações de debug
st.title("🚀 TESTE BÁSICO")
st.success("✅ Streamlit funcionando!")

# Debug de porta
port = os.getenv('PORT', '8501')
st.write(f"🔧 PORT detectada: {port}")

# Debug de ambiente
st.write("🔧 Variáveis de ambiente:")
for key in ['PORT', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME']:
    value = os.getenv(key, 'Não encontrada')
    st.write(f"- {key}: {value}")

# Teste básico de funcionalidade
if st.button("Testar"):
    st.balloons()
    st.success("🎉 APLICAÇÃO FUNCIONANDO!")