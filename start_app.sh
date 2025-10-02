#!/bin/bash

echo ""
echo "========================================"
echo "   🚀 Dojo Management System"
echo "========================================"
echo ""

echo "⚡ Ativando ambiente virtual..."
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado!"
    echo "💡 Execute: python3 -m venv venv"
    read -p "Pressione Enter para sair..."
    exit 1
fi

source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Erro ao ativar ambiente virtual!"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo ""
echo "📦 Verificando dependências..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências!"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo ""
echo "🌐 Iniciando Streamlit..."
echo ""
echo "========================================"
echo "📍 URL: http://localhost:8501"
echo "🔑 Login: admin / admin123"
echo "========================================"
echo ""
echo "💡 Pressione Ctrl+C para parar o servidor"
echo ""

streamlit run app.py --server.port=8501

echo ""
echo "👋 Aplicação encerrada"