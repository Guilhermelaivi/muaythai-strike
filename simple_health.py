import streamlit as st
import base64
from pathlib import Path

# Configurar página com favicon
st.set_page_config(
    page_title="Dojo Health Check",
    page_icon="🥋",
    layout="wide"
)

# Tentar adicionar favicon via HTML
favicon_path = Path(__file__).parent / "favicon.ico"
if favicon_path.exists():
    # Ler favicon e converter para base64
    with open(favicon_path, "rb") as f:
        favicon_data = f.read()
        favicon_b64 = base64.b64encode(favicon_data).decode()
    
    # Adicionar favicon via HTML
    st.markdown(f"""
    <link rel="shortcut icon" href="data:image/x-icon;base64,{favicon_b64}">
    <link rel="icon" href="data:image/x-icon;base64,{favicon_b64}">
    """, unsafe_allow_html=True)

st.title("🚀 Health Check Simples")
st.write("✅ Aplicação funcionando!")
st.write("🔥 Railway Deploy OK!")
st.write("🥋 Favicon configurado!")

# Verificar se favicon existe
if favicon_path.exists():
    st.success("✅ Favicon.ico encontrado!")
    st.write(f"📁 Tamanho: {favicon_path.stat().st_size} bytes")
else:
    st.error("❌ Favicon.ico não encontrado!")