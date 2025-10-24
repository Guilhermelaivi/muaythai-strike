#!/usr/bin/env python3
"""
🚀 RAILWAY DEPLOY - Script FINAL com Health Check
"""

import os
import sys
import subprocess
import time
import socket
import threading
from contextlib import closing

def check_port_open(port, timeout=5):
    """Verifica se a porta está aberta e aceitando conexões"""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', int(port)))
            return result == 0
    except:
        return False

def wait_for_streamlit(port, max_wait=60):
    """Aguarda o Streamlit estar pronto"""
    print(f"⏳ Aguardando Streamlit na porta {port}...")
    
    for i in range(max_wait):
        if check_port_open(port):
            print(f"✅ Streamlit respondendo na porta {port}!")
            return True
        
        if i % 10 == 0:  # Log a cada 10 segundos
            print(f"⏳ Aguardando... ({i}s/{max_wait}s)")
        
        time.sleep(1)
    
    print(f"❌ Timeout: Streamlit não respondeu em {max_wait}s")
    return False

def main():
    print("=" * 70)
    print("🚀 RAILWAY STARTUP SCRIPT - VERSÃO FINAL COM HEALTH CHECK")
    print("=" * 70)
    
    # Detectar porta
    port = os.environ.get('PORT', '8501')
    print(f"🎯 Porta detectada: {port}")
    
    # Verificar se Streamlit está instalado
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} instalado")
    except ImportError:
        print("❌ Streamlit não encontrado!")
        sys.exit(1)
    
    # Verificar arquivo
    if not os.path.exists('test_basic.py'):
        print("❌ test_basic.py não encontrado!")
        sys.exit(1)
    
    print("✅ test_basic.py encontrado")
    
    # Comando Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'test_basic.py',
        f'--server.port={port}',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.runOnSave=false',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false',
        '--logger.level=error'  # Reduzir logs para Railway
    ]
    
    print("🔥 Comando:")
    print(f"   {' '.join(cmd)}")
    print("=" * 70)
    
    # Executar Streamlit em background
    print("🚀 Iniciando Streamlit...")
    
    try:
        # Iniciar processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Dar tempo para inicializar
        time.sleep(5)
        
        # Verificar se processo ainda está rodando
        if process.poll() is not None:
            print("❌ Processo Streamlit falhou!")
            output = process.stdout.read()
            print(f"Saída: {output}")
            sys.exit(1)
        
        print("✅ Processo Streamlit iniciado")
        
        # Aguardar Streamlit estar pronto
        if wait_for_streamlit(port, max_wait=30):
            print("=" * 70)
            print("🎉 SUCESSO! Streamlit está rodando e respondendo!")
            print(f"🌐 URL: http://0.0.0.0:{port}")
            print("=" * 70)
            
            # Manter processo vivo
            try:
                process.wait()
            except KeyboardInterrupt:
                print("🛑 Parando aplicação...")
                process.terminate()
        else:
            print("❌ Falha no health check")
            process.terminate()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()