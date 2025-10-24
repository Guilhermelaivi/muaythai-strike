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
    print("🚀 DOJO MANAGEMENT SYSTEM - Railway Deploy")
    
    # Obter porta do Railway
    port = os.environ.get('PORT', '8501')
    entry = os.environ.get('ENTRYPOINT', 'app.py')  # Projeto REAL com Firestore
    
    print(f"� Entry: {entry}")
    print(f"�📡 Porta (env PORT): {port}")
    
    # Verificar arquivo
    if not os.path.exists(entry):
        print(f"❌ {entry} não encontrado!")
        sys.exit(1)
    
    # Comando otimizado
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', entry,
        '--server.port', str(port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false'
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