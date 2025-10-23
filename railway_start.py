#!/usr/bin/env python3
"""
🚀 RAILWAY DEPLOY - Script de inicialização forçada
"""

import os
import sys
import subprocess

def main():
    print("🚀 RAILWAY STARTUP SCRIPT")
    
    # Obter porta do Railway
    port = os.environ.get('PORT', '8501')
    print(f"🔧 Porta Railway: {port}")
    
    # Comando direto para Railway
    cmd = [
        'streamlit', 'run', 'test_basic.py',
        f'--server.port={port}',
        '--server.address=0.0.0.0',
        '--server.headless=true'
    ]
    
    print(f"🔥 Comando: {' '.join(cmd)}")
    
    # Executar
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()