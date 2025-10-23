#!/bin/bash

# Railway Startup Script for Streamlit
echo "🚀 Iniciando Dojo Management System..."

# Verificar variáveis de ambiente
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ GOOGLE_APPLICATION_CREDENTIALS não definida"
    exit 1
fi

if [ -z "$FIREBASE_PROJECT_ID" ]; then
    echo "❌ FIREBASE_PROJECT_ID não definida"
    exit 1
fi

# Definir porta padrão se não especificada
export PORT=${PORT:-8501}

echo "✅ Configurações verificadas"
echo "📡 Porta: $PORT"
echo "🔥 Firebase Project: $FIREBASE_PROJECT_ID"

# Executar Streamlit
exec streamlit run app.py \
    --server.port $PORT \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.address 0.0.0.0