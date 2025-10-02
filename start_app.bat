@echo off
echo.
echo ========================================
echo    🚀 Dojo Management System
echo ========================================
echo.
echo ⚡ Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro: Ambiente virtual não encontrado!
    echo 💡 Execute: python -m venv venv
    pause
    exit /b 1
)

echo.
echo 📦 Verificando dependências...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências!
    pause
    exit /b 1
)

echo.
echo 🌐 Iniciando Streamlit...
echo.
echo ========================================
echo 📍 URL: http://localhost:8501
echo 🔑 Login: admin / admin123
echo ========================================
echo.
echo 💡 Pressione Ctrl+C para parar o servidor
echo.

streamlit run app.py --server.port=8501

echo.
echo 👋 Aplicação encerrada
pause