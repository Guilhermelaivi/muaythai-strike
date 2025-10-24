#!/usr/bin/env python3
"""
🚀 RAILWAY DEPLOY - Script de inicialização forçada
"""

import os
import sys
import subprocess
import time

def main():
    print("=" * 50)
    print("🚀 RAILWAY STARTUP SCRIPT")
    print("=" * 50)
    
    # Debug completo do ambiente
    print("🔧 INFORMAÇÕES DO AMBIENTE:")
    port = os.environ.get('PORT', '8501')
    print(f"   📡 Porta Railway: {port}")
    print(f"   🐍 Python: {sys.version}")
    print(f"   📁 Diretório: {os.getcwd()}")
    
    # Verificar Railway vars
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'Não encontrada')
    railway_service = os.environ.get('RAILWAY_SERVICE_NAME', 'Não encontrada')
    print(f"   � Railway Environment: {railway_env}")
    print(f"   🏷️  Railway Service: {railway_service}")
    
    # Verificar se arquivo existe
    if not os.path.exists('test_basic.py'):
        print("❌ ERRO: test_basic.py não encontrado!")
        sys.exit(1)
    else:
        print("✅ test_basic.py encontrado")
    
    # Comando direto para Railway
    cmd = [
        'streamlit', 'run', 'test_basic.py',
        f'--server.port={port}',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false'
    ]
    
    print("=" * 50)
    print("🔥 COMANDO STREAMLIT:")
    print(f"   {' '.join(cmd)}")
    print("=" * 50)
    
    # Aguardar um pouco para garantir que logs apareçam
    time.sleep(2)
    
    # Executar
    try:
        print("🚀 INICIANDO STREAMLIT...")
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("❌ ERRO: Comando 'streamlit' não encontrado!")
        print("📦 Verificando instalação...")
        try:
            import streamlit
            print(f"✅ Streamlit {streamlit.__version__} instalado")
            # Tentar comando alternativo
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'test_basic.py', f'--server.port={port}', '--server.address=0.0.0.0', '--server.headless=true'])
        except Exception as e2:
            print(f"❌ ERRO CRÍTICO: {e2}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()