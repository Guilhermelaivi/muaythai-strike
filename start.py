#!/usr/bin/env python3
"""
🚀 RAILWAY - Script Único Simplificado
"""

import os
import sys
import subprocess
import time
import signal

# Variável global para controle
RUNNING = True

def signal_handler(signum, frame):
    global RUNNING
    RUNNING = False
    print("🛑 Recebido sinal de parada")
    sys.exit(0)

# Registrar handler para sinais
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    print("🚀 STARTUP ÚNICO - Railway Deploy")
    
    # Obter porta
    port = os.environ.get('PORT', '8501')
    print(f"📡 Porta: {port}")
    
    # Verificar arquivo
    if not os.path.exists('test_basic.py'):
        print("❌ test_basic.py não encontrado!")
        sys.exit(1)
    
    # Comando simples
    cmd = [
        'streamlit', 'run', 'test_basic.py',
        f'--server.port={port}',
        '--server.address=0.0.0.0',
        '--server.headless=true'
    ]
    
    print(f"🔥 Executando: {' '.join(cmd)}")
    
    try:
        # Executar e manter vivo
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("🛑 Parando...")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()