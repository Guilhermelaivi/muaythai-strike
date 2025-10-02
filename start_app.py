#!/usr/bin/env python3
"""
🚀 Dojo Management System - Startup Script
Ativa ambiente virtual e inicia a aplicação Streamlit
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Exibe banner de inicialização"""
    print("\n" + "=" * 50)
    print("    🚀 Dojo Management System")
    print("=" * 50)
    print("📍 URL: http://localhost:8501")
    print("🔑 Login: admin / admin123")
    print("=" * 50)
    print()

def check_venv():
    """Verifica se o ambiente virtual existe"""
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        python_path = os.path.join("venv", "Scripts", "python.exe")
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
    else:
        python_path = os.path.join("venv", "bin", "python")
        pip_path = os.path.join("venv", "bin", "pip")
    
    if not os.path.exists(python_path):
        print("❌ Erro: Ambiente virtual não encontrado!")
        print("💡 Execute: python -m venv venv")
        return None, None
    
    return python_path, pip_path

def install_dependencies(pip_path):
    """Instala dependências do requirements.txt"""
    print("📦 Verificando dependências...")
    
    if not os.path.exists("requirements.txt"):
        print("⚠️  Arquivo requirements.txt não encontrado")
        return True
    
    try:
        result = subprocess.run([
            pip_path, "install", "-q", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Erro ao instalar dependências:")
            print(result.stderr)
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao executar pip: {e}")
        return False

def start_streamlit(python_path):
    """Inicia a aplicação Streamlit"""
    print("🌐 Iniciando Streamlit...")
    print()
    print("💡 Pressione Ctrl+C para parar o servidor")
    print()
    
    try:
        subprocess.run([
            python_path, "-m", "streamlit", "run", "app.py", 
            "--server.port=8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar Streamlit: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print_banner()
    
    # Verifica se estamos no diretório correto
    if not os.path.exists("app.py"):
        print("❌ Erro: app.py não encontrado!")
        print("💡 Execute este script no diretório raiz do projeto")
        input("Pressione Enter para sair...")
        return
    
    print("⚡ Verificando ambiente virtual...")
    python_path, pip_path = check_venv()
    
    if not python_path:
        input("Pressione Enter para sair...")
        return
    
    # Instala dependências
    if not install_dependencies(pip_path):
        input("Pressione Enter para sair...")
        return
    
    # Inicia aplicação
    start_streamlit(python_path)
    
    print("\n👋 Script finalizado")

if __name__ == "__main__":
    main()